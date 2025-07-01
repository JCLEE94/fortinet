"""
Example of how to refactor hardcoded values using the new configuration modules.
This shows before and after examples.
"""

# ============================================
# BEFORE: Hardcoded values
# ============================================

# Example from auto_recovery.py
def check_internet_old():
    try:
        response = requests.get('http://8.8.8.8', timeout=5)
        return response.status_code == 200
    except:
        return False

def check_local_service_old():
    try:
        response = requests.get(f"http://localhost:{os.getenv('WEB_APP_PORT', '7777')}/api/settings", timeout=5)
        return response.status_code == 200
    except:
        return False

# Example from itsm/integration.py
class ITSMIntegrationOld:
    def __init__(self):
        self.base_url = "https://itsm2.nxtd.co.kr"
        self.api_key = None

# Example from mock/data_generator.py
def get_network_zone_old(ip):
    if ip in ipaddress.ip_network('192.168.0.0/16'):
        return 'internal'
    elif ip in ipaddress.ip_network('172.16.0.0/16'):
        return 'dmz'
    elif ip in ipaddress.ip_network('10.10.0.0/16'):
        return 'guest'
    else:
        return 'external'

# ============================================
# AFTER: Using configuration modules
# ============================================

from config.refactored import (
    EXTERNAL_SERVICES, SERVICE_PORTS, NETWORK_ZONES,
    TIMEOUT_LIMITS, get_service_url, get_api_endpoint,
    is_private_ip, get_network_info
)
import ipaddress
import requests

# Example from auto_recovery.py - REFACTORED
def check_internet():
    """Check internet connectivity using configured DNS server."""
    try:
        dns_check_url = EXTERNAL_SERVICES.get('dns_check', {}).get('url', 'http://8.8.8.8')
        timeout = TIMEOUT_LIMITS['internet_check']
        response = requests.get(dns_check_url, timeout=timeout)
        return response.status_code == 200
    except:
        return False

def check_local_service():
    """Check local service health using configured endpoint."""
    try:
        port = SERVICE_PORTS['web_app']
        endpoint = get_api_endpoint('internal', 'api', 'settings')
        url = f"http://localhost:{port}{endpoint}"
        timeout = TIMEOUT_LIMITS['health_check']
        response = requests.get(url, timeout=timeout)
        return response.status_code == 200
    except:
        return False

# Example from itsm/integration.py - REFACTORED
class ITSMIntegration:
    def __init__(self, api_key=None):
        self.base_url = get_service_url('itsm')
        self.api_key = api_key or os.getenv('ITSM_API_KEY')
        self.timeout = TIMEOUT_LIMITS['api_request']

# Example from mock/data_generator.py - REFACTORED
def get_network_zone(ip):
    """Determine network zone for an IP address using configuration."""
    try:
        ip_obj = ipaddress.ip_address(ip)
        
        # Check each configured network zone
        for zone_name, network_cidr in NETWORK_ZONES.items():
            if zone_name == 'external':  # Skip the catch-all
                continue
            
            network = ipaddress.ip_network(network_cidr, strict=False)
            if ip_obj in network:
                return zone_name
        
        # If not in any defined zone, it's external
        return 'external'
    except ValueError:
        return 'unknown'

# Example: Using multiple configurations together
def analyze_packet_path(src_ip, dst_ip, port, protocol='tcp'):
    """Analyze packet path with proper configuration."""
    # Determine zones
    src_zone = get_network_zone(src_ip)
    dst_zone = get_network_zone(dst_ip)
    
    # Get gateway information
    src_gateway = get_network_info(src_zone)['gateway']
    dst_gateway = get_network_info(dst_zone)['gateway']
    
    # Check if it's a well-known service
    from config.refactored.ports import get_service_by_port
    service = get_service_by_port(port)
    
    # Build analysis
    analysis = {
        'source': {
            'ip': src_ip,
            'zone': src_zone,
            'gateway': src_gateway,
            'is_private': is_private_ip(src_ip)
        },
        'destination': {
            'ip': dst_ip,
            'zone': dst_zone,
            'gateway': dst_gateway,
            'is_private': is_private_ip(dst_ip),
            'service': service,
            'port': port
        },
        'protocol': protocol
    }
    
    return analysis

# Example: Content Security Policy
def get_csp_header():
    """Generate CSP header from configuration."""
    from config.refactored.services import get_csp_header
    return get_csp_header()

# Example: Using limits
def get_top_traffic_sources(traffic_data):
    """Get top traffic sources using configured limits."""
    from config.refactored.limits import DISPLAY_LIMITS
    
    # Sort by traffic volume
    sorted_sources = sorted(
        traffic_data.items(),
        key=lambda x: x[1],
        reverse=True
    )
    
    # Return only configured number of top items
    return sorted_sources[:DISPLAY_LIMITS['top_items']]

# Example: File paths
def get_log_file():
    """Get log file path from configuration."""
    from config.refactored.paths import get_log_path
    
    # This will ensure the directory exists and return the path
    return get_log_path('app')

# Example: API endpoint construction
def get_fortigate_status_url(host, port=None):
    """Construct FortiGate status URL."""
    from config.refactored.ports import FORTIGATE_PORTS
    
    # Use configured port or default
    if port is None:
        port = FORTIGATE_PORTS['admin_https']
    
    # Get the monitoring endpoint
    endpoint = get_api_endpoint('fortigate', 'monitoring', 'system')
    status_endpoint = endpoint + '/status'  # Or use nested structure
    
    return f"https://{host}:{port}{status_endpoint}"