# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

FortiGate Nextrade is a comprehensive network monitoring and analysis platform that integrates with FortiGate firewalls, FortiManager, and ITSM systems. Designed for closed network (offline) environments, it provides real-time monitoring, policy analysis, network topology visualization, and automated firewall policy management.

Key differentiators:
- **Mock FortiGate** subsystem for hardware-free development and testing
- **FortiManager Advanced Hub** with AI-driven policy orchestration and compliance automation
- **Offline-first design** with comprehensive fallback mechanisms
- **GitHub Actions CI/CD** with automated deployment via Docker registry

## Architecture Overview

### Core Technology Stack
- **Backend**: Flask + Blueprint architecture (Python 3.11)
- **Frontend**: Bootstrap 5 + Vanilla JS (no React/Vue dependencies)
- **Database**: Redis (cache) + JSON file storage (persistence)
- **Container**: Docker/Podman with multi-stage builds
- **Deployment**: GitHub Actions → Docker Registry → Production Server
- **Monitoring**: Real-time SSE (Server-Sent Events) for log streaming

### Key Architecture Patterns

#### 1. Flask Blueprint Modular Architecture
```python
# src/web_app.py - Factory pattern
def create_app():
    app = Flask(__name__)
    # Blueprint registration
    app.register_blueprint(main_bp)        # Main pages
    app.register_blueprint(api_bp)         # REST APIs
    app.register_blueprint(fortimanager_bp) # FortiManager integration
    app.register_blueprint(itsm_bp)        # ITSM integration
    app.register_blueprint(logs_bp)        # Log management (NEW)
    return app
```

#### 2. API Client Session Management
**CRITICAL**: All API clients MUST initialize a requests session:
```python
class SomeAPIClient(BaseAPIClient):
    def __init__(self):
        super().__init__()
        self.session = requests.Session()  # REQUIRED!
        self.session.verify = self.verify_ssl
```

#### 3. Configuration Hierarchy
Priority order (highest to lowest):
1. `data/config.json` - Runtime configuration
2. Environment variables
3. `src/config/unified_settings.py` - Default values

#### 4. Mock System for Testing
```python
# Automatic mock activation
if os.getenv('APP_MODE', 'production').lower() == 'test':
    # Uses mock_fortigate for all operations
```

## Development Commands

### Local Development
```bash
# Run application (Flask development server)
cd src && python main.py --web

# Run with specific environment
APP_MODE=test python src/main.py --web
APP_MODE=production python src/main.py --web

# Run specific test file or test function
pytest tests/test_api_clients.py -v                           # Run single test file
pytest tests/test_api_clients.py::TestBaseApiClient -v       # Run single test class
pytest tests/test_api_clients.py::TestBaseApiClient::test_offline_mode_detection -v  # Run single test

# Run tests with coverage
pytest tests/ --cov=src --cov-report=html -v

# Code quality checks
black src/                          # Format code
isort src/                          # Sort imports
flake8 src/ --max-line-length=120  # Lint
mypy src/ --ignore-missing-imports  # Type check
```

### Docker Development
```bash
# Build production image
docker build -f Dockerfile.production -t fortigate-nextrade:latest .

# Run container with test mode
docker run -d --name fortigate-nextrade \
  -p 7777:7777 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  -e APP_MODE=test \
  -e OFFLINE_MODE=true \
  fortigate-nextrade:latest

# View container logs
docker logs -f fortigate-nextrade

# Access container shell
docker exec -it fortigate-nextrade /bin/bash
```

### GitHub Actions Deployment
```bash
# Deploy to production (automatic on push to master/main)
git add -A
git commit -m "feat: your feature description"
git push origin master

# Monitor deployment
gh run list --limit 5
gh run view <run-id>

# Required GitHub Secrets
DOCKER_USERNAME     # Docker Hub username
DOCKER_PASSWORD     # Docker Hub password
```

## Critical Implementation Details

### 1. Blueprint URL Namespacing
Templates MUST use blueprint namespaces:
```html
<!-- Correct -->
{{ url_for('main.dashboard') }}
{{ url_for('api.get_settings') }}
{{ url_for('logs.logs_management') }}

<!-- Wrong -->
{{ url_for('dashboard') }}
```

### 2. Error Handling Pattern
```python
try:
    result = api_client.method()
except FortiManagerAPIException as e:
    logger.error(f"FortiManager error: {e}")
    return jsonify({"error": str(e)}), 500
```

### 3. Security Decorators
```python
@rate_limit(max_requests=30, window=60)  # Rate limiting
@csrf_protect                            # CSRF protection
@admin_required                          # Authentication
def protected_endpoint():
    pass
```

### 4. Caching Pattern
```python
from src.utils.unified_cache_manager import get_cache_manager

cache_manager = get_cache_manager()
cache_manager.set('key', data, ttl=300)  # 5 minutes
data = cache_manager.get('key')
```

### 5. Logging Pattern
```python
from src.utils.unified_logger import get_logger

logger = get_logger(__name__)
logger.info("Operation successful")
logger.error(f"Operation failed: {error}")
```

## FortiManager Advanced Hub

The FortiManager integration includes four advanced modules:

### 1. Policy Orchestration Engine
```python
hub = FortiManagerAdvancedHub(api_client)
result = await hub.policy_orchestrator.apply_template(
    "zero_trust_access", 
    parameters={...}
)
```

### 2. Compliance Automation
```python
violations = await hub.compliance_framework.check_compliance(
    devices=["FW-01"], 
    frameworks=["PCI-DSS", "HIPAA", "ISO27001"]
)
```

### 3. Security Fabric Integration
```python
threats = await hub.security_fabric.detect_threats()
response = await hub.security_fabric.coordinate_response(threats)
```

### 4. Advanced Analytics
```python
trends = await hub.analytics_engine.analyze_trends_async()
anomalies = await hub.analytics_engine.detect_anomalies()
```

## Testing Guidelines

### Mock FortiGate Testing
```bash
# Enable test mode (uses mock data)
export APP_MODE=test

# Test packet analysis
curl -X POST http://localhost:7777/api/fortimanager/analyze-packet-path \
  -H "Content-Type: application/json" \
  -d '{"src_ip": "192.168.1.100", "dst_ip": "172.16.10.100", "port": 80, "protocol": "tcp"}'

# Test health endpoint
curl http://localhost:7777/api/health
```

### Running Test Suite
```bash
# Unit tests
pytest tests/unit/ -v

# Integration tests
pytest tests/integration/ -v

# All tests with coverage
pytest --cov=src --cov-report=html --cov-report=term-missing
```

## Common Issues & Solutions

### Port 7777 Already in Use
```bash
# Linux/Mac
sudo lsof -ti:7777 | xargs kill -9

# Docker containers
docker ps --filter "publish=7777" -q | xargs docker stop
docker ps -a --filter "publish=7777" -q | xargs docker rm

# Windows PowerShell
Get-Process -Id (Get-NetTCPConnection -LocalPort 7777).OwningProcess | Stop-Process -Force
```

### Flask Development Server Warning
The application currently uses Flask development server in production due to a Gunicorn configuration issue. This is tracked for resolution but doesn't affect functionality.

### Redis Connection Failed
This is a warning, not an error. The system falls back to memory cache when Redis is unavailable.

## Project Structure

```
fortinet/
├── src/
│   ├── main.py                 # Entry point with CLI args
│   ├── web_app.py             # Flask application factory
│   ├── routes/                # Blueprint routes
│   │   ├── main_routes.py    # Page routes
│   │   ├── api_routes.py     # REST API routes
│   │   ├── fortimanager.py   # FortiManager routes
│   │   ├── itsm_routes.py    # ITSM routes
│   │   └── logs_routes.py    # Log management routes
│   ├── api/clients/          # External API clients
│   ├── modules/              # Core business logic
│   ├── utils/                # Utilities (logging, caching, security)
│   ├── config/               # Configuration management
│   ├── templates/            # Jinja2 HTML templates
│   └── static/               # CSS, JS, images
├── data/                     # Runtime data and configs
├── logs/                     # Application logs
├── tests/                    # Test suite
├── .github/workflows/        # GitHub Actions CI/CD
└── Dockerfile.production     # Production Docker image
```

## Environment Variables

### Core Settings
- `APP_MODE`: `production` | `test` | `development`
- `OFFLINE_MODE`: `true` | `false` (for closed networks)
- `WEB_APP_PORT`: Default `7777`
- `WEB_APP_HOST`: Default `0.0.0.0`

### Feature Flags
- `DISABLE_SOCKETIO`: Disable WebSocket support
- `DISABLE_EXTERNAL_CALLS`: Block all external API calls
- `REDIS_ENABLED`: Enable/disable Redis cache

### API Configuration
- `FORTIMANAGER_HOST`: FortiManager server address
- `FORTIMANAGER_API_KEY`: API authentication key
- `FORTIGATE_HOST`: FortiGate device address
- `FORTIGATE_API_KEY`: API authentication key

## API Endpoints

### Core APIs
- `GET /api/health` - Health check
- `GET /api/settings` - Get current settings
- `POST /api/settings` - Update settings

### FortiManager APIs
- `POST /api/fortimanager/analyze-packet-path` - Analyze firewall path
- `GET /api/fortimanager/devices` - List managed devices
- `POST /api/fortimanager/policies` - Get firewall policies

### Log Management APIs (NEW)
- `GET /api/logs/container` - Get Docker container logs
- `GET /api/logs/application` - Get application logs
- `GET /api/logs/stream` - Real-time log streaming (SSE)
- `POST /api/logs/search` - Search logs
- `GET /api/logs/stats` - Log statistics

## Security Considerations

1. **CSRF Protection**: All POST endpoints require CSRF tokens
2. **Rate Limiting**: API endpoints have request limits
3. **Admin Authentication**: Sensitive endpoints require admin access
4. **Input Validation**: All user inputs are validated
5. **XSS Protection**: Security headers prevent XSS attacks
6. **No Hardcoded Secrets**: All secrets use environment variables

## Performance Optimization

1. **Caching**: Redis/memory cache for API responses
2. **Lazy Loading**: Blueprints loaded on demand
3. **Connection Pooling**: Reused HTTP sessions
4. **Async Operations**: FortiManager advanced features use async
5. **Log Rotation**: Automatic log file management

## Troubleshooting Guide

### Mock FortiGate Not Working
If test mode isn't activating the mock system:
```bash
# Verify environment variable
echo $APP_MODE
# Should output: test

# Force mock mode
export FORTIGATE_HOST="mock://fortigate"
export FORTIMANAGER_HOST="mock://fortimanager"
```

### WebSocket Connection Issues
If real-time monitoring isn't working:
```bash
# Check if Socket.IO is disabled
echo $DISABLE_SOCKETIO

# Enable Socket.IO
unset DISABLE_SOCKETIO
```

### API Authentication Failures
For FortiManager API authentication issues:
```python
# The client tries multiple auth methods in order:
# 1. Bearer token
# 2. X-API-Key (usually works for demos)
# 3. Session-based
# Check logs/web_app.log for which method succeeded
```

## Dependencies

### Core Requirements (requirements.txt)
- Flask==2.3.2
- requests==2.31.0
- redis==4.5.5
- pytest==7.3.1
- gunicorn==20.1.0

### Development Tools
- black - Code formatter
- flake8 - Linter
- mypy - Type checker
- isort - Import sorter
- pytest-cov - Test coverage

## Important Notes

### Session Management
Every API client MUST properly initialize and maintain a requests session. This is critical for connection pooling and performance. The base class handles this, but if overriding `__init__`, always call `super().__init__()`.

### Template Routing
Always use blueprint namespaces in templates. This is a common source of errors:
```jinja2
{# WRONG - Will cause 404 errors #}
<a href="{{ url_for('dashboard') }}">Dashboard</a>

{# CORRECT - Uses blueprint namespace #}
<a href="{{ url_for('main.dashboard') }}">Dashboard</a>
```

### Mock Mode Activation
The mock system activates automatically when `APP_MODE=test`. This allows full testing without FortiGate hardware. Mock data is comprehensive and includes:
- System status and health metrics
- Firewall policies and rules
- Network topology
- Security events
- Performance metrics