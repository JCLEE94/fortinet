"""
Refactored configuration module to replace hardcoded values.
Import all configuration from submodules.
"""

from .network import NETWORK_ZONES, DEFAULT_GATEWAYS, DNS_SERVERS, PRIVATE_NETWORKS
from .services import EXTERNAL_SERVICES, CDN_URLS, API_ENDPOINTS
from .ports import SERVICE_PORTS, PROTOCOL_PORTS
from .paths import PATHS, get_path
from .endpoints import API_VERSIONS, MONITORING_ENDPOINTS, get_api_endpoint
from .limits import DISPLAY_LIMITS, TIMEOUT_LIMITS, SIZE_LIMITS

__all__ = [
    # Network
    'NETWORK_ZONES',
    'DEFAULT_GATEWAYS',
    'DNS_SERVERS',
    'PRIVATE_NETWORKS',
    
    # Services
    'EXTERNAL_SERVICES',
    'CDN_URLS',
    'API_ENDPOINTS',
    
    # Ports
    'SERVICE_PORTS',
    'PROTOCOL_PORTS',
    
    # Paths
    'PATHS',
    'get_path',
    
    # Endpoints
    'API_VERSIONS',
    'MONITORING_ENDPOINTS',
    'get_api_endpoint',
    
    # Limits
    'DISPLAY_LIMITS',
    'TIMEOUT_LIMITS',
    'SIZE_LIMITS',
]