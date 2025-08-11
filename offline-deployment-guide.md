# FortiGate Nextrade Offline Deployment Guide

## Overview

This guide covers the complete process of deploying FortiGate Nextrade in offline/air-gapped environments where internet access is not available. The offline deployment excludes Cloudflare tunnel integration and focuses on internal network accessibility.

## Table of Contents

1. [Offline Package Creation](#offline-package-creation)
2. [Secret Management](#secret-management)
3. [Deployment Methods](#deployment-methods)
4. [Configuration](#configuration)
5. [Troubleshooting](#troubleshooting)

## Offline Package Creation

### Automated CI/CD Process

The GitHub Actions pipeline automatically creates offline packages on successful deployments to main/master branches:

1. **Trigger**: Push to main/master with successful tests
2. **Process**:
   - Pulls latest production image
   - Saves Docker image as tar file
   - Bundles Kubernetes manifests (without Cloudflare)
   - Creates deployment scripts
   - Generates offline-specific documentation
3. **Output**: Downloadable artifact with 30-day retention

### Manual Package Creation

To create an offline package manually:

```bash
# 1. Pull the latest image
docker pull registry.jclee.me/fortinet:latest

# 2. Save the image
docker save -o fortinet-image.tar registry.jclee.me/fortinet:latest

# 3. Create package structure
mkdir fortinet-offline-package
cp fortinet-image.tar fortinet-offline-package/
cp -r k8s/manifests fortinet-offline-package/k8s/
cp scripts/deploy-offline-advanced.sh fortinet-offline-package/

# 4. Remove Cloudflare-specific files
rm -f fortinet-offline-package/k8s/manifests/deployment-with-cloudflare.yaml
rm -f fortinet-offline-package/k8s/manifests/cloudflare-*.yaml

# 5. Create tarball
tar -czf fortinet-offline-package.tar.gz fortinet-offline-package/
```

## Secret Management

### For Online Environments (with Cloudflare)

1. **Create Secret Using Script**:
```bash
# Using token directly
./scripts/setup-cloudflare-tunnel.sh --token "your-cloudflare-token"

# Using environment variable
export CLOUDFLARE_TUNNEL_TOKEN="your-cloudflare-token"
./scripts/setup-cloudflare-tunnel.sh
```

2. **Create Secret Manually**:
```bash
# Create from template
cat k8s/templates/cloudflare-tunnel-token.yaml.template | \
  sed "s/CLOUDFLARE_TUNNEL_TOKEN_PLACEHOLDER/your-token/" | \
  kubectl apply -f -
```

3. **Using GitHub Secrets**:
Add to repository secrets:
- `CLOUDFLARE_TUNNEL_TOKEN` - Cloudflare tunnel token
- `REGISTRY_USERNAME` - Docker registry username
- `REGISTRY_PASSWORD` - Docker registry password

### For Offline Environments

Offline deployments don't require Cloudflare secrets. Only registry credentials are needed if using a private registry:

```bash
# Create registry secret for Kubernetes
kubectl create secret docker-registry registry-credentials \
  --docker-server=your-registry.com \
  --docker-username=your-username \
  --docker-password=your-password \
  --namespace=fortinet
```

## Deployment Methods

### Method 1: Docker Standalone

Quick deployment for single-node environments:

```bash
# Load image
docker load -i fortinet-image.tar

# Run container
docker run -d \
  --name fortinet-app \
  -p 7777:7777 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  -e APP_MODE=production \
  -e OFFLINE_MODE=true \
  --restart unless-stopped \
  fortinet:latest
```

### Method 2: Docker Compose

For multi-container deployments with Redis:

```yaml
version: '3.8'
services:
  fortinet:
    image: fortinet:latest
    ports:
      - "7777:7777"
    environment:
      - APP_MODE=production
      - OFFLINE_MODE=true
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    restart: unless-stopped

  redis:
    image: redis:alpine
    volumes:
      - ./redis-data:/data
    restart: unless-stopped
```

### Method 3: Kubernetes

For production-grade deployments:

```bash
# 1. Load image to all nodes or local registry
docker load -i fortinet-image.tar

# 2. Push to local registry (if available)
docker tag fortinet:latest localhost:5000/fortinet:latest
docker push localhost:5000/fortinet:latest

# 3. Update kustomization with local registry
sed -i 's|registry.jclee.me|localhost:5000|g' k8s/manifests/kustomization.yaml

# 4. Deploy
kubectl apply -k k8s/manifests/
```

### Method 4: Using Advanced Script

The provided script handles all deployment methods:

```bash
./deploy-offline-advanced.sh
```

Features:
- Interactive deployment selection
- Prerequisite checking
- Automatic health verification
- Post-deployment information

## Configuration

### Environment Variables

| Variable | Description | Default | Offline Mode |
|----------|-------------|---------|--------------|
| `APP_MODE` | Application mode | `production` | Required |
| `OFFLINE_MODE` | Disable external API calls | `false` | Set to `true` |
| `WEB_APP_PORT` | Application port | `7777` | Same |
| `REDIS_ENABLED` | Enable Redis cache | `true` | Optional |
| `DISABLE_EXTERNAL_CALLS` | Block external APIs | `false` | Set to `true` |

### Configuration File

Edit `data/config.json` for runtime configuration:

```json
{
  "offline_mode": true,
  "fortigate": {
    "host": "192.168.1.100",
    "use_mock": true
  },
  "fortimanager": {
    "host": "192.168.1.101",
    "use_mock": true
  }
}
```

### Network Configuration

For offline environments, ensure:

1. **DNS Resolution**: Add entries to `/etc/hosts` if needed
2. **Firewall Rules**: Allow traffic on port 7777
3. **Load Balancer**: Configure for high availability

## Troubleshooting

### Common Issues

1. **Image Loading Fails**
```bash
# Check Docker daemon
docker info

# Check available space
df -h

# Try with sudo
sudo docker load -i fortinet-image.tar
```

2. **Container Won't Start**
```bash
# Check logs
docker logs fortinet-app

# Check port availability
lsof -i :7777

# Run in foreground for debugging
docker run --rm -it fortinet:latest
```

3. **Kubernetes Deployment Issues**
```bash
# Check pod status
kubectl describe pod -n fortinet

# Check events
kubectl get events -n fortinet --sort-by='.lastTimestamp'

# Check image pull
kubectl get pods -n fortinet -o yaml | grep -A5 "containerStatuses"
```

4. **Application Not Accessible**
```bash
# Test from container
docker exec fortinet-app curl http://localhost:7777/api/health

# Check network
docker inspect fortinet-app | grep IPAddress

# Check firewall
sudo iptables -L -n | grep 7777
```

### Health Verification

Always verify deployment health:

```bash
# Direct health check
curl http://localhost:7777/api/health

# Detailed health check
curl http://localhost:7777/api/health | jq .

# Container health
docker inspect fortinet-app --format='{{.State.Health.Status}}'
```

### Logs and Debugging

Access logs for troubleshooting:

```bash
# Application logs
docker logs -f fortinet-app

# Kubernetes logs
kubectl logs -f deployment/fortinet-app -n fortinet

# File logs
tail -f ./logs/web_app.log
```

## Best Practices

1. **Pre-deployment Checklist**
   - [ ] Verify Docker/Kubernetes availability
   - [ ] Check disk space (minimum 5GB)
   - [ ] Confirm network connectivity
   - [ ] Review security policies

2. **Security Considerations**
   - Run containers as non-root user
   - Use secrets for sensitive data
   - Enable network policies in Kubernetes
   - Regular security updates

3. **Monitoring**
   - Set up health check endpoints
   - Monitor resource usage
   - Configure alerts for failures
   - Regular backup of data volumes

4. **Updates and Maintenance**
   - Test updates in staging environment
   - Keep offline packages versioned
   - Document configuration changes
   - Maintain rollback procedures

## Appendix

### Package Contents

A typical offline package includes:
```
fortinet-offline-package/
├── fortinet-image.tar          # Docker image
├── k8s/
│   └── manifests/             # Kubernetes YAML files
├── scripts/
│   ├── deploy-offline-advanced.sh
│   └── k8s-deploy.sh
├── deploy-offline.sh          # Simple deployment script
└── README-OFFLINE.md          # Offline-specific docs
```

### Version Compatibility

| Component | Version | Notes |
|-----------|---------|-------|
| Docker | 20.10+ | Required for image format |
| Kubernetes | 1.20+ | For manifest compatibility |
| Python | 3.11 | Application runtime |
| Redis | 6.0+ | Optional cache backend |

### Support

For offline environments without internet access:
1. Refer to bundled documentation
2. Check application logs
3. Use mock mode for testing
4. Contact support with diagnostic bundle