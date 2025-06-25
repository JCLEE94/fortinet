"""
API endpoint configuration to replace hardcoded endpoints.
"""
import os
from typing import Dict, Optional

# API version configuration
API_VERSIONS = {
    'fortigate': os.getenv('FORTIGATE_API_VERSION', '/api/v2'),
    'fortimanager': os.getenv('FORTIMANAGER_API_VERSION', '/jsonrpc'),
    'fortianalyzer': os.getenv('FORTIANALYZER_API_VERSION', '/jsonrpc'),
    'fortisiem': os.getenv('FORTISIEM_API_VERSION', '/api/v2.0'),
}

# Monitoring endpoints
MONITORING_ENDPOINTS = {
    'system': {
        'status': '/monitor/system/status',
        'performance': '/monitor/system/performance',
        'interface': '/monitor/system/interface',
        'resource_usage': '/monitor/system/resource/usage',
    },
    'firewall': {
        'session': '/monitor/firewall/session',
        'policy_stats': '/monitor/firewall/policy-stats',
    },
    'router': {
        'ipv4': '/monitor/router/ipv4',
        'ipv6': '/monitor/router/ipv6',
        'bgp': '/monitor/router/bgp',
        'ospf': '/monitor/router/ospf',
    },
    'vpn': {
        'ipsec': '/monitor/vpn/ipsec',
        'ssl': '/monitor/vpn/ssl',
    },
    'packet_capture': {
        'start': '/monitor/system/packet-capture/start',
        'stop': '/monitor/system/packet-capture/stop',
        'status': '/monitor/system/packet-capture/status',
        'download': '/monitor/system/packet-capture/download',
    },
}

# CMDB (Configuration Management Database) endpoints
CMDB_ENDPOINTS = {
    'system': {
        'global': '/cmdb/system/global',
        'interface': '/cmdb/system/interface',
        'admin': '/cmdb/system/admin',
        'dns': '/cmdb/system/dns',
        'ntp': '/cmdb/system/ntp',
    },
    'firewall': {
        'policy': '/cmdb/firewall/policy',
        'address': '/cmdb/firewall/address',
        'service': '/cmdb/firewall/service/custom',
        'vip': '/cmdb/firewall/vip',
        'ippool': '/cmdb/firewall/ippool',
    },
    'router': {
        'static': '/cmdb/router/static',
        'policy': '/cmdb/router/policy',
    },
    'vpn': {
        'ipsec_phase1': '/cmdb/vpn.ipsec/phase1-interface',
        'ipsec_phase2': '/cmdb/vpn.ipsec/phase2-interface',
    },
}

# Internal application endpoints
INTERNAL_ENDPOINTS = {
    'api': {
        'settings': '/api/settings',
        'devices': '/api/devices',
        'monitoring': '/api/monitoring',
        'dashboard': '/api/dashboard',
        'system_stats': '/api/system/stats',
        'test_connection': '/api/test_connection',
        'mode': '/api/settings/mode',
    },
    'fortimanager': {
        'base': '/api/fortimanager',
        'status': '/api/fortimanager/status',
        'devices': '/api/fortimanager/devices',
        'device_detail': '/api/fortimanager/device/{device_id}',
        'policies': '/api/fortimanager/policies',
        'policy_detail': '/api/fortimanager/policies/{policy_id}',
        'analyze_path': '/api/fortimanager/analyze-packet-path',
        'test_analysis': '/api/fortimanager/test-policy-analysis',
        'advanced': {
            'analytics_trends': '/api/fortimanager/advanced/analytics/trends',
            'compliance_check': '/api/fortimanager/advanced/compliance/check',
            'policy_orchestration': '/api/fortimanager/advanced/policy/orchestrate',
            'security_fabric': '/api/fortimanager/advanced/fabric/status',
        },
    },
    'itsm': {
        'base': '/api/itsm',
        'scrape': '/api/itsm/scrape-requests',
        'request_detail': '/api/itsm/request-detail/{request_id}',
        'map_to_fortigate': '/api/itsm/map-to-fortigate',
        'bridge_status': '/api/itsm/bridge-status',
        'policy_request': '/api/itsm/policy-request',
        'scraper_status': '/api/itsm/scraper/status',
        'demo_mapping': '/api/itsm/demo-mapping',
        'automation': {
            'base': '/api/itsm/automation',
            'status': '/api/itsm/automation/status',
            'rules': '/api/itsm/automation/rules',
        },
    },
    'performance': {
        'base': '/api/performance',
        'metrics': '/api/performance/metrics',
        'history': '/api/performance/history',
    },
    'firewall_policy': {
        'analyze': '/api/firewall-policy/analyze',
        'create_ticket': '/api/firewall-policy/create-ticket',
        'zones': '/api/firewall-policy/zones',
    },
}

def get_api_endpoint(service: str, endpoint_type: str, endpoint_name: str = None) -> str:
    """
    Get API endpoint URL.
    
    Args:
        service: Service name (fortigate, fortimanager, internal, etc.)
        endpoint_type: Type of endpoint (monitoring, cmdb, etc.)
        endpoint_name: Specific endpoint name
        
    Returns:
        Full endpoint path
    """
    if service == 'fortigate':
        base = API_VERSIONS['fortigate']
        if endpoint_type == 'monitoring':
            endpoints = MONITORING_ENDPOINTS
        elif endpoint_type == 'cmdb':
            endpoints = CMDB_ENDPOINTS
        else:
            return base
    elif service in ['fortimanager', 'fortianalyzer', 'fortisiem']:
        return API_VERSIONS[service]
    elif service == 'internal':
        endpoints = INTERNAL_ENDPOINTS
        base = ''
    else:
        raise ValueError(f"Unknown service: {service}")
    
    # Navigate through nested structure
    if endpoint_type in endpoints:
        if endpoint_name and isinstance(endpoints[endpoint_type], dict):
            endpoint = endpoints[endpoint_type].get(endpoint_name, '')
        else:
            endpoint = endpoints[endpoint_type]
        
        if service == 'fortigate':
            return f"{base}{endpoint}"
        return endpoint
    
    return base

def format_endpoint(endpoint: str, **kwargs) -> str:
    """
    Format endpoint with parameters.
    
    Example:
        format_endpoint('/api/device/{device_id}', device_id='FW-01')
        Returns: '/api/device/FW-01'
    """
    return endpoint.format(**kwargs)