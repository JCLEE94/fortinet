# FortiGate Nextrade Project Overview

## Purpose
FortiGate Nextrade is a comprehensive network monitoring and analysis platform that integrates with FortiGate firewalls, FortiManager, and ITSM systems. It's designed for closed network (offline) environments and provides real-time monitoring, policy analysis, network topology visualization, and automated firewall policy management.

## Tech Stack
- **Language**: Python 3.11+
- **Backend Framework**: Flask 3.0.0 with Blueprint architecture
- **Frontend**: Bootstrap 5 + Vanilla JavaScript (no React/Vue dependencies)
- **Database**: Redis (cache) + JSON file storage (persistence)
- **Container**: Docker/Podman with multi-stage builds
- **Testing**: pytest 8.3.3 with pytest-cov
- **Code Quality**: black, flake8, mypy, isort
- **CI/CD**: GitHub Actions → Docker Registry (registry.jclee.me) → Watchtower → Production
- **Real-time Communication**: Flask-SocketIO with Server-Sent Events (SSE)
- **Security**: CSRF protection, Rate limiting, Input validation

## Key Features
- Real-time network monitoring (traffic, CPU, memory)
- Firewall policy analysis and packet path tracing
- Network topology visualization
- ITSM integration for policy requests and ticket management
- FortiManager Advanced Hub with AI-driven policy orchestration
- Mock FortiGate subsystem for hardware-free development/testing
- Docker support with container orchestration
- Comprehensive log management with real-time streaming

## Deployment
- Production URL: https://fortinet.jclee.me
- Default Port: 7777
- Automated deployment via GitHub Actions when pushing to main/master branches
- Uses private Docker registry at registry.jclee.me
- Watchtower handles automatic container updates