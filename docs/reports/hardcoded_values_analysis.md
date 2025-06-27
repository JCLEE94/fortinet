# Hardcoded Values Analysis Report

## 1. Hardcoded URLs

### External URLs
- `https://itsm2.nxtd.co.kr` - Found in multiple ITSM integration files
- `https://cdnjs.cloudflare.com` - Content Security Policy
- `https://cdn.jsdelivr.net` - Content Security Policy
- `https://fonts.googleapis.com` - Content Security Policy
- `https://fonts.gstatic.com` - Content Security Policy
- `http://8.8.8.8` - Used for internet connectivity checks
- `https://gitlab.com` - Default GitLab URL

### Internal URLs/Endpoints
- `http://localhost:7777` - Hardcoded in multiple places
- `http://localhost:7778` - Test endpoints
- `http://localhost:6666` - Mock server
- Various API endpoints: `/api/v2/`, `/jsonrpc`, `/monitor/system/status`

## 2. Hardcoded IP Addresses

### Network Ranges
- `192.168.0.0/16` - Internal network
- `172.16.0.0/16` - DMZ network
- `10.0.0.0/8` - Private network
- `10.10.0.0/16` - Guest network
- `0.0.0.0/0` - Any/All network

### Specific IPs
- `192.168.1.1`, `192.168.1.100`, `192.168.1.10` - Internal IPs
- `172.16.1.1`, `172.16.10.100` - DMZ IPs
- `203.0.113.1`, `203.0.113.50` - External IPs (documentation range)
- `8.8.8.8`, `1.1.1.1` - Public DNS servers
- `127.0.0.1`, `::1` - Localhost
- `0.0.0.0` - Bind all interfaces

## 3. Hardcoded Ports

- `:7777` - Main application port
- `:7778` - Test/development port
- `:6666` - Mock server port
- `:6379` - Redis port
- `:443` - HTTPS port
- `:80` - HTTP port
- `:22` - SSH port

## 4. Hardcoded File Paths

### Container Paths
- `/app/data/config.json`
- `/app/data/default_config.json`
- `/app/logs`
- `/app/src`
- `/app/service/fortigate/logs`

### System Paths
- `/var/run/docker.sock`
- `/var/log/auth.log`
- `/var/log/syslog`
- `/tmp/deployment_monitor.log`
- `/tmp/pipeline_monitor.log`

### Development Paths
- `/home/jclee/dev/fortinet/.env`
- `/home/jclee/dev/fortinet/data/config.json`
- `/home/jclee/dev/fortinet/api_test_report.json`

## 5. Hardcoded Credentials/Tokens

- Password "test" in test files
- API token "test-token" in tests
- Username "admin" in tests
- Placeholder tokens like "xxx"

## 6. Magic Numbers

- `[:16]`, `[:32]` - Hash truncation lengths
- `[:10]`, `[:5]` - Array slicing limits
- `500`, `100`, `50` - Various limits
- `5`, `10`, `20` - Display limits
- Time values: `09:00-18:00` (business hours)

## 7. Recommendations for Refactoring

### Create Configuration Files

1. **Network Configuration** (`config/network.py`):
```python
NETWORK_ZONES = {
    'internal': '192.168.0.0/16',
    'dmz': '172.16.0.0/16',
    'external': '0.0.0.0/0',
    'guest': '10.10.0.0/16',
    'management': '10.100.0.0/24'
}

DEFAULT_GATEWAYS = {
    'internal': '192.168.1.1',
    'dmz': '172.16.1.1',
    'external': '203.0.113.1',
    'guest': '10.10.1.1'
}
```

2. **Service URLs** (`config/services.py`):
```python
EXTERNAL_SERVICES = {
    'itsm': os.getenv('ITSM_BASE_URL', 'https://itsm2.nxtd.co.kr'),
    'gitlab': os.getenv('GITLAB_URL', 'https://gitlab.com'),
    'dns_check': os.getenv('DNS_CHECK_URL', 'http://8.8.8.8')
}

CDN_URLS = {
    'cloudflare': 'https://cdnjs.cloudflare.com',
    'jsdelivr': 'https://cdn.jsdelivr.net',
    'google_fonts': 'https://fonts.googleapis.com',
    'gstatic': 'https://fonts.gstatic.com'
}
```

3. **Port Configuration** (`config/ports.py`):
```python
SERVICE_PORTS = {
    'web_app': int(os.getenv('WEB_APP_PORT', 7777)),
    'test_app': int(os.getenv('TEST_APP_PORT', 7778)),
    'mock_server': int(os.getenv('MOCK_SERVER_PORT', 6666)),
    'redis': int(os.getenv('REDIS_PORT', 6379))
}
```

4. **File Paths** (`config/paths.py`):
```python
import os

BASE_DIR = os.getenv('APP_BASE_DIR', '/app')

PATHS = {
    'config': os.path.join(BASE_DIR, 'data', 'config.json'),
    'default_config': os.path.join(BASE_DIR, 'data', 'default_config.json'),
    'logs': os.path.join(BASE_DIR, 'logs'),
    'data': os.path.join(BASE_DIR, 'data'),
    'src': os.path.join(BASE_DIR, 'src')
}
```

5. **API Endpoints** (`config/endpoints.py`):
```python
API_VERSIONS = {
    'fortigate': '/api/v2',
    'fortimanager': '/jsonrpc',
    'fortianalyzer': '/jsonrpc',
    'fortisiem': '/api/v2.0'
}

MONITORING_ENDPOINTS = {
    'system_status': '/monitor/system/status',
    'performance': '/monitor/system/performance',
    'interfaces': '/monitor/system/interface'
}
```

## 8. Missing Dependencies

Based on the import analysis, the following packages are used but not in requirements.txt:

1. **ipaddress** - Used for IP address manipulation (part of Python stdlib since 3.3)
2. **asyncio** - Used for async operations (part of Python stdlib)
3. **netaddr** - Might be needed for advanced network operations (consider adding if used)

## 9. Action Items

1. **Immediate Actions**:
   - Create configuration modules for all hardcoded values
   - Update all files to use configuration imports instead of hardcoded values
   - Add environment variable support for all configurable values

2. **Environment Variables to Add**:
   ```bash
   # Network Configuration
   INTERNAL_NETWORK=192.168.0.0/16
   DMZ_NETWORK=172.16.0.0/16
   GUEST_NETWORK=10.10.0.0/16
   
   # Service URLs
   ITSM_BASE_URL=https://itsm2.nxtd.co.kr
   GITLAB_URL=https://gitlab.com
   
   # Ports
   WEB_APP_PORT=7777
   TEST_APP_PORT=7778
   MOCK_SERVER_PORT=6666
   
   # Paths
   APP_BASE_DIR=/app
   LOG_DIR=/app/logs
   DATA_DIR=/app/data
   ```

3. **Configuration File Structure**:
   ```
   config/
   ├── __init__.py
   ├── network.py      # Network-related constants
   ├── services.py     # External service URLs
   ├── ports.py        # Port configurations
   ├── paths.py        # File path configurations
   ├── endpoints.py    # API endpoint configurations
   └── limits.py       # Numeric limits and thresholds
   ```

4. **Update Docker Compose**:
   - Add all environment variables to docker-compose files
   - Use .env file for local development
   - Document all configurable values in README

This refactoring will make the application more maintainable, secure, and deployable across different environments.