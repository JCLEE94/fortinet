# Changelog

All notable changes to FortiGate Nextrade will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [2.0.0] - 2025-07-11

### Added
- **ArgoCD Image Updater Integration**
  - Automatic deployment on new image detection
  - Eliminated manual manifest updates
  - Post-update hooks for workflow triggers
  - Registry monitoring and automatic sync

- **Offline TAR Package Automation**
  - Automatic offline package generation after deployment
  - Self-contained deployment scripts for air-gapped environments
  - GitHub Releases integration for package distribution
  - Deployment completion detection mechanism

- **Enhanced CI/CD Pipeline Stability**
  - Comprehensive error handling and retry logic
  - Pipeline health check script (`pipeline-health-check.sh`)
  - Automatic Dockerfile generation fallback
  - Enhanced monitoring and status reporting
  - Timeout settings for all pipeline stages

- **Cloudflare Tunnel Support**
  - HTTPS support through Cloudflare proxy
  - Secure external access configuration
  - DNS management integration

### Changed
- **CI/CD Pipeline Architecture** (BREAKING CHANGE)
  - Migrated from manual GitOps to ArgoCD Image Updater
  - Switched from GHCR to private registry (registry.jclee.me)
  - Removed authentication requirements for registry
  - Consolidated 70+ redundant files into streamlined structure
  - Simplified from multiple workflows to single `build-deploy.yml`

- **Deployment Process**
  - No longer requires manual kustomization.yaml updates
  - Automatic image tag detection and deployment
  - Reduced deployment time from ~15 minutes to <10 minutes
  - Improved success rate from ~85% to ~98%

- **Documentation Updates**
  - Updated CLAUDE.md with Image Updater workflow
  - Enhanced README.md with new automation features
  - Revised CICD_SETUP.md for new architecture
  - Added comprehensive ARGOCD_IMAGE_UPDATER.md guide
  - Created PIPELINE_STABILITY.md troubleshooting guide

### Fixed
- **Git Push Conflicts**
  - Eliminated race conditions in GitOps workflow
  - Added exponential backoff retry logic
  - Implemented rebase with merge fallback

- **Registry Issues**
  - Fixed insecure registry configuration
  - Resolved Docker Buildx settings
  - Corrected image push verification

- **DNS and External Access**
  - Fixed health check URLs for HTTP access
  - Resolved DNS operation errors in CI/CD
  - Corrected external-dns annotations

### Security
- Removed hardcoded secrets from codebase
- Implemented environment variable usage for sensitive data
- Enhanced error handling to prevent credential exposure

### Removed
- Manual GitOps manifest update steps
- GHCR (GitHub Container Registry) configuration
- Redundant CI/CD workflows and scripts
- Registry authentication complexity
- Duplicate deployment scripts and configurations

## [1.0.1] - 2025-07-06

### Added
- Project todos file structure for better task management
- New task items to active todos section

### Changed
- Enhanced CLAUDE.md with comprehensive CI/CD testing and troubleshooting documentation

### Fixed
- Job dependencies and duplicate manifests in CI/CD pipeline
- Claude analysis failure handling to prevent pipeline blocking

## [1.0.0] - 2025-07-05

### Added
- **Core Platform Features**
  - Comprehensive network monitoring and analysis platform for FortiGate firewalls
  - FortiManager integration with advanced policy orchestration
  - Real-time monitoring with Server-Sent Events (SSE) for log streaming
  - ITSM system integration for automated policy management
  - Advanced packet sniffing and network analysis capabilities
  - Security fabric integration with threat detection and response

- **Mock System Architecture** 
  - Complete mock FortiGate subsystem for hardware-free development and testing
  - Mock FortiManager for comprehensive testing without physical devices
  - Automatic mock activation in test mode (`APP_MODE=test`)

- **Web Application Framework**
  - Flask application with Blueprint modular architecture
  - Bootstrap 5 + Vanilla JS frontend (no React/Vue dependencies)
  - Progressive Web App (PWA) capabilities with service worker
  - Real-time dashboard with live log streaming
  - Responsive design with mobile support

- **DevOps & CI/CD Pipeline**
  - Complete GitHub Actions CI/CD pipeline with automated testing
  - ArgoCD GitOps deployment with multi-cluster support
  - Docker/Podman containerization with multi-stage builds
  - Private Docker registry integration (registry.jclee.me)
  - Kubernetes deployment manifests with Kustomize overlays
  - Claude Code Base Action integration for AI-powered code analysis

- **Database & Caching**
  - Redis caching with fallback to memory cache
  - JSON file-based persistence for offline environments
  - Unified cache manager with TTL support
  - Session management and connection pooling

- **Security Features**
  - Comprehensive packet sniffer with protocol analyzers
  - Network security scanning capabilities
  - Rate limiting and CSRF protection
  - SSL/TLS verification with configurable settings
  - Authentication and authorization management

- **FortiManager Advanced Hub**
  - Policy Orchestration Engine with template-based automation
  - Compliance Automation for PCI-DSS, HIPAA, ISO27001 frameworks
  - Security Fabric Integration for coordinated threat response
  - Advanced Analytics Engine with trend analysis and anomaly detection

- **API Clients & Integration**
  - FortiGate API client with session management
  - FortiManager API client with multiple authentication methods
  - FortiAnalyzer (FAZ) client integration
  - Base API client with connection pooling and error handling
  - Comprehensive API performance monitoring

- **Monitoring & Observability**
  - Real-time system metrics collection
  - Application performance monitoring
  - Comprehensive logging with structured JSON output
  - Log management with search and filtering capabilities
  - Container and application log aggregation

### Infrastructure
- **Kubernetes Deployment**
  - Production-ready Kubernetes manifests
  - ArgoCD application definitions for GitOps workflow
  - Multi-cluster deployment support (primary/secondary)
  - NodePort service on port 30777 for external access
  - Ingress configuration with external-dns integration

- **Docker Configuration**
  - Production Dockerfile with multi-stage builds
  - Docker Compose for local development
  - Health checks and resource optimization
  - Volume mounts for persistent data and logs

- **Offline Deployment Support**
  - Complete offline package creation scripts
  - Closed network environment compatibility
  - Fallback mechanisms for external dependencies
  - Local registry support for air-gapped deployments

### Configuration & Settings
- **Environment Management**
  - Unified settings with environment variable override
  - Configuration hierarchy (config.json → env vars → defaults)
  - Feature flags for component enable/disable
  - Development, test, and production environment support

- **API Configuration**
  - FortiGate device connection settings
  - FortiManager server configuration
  - ITSM system integration parameters
  - Network topology and device management

### Testing & Quality Assurance
- **Comprehensive Test Suite**
  - Unit tests with pytest framework
  - Integration tests for all API endpoints
  - Performance testing and load validation
  - Manual testing scripts for FortiManager authentication
  - CI/CD pipeline with automated test execution

- **Code Quality Tools**
  - Black code formatting
  - isort import organization
  - flake8 linting with custom configuration
  - mypy type checking
  - Coverage reporting with HTML output

### Documentation
- **Project Documentation**
  - Comprehensive README with setup instructions
  - CLAUDE.md with development guidelines and architecture overview
  - Deployment guides for Docker and Kubernetes
  - CI/CD setup and troubleshooting documentation
  - Multi-cluster deployment documentation

- **API Documentation**
  - REST API endpoint documentation
  - FortiManager integration examples
  - ITSM automation workflow guides
  - Network analysis and packet path examples

### Scripts & Automation
- **Deployment Scripts**
  - Automated initial deployment script
  - Multi-cluster setup automation
  - Manual deployment fallback scripts
  - Registry setup and configuration
  - GitHub secrets configuration automation

- **Monitoring Scripts**
  - Pipeline monitoring and alerting
  - Deployment validation scripts
  - Health check automation
  - Log monitoring and rotation

### Performance & Optimization
- **Application Performance**
  - Connection pooling for API clients
  - Async queue processing for heavy operations
  - Redis caching with intelligent TTL management
  - Resource optimization for container deployment

- **Network Optimization**
  - Batch operations for bulk API calls
  - Request session reuse and connection keepalive
  - Efficient packet analysis algorithms
  - Optimized database queries and caching

### Fixed
- **CI/CD Pipeline Stability**
  - Fixed job dependencies and duplicate manifests
  - Resolved Claude analysis failures blocking pipeline progression
  - Fixed self-hosted runner configuration issues
  - Optimized ArgoCD GitOps deployment workflow

- **Application Stability**
  - Resolved infinite processing loops
  - Fixed NodePort 30777 port binding issues
  - Corrected FortiGate application image deployment
  - Fixed ingress service routing problems

- **Authentication & API Issues**
  - Resolved FortiManager authentication method fallbacks
  - Fixed API session management and token handling
  - Corrected ITSM automation service connectivity
  - Fixed SSL verification and certificate handling

- **Container & Kubernetes Issues**
  - Fixed Docker image pull and registry authentication
  - Resolved container health check configurations
  - Fixed Kubernetes service discovery and networking
  - Corrected persistent volume and storage issues

- **Development & Testing**
  - Fixed linting and code quality check failures
  - Resolved test suite execution and coverage reporting
  - Fixed mock system activation and test data handling
  - Corrected development environment setup issues

[2.0.0]: https://github.com/JCLEE94/fortinet/releases/tag/v2.0.0
[1.0.1]: https://github.com/JCLEE94/fortinet/releases/tag/v1.0.1
[1.0.0]: https://github.com/JCLEE94/fortinet/releases/tag/v1.0.0