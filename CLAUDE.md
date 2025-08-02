# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

FortiGate Nextrade is a comprehensive network monitoring and analysis platform that integrates with FortiGate firewalls, FortiManager, and ITSM systems. Designed for closed network (offline) environments with both monolithic and microservices architecture support.

**Key Features:**
- Mock FortiGate subsystem for hardware-free development
- FortiManager Advanced Hub with AI-driven policy orchestration
- Real-time packet capture and analysis
- Offline-first design with comprehensive fallback mechanisms
- Dual architecture: Monolithic (legacy) + MSA (microservices)
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
- **MSA Infrastructure**: Kong Gateway, Consul, RabbitMQ

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
```

## Development Commands

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run application (monolithic mode)
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

# Run feature test (validates 10 core features)
cd src && python3 test_features.py
```

### MSA Development
```bash
# Start full MSA stack
docker-compose -f docker-compose.msa.yml up -d

# Configure Kong Gateway routes
./scripts/setup-kong-routes.sh

# Check service status
docker-compose -f docker-compose.msa.yml ps

# Access MSA endpoints
# Kong Gateway: http://localhost:8000
# Consul UI: http://localhost:8500
# RabbitMQ UI: http://localhost:15672
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
curl http://192.168.50.110:30777/api/health  # Current NodePort
curl http://fortinet.jclee.me/api/health     # Domain (needs /etc/hosts entry)

# Monitor ArgoCD deployment
argocd app get fortinet
argocd app sync fortinet

# Check pods
kubectl get pods -n fortinet
kubectl logs -l app=fortinet -n fortinet -f
```

## Testing Framework

### Pytest Configuration
- **Markers**: `slow`, `integration`, `unit`, `fortimanager`, `monitoring`
- **Coverage target**: 5% minimum (configurable in pytest.ini)
- **Test discovery**: `tests/` directory

### Custom Rust-Style Testing Framework
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

## Key Components

### FortiManager Advanced Hub
Four specialized modules accessible via:
```python
hub = FortiManagerAdvancedHub(api_client)
```

1. **Policy Orchestrator**: `hub.policy_orchestrator` - AI-driven policy management
2. **Compliance Framework**: `hub.compliance_framework` - Automated compliance checks
3. **Security Fabric**: `hub.security_fabric` - Integrated security management
4. **Analytics Engine**: `hub.analytics_engine` - Advanced analytics and reporting

### Packet Sniffer System
Located in `src/security/packet_sniffer/`:
- **Analyzers**: Protocol-specific analysis (DNS, HTTP, TLS, FortiManager)
- **Filters**: BPF and advanced packet filtering
- **Exporters**: Multiple format support (CSV, JSON, PCAP, Reports)
- **Inspectors**: Deep packet inspection capabilities
- **Session Management**: Stateful packet tracking

### ITSM Integration
Located in `src/itsm/`:
- **Ticket Automation**: Automated ticket creation/updates
- **Policy Requests**: Firewall policy request workflows
- **Approval Workflows**: Multi-level approval processes
- **ServiceNow Integration**: API client for ServiceNow

## CI/CD Pipeline

### GitHub Actions Workflow (gitops-pipeline.yml)
1. **Test Stage**: pytest, flake8, safety, bandit (parallel)
2. **Build Stage**: Docker buildx → Harbor Registry
3. **Helm Deploy**: Package → ChartMuseum upload → ArgoCD sync
4. **Verify Stage**: Health checks on NodePort 30777

### Required GitHub Secrets
- `REGISTRY_URL`: registry.jclee.me
- `REGISTRY_USERNAME`, `REGISTRY_PASSWORD`
- `CHARTMUSEUM_URL`: https://charts.jclee.me
- `CHARTMUSEUM_USERNAME`, `CHARTMUSEUM_PASSWORD`
- `APP_NAME`: fortinet
- `DEPLOYMENT_HOST`: 192.168.50.110
- `DEPLOYMENT_PORT`: 30777

## Project Structure
```
fortinet/
├── src/                      # Monolithic application (139 Python files)
│   ├── web_app.py           # Flask factory (8 blueprints)
│   ├── main.py              # Entry point
│   ├── routes/              # Blueprint routes (8 modules)
│   ├── api/clients/         # External API clients (4)
│   ├── fortimanager/        # Advanced features (5 modules)
│   ├── itsm/                # ITSM integration (7 modules)
│   ├── security/            # Security components
│   │   └── packet_sniffer/  # Packet capture system
│   ├── monitoring/          # Monitoring system
│   ├── analysis/            # Analysis engines
│   ├── utils/               # Utilities (17 modules)
│   └── templates/           # Jinja2 templates (20)
├── services/                # MSA microservices
│   ├── auth/                # Authentication service (8081)
│   ├── fortimanager/        # FortiManager service (8082)
│   ├── itsm/                # ITSM service (8083)
│   ├── monitoring/          # Monitoring service (8084)
│   ├── security/            # Security service (8085)
│   ├── analysis/            # Analysis service (8086)
│   └── config/              # Configuration service (8087)
├── tests/                   # Test suite (62 files)
│   ├── unit/                # Unit tests
│   ├── integration/         # Integration tests (70+ endpoints)
│   ├── manual/              # Manual test suite (26 files)
│   └── msa/                 # MSA-specific tests
├── charts/fortinet/         # Helm chart (Traefik ingress)
├── docker-compose.msa.yml   # MSA development stack
├── .github/workflows/       # CI/CD (self-hosted runners)
└── requirements.txt         # Python dependencies
```

## Key API Endpoints

### Core APIs (Monolithic)
- `GET /api/health` - Health check
- `GET/POST /api/settings` - Settings management

### FortiManager APIs
- `POST /api/fortimanager/analyze-packet-path` - Packet path analysis
- `GET /api/fortimanager/devices` - List devices
- `POST /api/fortimanager/policies` - Get policies
- `GET /api/fortimanager/compliance` - Compliance status

### ITSM APIs
- `GET/POST /api/itsm/tickets` - Ticket management
- `POST /api/itsm/policy-requests` - Policy request automation
- `GET /api/itsm/approvals` - Approval workflows

### Monitoring APIs
- `GET /api/logs/stream` - Real-time log streaming (SSE)
- `GET /api/logs/container` - Container logs
- `GET /api/monitoring/metrics` - System metrics
- `GET /api/monitoring/alerts` - Alert management

### Security APIs
- `POST /api/security/scan` - Security scanning
- `GET /api/security/packets` - Packet analysis results
- `GET /api/security/threats` - Threat detection

## Environment Variables

### Core Settings
- `APP_MODE`: `production` | `test` | `development`
- `OFFLINE_MODE`: `true` | `false`
- `WEB_APP_PORT`: Default `7777`
- `SECRET_KEY`: Required for production

### API Configuration
- `FORTIMANAGER_HOST`, `FORTIMANAGER_API_KEY`
- `FORTIGATE_HOST`, `FORTIGATE_API_KEY`
- `ITSM_BASE_URL`, `ITSM_API_KEY`

### MSA Configuration
- `CONSUL_URL`: Service discovery
- `RABBITMQ_URL`: Message queue
- `REDIS_URL`: Cache backend
- `KONG_ADMIN_URL`: API Gateway admin

## Common Issues & Solutions

### Port 7777 in Use
```bash
sudo lsof -ti:7777 | xargs kill -9
```

### Import Errors
Ensure you're running from the correct directory:
```bash
cd src && python main.py --web  # Correct
python src/main.py --web        # Wrong - causes import errors
```

### Mock Mode Not Working
Check environment variable:
```bash
export APP_MODE=test
python src/main.py --web
```

### Domain Access Issues
Add to hosts file:
```bash
echo "192.168.50.110 fortinet.jclee.me" | sudo tee -a /etc/hosts
```

### ArgoCD Sync Issues
```bash
# Create image pull secret
kubectl create secret docker-registry harbor-registry \
  --docker-server=registry.jclee.me \
  --docker-username=admin \
  --docker-password=$PASSWORD \
  -n fortinet

# Force sync
argocd app sync fortinet --prune
```

## Development Guidelines

### Do's
- Always use `APP_MODE=test` for local development
- Use blueprint namespaces in templates: `{{ url_for('main.dashboard') }}`
- Call `super().__init__()` when extending API clients
- Run tests before committing: `pytest tests/ -v`
- Use environment variables instead of hardcoded values
- Run code quality checks: `black src/ && isort src/ && flake8 src/`
- Use the custom test framework for integration tests

### Don'ts
- Don't use absolute imports within src/ directory
- Don't hardcode IPs, URLs, or credentials
- Don't bypass the mock system when `APP_MODE=test`
- Don't forget session management in API clients
- Don't use uppercase in Docker image names
- Don't commit without running the linter

### Testing Best Practices
- Mark tests appropriately: `@pytest.mark.unit`, `@pytest.mark.integration`
- Use fixtures for common test data
- Mock external API calls in unit tests
- Use `APP_MODE=test` for integration tests
- Run the feature test to validate core functionality: `python src/test_features.py`

## MSA Service Architecture

### Service Ports
- **Kong Gateway**: 8000 (proxy), 8001 (admin), 8002 (GUI)
- **Auth Service**: 8081
- **FortiManager Service**: 8082
- **ITSM Service**: 8083
- **Monitoring Service**: 8084
- **Security Service**: 8085
- **Analysis Service**: 8086
- **Configuration Service**: 8087
- **Consul**: 8500
- **RabbitMQ**: 5672 (AMQP), 15672 (Management)

### Service Communication
- All external requests go through Kong Gateway
- Services discover each other via Consul
- Async messaging via RabbitMQ
- Shared cache via Redis

## Running Tests

### Single Test Execution
```bash
# Run specific test file
pytest tests/unit/test_specific.py -v

# Run specific test function
pytest tests/unit/test_specific.py::TestClass::test_function -v

# Run tests with specific marker
pytest -m "unit and not slow" -v

# Run with debugging output
pytest tests/unit/test_specific.py -xvs
```

### Performance Testing
```bash
# Run feature validation (10 core features)
cd src && python3 test_features.py

# Run integration test suite
python src/utils/test_master_integration_suite.py
```

## High-Level Architecture

### Request Flow (Monolithic Mode)
1. **Entry Point**: `src/main.py --web` starts Flask app on port 7777
2. **Application Factory**: `src/web_app.py` creates Flask app with 8 blueprints
3. **Blueprint Routes**: Each blueprint handles specific domain (main, api, fortimanager, itsm, etc.)
4. **API Clients**: All clients extend `BaseAPIClient` for session management
5. **Cache Layer**: `UnifiedCacheManager` handles Redis/memory caching
6. **Data Layer**: JSON file storage for persistence in offline mode

### MSA Request Flow
1. **Kong Gateway** (8000): All external requests entry point
2. **Service Discovery**: Consul (8500) manages service registration
3. **Message Queue**: RabbitMQ (5672) for async communication
4. **Microservices**: 7 services (8081-8087) handle specific domains
5. **Shared Cache**: Redis for cross-service data sharing

### Critical Design Patterns

#### Session Management Pattern
All API clients must properly initialize sessions to avoid connection issues:
```python
class CustomAPIClient(BaseAPIClient):
    def __init__(self):
        super().__init__()  # CRITICAL - initializes self.session
        self.session.headers.update({...})  # Then customize
```

#### Configuration Loading Pattern
Configuration follows a strict hierarchy:
1. Check `data/config.json` (runtime config)
2. Check environment variables
3. Use defaults from `src/config/unified_settings.py`

#### Mock Mode Pattern
When `APP_MODE=test`, the system automatically:
- Uses mock FortiGate responses from `data/mock_responses/`
- Activates Postman-based mock server on port 6666
- Disables external API calls
- Uses test database connections

## Recent Updates & Current State

### System Status
- **ALL hardcoded values removed** - project uses environment variables
- **Import paths fixed** - All files use relative imports within src/
- **Feature test passing** - 10/10 core features verified
- **NodePort standardized** - Consistent use of 30777
- **MSA architecture implemented** - 7 microservices with full infrastructure
- **Critical import bug fixed** - `src/utils/security_fixes.py:210`
- **Docker security enhanced** - Non-root user enabled, bytecode compilation fixed

### Code Quality Metrics
- **Black formatting**: Applied to all Python files
- **Import sorting**: Fixed with isort
- **Flake8 compliance**: 269 issues remaining (down from 338)
- **Test coverage**: Growing (minimum 5% enforced)
- **File count**: 142 Python files in src/, 76 test files

### Deployment Notes
- Harbor Registry path: `registry.jclee.me/fortinet` (not jclee94/fortinet)
- Helm chart version: 1.0.5
- TLS currently disabled due to certificate issues
- Self-hosted GitHub Actions runners in use
- GitOps pipeline: Test → Build → Helm → ArgoCD