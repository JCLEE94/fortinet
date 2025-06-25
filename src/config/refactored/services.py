"""
External service URLs and API endpoints configuration.
"""
import os

# External service URLs
EXTERNAL_SERVICES = {
    'itsm': {
        'base_url': os.getenv('ITSM_BASE_URL', 'https://itsm2.nxtd.co.kr'),
        'api_version': os.getenv('ITSM_API_VERSION', 'v1'),
    },
    'gitlab': {
        'base_url': os.getenv('GITLAB_URL', 'https://gitlab.com'),
        'api_version': os.getenv('GITLAB_API_VERSION', 'v4'),
    },
    'registry': {
        'base_url': os.getenv('DOCKER_REGISTRY', 'registry.jclee.me'),
        'username': os.getenv('REGISTRY_USERNAME'),
        'password': os.getenv('REGISTRY_PASSWORD'),
    },
}

# CDN URLs for frontend resources
CDN_URLS = {
    'cloudflare': 'https://cdnjs.cloudflare.com',
    'jsdelivr': 'https://cdn.jsdelivr.net',
    'google_fonts': 'https://fonts.googleapis.com',
    'gstatic': 'https://fonts.gstatic.com',
}

# API endpoint patterns
API_ENDPOINTS = {
    'fortigate': {
        'base': '/api/v2',
        'status': '/monitor/system/status',
        'performance': '/monitor/system/performance',
        'interfaces': '/monitor/system/interface',
        'firewall_policy': '/cmdb/firewall/policy',
        'system_interface': '/cmdb/system/interface',
        'routing_table': '/monitor/router/ipv4',
        'arp_table': '/monitor/system/arp',
        'dhcp_leases': '/monitor/system/dhcp',
        'packet_capture': {
            'start': '/monitor/system/packet-capture/start',
            'stop': '/monitor/system/packet-capture/stop',
            'status': '/monitor/system/packet-capture/status',
            'download': '/monitor/system/packet-capture/download',
        },
    },
    'fortimanager': {
        'base': '/jsonrpc',
        'login': '/sys/login/user',
        'logout': '/sys/logout',
        'adom_list': '/dvmdb/adom',
        'device_list': '/dvmdb/device',
        'policy_list': '/pm/config/adom/{adom}/pkg/{pkg}/firewall/policy',
    },
    'fortianalyzer': {
        'base': '/jsonrpc',
        'login': '/sys/login/user',
        'logout': '/sys/logout',
        'log_search': '/logview/adom/{adom}/logsearch',
    },
    'internal': {
        'settings': '/api/settings',
        'devices': '/api/devices',
        'monitoring': '/api/monitoring',
        'dashboard': '/api/dashboard',
        'system_stats': '/api/system/stats',
        'firewall_policy': {
            'analyze': '/api/firewall-policy/analyze',
            'create_ticket': '/api/firewall-policy/create-ticket',
            'zones': '/api/firewall-policy/zones',
        },
    },
}

# Health check and monitoring URLs
HEALTH_CHECK_URLS = {
    'internal': os.getenv('HEALTH_CHECK_URL', 'http://localhost:{port}/health'),
    'internet': os.getenv('INTERNET_CHECK_URL', 'http://8.8.8.8'),
    'mock_server': os.getenv('MOCK_SERVER_URL', 'http://localhost:{port}/api/v2/monitor/system/status'),
}

# Content Security Policy sources
CSP_SOURCES = {
    'default': ["'self'"],
    'script': ["'self'", "'unsafe-inline'", "'unsafe-eval'"] + list(CDN_URLS.values()),
    'style': ["'self'", "'unsafe-inline'"] + [CDN_URLS['cloudflare'], CDN_URLS['google_fonts']],
    'font': ["'self'", CDN_URLS['cloudflare'], CDN_URLS['gstatic'], 'data:'],
    'img': ["'self'", 'data:', 'blob:'],
    'connect': ["'self'", 'ws:', 'wss:'],
}

def get_service_url(service: str, endpoint: str = None) -> str:
    """Get the full URL for a service endpoint."""
    service_config = EXTERNAL_SERVICES.get(service, {})
    base_url = service_config.get('base_url', '')
    
    if endpoint:
        return f"{base_url}{endpoint}"
    return base_url

def get_csp_header() -> str:
    """Generate Content Security Policy header."""
    policies = []
    for directive, sources in CSP_SOURCES.items():
        if directive == 'default':
            policies.append(f"default-src {' '.join(sources)}")
        else:
            policies.append(f"{directive}-src {' '.join(sources)}")
    return "; ".join(policies)