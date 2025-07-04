# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

FortiGate Nextrade is a comprehensive network monitoring and analysis platform that integrates with FortiGate firewalls, FortiManager, and ITSM systems. Designed for closed network (offline) environments, it provides real-time monitoring, policy analysis, network topology visualization, and automated firewall policy management.

Key differentiators:
- **Mock FortiGate** subsystem for hardware-free development and testing
- **FortiManager Advanced Hub** with AI-driven policy orchestration and compliance automation
- **Offline-first design** with comprehensive fallback mechanisms
- **ArgoCD GitOps** deployment with multi-cluster support
- **GitHub Actions CI/CD** with automated deployment via Docker registry

## Architecture Overview

### Core Technology Stack
- **Backend**: Flask + Blueprint architecture (Python 3.11)
- **Frontend**: Bootstrap 5 + Vanilla JS (no React/Vue dependencies)
- **Database**: Redis (cache) + JSON file storage (persistence)
- **Container**: Docker/Podman with multi-stage builds
- **Orchestration**: Kubernetes + ArgoCD GitOps
- **CI/CD**: GitHub Actions → registry.jclee.me → ArgoCD → Kubernetes
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

# Run tests
pytest tests/ -v                                    # All tests
pytest tests/test_api_clients.py -v                # Single test file
pytest tests/test_api_clients.py::TestBaseApiClient -v  # Single test class
pytest --cov=src --cov-report=html -v             # With coverage

# Code quality checks
black src/                          # Format code
isort src/                          # Sort imports
flake8 src/ --max-line-length=120  # Lint
mypy src/ --ignore-missing-imports  # Type check

# Quick quality check (run all at once)
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

# Docker Compose operations
./scripts/docker-start.sh  # Start with Docker Compose
./scripts/docker-stop.sh   # Stop containers
```

### ArgoCD GitOps Deployment
```bash
# Deploy to production (automatic on push to master/main)
git add -A
git commit -m "feat: your feature description"
git push origin master

# Monitor ArgoCD deployment
argocd app get fortinet-primary    # Primary cluster
argocd app list                    # All applications

# Check deployment status
curl https://fortinet.jclee.me/api/health

# Validate CI/CD configuration
./scripts/validate-cicd.sh all
```

### Manual Deployment Scripts
```bash
# Initial deployment to production (first time)
./scripts/initial-deploy.sh

# Multi-cluster deployment setup
./scripts/setup-multi-cluster-simple.sh

# Add new cluster (when 192.168.50.110 is ready)
./scripts/add-cluster.sh

# Deploy manually to production
./scripts/manual-deploy.sh
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

### ArgoCD GitOps Workflow
The pipeline runs on push to main/master/develop branches:

1. **Test Stage**: Runs pytest with coverage
2. **Build Stage**: Creates Docker image
3. **Push Stage**: Pushes to registry.jclee.me
4. **GitOps Stage**: Updates kustomization.yaml with new image tag and commits to Git
5. **ArgoCD Pull**: ArgoCD polls Git repository (every 3 minutes) and auto-deploys changes

### Required GitHub Secrets
```
REGISTRY_USERNAME    # Private registry username (qws9411)
REGISTRY_PASSWORD    # Private registry password
ARGOCD_AUTH_TOKEN    # ArgoCD API authentication token
ARGOCD_PASSWORD      # ArgoCD admin password
```

### ArgoCD Application Management

#### Quick Sync Commands
```bash
# 1. Login (once)
argocd login argo.jclee.me --username admin --password bingogo1 --insecure --grpc-web

# 2. Check status
argocd app list                    # All applications
argocd app get fortinet-primary    # Primary cluster

# 3. Manual sync (emergency deployment)
argocd app sync fortinet-primary --prune

# 4. Web dashboard
# https://argo.jclee.me/applications/fortinet-primary
```

#### Direct Kubernetes Deployment (Emergency)
```bash
# Bypass ArgoCD
kubectl apply -k k8s/manifests/

# Update image directly
kubectl set image deployment/fortinet-app fortinet=registry.jclee.me/fortinet:new-tag -n fortinet
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

# Run tests with markers
pytest -m "unit" -v         # Unit tests only
pytest -m "integration" -v  # Integration tests only
pytest -m "not slow" -v     # Skip slow tests
```

## Multi-Cluster Deployment

### Current Status
- **Primary Cluster**: kubernetes.default.svc ✅ Active
  - Application: fortinet-primary
  - Replicas: 3 (High resources)
  
- **Secondary Cluster**: 192.168.50.110:6443 ⚠️ Ready for activation
  - Application: fortinet-secondary (prepared)
  - Replicas: 2 (Medium resources)

### Multi-Cluster Setup
```bash
# When secondary cluster is ready:
./scripts/add-cluster.sh             # Register cluster with ArgoCD
./scripts/setup-multi-cluster-simple.sh  # Create multi-cluster apps

# Monitor both clusters
argocd app list
argocd cluster list
```

For detailed multi-cluster setup, see `docs/multi-cluster-setup.md`.

## Common Issues & Solutions

### Port 7777 Already in Use
```bash
# Linux/Mac
sudo lsof -ti:7777 | xargs kill -9

# Docker containers
docker ps --filter "publish=7777" -q | xargs docker stop
```

### Flask Development Server Warning
The application currently uses Flask development server in production due to a Gunicorn configuration issue. This is tracked for resolution but doesn't affect functionality.

### Redis Connection Failed
This is a warning, not an error. The system falls back to memory cache when Redis is unavailable.

### Docker Build Failures
```bash
export DOCKER_BUILDKIT=0
docker build -f Dockerfile.production -t fortigate-nextrade:latest .
```

## Project Structure

```
fortinet/
├── src/
│   ├── main.py                 # Entry point with CLI args
│   ├── web_app.py             # Flask application factory
│   ├── routes/                # Blueprint routes
│   ├── api/clients/          # External API clients
│   ├── modules/              # Core business logic
│   ├── fortimanager/         # Advanced FortiManager features
│   ├── utils/                # Utilities (logging, caching, security)
│   ├── config/               # Configuration management
│   ├── templates/            # Jinja2 HTML templates
│   └── static/               # CSS, JS, images
├── tests/                    # Test suite
├── docs/                    # Documentation
├── scripts/                # Utility scripts
├── k8s/
│   ├── manifests/          # Kubernetes deployment manifests
│   └── overlays/           # Environment-specific configurations
├── argocd/                  # ArgoCD application definitions
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
Always use blueprint namespaces in templates to avoid 404 errors.

### Mock Mode Activation
The mock system activates automatically when `APP_MODE=test`. This allows full testing without FortiGate hardware.

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
4. GitHub Actions updates kustomization.yaml with new image tag
5. ArgoCD polls Git repository and detects changes
6. ArgoCD automatically deploys to all configured clusters
7. Available at https://fortinet.jclee.me

### ArgoCD Application Structure
- **fortinet-primary**: Main application on primary cluster ✅
- **fortinet-secondary**: Secondary cluster deployment (ready when cluster is available)
- **blacklist**: IP blacklist management system (separate namespace)

Each application has independent deployment cycles and can target different clusters.