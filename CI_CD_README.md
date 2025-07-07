# CI/CD Pipeline Documentation

## Overview

Unified CI/CD pipeline for FortiGate Nextrade application using GitHub Actions and ArgoCD GitOps.

## Pipeline Architecture

```
GitHub Push → GitHub Actions → Docker Registry → GitOps Update → ArgoCD → Kubernetes
```

## Workflow Types

### 1. Automatic Deployment (Push to main/master)
- Triggers on push to `main` or `master` branches
- Runs full test suite
- Builds and pushes Docker image
- Updates GitOps configuration
- ArgoCD automatically syncs changes

### 2. Manual Deployment (workflow_dispatch)
- Can be triggered manually from GitHub Actions UI
- Choose environment: production/staging
- Option to skip tests (emergency mode)
- Provide deployment reason

## Jobs Structure

### 🧪 Test Job
- Runs Python tests and import checks
- Uses pip cache for faster execution
- Can be skipped in emergency mode

### 🏗️ Build & Push Job
- Builds Docker image using Dockerfile.production
- Pushes to private registry: `registry.jclee.me`
- Tags with commit SHA and `latest`
- Uses GitHub Actions cache for build optimization

### 🚀 Deploy Job
- Updates `k8s/manifests/kustomization.yaml` with new image tag
- Commits changes to trigger ArgoCD sync
- Updates deployment timestamp

### 🏥 Verify Job
- Waits for ArgoCD sync (120 seconds)
- Tests multiple health endpoints:
  - `https://fortinet.jclee.me/api/health`
  - `http://192.168.50.110:30777/api/health`
- Reports deployment success/failure

### 📊 Summary Job
- Creates deployment summary in GitHub Actions
- Links to ArgoCD dashboard and application
- Reports final status

## Environment Variables

```yaml
REGISTRY: 'registry.jclee.me'
IMAGE_NAME: 'fortinet'
PYTHON_VERSION: '3.11'
```

## Required Secrets

- `REGISTRY_USERNAME`: Private registry username
- `REGISTRY_PASSWORD`: Private registry password
- `GITHUB_TOKEN`: Automatically provided by GitHub

## GitOps Flow

1. **Image Build**: `registry.jclee.me/fortinet:${COMMIT_SHA}`
2. **GitOps Update**: Update `kustomization.yaml` with new image tag
3. **ArgoCD Sync**: ArgoCD polls repository every 3 minutes
4. **Deployment**: Kubernetes applies new configuration

## Deployment Types

### Standard Deployment
```bash
# Automatic on push
git push origin main

# Manual with all checks
gh workflow run deploy.yml -f environment=production -f reason="Feature update"
```

### Emergency Deployment
```bash
# Skip tests and deploy immediately
gh workflow run deploy.yml -f environment=production -f skip_tests=true -f reason="Critical security fix"
```

## Monitoring

- **ArgoCD Dashboard**: https://argo.jclee.me/applications/fortinet
- **Application (HTTPS)**: https://fortinet.jclee.me
- **Application (NodePort)**: http://192.168.50.110:30777
- **Health Endpoint**: `/api/health`

## Troubleshooting

### Build Failures
1. Check GitHub Actions logs
2. Verify requirements.txt is up to date
3. Check Dockerfile.production syntax

### Deployment Failures
1. Check ArgoCD application status
2. Verify image registry access
3. Check Kubernetes resources: `kubectl get pods -n fortinet`

### Health Check Failures
1. Check pod logs: `kubectl logs -n fortinet deployment/fortinet-app`
2. Verify service connectivity
3. Check ingress configuration

## Pipeline Optimization Features

- **Caching**: Pip cache and Docker build cache
- **Parallel Jobs**: Test and build run in optimal sequence
- **Smart Tagging**: Emergency vs standard deployment tags
- **Multi-endpoint Health Checks**: Fallback to NodePort if HTTPS fails
- **Comprehensive Logging**: Detailed status in GitHub Actions summary

## Cleanup Completed

### Removed Duplicates
- ✅ Merged `stable-deploy.yml` and `emergency-deploy.yml` into single `deploy.yml`
- ✅ Removed duplicate ConfigMaps:
  - `app-configmap.yaml`
  - `real-app-configmap.yaml` 
  - `working-app-configmap.yaml`
- ✅ Cleaned up `kustomization.yaml` resources
- ✅ Unified image references

### Result
- Single, maintainable CI/CD workflow
- Reduced repository complexity
- Clear separation of concerns
- Better error handling and reporting