"""
Network configuration to replace hardcoded IP addresses and network ranges.
"""
import os
import ipaddress

# Network zones configuration
NETWORK_ZONES = {
    'internal': os.getenv('INTERNAL_NETWORK', '192.168.0.0/16'),
    'dmz': os.getenv('DMZ_NETWORK', '172.16.0.0/16'),
    'external': os.getenv('EXTERNAL_NETWORK', '0.0.0.0/0'),
    'guest': os.getenv('GUEST_NETWORK', '10.10.0.0/16'),
    'management': os.getenv('MANAGEMENT_NETWORK', '10.100.0.0/24'),
    'private_class_a': os.getenv('PRIVATE_CLASS_A', '10.0.0.0/8'),
    'private_class_b': os.getenv('PRIVATE_CLASS_B', '172.16.0.0/12'),
    'private_class_c': os.getenv('PRIVATE_CLASS_C', '192.168.0.0/16'),
}

# Default gateway configuration
DEFAULT_GATEWAYS = {
    'internal': os.getenv('INTERNAL_GATEWAY', '192.168.1.1'),
    'dmz': os.getenv('DMZ_GATEWAY', '172.16.1.1'),
    'external': os.getenv('EXTERNAL_GATEWAY', '203.0.113.1'),
    'guest': os.getenv('GUEST_GATEWAY', '10.10.1.1'),
    'management': os.getenv('MANAGEMENT_GATEWAY', '10.100.0.1'),
}

# DNS servers
DNS_SERVERS = {
    'primary': os.getenv('PRIMARY_DNS', '8.8.8.8'),
    'secondary': os.getenv('SECONDARY_DNS', '1.1.1.1'),
    'internal': os.getenv('INTERNAL_DNS', '192.168.1.10'),
}

# Private network ranges (RFC 1918)
PRIVATE_NETWORKS = [
    ipaddress.ip_network('10.0.0.0/8'),
    ipaddress.ip_network('172.16.0.0/12'),
    ipaddress.ip_network('192.168.0.0/16'),
]

# Special addresses
SPECIAL_ADDRESSES = {
    'localhost': '127.0.0.1',
    'localhost_v6': '::1',
    'any': '0.0.0.0',
    'any_v6': '::',
    'broadcast': '255.255.255.255',
}

# Common test IPs
TEST_IPS = {
    'internal_host': os.getenv('TEST_INTERNAL_HOST', '192.168.1.100'),
    'dmz_server': os.getenv('TEST_DMZ_SERVER', '172.16.10.100'),
    'external_host': os.getenv('TEST_EXTERNAL_HOST', '203.0.113.50'),
    'guest_host': os.getenv('TEST_GUEST_HOST', '10.10.1.50'),
}

# Network masks
NETWORK_MASKS = {
    '/8': '255.0.0.0',
    '/16': '255.255.0.0',
    '/24': '255.255.255.0',
    '/32': '255.255.255.255',
}

def get_network_info(zone: str) -> dict:
    """Get network information for a specific zone."""
    return {
        'network': NETWORK_ZONES.get(zone),
        'gateway': DEFAULT_GATEWAYS.get(zone),
        'is_private': any(
            ipaddress.ip_network(NETWORK_ZONES.get(zone, '0.0.0.0/0'), strict=False).overlaps(net)
            for net in PRIVATE_NETWORKS
        ) if zone in NETWORK_ZONES else False
    }

def is_private_ip(ip: str) -> bool:
    """Check if an IP address is in private range."""
    try:
        ip_obj = ipaddress.ip_address(ip)
        return any(ip_obj in network for network in PRIVATE_NETWORKS)
    except ValueError:
        return False