# Complete GitOps Deployment Guide

## Overview
This project implements a complete GitOps workflow with automated CI/CD pipeline, removing all hardcoded values and enabling fully automated deployments.

## Architecture
```
GitHub Push → GitHub Actions → Docker Build → Harbor Registry → ArgoCD Image Updater → Kubernetes
```

## Key Features
- ✅ **No Hardcoded Values**: All configurations use environment variables or Helm values
- ✅ **Persistent Storage**: Settings persist across pod restarts
- ✅ **Automated Deployment**: Push to master triggers automatic deployment
- ✅ **Multi-Environment Support**: Easy to deploy to different environments
- ✅ **GitOps Automation**: ArgoCD manages all deployments

## Quick Start

### 1. Setup ArgoCD Image Updater
```bash
cd /home/jclee/app/fortinet
./scripts/setup-image-updater.sh
```

### 2. Configure GitHub Secrets
Add these secrets to your GitHub repository:
- `REGISTRY_URL`: registry.jclee.me
- `REGISTRY_USERNAME`: your-harbor-username
- `REGISTRY_PASSWORD`: your-harbor-password
- `CHARTMUSEUM_USERNAME`: your-chartmuseum-username
- `CHARTMUSEUM_PASSWORD`: your-chartmuseum-password
- `APP_NAME`: fortinet

### 3. Deploy Application
```bash
# Commit and push to trigger deployment
git add -A
git commit -m "feat: enable gitops deployment"
git push origin master
```

### 4. Monitor Deployment
```bash
# Watch GitHub Actions
# https://github.com/your-repo/actions

# Monitor ArgoCD
argocd app get fortinet
argocd app sync fortinet

# Check Image Updater logs
kubectl -n argocd logs -l app.kubernetes.io/name=argocd-image-updater -f
```

## Configuration

### Environment Variables (No Hardcoding!)
All configurations are now environment-based:

```yaml
env:
  # Application Settings
  APP_MODE: production
  OFFLINE_MODE: "false"
  
  # FortiGate Configuration
  FORTIGATE_HOST: ""  # Set via Helm values
  FORTIGATE_USERNAME: "admin"
  FORTIGATE_PASSWORD: ""  # Set via Helm values
  
  # FortiManager Configuration
  FORTIMANAGER_HOST: ""  # Set via Helm values
  FORTIMANAGER_USERNAME: "admin"
  FORTIMANAGER_PASSWORD: ""  # Set via Helm values
```

### Persistent Storage
Data persists in `/app/data` directory:
- `config.json`: Runtime configuration
- Device registrations
- User settings

## CI/CD Pipeline

### GitHub Actions Workflow
1. **Test Stage**: Runs pytest and linting
2. **Build Stage**: Builds and pushes Docker image to Harbor
3. **Helm Deploy**: Packages and uploads Helm chart to ChartMuseum
4. **Verify Stage**: Checks deployment health
5. **Notify Stage**: Reports deployment status

### ArgoCD Automation
- Automatically syncs every 5 minutes
- Image Updater checks for new images
- Supports these tag patterns:
  - `master`, `main`
  - `latest`
  - `v1.0.0`, `v2.3.4` (semantic versions)
  - `master-abc123` (branch-sha format)

## Accessing the Application

### Production URL
https://fortinet.jclee.me

### Direct NodePort Access
http://192.168.50.110:30777

### Health Check
```bash
curl https://fortinet.jclee.me/api/health
```

## Troubleshooting

### CI/CD Pipeline Failed
Check GitHub Actions logs for:
- ChartMuseum authentication errors → Update GitHub Secrets
- Docker build failures → Check Dockerfile syntax
- Test failures → Fix code issues

### Application Not Updating
1. Check ArgoCD sync status:
   ```bash
   argocd app get fortinet
   ```

2. Force sync if needed:
   ```bash
   argocd app sync fortinet --prune
   ```

3. Check Image Updater logs:
   ```bash
   kubectl -n argocd logs -l app.kubernetes.io/name=argocd-image-updater -f
   ```

### Settings Not Persisting
Verify PersistentVolume is enabled:
```bash
kubectl -n fortinet get pvc
```

## Manual Operations

### Deploy Specific Version
```bash
# Update image tag in ArgoCD app
kubectl -n fortinet set image deployment/fortinet-app fortinet=registry.jclee.me/fortinet:v1.2.3
```

### Rollback
```bash
# Via ArgoCD
argocd app rollback fortinet <revision>

# Via Helm
helm rollback fortinet -n fortinet
```

### Direct Kubernetes Apply
```bash
# Emergency deployment bypass
kubectl apply -k k8s/manifests/
```

## Best Practices

1. **Never hardcode values** - Use environment variables or Helm values
2. **Test locally first** - Use `APP_MODE=test` for mock data
3. **Monitor deployments** - Check ArgoCD dashboard after pushing
4. **Use semantic versioning** - Tag releases as `v1.0.0`
5. **Document changes** - Update CHANGELOG.md

## Next Steps

1. **Add more environments**: Create dev/staging overlays
2. **Implement secrets management**: Use Sealed Secrets or External Secrets
3. **Add monitoring**: Prometheus + Grafana integration
4. **Setup alerts**: Configure ArgoCD notifications
5. **Multi-cluster deployment**: When secondary cluster is ready

## Support

- ArgoCD Dashboard: https://argo.jclee.me
- Harbor Registry: https://registry.jclee.me
- ChartMuseum: https://charts.jclee.me
- Application: https://fortinet.jclee.me