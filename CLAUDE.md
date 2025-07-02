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
- **Deployment**: GitHub Actions → registry.jclee.me → Watchtower → Production
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
    app.register_blueprint(logs_bp)        # Log management
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

# Quick quality check command (run all at once)
black src/ && isort src/ && flake8 src/ --max-line-length=120 --ignore=E203,W503 && mypy src/ --ignore-missing-imports
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

# Docker Compose operations
./scripts/docker-start.sh  # Start with Docker Compose
./scripts/docker-stop.sh   # Stop containers
```

### GitHub Actions Deployment
```bash
# Deploy to production (automatic on push to master/main)
git add -A
git commit -m "feat: your feature description"
git push origin master

# Monitor deployment
gh run list --limit 5 --repo JCLEE94/fortinet
gh run view <run-id> --repo JCLEE94/fortinet

# Check deployment status
curl https://fortinet.jclee.me/api/health

# Validate CI/CD configuration
./scripts/validate-cicd.sh all
```

### Manual Deployment
```bash
# Deploy manually to production
./scripts/manual-deploy.sh

# Deploy with specific options
./scripts/deploy.sh build   # Build only
./scripts/deploy.sh push    # Push to registry
./scripts/deploy.sh deploy  # Full deployment
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

## CI/CD Pipeline

### GitHub Actions Workflow
The pipeline runs on push to main/master/develop branches:

1. **Test Stage**: Runs pytest with coverage
2. **Security Scan**: Checks for vulnerabilities
3. **Build Stage**: Creates Docker image
4. **Push Stage**: Pushes to registry.jclee.me
5. **Deploy Stage**: Watchtower auto-deploys

### Required GitHub Secrets
```
DOCKER_USERNAME     # Docker Hub username
DOCKER_PASSWORD     # Docker Hub password
REGISTRY_USERNAME   # Private registry username  
REGISTRY_PASSWORD   # Private registry password
```

### Pipeline Validation
```bash
# Validate entire CI/CD setup
./scripts/validate-cicd.sh all

# Individual checks
./scripts/validate-cicd.sh github      # GitHub Actions validation
./scripts/validate-cicd.sh docker      # Docker build validation
./scripts/validate-cicd.sh secrets     # Secrets validation
./scripts/validate-cicd.sh deployment  # Deployment validation
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

# Manual tests (specific FortiManager scenarios)
python tests/manual/test_fortimanager_demo.py

# Run tests with markers
pytest -m "unit" -v         # Unit tests only
pytest -m "integration" -v  # Integration tests only
pytest -m "not slow" -v     # Skip slow tests
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

### Docker Build Failures
If BuildKit errors occur:
```bash
export DOCKER_BUILDKIT=0
docker build -f Dockerfile.production -t fortigate-nextrade:latest .
```

### Troubleshooting Script
```bash
# Run comprehensive troubleshooting
./scripts/troubleshoot.sh all

# Specific checks
./scripts/troubleshoot.sh docker
./scripts/troubleshoot.sh network
./scripts/troubleshoot.sh app
```

## Project Structure

```
fortinet/
├── src/
│   ├── main.py                 # Entry point with CLI args
│   ├── web_app.py             # Flask application factory
│   ├── routes/                # Blueprint routes
│   │   ├── main_routes.py    # Page routes
│   │   ├── api_routes.py     # REST API routes
│   │   ├── fortimanager_routes.py   # FortiManager routes
│   │   ├── itsm_routes.py    # ITSM routes
│   │   └── logs_routes.py    # Log management routes
│   ├── api/clients/          # External API clients
│   ├── modules/              # Core business logic
│   ├── fortimanager/         # Advanced FortiManager features
│   ├── utils/                # Utilities (logging, caching, security)
│   ├── config/               # Configuration management
│   ├── templates/            # Jinja2 HTML templates
│   └── static/               # CSS, JS, images
├── tests/                    # Test suite
│   ├── unit/                # Unit tests
│   ├── integration/         # Integration tests
│   └── manual/              # Manual test scripts
├── docs/                    # Documentation
│   ├── guides/             # User guides
│   ├── deployment/         # Deployment guides
│   └── reports/            # Analysis reports
├── scripts/                # Utility scripts
├── data/                   # Runtime data and configs
├── logs/                   # Application logs
├── .github/workflows/      # GitHub Actions CI/CD
└── Dockerfile.production   # Production Docker image
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
- `GET /api/fortimanager/adom/list` - List ADOMs
- `POST /api/fortimanager/policy-packages` - Get policy packages

### Log Management APIs
- `GET /api/logs/container` - Get Docker container logs
- `GET /api/logs/application` - Get application logs
- `GET /api/logs/stream` - Real-time log streaming (SSE)
- `POST /api/logs/search` - Search logs
- `GET /api/logs/stats` - Log statistics

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

### FortiManager Authentication
The client tries multiple auth methods in order:
1. Bearer token
2. X-API-Key (usually works for demos)
3. Session-based

Check `logs/web_app.log` for which method succeeded.

### Production Deployment Flow
1. Code pushed to GitHub
2. GitHub Actions builds and tests
3. Docker image pushed to registry.jclee.me
4. Watchtower detects new image
5. Automatic rolling update in production
6. Available at https://fortinet.jclee.me