# Flask Application ConfigMap Deployment Guide

## Overview

This document describes the complete Flask application deployment using Kubernetes ConfigMap. The original Flask application structure has been recreated in a ConfigMap to run without building a custom Docker image.

## What Was Changed

### 1. Created Complete ConfigMap (`fortinet-app-complete`)

The new ConfigMap includes:
- **Main Application Files**:
  - `start.sh` - Startup script that installs dependencies and creates directory structure
  - `main.py` - Entry point that starts the Flask application
  - `web_app.py` - Flask application factory with blueprint registration

- **Route Modules**:
  - `routes/main_routes.py` - Main page routes (dashboard, devices, settings)
  - `routes/api_routes.py` - API endpoints for health checks and data

- **Utilities**:
  - `utils/unified_logger.py` - Logging wrapper
  - `utils/security.py` - Security decorators and CSRF protection

- **Templates**:
  - `templates/base.html` - Base template with Nextrade branding
  - `templates/dashboard.html` - Main dashboard with stats and charts
  - `templates/devices.html` - Device management page
  - `templates/settings.html` - Configuration page
  - `templates/404.html` & `templates/500.html` - Error pages

- **Static Files**:
  - `static/css/nextrade-unified-system.css` - Complete CSS design system
  - `static/img/nextrade/logo_new.svg` - Nextrade logo
  - `static/js/dashboard-realtime.js` - Dashboard JavaScript (simplified)

### 2. Updated Deployment

Modified `deployment.yaml` to use the new ConfigMap:
```yaml
volumes:
- name: app-code
  configMap:
    name: fortinet-app-complete  # Changed from fortinet-nextrade-original
    defaultMode: 0755
```

### 3. Updated Kustomization

Added the new ConfigMap to `kustomization.yaml`:
```yaml
resources:
  - fortinet-app-complete-configmap.yaml  # Added
```

## Application Structure in Container

When the container starts:
1. Files are mounted from ConfigMap to `/app/`
2. `start.sh` script runs and:
   - Installs Flask and dependencies via pip
   - Creates directory structure (`src/`, `templates/`, `static/`)
   - Copies files to appropriate locations
   - Starts the Flask application

## Key Features Included

1. **Nextrade Branding**: Complete with logo and unified design system
2. **Dashboard Page**: 
   - Network statistics cards
   - Performance charts using Chart.js
   - Device list
   - Quick actions
3. **API Endpoints**:
   - `/api/health` - Health check
   - `/api/devices` - Device list
   - `/api/settings` - Configuration
4. **Responsive Design**: Mobile-friendly with collapsible sidebar
5. **Security**: CSRF protection and security headers

## Deployment Instructions

### Apply the Changes

```bash
# Option 1: Use the deployment script
./scripts/apply-configmap-update.sh

# Option 2: Manual deployment
kubectl apply -f k8s/manifests/fortinet-app-complete-configmap.yaml
kubectl apply -k k8s/manifests/
kubectl rollout restart deployment/fortinet-app -n fortinet
```

### Verify Deployment

```bash
# Check pod status
kubectl get pods -n fortinet

# View logs
kubectl logs -n fortinet -l app=fortinet

# Test locally
kubectl port-forward -n fortinet svc/fortinet-service 7777:7777
# Then visit http://localhost:7777
```

### Access the Application

- **NodePort**: `http://<node-ip>:30777`
- **Port-forward**: `kubectl port-forward -n fortinet svc/fortinet-service 7777:7777`
- **Production**: `https://fortinet.jclee.me`

## Routes Available

- `/` - Redirects to dashboard
- `/dashboard` - Main dashboard page
- `/devices` - Device management
- `/policy-analysis` - Policy analysis tool
- `/settings` - Configuration settings
- `/api/health` - Health check endpoint
- `/api/devices` - Device list API
- `/api/settings` - Settings API

## Troubleshooting

### Check ConfigMap Content
```bash
kubectl describe configmap fortinet-app-complete -n fortinet
```

### View Container Files
```bash
kubectl exec -it -n fortinet <pod-name> -- ls -la /app/
kubectl exec -it -n fortinet <pod-name> -- cat /app/start.sh
```

### Common Issues

1. **Import Errors**: The start script creates necessary directory structure
2. **Static Files Not Found**: Files are embedded in ConfigMap and copied on startup
3. **Template Not Found**: Templates are in the ConfigMap under `templates/` key

## Future Improvements

1. **Build Custom Image**: For production, build a proper Docker image with all dependencies
2. **External Static Files**: Serve static files via NGINX or CDN
3. **Persistent Storage**: Use PVC for data and logs
4. **Environment-specific Configs**: Use different ConfigMaps per environment

## Summary

This deployment recreates the complete Flask application structure using Kubernetes ConfigMap. While not ideal for production (custom Docker image would be better), it allows running the full application without building and pushing Docker images.