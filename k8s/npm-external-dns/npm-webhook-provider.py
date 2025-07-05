#!/usr/bin/env python3
"""
External-DNS Webhook Provider for Nginx Proxy Manager
This webhook provider allows External-DNS to manage NPM proxy hosts automatically
"""

import os
import json
import logging
import requests
from flask import Flask, request, jsonify
from typing import Dict, List, Optional
import re

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
NPM_URL = os.getenv('NPM_URL', 'http://192.168.50.215:81')
NPM_EMAIL = os.getenv('NPM_EMAIL', 'admin@example.com')
NPM_PASSWORD = os.getenv('NPM_PASSWORD', 'changeme')
DEFAULT_FORWARD_SCHEME = os.getenv('DEFAULT_FORWARD_SCHEME', 'http')
DEFAULT_FORWARD_PORT = os.getenv('DEFAULT_FORWARD_PORT', '80')

# Kubernetes node IPs (can be dynamically discovered)
K8S_NODES = os.getenv('K8S_NODES', '192.168.50.110,192.168.50.100').split(',')


class NPMClient:
    """Nginx Proxy Manager API Client"""
    
    def __init__(self, url: str, email: str, password: str):
        self.url = url
        self.email = email
        self.password = password
        self.token = None
        self.session = requests.Session()
        self.authenticate()
    
    def authenticate(self):
        """Authenticate with NPM and get token"""
        response = self.session.post(
            f"{self.url}/api/tokens",
            json={"identity": self.email, "secret": self.password}
        )
        response.raise_for_status()
        self.token = response.json()['token']
        self.session.headers.update({'Authorization': f'Bearer {self.token}'})
        logger.info("Successfully authenticated with NPM")
    
    def get_proxy_hosts(self) -> List[Dict]:
        """Get all proxy hosts"""
        response = self.session.get(f"{self.url}/api/nginx/proxy-hosts")
        response.raise_for_status()
        return response.json()
    
    def get_proxy_host_by_domain(self, domain: str) -> Optional[Dict]:
        """Find proxy host by domain name"""
        hosts = self.get_proxy_hosts()
        for host in hosts:
            if domain in host.get('domain_names', []):
                return host
        return None
    
    def create_proxy_host(self, domain: str, forward_host: str, 
                         forward_port: int = 80, **kwargs) -> Dict:
        """Create a new proxy host"""
        data = {
            "domain_names": [domain],
            "forward_scheme": kwargs.get('forward_scheme', DEFAULT_FORWARD_SCHEME),
            "forward_host": forward_host,
            "forward_port": forward_port,
            "access_list_id": 0,
            "certificate_id": 0,
            "meta": {
                "letsencrypt_agree": False,
                "dns_challenge": False
            },
            "advanced_config": kwargs.get('advanced_config', ''),
            "locations": [],
            "block_exploits": True,
            "caching_enabled": False,
            "allow_websocket_upgrade": True,
            "http2_support": True,
            "hsts_enabled": False,
            "hsts_subdomains": False,
            "ssl_forced": False
        }
        
        # Add external-dns metadata
        data['meta']['external_dns_managed'] = True
        data['meta']['k8s_service'] = kwargs.get('k8s_service', '')
        data['meta']['k8s_namespace'] = kwargs.get('k8s_namespace', '')
        
        response = self.session.post(f"{self.url}/api/nginx/proxy-hosts", json=data)
        response.raise_for_status()
        logger.info(f"Created proxy host for domain: {domain}")
        return response.json()
    
    def update_proxy_host(self, host_id: int, forward_host: str, 
                         forward_port: int = 80, **kwargs) -> Dict:
        """Update existing proxy host"""
        # Get current host data
        response = self.session.get(f"{self.url}/api/nginx/proxy-hosts/{host_id}")
        response.raise_for_status()
        current_data = response.json()
        
        # Update only necessary fields
        current_data['forward_host'] = forward_host
        current_data['forward_port'] = forward_port
        
        if 'forward_scheme' in kwargs:
            current_data['forward_scheme'] = kwargs['forward_scheme']
        
        # Update metadata
        if 'meta' not in current_data:
            current_data['meta'] = {}
        current_data['meta']['external_dns_managed'] = True
        current_data['meta']['k8s_service'] = kwargs.get('k8s_service', '')
        current_data['meta']['k8s_namespace'] = kwargs.get('k8s_namespace', '')
        
        response = self.session.put(
            f"{self.url}/api/nginx/proxy-hosts/{host_id}", 
            json=current_data
        )
        response.raise_for_status()
        logger.info(f"Updated proxy host ID: {host_id}")
        return response.json()
    
    def delete_proxy_host(self, host_id: int):
        """Delete proxy host"""
        response = self.session.delete(f"{self.url}/api/nginx/proxy-hosts/{host_id}")
        response.raise_for_status()
        logger.info(f"Deleted proxy host ID: {host_id}")


# Initialize NPM client
npm_client = None

def init_npm_client():
    """Initialize NPM client with retry"""
    global npm_client
    try:
        npm_client = NPMClient(NPM_URL, NPM_EMAIL, NPM_PASSWORD)
        return True
    except Exception as e:
        logger.error(f"Failed to initialize NPM client: {e}")
        return False


def parse_k8s_annotation(annotation: str) -> Dict:
    """Parse Kubernetes service/ingress annotation"""
    # Format: "service-name.namespace:port" or "service-name.namespace"
    match = re.match(r'([^.]+)\.([^:]+)(?::(\d+))?', annotation)
    if match:
        return {
            'service': match.group(1),
            'namespace': match.group(2),
            'port': int(match.group(3)) if match.group(3) else 80
        }
    return {}


def get_target_from_annotation(annotation: str) -> tuple:
    """Get target host and port from annotation"""
    parsed = parse_k8s_annotation(annotation)
    
    # For NodePort services, use node IP
    # In a real implementation, this would query Kubernetes API
    # to get the actual NodePort
    node_ip = K8S_NODES[0]  # Simple round-robin or load balancing can be added
    
    # Default NodePort (should be queried from K8s)
    node_port = 30777  # This should be dynamic
    
    return node_ip, node_port


@app.route('/healthz', methods=['GET'])
def health():
    """Health check endpoint"""
    if npm_client:
        return jsonify({"status": "healthy"}), 200
    else:
        # Try to reinitialize
        if init_npm_client():
            return jsonify({"status": "healthy"}), 200
        return jsonify({"status": "unhealthy", "error": "NPM client not initialized"}), 503


@app.route('/records', methods=['GET'])
def get_records():
    """Get current DNS records (proxy hosts in NPM)"""
    try:
        if not npm_client:
            init_npm_client()
        
        hosts = npm_client.get_proxy_hosts()
        records = []
        
        for host in hosts:
            # Only return hosts managed by external-dns
            if host.get('meta', {}).get('external_dns_managed'):
                for domain in host.get('domain_names', []):
                    records.append({
                        "dnsName": domain,
                        "targets": [f"{host['forward_host']}:{host['forward_port']}"],
                        "recordType": "A",
                        "recordTTL": 300,
                        "labels": {
                            "npm-host-id": str(host['id']),
                            "k8s-service": host.get('meta', {}).get('k8s_service', ''),
                            "k8s-namespace": host.get('meta', {}).get('k8s_namespace', '')
                        }
                    })
        
        return jsonify(records), 200
    except Exception as e:
        logger.error(f"Failed to get records: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/records', methods=['POST'])
def apply_changes():
    """Apply DNS record changes"""
    try:
        if not npm_client:
            init_npm_client()
        
        changes = request.json
        results = {"created": [], "updated": [], "deleted": []}
        
        # Process creates
        for create in changes.get('Create', []):
            domain = create['dnsName']
            annotation = create.get('labels', {}).get('k8s-target', '')
            
            if annotation:
                forward_host, forward_port = get_target_from_annotation(annotation)
            else:
                # Default to first target
                target = create['targets'][0] if create['targets'] else K8S_NODES[0]
                if ':' in target:
                    forward_host, forward_port = target.split(':', 1)
                    forward_port = int(forward_port)
                else:
                    forward_host = target
                    forward_port = 80
            
            # Check if already exists
            existing = npm_client.get_proxy_host_by_domain(domain)
            if existing:
                # Update instead
                npm_client.update_proxy_host(
                    existing['id'], 
                    forward_host, 
                    forward_port,
                    k8s_service=create.get('labels', {}).get('k8s-service', ''),
                    k8s_namespace=create.get('labels', {}).get('k8s-namespace', '')
                )
                results['updated'].append(domain)
            else:
                # Create new
                npm_client.create_proxy_host(
                    domain, 
                    forward_host, 
                    forward_port,
                    k8s_service=create.get('labels', {}).get('k8s-service', ''),
                    k8s_namespace=create.get('labels', {}).get('k8s-namespace', '')
                )
                results['created'].append(domain)
        
        # Process updates
        for update_old, update_new in zip(changes.get('UpdateOld', []), 
                                         changes.get('UpdateNew', [])):
            domain = update_new['dnsName']
            existing = npm_client.get_proxy_host_by_domain(domain)
            
            if existing:
                annotation = update_new.get('labels', {}).get('k8s-target', '')
                if annotation:
                    forward_host, forward_port = get_target_from_annotation(annotation)
                else:
                    target = update_new['targets'][0] if update_new['targets'] else K8S_NODES[0]
                    if ':' in target:
                        forward_host, forward_port = target.split(':', 1)
                        forward_port = int(forward_port)
                    else:
                        forward_host = target
                        forward_port = 80
                
                npm_client.update_proxy_host(
                    existing['id'], 
                    forward_host, 
                    forward_port,
                    k8s_service=update_new.get('labels', {}).get('k8s-service', ''),
                    k8s_namespace=update_new.get('labels', {}).get('k8s-namespace', '')
                )
                results['updated'].append(domain)
        
        # Process deletes
        for delete in changes.get('Delete', []):
            domain = delete['dnsName']
            existing = npm_client.get_proxy_host_by_domain(domain)
            
            if existing and existing.get('meta', {}).get('external_dns_managed'):
                npm_client.delete_proxy_host(existing['id'])
                results['deleted'].append(domain)
        
        return jsonify(results), 200
    except Exception as e:
        logger.error(f"Failed to apply changes: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/adjustendpoints', methods=['POST'])
def adjust_endpoints():
    """Adjust endpoints (optional endpoint for external-dns)"""
    # This endpoint is optional and can be used for advanced adjustments
    return jsonify(request.json), 200


if __name__ == '__main__':
    # Initialize NPM client on startup
    init_npm_client()
    
    # Run webhook server
    port = int(os.getenv('WEBHOOK_PORT', '8888'))
    app.run(host='0.0.0.0', port=port, debug=False)