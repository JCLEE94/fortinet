"""
Port configuration to replace hardcoded port numbers.
"""
import os

# Service ports
SERVICE_PORTS = {
    'web_app': int(os.getenv('WEB_APP_PORT', '7777')),
    'test_app': int(os.getenv('TEST_APP_PORT', '7778')),
    'mock_server': int(os.getenv('MOCK_SERVER_PORT', '6666')),
    'redis': int(os.getenv('REDIS_PORT', '6379')),
    'postgres': int(os.getenv('POSTGRES_PORT', '5432')),
    'mysql': int(os.getenv('MYSQL_PORT', '3306')),
    'elasticsearch': int(os.getenv('ELASTICSEARCH_PORT', '9200')),
    'kibana': int(os.getenv('KIBANA_PORT', '5601')),
}

# Network protocol ports
PROTOCOL_PORTS = {
    'http': 80,
    'https': 443,
    'ssh': 22,
    'telnet': 23,
    'ftp': 21,
    'smtp': 25,
    'dns': 53,
    'dhcp': 67,
    'tftp': 69,
    'snmp': 161,
    'ldap': 389,
    'ldaps': 636,
    'syslog': 514,
    'ntp': 123,
    'rdp': 3389,
    'vnc': 5900,
}

# FortiGate specific ports
FORTIGATE_PORTS = {
    'admin_https': int(os.getenv('FORTIGATE_ADMIN_PORT', '443')),
    'admin_ssh': int(os.getenv('FORTIGATE_SSH_PORT', '22')),
    'admin_telnet': int(os.getenv('FORTIGATE_TELNET_PORT', '23')),
    'fortimanager': int(os.getenv('FORTIMANAGER_PORT', '541')),
    'fortiguard': int(os.getenv('FORTIGUARD_PORT', '8888')),
    'fortianalyzer': int(os.getenv('FORTIANALYZER_PORT', '514')),
}

# Application internal ports
INTERNAL_PORTS = {
    'metrics': int(os.getenv('METRICS_PORT', '9090')),
    'health_check': int(os.getenv('HEALTH_CHECK_PORT', '8080')),
    'debug': int(os.getenv('DEBUG_PORT', '5678')),
    'websocket': int(os.getenv('WEBSOCKET_PORT', '8765')),
}

def get_port(service: str, default: int = None) -> int:
    """Get port for a service with optional default."""
    # Check all port dictionaries
    for port_dict in [SERVICE_PORTS, PROTOCOL_PORTS, FORTIGATE_PORTS, INTERNAL_PORTS]:
        if service in port_dict:
            return port_dict[service]
    
    # Return default if provided, otherwise raise error
    if default is not None:
        return default
    
    raise ValueError(f"Unknown service: {service}")

def get_service_by_port(port: int) -> str:
    """Get service name by port number."""
    all_ports = {
        **{v: k for k, v in SERVICE_PORTS.items()},
        **{v: k for k, v in PROTOCOL_PORTS.items()},
        **{v: k for k, v in FORTIGATE_PORTS.items()},
        **{v: k for k, v in INTERNAL_PORTS.items()},
    }
    return all_ports.get(port, 'unknown')

def is_well_known_port(port: int) -> bool:
    """Check if port is in well-known range (0-1023)."""
    return 0 <= port <= 1023

def is_registered_port(port: int) -> bool:
    """Check if port is in registered range (1024-49151)."""
    return 1024 <= port <= 49151

def is_dynamic_port(port: int) -> bool:
    """Check if port is in dynamic/private range (49152-65535)."""
    return 49152 <= port <= 65535