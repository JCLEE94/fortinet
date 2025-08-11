# CI/CD Setup Guide

This document describes the streamlined CI/CD pipeline setup for FortiGate Nextrade.

## Overview

The CI/CD pipeline uses:
- **GitHub Actions** for automated building and testing
- **Private Registry (registry.jclee.me)** for Docker image storage (no auth required)
- **ArgoCD Image Updater** for automatic deployment on new images
- **Offline TAR Generation** for air-gapped environment deployments

## Pipeline Architecture

### 1. GitHub Actions Workflow
- File: `.github/workflows/build-deploy.yml`
- Triggers: Push to main/master branches
- Stages:
  1. **Test**: Run pytest suite with coverage
  2. **Build**: Build Docker image and push to registry.jclee.me
  3. **Notify**: Image Updater automatically detects new images

### 2. ArgoCD Image Updater
- Monitors registry for new images
- Automatically updates deployments without manual manifest changes
- Triggers offline TAR generation on deployment completion

### 3. Offline Package Generation
- File: `.github/workflows/offline-tar.yml`
- Triggers: After deployment completion
- Creates self-contained packages for air-gapped environments

## Deployment Process

1. **Push Code**
   ```bash
   git add .
   git commit -m "feat: your feature description"
   git push origin main
   ```

2. **Automatic Build and Deploy**
   - GitHub Actions automatically runs
   - Builds and tests the application
   - Creates Docker image and pushes to registry.jclee.me
   - ArgoCD Image Updater detects new image and deploys
   - Offline TAR package is generated after deployment

3. **Monitor Progress**
   - GitHub Actions: https://github.com/YOUR_USERNAME/fortinet/actions
   - ArgoCD Dashboard: https://argo.jclee.me/applications/fortinet
   - Application: https://fortinet.jclee.me

## Setup

### ArgoCD Image Updater Installation
```bash
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj-labs/argocd-image-updater/stable/manifests/install.yaml
```

### Apply Configuration
```bash
./scripts/apply-argocd-image-updater.sh
```

### Registry Configuration
The private registry at registry.jclee.me is configured without authentication for ease of use in closed environments.

### Kubernetes Configuration
The registry secret is already configured in the manifests with no authentication required:

```yaml
# k8s/manifests/registry-noauth-secret.yaml
apiVersion: v1
kind: Secret
metadata:
  name: registry-credentials
  namespace: fortinet
type: kubernetes.io/dockerconfigjson
stringData:
  .dockerconfigjson: |
    {
      "auths": {
        "registry.jclee.me": {}
      }
    }
```

## Manual Deployment

For manual deployments, use the consolidated script:

```bash
# Deploy using ArgoCD (default)
./scripts/deploy.sh

# Deploy using kubectl directly
./scripts/deploy.sh -m kubectl -t v1.2.3

# Show help
./scripts/deploy.sh -h
```

## Verification Steps

1. **Check GitHub Actions**
   - Workflow should show green checkmarks
   - All test, build, and deploy jobs should pass

2. **Verify Registry Images**
   - Check registry: `curl https://registry.jclee.me/v2/fortinet/tags/list`
   - New image tags should appear after each push

3. **Monitor ArgoCD**
   - Application should show "Synced" status
   - New deployments should appear within 3 minutes

4. **Test Application**
   ```bash
   # Check pods
   kubectl -n fortinet get pods
   
   # Check service
   kubectl -n fortinet get svc
   
   # Test endpoint
   curl https://fortinet.jclee.me/api/health
   ```

## Troubleshooting

### Common Issues

1. **Image Pull Errors**
   - Verify registry.jclee.me is accessible
   - Check that registry-credentials secret exists
   - Ensure image name and tag are correct

2. **ArgoCD Not Syncing**
   - Manual sync: `argocd app sync fortinet`
   - Check Git webhook or polling interval
   - Verify ArgoCD has repository access

3. **Build Failures**
   - Check test results in GitHub Actions logs
   - Ensure all dependencies are in requirements.txt
   - Verify Dockerfile.production is valid