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

## Technology Stack
- **Backend**: Flask + Blueprint architecture (Python 3.11)
- **Frontend**: Bootstrap 5 + Vanilla JS (no React/Vue)
- **Database**: Redis (cache) + JSON file storage
- **Container**: Docker with multi-stage builds
- **Orchestration**: Kubernetes + ArgoCD GitOps
- **CI/CD**: GitHub Actions (self-hosted runners) → Harbor Registry → ChartMuseum → ArgoCD
- **Ingress**: Traefik (not NGINX)
- **MSA Infrastructure**: Kong Gateway, Consul, RabbitMQ

## Development Commands

### Local Development
```bash
# Install dependencies (supports pyproject.toml)
pip install -r requirements.txt
# OR with development dependencies
pip install -e ".[dev]"

# Run application (monolithic mode)
cd src && python main.py --web

# Run with mock mode (activates simple mock server on port 6666)
APP_MODE=test python src/main.py --web

# Run specific test categories
pytest -m "unit" -v                        # Unit tests only
pytest -m "integration" -v                 # Integration tests only
pytest -m "not slow" -v                    # Skip slow tests
pytest tests/manual/ -v                    # Manual testing suite (26 files)
pytest tests/functional/ -v                # Feature validation tests
pytest --cov=src --cov-report=html -v      # With coverage

# Code quality (configured in pyproject.toml)
black src/ && isort src/ && flake8 src/ --max-line-length=120 --ignore=E203,W503

# Alternative: Use pyproject.toml configured tools
python -m black src/
python -m isort src/
python -m flake8 src/

# Run feature test (validates 10 core features)
pytest tests/functional/test_features.py -v
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
# Build production image (multi-stage build)
docker build -f Dockerfile.production -t fortigate-nextrade:latest .

# Run with mock mode (uses start.sh for production startup)
docker run -d --name fortigate-nextrade \
  -p 7777:7777 \
  -e APP_MODE=test \
  -e OFFLINE_MODE=true \
  -e WEB_APP_PORT=7777 \
  fortigate-nextrade:latest

# Development with simple mock server
docker run -d --name fortinet-debug \
  -p 7777:7777 \
  -v $(pwd)/dev-tools:/app/dev-tools \
  python:3.11-slim python /app/dev-tools/simple-mock-server.py
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

## Critical Architecture Patterns

### 1. API Client Session Management
**CRITICAL**: All API clients MUST initialize a requests session:
```python
class SomeAPIClient(BaseAPIClient):
    def __init__(self):
        super().__init__()  # REQUIRED - handles session initialization
```

### 2. Blueprint URL Namespacing
Templates MUST use blueprint namespaces:
```html
{{ url_for('main.dashboard') }}      <!-- Correct -->
{{ url_for('dashboard') }}            <!-- Wrong -->
```

### 3. Configuration Hierarchy
1. `data/config.json` - Runtime configuration (highest priority)
2. Environment variables
3. `src/config/unified_settings.py` - Default values

### 4. Mock System Activation
```python
# Automatic when APP_MODE=test
if os.getenv('APP_MODE', 'production').lower() == 'test':
    # Uses mock_fortigate and Postman-based mock server
```

### 5. Import Path Structure
**CRITICAL**: All imports within src/ must use relative paths:
```python
# Correct - relative imports from src/
from utils.unified_logger import get_logger
from api.clients.fortigate_api_client import FortiGateAPIClient

# Wrong - absolute imports cause ModuleNotFoundError
from src.utils.unified_logger import get_logger
```

## Key Components

### Flask Application Factory Pattern
The system uses a sophisticated Flask application factory with blueprint modularity:
```python
def create_app():
    app = Flask(__name__)
    # Security configurations
    # Blueprint registration
    # Cache manager initialization
    return app
```
- 8 blueprints handle domain-specific routing
- Unified security headers and CSRF protection
- Dynamic SocketIO integration based on OFFLINE_MODE

### FortiManager Advanced Hub
Four specialized modules accessible via:
```python
hub = FortiManagerAdvancedHub(api_client)
```

1. **Policy Orchestrator**: `hub.policy_orchestrator` - AI-driven policy management
2. **Compliance Framework**: `hub.compliance_framework` - Automated compliance checks
3. **Security Fabric**: `hub.security_fabric` - Integrated security management
4. **Analytics Engine**: `hub.analytics_engine` - Advanced analytics and reporting

### Connection Pool Management
Located in `src/core/connection_pool.py`:
- **connection_pool_manager**: Global connection pool for API clients
- **Session reuse**: Prevents connection exhaustion
- **Thread-safe**: Supports concurrent requests
- **Auto-cleanup**: Handles connection lifecycle

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
- Use fixtures for common test data (defined in `tests/conftest.py`)
- Mock external API calls in unit tests
- Use `APP_MODE=test` for integration tests
- Run the feature test to validate core functionality: `pytest tests/functional/test_features.py -v`
- Use custom Rust-style test framework: `@test_framework.test("description")`

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

### Offline-First Architecture
**CRITICAL**: System automatically detects and adapts to offline environments:
```python
OFFLINE_MODE = (
    os.getenv("OFFLINE_MODE", "false").lower() == "true"
    or os.getenv("NO_INTERNET", "false").lower() == "true"
    or os.getenv("DISABLE_EXTERNAL_CALLS", "false").lower() == "true"
)
```
- Disables SocketIO, updates, and telemetry
- Activates mock servers on port 6666
- Uses JSON file storage instead of external databases

### Configuration Hierarchy Pattern
Strict 3-tier configuration loading:
1. **data/config.json** (runtime configuration - highest priority)
2. **Environment variables** (deployment-specific)
3. **src/config/unified_settings.py** (application defaults)

### Security-First Design
Multiple security layers implemented:
- **Enhanced security**: `src/utils/enhanced_security.py`
- **Security fixes**: `src/utils/security_fixes.py` (critical import at line 210)
- **Security scanner**: `src/utils/security_scanner.py`
- **Rate limiting**: Built into Flask routes
- **CSRF protection**: Automatic token generation