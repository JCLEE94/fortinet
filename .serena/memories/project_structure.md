# FortiGate Nextrade Project Structure

## Directory Layout

```
fortinet/
├── src/                        # Source code
│   ├── main.py                # Entry point with CLI arguments
│   ├── web_app.py            # Flask application factory
│   ├── routes/               # Flask Blueprint routes
│   │   ├── main_routes.py    # Page routes (/, /dashboard, etc.)
│   │   ├── api_routes.py     # Core API routes (/api/*)
│   │   ├── fortimanager_routes.py  # FortiManager routes
│   │   ├── itsm_routes.py    # ITSM integration routes
│   │   └── logs_routes.py    # Log management routes
│   ├── api/clients/          # External API clients
│   │   ├── base_api_client.py      # Base class (session management)
│   │   ├── fortigate_api_client.py
│   │   ├── fortimanager_api_client.py
│   │   └── fortianalyzer_api_client.py
│   ├── modules/              # Core business logic
│   │   ├── firewall_analyzer.py
│   │   ├── network_topology.py
│   │   └── policy_optimizer.py
│   ├── fortimanager/         # Advanced FortiManager features
│   │   ├── hub.py           # FortiManager Advanced Hub
│   │   ├── orchestrator.py  # Policy orchestration
│   │   └── compliance.py    # Compliance automation
│   ├── utils/               # Utilities
│   │   ├── unified_logger.py       # Logging system
│   │   ├── unified_cache_manager.py # Caching
│   │   ├── security_utils.py      # Security helpers
│   │   └── common_imports.py       # Shared imports
│   ├── config/              # Configuration
│   │   ├── unified_settings.py     # Central config
│   │   ├── constants.py            # Constants
│   │   └── services.py             # Service config
│   ├── mock/                # Mock system for testing
│   │   ├── mock_fortigate.py
│   │   └── mock_data.py
│   ├── templates/           # Jinja2 HTML templates
│   │   ├── base.html
│   │   ├── dashboard.html
│   │   └── components/
│   └── static/              # Static assets
│       ├── css/
│       ├── js/
│       └── images/
├── tests/                   # Test suite
│   ├── unit/               # Unit tests
│   ├── integration/        # Integration tests
│   └── manual/             # Manual test scripts
├── data/                   # Runtime data
│   ├── config.json         # Runtime configuration
│   └── cache/              # Cache files
├── logs/                   # Application logs
│   └── web_app.log        # Main app log
├── docs/                   # Documentation
│   ├── guides/            # User guides
│   ├── deployment/        # Deployment docs
│   └── reports/           # Analysis reports
├── scripts/               # Utility scripts
│   ├── deploy.sh
│   └── docker-manage.sh
├── .github/workflows/     # GitHub Actions
│   └── ci-cd.yml         # CI/CD pipeline
├── k8s/                   # Kubernetes configs
├── config/                # Legacy configs
├── docker-compose.yml     # Docker Compose
├── docker-compose.production.yml
├── Dockerfile.production  # Production image
├── requirements.txt       # Python dependencies
├── pytest.ini            # Pytest configuration
├── README.md             # Project documentation
└── CLAUDE.md             # AI agent instructions
```

## Key Design Patterns

### 1. Flask Blueprint Architecture
- Modular route organization
- Each blueprint handles a specific domain
- Centralized registration in `web_app.py`

### 2. API Client Hierarchy
- `BaseAPIClient` provides session management
- All API clients inherit from base
- Automatic retry and error handling

### 3. Configuration Priority
1. Runtime config (`data/config.json`)
2. Environment variables
3. Default values in code

### 4. Mock System
- Activated with `APP_MODE=test`
- Provides realistic test data
- No hardware dependencies

### 5. Advanced Features
- FortiManager Hub for AI-driven automation
- Policy orchestration engine
- Compliance framework
- Security fabric integration

## Important Files

### Entry Points
- `src/main.py` - CLI entry with `--web` flag
- `src/web_app.py` - Flask app factory

### Configuration
- `src/config/unified_settings.py` - Central config
- `data/config.json` - Runtime overrides

### Core Logic
- `src/modules/firewall_analyzer.py` - Policy analysis
- `src/fortimanager/hub.py` - Advanced features

### Testing
- `pytest.ini` - Test configuration
- `tests/` - Comprehensive test suite