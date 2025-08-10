"""
Constants and configuration values for FortiGate Nextrade.
This file centralizes hardcoded values to improve maintainability.
"""

import os

# Port Configuration
DEFAULT_PORTS = {
    "HTTPS": 443,
    "HTTP": 80,
    "SSH": 22,
    "FLASK": int(os.getenv("FLASK_PORT", "5000")),
    "APP": int(os.getenv("APP_PORT", "7777")),
    "MOCK_SERVER": int(os.getenv("MOCK_SERVER_PORT", "8090")),
    "REDIS": int(os.getenv("REDIS_PORT", "6379")),
}

# Timeout Configuration (in seconds)
TIMEOUTS = {
    "HEALTH_CHECK": int(os.getenv("HEALTH_CHECK_TIMEOUT", "5")),
    "API_REQUEST": int(os.getenv("API_REQUEST_TIMEOUT", "30")),
    "LONG_OPERATION": int(os.getenv("LONG_OPERATION_TIMEOUT", "300")),
    "CONNECTION": int(os.getenv("CONNECTION_TIMEOUT", "10")),
    "READ": int(os.getenv("READ_TIMEOUT", "30")),
}

# Check Intervals (in seconds)
CHECK_INTERVALS = {
    "HEALTH": int(os.getenv("HEALTH_CHECK_INTERVAL", "30")),
    "RECOVERY": int(os.getenv("RECOVERY_CHECK_INTERVAL", "60")),
    "MONITORING": int(os.getenv("MONITORING_INTERVAL", "300")),
    "SECURITY_SCAN": int(os.getenv("SECURITY_SCAN_INTERVAL", "3600")),
}

# Cache Configuration
CACHE_SETTINGS = {
    "MAX_SIZE": int(os.getenv("CACHE_MAX_SIZE", "1000")),
    "CLEANUP_INTERVAL": int(os.getenv("CACHE_CLEANUP_INTERVAL", "300")),
    "TTL_DEFAULT": int(os.getenv("CACHE_TTL_DEFAULT", "3600")),
    "REDIS_MAX_CONNECTIONS": int(os.getenv("REDIS_MAX_CONNECTIONS", "50")),
}

# Batch Operation Settings
BATCH_SETTINGS = {
    "MAX_WORKERS": int(os.getenv("BATCH_MAX_WORKERS", "10")),
    "MAX_RETRIES": int(os.getenv("BATCH_MAX_RETRIES", "3")),
    "CHUNK_SIZE": int(os.getenv("BATCH_CHUNK_SIZE", "100")),
    "CONNECTION_POOL_SIZE": int(os.getenv("CONNECTION_POOL_SIZE", "100")),
}

# Pagination Settings
PAGINATION = {
    "DEFAULT_PER_PAGE": int(os.getenv("DEFAULT_PER_PAGE", "20")),
    "MAX_PER_PAGE": int(os.getenv("MAX_PER_PAGE", "100")),
}

# File Size Limits (in bytes)
FILE_LIMITS = {
    "LOG_MAX_SIZE": int(os.getenv("LOG_MAX_SIZE", str(10 * 1024 * 1024))),  # 10MB
    "ERROR_LOG_MAX_SIZE": int(os.getenv("ERROR_LOG_MAX_SIZE", str(5 * 1024 * 1024))),  # 5MB
    "LOG_BACKUP_COUNT": int(os.getenv("LOG_BACKUP_COUNT", "3")),
}

# Traffic Thresholds
TRAFFIC_THRESHOLDS = {
    "HIGH": int(os.getenv("TRAFFIC_HIGH_THRESHOLD", "5000")),
    "MEDIUM": int(os.getenv("TRAFFIC_MEDIUM_THRESHOLD", "1000")),
    "LOW": int(os.getenv("TRAFFIC_LOW_THRESHOLD", "100")),
}

# Rate Limiting
RATE_LIMITS = {
    "MAX_REQUESTS": int(os.getenv("RATE_LIMIT_MAX_REQUESTS", "60")),
    "WINDOW_SECONDS": int(os.getenv("RATE_LIMIT_WINDOW", "60")),
    "ERROR_THRESHOLD": int(os.getenv("RATE_LIMIT_ERROR_THRESHOLD", "10")),
}

# Security Headers
SECURITY_HEADERS = {
    "HSTS_MAX_AGE": int(os.getenv("HSTS_MAX_AGE", "31536000")),  # 1 year
    "CSP_ENABLED": os.getenv("CSP_ENABLED", "true").lower() == "true",
}

# File Paths
DEFAULT_PATHS = {
    "CONFIG": os.getenv("CONFIG_PATH", os.path.join(os.getcwd(), "data", "config.json")),
    "DEFAULT_CONFIG": os.getenv("DEFAULT_CONFIG_PATH", os.path.join(os.getcwd(), "data", "default_config.json")),
    "LOG_DIR": os.getenv("LOG_DIR", os.path.join(os.getcwd(), "logs")),
    "DATA_DIR": os.getenv("DATA_DIR", os.path.join(os.getcwd(), "data")),
    "TEMP_DIR": os.getenv("TEMP_DIR", "/tmp"),
}

# Service URLs
BASE_URL = os.getenv("BASE_URL", "http://localhost")
SERVICE_URLS = {
    "HEALTH_CHECK": os.getenv("HEALTH_CHECK_URL", f"{BASE_URL}:{{port}}/health"),
    "MOCK_SERVER": os.getenv("MOCK_SERVER_URL", f"{BASE_URL}:{{port}}{{api_version}}/monitor/system/status"),
    "REDIS": os.getenv("REDIS_URL", f'redis://redis:{DEFAULT_PORTS["REDIS"]}/0'),
}

# Default Values
DEFAULTS = {
    "SECRET_KEY": os.getenv("SECRET_KEY", "change_this_in_production_seriously"),
    "FLASK_ENV": os.getenv("FLASK_ENV", "production"),
    "DEBUG": os.getenv("DEBUG", "false").lower() == "true",
    "APP_MODE": os.getenv("APP_MODE", "production"),
    "OFFLINE_MODE": os.getenv("OFFLINE_MODE", "false").lower() == "true",
}

# Mock Data Settings
MOCK_DATA = {
    "DEVICE_COUNT": int(os.getenv("MOCK_DEVICE_COUNT", "10")),
    "POLICY_COUNT": int(os.getenv("MOCK_POLICY_COUNT", "50")),
    "LOG_COUNT": int(os.getenv("MOCK_LOG_COUNT", "100")),
}

# Common Service Ports (for mock data generation)
COMMON_PORTS = [
    DEFAULT_PORTS["SSH"],
    DEFAULT_PORTS["HTTP"],
    DEFAULT_PORTS["HTTPS"],
    3389,  # RDP
    8080,  # Alternative HTTP
    8443,  # Alternative HTTPS
]

# Example IP Ranges (for documentation and examples)
# These use RFC 5737 and RFC 1918 addresses which are reserved for documentation
EXAMPLE_IPS = {
    "INTERNAL": os.getenv("INTERNAL_NETWORKS", "192.168.0.0/16,10.0.0.0/8").split(","),
    "DMZ": [os.getenv("DMZ_NETWORK", "172.16.0.0/24")],
    "PUBLIC": os.getenv("PUBLIC_DNS_SERVERS", "8.8.8.8,1.1.1.1").split(","),
}
