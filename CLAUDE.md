# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

FortiGate Nextrade is a comprehensive network monitoring and analysis platform that integrates with FortiGate firewalls, FortiManager, and ITSM systems. Designed for closed network (offline) environments, it provides real-time monitoring, policy analysis, network topology visualization, and automated firewall policy management.

Key differentiators:
- **Mock FortiGate** subsystem for hardware-free development and testing
- **FortiManager Advanced Hub** with AI-driven policy orchestration and compliance automation
- **Offline-first design** with comprehensive fallback mechanisms
- **GitLab CI/CD integration** with automated deployment to production servers

## Architecture Patterns

### 1. Flask Blueprint Architecture
The application was refactored from a 2,992-line monolith to a modular blueprint structure (254 lines):
```python
# src/web_app.py - Factory pattern
def create_app():
    app = Flask(__name__)
    # Blueprint registration
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(fortimanager_bp)
    return app
```

### 2. API Client Initialization Pattern
**CRITICAL**: All API clients MUST initialize a requests session:
```python
class SomeAPIClient(BaseAPIClient):
    def __init__(self):
        super().__init__()
        self.session = requests.Session()  # REQUIRED!
        self.session.verify = self.verify_ssl
```

### 3. Configuration Hierarchy
Priority order (highest to lowest):
1. `data/config.json` - Runtime configuration
2. Environment variables
3. `src/config/settings.py` - Default values

### 4. Settings Data Attribute
The Settings class requires a `data` attribute for API compatibility:
```python
self.data = {
    'fortimanager': self.fortimanager,
    'fortigate': self.fortigate,
    'fortianalyzer': self.fortianalyzer,
    'app_mode': self.app_mode
}
```

### 5. Async Operations Pattern
FortiManager advanced features use async patterns:
```python
@fortimanager_bp.route('/advanced/analytics/trends', methods=['POST'])
async def analyze_trends():
    result = await hub.analytics_engine.analyze_trends_async(...)
    return jsonify(result)
```

## Development Commands

### Core Development
```bash
# Run application (primary method)
cd src && python main.py --web

# Run tests with coverage
pytest --cov=src --cov-report=html

# Code quality checks
black src/
flake8 src/ --max-line-length=120
mypy src/ --ignore-missing-imports
isort src/
```

### Docker Operations
```bash
# Build with proper cache invalidation
docker build --no-cache -f Dockerfile.offline -t fortigate-nextrade:latest .

# Run with proper volume mounts and test mode
docker run -d --name fortigate-nextrade -p 7777:7777 \
  -v $(pwd)/data:/app/data -v $(pwd)/logs:/app/logs \
  -e APP_MODE=test -e OFFLINE_MODE=true \
  fortigate-nextrade:latest
```

### Deployment
```bash
# Create offline package
./create-offline-package.sh

# Deploy via GitLab CI/CD (automatic on push)
git push origin offline-deployment

# Manual deployment fallback
./smart-offline-deploy.sh
```

## FortiManager Advanced Hub Architecture

The FortiManager integration now includes four advanced modules:

### 1. Policy Orchestration Engine
- **Templates**: Web App Security, Zero Trust, Microsegmentation
- **Features**: Conflict detection, AI optimization, bulk operations
- **Key Methods**: `apply_template()`, `analyze_conflicts()`, `optimize_policies()`

### 2. Compliance Automation Framework  
- **Frameworks**: PCI-DSS, HIPAA, ISO27001, NIST, SOX
- **Features**: Auto-remediation, custom rules, scheduled checks
- **Key Methods**: `check_compliance()`, `remediate_violations()`, `generate_report()`

### 3. Security Fabric Integration
- **Features**: Threat detection, incident response, threat hunting
- **Key Methods**: `detect_threats()`, `coordinate_response()`, `hunt_threats()`

### 4. Advanced Analytics Engine
- **Features**: Predictive analytics, anomaly detection, capacity planning
- **Key Methods**: `analyze_trends_async()`, `detect_anomalies()`, `predict_capacity()`

### Integration Hub Usage
```python
from modules.fortimanager_advanced_integration import FortiManagerAdvancedHub

# Initialize with existing API client
hub = FortiManagerAdvancedHub(api_client)

# Apply security template
result = await hub.policy_orchestrator.apply_template(
    "zero_trust_access", 
    parameters={...}
)

# Check compliance
violations = await hub.compliance_framework.check_compliance(
    devices=["FW-01"], 
    frameworks=["PCI-DSS"]
)
```

## Critical Implementation Details

### 1. Mock FortiGate System
When `APP_MODE=test`, the system automatically uses Mock FortiGate:
```python
# Automatic mock activation
if os.getenv('APP_MODE', 'production').lower() == 'test':
    # Uses mock_fortigate for all operations
```

### 2. Offline Mode Detection
```python
OFFLINE_MODE = any([
    os.getenv('OFFLINE_MODE', 'false').lower() == 'true',
    os.getenv('NO_INTERNET', 'false').lower() == 'true',
    os.getenv('DISABLE_EXTERNAL_CALLS', 'false').lower() == 'true'
])
```

### 3. Blueprint URL References
Templates MUST use blueprint namespaces:
```html
<!-- Correct -->
{{ url_for('main.dashboard') }}
{{ url_for('api.get_settings') }}

<!-- Wrong -->
{{ url_for('dashboard') }}
```

### 4. Health Check Pattern (Podman Compatible)
```yaml
healthcheck:
  test: ["CMD-SHELL", "python3 -c 'import urllib.request; urllib.request.urlopen(\"http://localhost:7777\", timeout=5).read()'"]
```

## GitLab CI/CD Pipeline

The project uses a 4-stage pipeline for automated deployment:

### Pipeline Stages
1. **build**: Docker image creation
2. **test**: Automated testing and validation
3. **deploy**: Deployment to production server
4. **monitor**: Post-deployment validation

### Required CI/CD Variables
- `DEPLOY_HOST`: Production server address
- `DEPLOY_PORT`: SSH port (usually 22)
- `DEPLOY_PATH`: Target deployment directory
- `DEPLOY_USER`: SSH username
- `DEPLOY_USER_PASSWORD`: SSH password

### Deployment Triggers
- Push to `offline-deployment` branch
- Push to `main` or `master` branches
- Manual pipeline trigger

## Common Patterns & Solutions

### API Method Naming
- Use simplified names: `get_devices()` not `get_all_fortigate_devices()`
- FortiManager client provides `get_managed_devices()` alias

### Module Import Style
```python
# Always use absolute imports
from src.modules.fortimanager_api_client import FortiManagerAPIClient
from src.utils.unified_logger import UnifiedLogger
```

### Caching Pattern
```python
@api_bp.route('/endpoint')
@cached(ttl=30)  # 30-second cache
def get_data():
    pass
```

### Error Handling Pattern
```python
try:
    result = api_client.method()
except FortiManagerAPIException as e:
    logger.error(f"FortiManager error: {e}")
    return jsonify({"error": str(e)}), 500
```

## Testing Guidelines

### Mock FortiGate Testing
```bash
# Enable test mode
export APP_MODE=test

# Test packet analysis
curl -X POST http://localhost:7777/api/fortimanager/analyze-packet-path \
  -H "Content-Type: application/json" \
  -d '{"src_ip": "192.168.1.100", "dst_ip": "172.16.10.100", "port": 80, "protocol": "tcp"}'
```

### Compliance Testing
```python
# Test compliance check
POST /api/fortimanager/advanced/compliance/check
{
    "devices": ["FW-01"],
    "frameworks": ["PCI-DSS"],
    "auto_remediate": false
}
```

### Performance Testing
- Use `APP_MODE=test` for load testing without hardware
- Monitor with: `docker stats fortigate-nextrade`
- Check health: `docker inspect fortigate-nextrade | jq '.[0].State.Health'`

## Port Conflict Resolution

When port 7777 is already in use, terminate the existing process:

```bash
# Find and kill process using port 7777
sudo lsof -ti:7777 | xargs kill -9

# Alternative method using netstat
sudo netstat -tulpn | grep :7777
# Then kill the process using the PID

# For Docker containers using the port
docker ps --filter "publish=7777" -q | xargs docker stop
docker ps -a --filter "publish=7777" -q | xargs docker rm

# Windows PowerShell
Get-Process -Id (Get-NetTCPConnection -LocalPort 7777).OwningProcess | Stop-Process -Force
```