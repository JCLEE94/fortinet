# FortiGate Nextrade Helm Chart

A Helm chart for deploying FortiGate Nextrade - a comprehensive network monitoring and analysis platform that integrates with FortiGate firewalls, FortiManager, and ITSM systems.

## Prerequisites

- Kubernetes 1.19+
- Helm 3.2.0+
- PVC provisioner support in the underlying infrastructure (for persistent storage)

## Repository Setup

Add the ChartMuseum repository:

```bash
helm repo add chartmuseum https://charts.jclee.me --username admin --password bingogo1
helm repo update
```

## Installation

### Install from ChartMuseum

```bash
# Install with default values
helm install fortinet-nextrade chartmuseum/fortinet-nextrade \
  --namespace fortinet \
  --create-namespace

# Install with custom values
helm install fortinet-nextrade chartmuseum/fortinet-nextrade \
  --namespace fortinet \
  --create-namespace \
  --set fortinet.appMode=production \
  --set fortinet.fortimanager.host=192.168.1.100 \
  --set fortinet.fortigate.host=192.168.1.101
```

### Install from local chart

```bash
# Install from local directory
helm install fortinet-nextrade ./helm/fortinet-nextrade \
  --namespace fortinet \
  --create-namespace
```

## Configuration

The following table lists the configurable parameters and their default values:

### Application Configuration

| Parameter | Description | Default |
|-----------|-------------|---------|
| `fortinet.appMode` | Application mode (production/test/development) | `production` |
| `fortinet.webPort` | Web server port | `7777` |
| `fortinet.webHost` | Web server bind address | `0.0.0.0` |
| `fortinet.offlineMode` | Enable offline mode for closed networks | `false` |

### FortiManager Integration

| Parameter | Description | Default |
|-----------|-------------|---------|
| `fortinet.fortimanager.enabled` | Enable FortiManager integration | `true` |
| `fortinet.fortimanager.host` | FortiManager server address | `""` |
| `fortinet.fortimanager.apiKey` | FortiManager API key | `""` |

### FortiGate Integration

| Parameter | Description | Default |
|-----------|-------------|---------|
| `fortinet.fortigate.enabled` | Enable FortiGate integration | `true` |
| `fortinet.fortigate.host` | FortiGate device address | `""` |
| `fortinet.fortigate.apiKey` | FortiGate API key | `""` |

### ITSM Integration

| Parameter | Description | Default |
|-----------|-------------|---------|
| `fortinet.itsm.enabled` | Enable ITSM integration | `false` |
| `fortinet.itsm.url` | ITSM system URL | `""` |
| `fortinet.itsm.apiKey` | ITSM API key | `""` |

### Service Configuration

| Parameter | Description | Default |
|-----------|-------------|---------|
| `service.type` | Kubernetes service type | `ClusterIP` |
| `service.port` | Service port | `80` |
| `service.targetPort` | Container target port | `7777` |

### NodePort Service

| Parameter | Description | Default |
|-----------|-------------|---------|
| `nodePortService.enabled` | Enable NodePort service for external access | `true` |
| `nodePortService.type` | Service type | `NodePort` |
| `nodePortService.port` | Service port | `80` |
| `nodePortService.nodePort` | Node port for external access | `30777` |
| `nodePortService.targetPort` | Container target port | `7777` |

### Ingress Configuration

| Parameter | Description | Default |
|-----------|-------------|---------|
| `ingress.enabled` | Enable ingress | `true` |
| `ingress.className` | Ingress class name | `nginx` |
| `ingress.hosts[0].host` | Hostname for ingress | `fortinet.jclee.me` |
| `ingress.tls[0].secretName` | TLS secret name | `fortinet-tls` |

### Persistence

| Parameter | Description | Default |
|-----------|-------------|---------|
| `persistence.enabled` | Enable persistent storage | `true` |
| `persistence.storageClass` | Storage class | `local-path` |
| `persistence.accessMode` | Access mode | `ReadWriteOnce` |
| `persistence.size` | Storage size | `5Gi` |

### Redis Configuration

| Parameter | Description | Default |
|-----------|-------------|---------|
| `redis.enabled` | Enable Redis dependency | `true` |
| `redis.auth.enabled` | Enable Redis authentication | `false` |
| `redis.master.persistence.enabled` | Enable Redis persistence | `true` |
| `redis.master.persistence.size` | Redis storage size | `1Gi` |

### Resource Configuration

| Parameter | Description | Default |
|-----------|-------------|---------|
| `resources.requests.memory` | Memory request | `512Mi` |
| `resources.requests.cpu` | CPU request | `100m` |
| `resources.limits.memory` | Memory limit | `2Gi` |
| `resources.limits.cpu` | CPU limit | `1000m` |

### Health Checks

| Parameter | Description | Default |
|-----------|-------------|---------|
| `livenessProbe.httpGet.path` | Liveness probe path | `/api/health` |
| `livenessProbe.httpGet.port` | Liveness probe port | `7777` |
| `livenessProbe.initialDelaySeconds` | Initial delay for liveness probe | `30` |
| `livenessProbe.periodSeconds` | Period for liveness probe | `30` |
| `readinessProbe.httpGet.path` | Readiness probe path | `/api/health` |
| `readinessProbe.httpGet.port` | Readiness probe port | `7777` |
| `readinessProbe.initialDelaySeconds` | Initial delay for readiness probe | `20` |
| `readinessProbe.periodSeconds` | Period for readiness probe | `10` |

## Examples

### Production Deployment with FortiManager

```bash
helm install fortinet-prod chartmuseum/fortinet-nextrade \
  --namespace fortinet \
  --create-namespace \
  --set fortinet.appMode=production \
  --set fortinet.fortimanager.enabled=true \
  --set fortinet.fortimanager.host=192.168.1.100 \
  --set fortinet.fortimanager.apiKey=your-api-key \
  --set fortinet.fortigate.enabled=true \
  --set fortinet.fortigate.host=192.168.1.101 \
  --set fortinet.fortigate.apiKey=your-fortigate-key \
  --set ingress.hosts[0].host=fortinet.yourdomain.com \
  --set ingress.tls[0].hosts[0]=fortinet.yourdomain.com
```

### Test Environment Deployment

```bash
helm install fortinet-test chartmuseum/fortinet-nextrade \
  --namespace fortinet-test \
  --create-namespace \
  --set fortinet.appMode=test \
  --set fortinet.offlineMode=true \
  --set redis.enabled=false \
  --set persistence.enabled=false \
  --set ingress.enabled=false
```

### Development with External Redis

```bash
helm install fortinet-dev chartmuseum/fortinet-nextrade \
  --namespace fortinet-dev \
  --create-namespace \
  --set fortinet.appMode=development \
  --set redis.enabled=false \
  --set extraEnvVars[0].name=REDIS_HOST \
  --set extraEnvVars[0].value=external-redis.example.com \
  --set extraEnvVars[1].name=REDIS_PORT \
  --set extraEnvVars[1].value=6379
```

## Accessing the Application

### Via NodePort (Default)

```bash
# Get the NodePort
kubectl get svc fortinet-nextrade-nodeport -n fortinet

# Access via NodePort (typically port 30777)
curl http://<node-ip>:30777/api/health
```

### Via Ingress

```bash
# Check ingress status
kubectl get ingress -n fortinet

# Access via hostname (if DNS configured)
curl https://fortinet.jclee.me/api/health
```

### Via Port Forward

```bash
# Port forward for local access
kubectl port-forward svc/fortinet-nextrade 8080:80 -n fortinet

# Access locally
curl http://localhost:8080/api/health
```

## Monitoring and Troubleshooting

### Check Pod Status

```bash
kubectl get pods -n fortinet
kubectl describe pod <pod-name> -n fortinet
```

### View Logs

```bash
# Application logs
kubectl logs -f deployment/fortinet-nextrade -n fortinet

# Redis logs
kubectl logs -f statefulset/fortinet-nextrade-redis-master -n fortinet
```

### Check Persistent Storage

```bash
kubectl get pvc -n fortinet
kubectl describe pvc fortinet-nextrade-data -n fortinet
```

### Validate Configuration

```bash
# Check configmaps
kubectl get configmap -n fortinet
kubectl describe configmap fortinet-nextrade-scripts -n fortinet

# Check secrets
kubectl get secrets -n fortinet
kubectl describe secret registry-credentials -n fortinet
```

## Upgrading

```bash
# Upgrade to latest version
helm upgrade fortinet-nextrade chartmuseum/fortinet-nextrade -n fortinet

# Upgrade with new values
helm upgrade fortinet-nextrade chartmuseum/fortinet-nextrade \
  -n fortinet \
  --set fortinet.appMode=production \
  --set resources.limits.memory=4Gi
```

## Uninstalling

```bash
# Uninstall the release
helm uninstall fortinet-nextrade -n fortinet

# Clean up persistent volumes (if needed)
kubectl delete pvc -l app.kubernetes.io/instance=fortinet-nextrade -n fortinet
```

## Security Considerations

1. **API Keys**: Store sensitive API keys in Kubernetes secrets rather than values files
2. **Network Policies**: Implement network policies to restrict traffic between pods
3. **RBAC**: Configure appropriate RBAC rules for the service account
4. **Image Security**: Use specific image tags rather than 'latest' in production

## Support and Documentation

- **Project Repository**: https://github.com/JCLEE94/fortinet
- **Documentation**: Check the `/docs` directory in the repository
- **Issues**: Report issues via GitHub Issues

## License

This chart is part of the FortiGate Nextrade project and follows the same licensing terms.