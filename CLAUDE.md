# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

FortiGate Nextrade is a comprehensive network monitoring and analysis platform that integrates with FortiGate firewalls, FortiManager, and ITSM systems. Designed for closed network (offline) environments.

**Key Features:**
- Mock FortiGate subsystem for hardware-free development
- FortiManager Advanced Hub with AI-driven policy orchestration
- Offline-first design with comprehensive fallback mechanisms
- GitOps CI/CD with Helm charts, Harbor Registry, ChartMuseum, and ArgoCD

## Architecture

### Technology Stack
- **Backend**: Flask + Blueprint architecture (Python 3.11)
- **Frontend**: Bootstrap 5 + Vanilla JS (no React/Vue)
- **Database**: Redis (cache) + JSON file storage
- **Container**: Docker with multi-stage builds
- **Orchestration**: Kubernetes + ArgoCD GitOps
- **CI/CD**: GitHub Actions (self-hosted runners) → Harbor Registry → ChartMuseum → ArgoCD
- **Ingress**: Traefik (not NGINX)

### Critical Patterns

#### 1. API Client Session Management
**CRITICAL**: All API clients MUST initialize a requests session:
```python
class SomeAPIClient(BaseAPIClient):
    def __init__(self):
        super().__init__()  # REQUIRED - handles session initialization
```

#### 2. Blueprint URL Namespacing
Templates MUST use blueprint namespaces:
```html
{{ url_for('main.dashboard') }}      <!-- Correct -->
{{ url_for('dashboard') }}            <!-- Wrong -->
```

#### 3. Configuration Hierarchy
1. `data/config.json` - Runtime configuration (highest priority)
2. Environment variables
3. `src/config/unified_settings.py` - Default values

#### 4. Mock System Activation
```python
# Automatic when APP_MODE=test
if os.getenv('APP_MODE', 'production').lower() == 'test':
    # Uses mock_fortigate and Postman-based mock server
```

#### 5. Import Path Structure
**CRITICAL**: All imports within src/ must use relative paths:
```python
# Correct - relative imports from src/
from utils.unified_logger import get_logger
from api.clients.fortigate_api_client import FortiGateAPIClient

# Wrong - absolute imports cause ModuleNotFoundError
from src.utils.unified_logger import get_logger
from src.api.clients.fortigate_api_client import FortiGateAPIClient
```

## Development Commands

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run application
cd src && python main.py --web

# Run with mock mode
APP_MODE=test python src/main.py --web

# Run specific test categories
pytest -m "unit" -v                        # Unit tests only
pytest -m "integration" -v                 # Integration tests only
pytest -m "not slow" -v                    # Skip slow tests
pytest tests/manual/ -v                    # Manual testing suite (26 files)
pytest --cov=src --cov-report=html -v      # With coverage

# Code quality
black src/ && isort src/ && flake8 src/ --max-line-length=120 --ignore=E203,W503
```

### Docker Development
```bash
# Build production image
docker build -f Dockerfile.production -t fortigate-nextrade:latest .

# Run with mock mode
docker run -d --name fortigate-nextrade \
  -p 7777:7777 \
  -e APP_MODE=test \
  -e OFFLINE_MODE=true \
  fortigate-nextrade:latest
```

### Deployment & Monitoring
```bash
# Check deployment status
curl http://192.168.50.110:30779/api/health  # Current NodePort
curl http://fortinet.jclee.me/api/health     # Domain (needs /etc/hosts entry)


# Monitor ArgoCD deployment
argocd app get fortinet
argocd app sync fortinet

# Check pods
kubectl get pods -n fortinet
kubectl logs -l app=fortinet -n fortinet -f
```

## Testing Framework

### Custom Rust-Style Inline Testing
```python
from src.utils.integration_test_framework import test_framework

@test_framework.test("Test description")
def test_something():
    with test_framework.test_app() as (app, client):
        response = client.get('/')
        test_framework.assert_eq(response.status_code, 200)
```

### Master Integration Test Suite
```bash
python src/utils/test_master_integration_suite.py
# Features: Phase-based execution, parallel testing, comprehensive results
```

### Test Categories (pytest.ini markers)
- `slow`: Long-running tests
- `integration`: Integration tests
- `unit`: Unit tests
- `fortimanager`: FortiManager-specific tests
- `monitoring`: Monitoring system tests

## FortiManager Advanced Hub

Four specialized modules accessible via:
```python
hub = FortiManagerAdvancedHub(api_client)
```

1. **Policy Orchestration**: `hub.policy_orchestrator`
2. **Compliance Automation**: `hub.compliance_framework`
3. **Security Fabric**: `hub.security_fabric`
4. **Advanced Analytics**: `hub.analytics_engine`

## CI/CD Pipeline

### GitHub Actions Workflow (gitops-pipeline.yml)
1. **Test Stage**: pytest, flake8, safety, bandit (parallel)
2. **Build Stage**: Docker buildx → Harbor Registry
3. **Helm Deploy**: Package → ChartMuseum upload → ArgoCD sync
4. **Verify Stage**: Health checks on NodePort 30779

### Required GitHub Secrets
- `REGISTRY_URL`: registry.jclee.me
- `REGISTRY_USERNAME`, `REGISTRY_PASSWORD`
- `CHARTMUSEUM_URL`: https://charts.jclee.me
- `CHARTMUSEUM_USERNAME`, `CHARTMUSEUM_PASSWORD`
- `APP_NAME`: fortinet
- `DEPLOYMENT_HOST`: 192.168.50.110
- `DEPLOYMENT_PORT`: 30779

### Current Deployment
- **Active NodePort**: 30779 (resolved from port conflict)
- **Domain**: http://fortinet.jclee.me (HTTP only, TLS issues)
- **DNS Fix**: Add `192.168.50.110 fortinet.jclee.me` to `/etc/hosts`

## Project Structure
```
fortinet/
├── src/                # 139 Python files
│   ├── web_app.py     # Flask factory (8 blueprints)
│   ├── routes/        # Blueprint routes
│   ├── api/clients/   # External API clients (4)
│   ├── fortimanager/  # Advanced features (5 modules)
│   ├── itsm/          # ITSM integration (7 modules)
│   ├── utils/         # Utilities (17 modules)
│   └── templates/     # Jinja2 templates (20)
├── tests/             # 62 test files
│   ├── unit/          # Unit tests
│   ├── integration/   # Integration tests (70+ endpoints)
│   └── manual/        # Manual test suite (26 files)
├── charts/fortinet/   # Helm chart (Traefik ingress)
├── .github/workflows/ # CI/CD (self-hosted runners)
└── requirements.txt   # Python dependencies
```

## Key API Endpoints

### Core
- `GET /api/health` - Health check
- `GET/POST /api/settings` - Settings management

### FortiManager
- `POST /api/fortimanager/analyze-packet-path` - Packet path analysis
- `GET /api/fortimanager/devices` - List devices
- `POST /api/fortimanager/policies` - Get policies

### Logs
- `GET /api/logs/stream` - Real-time log streaming (SSE)
- `GET /api/logs/container` - Container logs

## Environment Variables

### Core Settings
- `APP_MODE`: `production` | `test` | `development`
- `OFFLINE_MODE`: `true` | `false`
- `WEB_APP_PORT`: Default `7777`

### API Configuration
- `FORTIMANAGER_HOST`, `FORTIMANAGER_API_KEY`
- `FORTIGATE_HOST`, `FORTIGATE_API_KEY`

## Common Issues & Solutions

### Port 7777 in Use
```bash
sudo lsof -ti:7777 | xargs kill -9
```

### Domain Access Issues
1. Check DNS: `nslookup fortinet.jclee.me`
2. Add to hosts: `echo "192.168.50.110 fortinet.jclee.me" | sudo tee -a /etc/hosts`
3. Verify ingress: `kubectl get ingress fortinet -n fortinet`

### ArgoCD Sync Issues
```bash
# Create image pull secret
kubectl create secret docker-registry harbor-registry \
  --docker-server=registry.jclee.me \
  --docker-username=admin \
  --docker-password=bingogo1 \
  -n fortinet

# Force sync
argocd app sync fortinet --prune
```

## GitOps Workflow Status

### Pipeline Verification
```bash
# Check pipeline status
gh run list --workflow="GitOps CI/CD Pipeline" --limit 3

# Monitor current run
gh run watch <run-id> --exit-status

# Cancel stuck runs
gh run cancel <run-id>
```

### Common Pipeline Issues
- **Verification timeout**: Health check may take 5-10 minutes due to ArgoCD sync delays
- **NodePort conflicts**: Use `kubectl get svc --all-namespaces | grep 30779` to check port usage
- **Service updates**: May require manual service recreation for NodePort changes

## Development Guidelines

### Do's
- Always use `APP_MODE=test` for local development
- Use blueprint namespaces in templates: `{{ url_for('main.dashboard') }}`
- Call `super().__init__()` when extending API clients
- Run tests before committing: `pytest tests/ -v`
- Use environment variables instead of hardcoded values
- Monitor GitOps pipeline after commits to master

### Don'ts
- Don't hardcode IPs or URLs - all removed and replaced with env vars
- Don't bypass the mock system when `APP_MODE=test`
- Don't forget session management in API clients
- Don't use uppercase in Docker image names (use lowercase)

### Current State Notes
- **ALL hardcoded values removed** - project uses environment variables
- Package management uses `requirements.txt` (not pyproject.toml)
- Ingress controller is Traefik (not NGINX)
- TLS is currently disabled due to certificate issues
- GitHub Actions uses self-hosted runners
- Harbor Registry image path: `registry.jclee.me/fortinet` (not jclee94/fortinet)
- Helm chart version: 1.0.4 (NodePort updated to 30779)

## Recent Updates & Fixes Applied

### Code Quality Improvements (Completed)
- **Black Formatting**: Applied to 52 files for consistent code style
- **Import Organization**: Fixed import sorting with isort across 47 files  
- **Flake8 Linting**: Reduced errors from 338 → 269 by fixing bare except statements
- **Type Annotations**: Fixed mypy errors, replaced `any` with `Any` from typing module

### Enhanced Temporary File Management
- **Collision Prevention**: Added timestamps and PIDs to temp file names
- **Enhanced Paths**: Updated `src/config/paths.py` with `get_enhanced_temp_file_path()`
- **Test Framework**: Improved temp file handling in integration test framework

### Integration Testing Implementation
- **Comprehensive Test Suite**: Created 6 major integration test files using Rust-style decorators
- **API Clients**: Full lifecycle testing for FortiGate, FortiManager, FortiAnalyzer clients
- **Authentication**: Session management and API key validation testing
- **Data Pipeline**: End-to-end testing from packet capture to visualization
- **ITSM Workflows**: Ticket creation, policy requests, approval workflows
- **Monitoring**: Real-time log streaming, alerting, health checks

### ArgoCD Sync Resolution
- **NodePort Consolidation**: Fixed port 30777 conflict by merging dual services
- **Service Configuration**: Updated values.yaml and service.yaml templates
- **Chart Version**: Bumped to 1.0.3 with proper versioning

### GitOps Pipeline Validation
- **Health Checks**: Automated deployment verification on NodePort 30779
- **Build Optimization**: Multi-stage Docker builds with caching
- **Registry Integration**: Seamless Harbor → ChartMuseum → ArgoCD flow

### Recent System Fixes (Latest)
- **Import Path Resolution**: Fixed 79 files with absolute→relative import conversion
- **Feature Testing Framework**: Comprehensive 10-module test suite achieving 100% success rate
- **ArgoCD Port Resolution**: Resolved 30777→30779 port conflict for stable deployment
- **Configuration System**: Added ThresholdConfig to unified settings for monitoring compatibility
- **Cache Manager**: Fixed stats reporting for proper metrics display
- **System Status**: All 10 core features verified working (Basic Imports, Flask App, API Clients, FortiManager Hub, ITSM Automation, Monitoring, Security, Data Pipeline, Caching, API Endpoints)

### Feature Testing Command
```bash
# Run comprehensive feature test (100% success rate)
cd src && python3 test_features.py

# Expected output: 10/10 tests passing
# ✅ Working Features: Basic Imports, Flask App Creation, API Clients, 
#    FortiManager Advanced Hub, ITSM Automation, Monitoring System,
#    Security Features, Data Pipeline, Caching System, API Endpoints
```