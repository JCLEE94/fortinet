# Cloudflare Tunnel Integration for FortiGate Nextrade

## Overview

This document describes how to integrate Cloudflare Tunnel with the FortiGate Nextrade application deployment. The Cloudflare tunnel provides secure, reliable connectivity without exposing ports directly to the internet.

## Architecture

The Cloudflare tunnel is deployed as a sidecar container alongside the main FortiGate application in the Kubernetes pod. This ensures:

- Zero-trust security model
- No exposed public IPs
- Automatic failover and load balancing
- Built-in DDoS protection

## Deployment Methods

### Method 1: Automated GitHub Actions Workflow

Use the dedicated workflow for Cloudflare tunnel management:

```bash
# Deploy tunnel
gh workflow run cloudflare-tunnel-deploy.yml -f action=deploy -f environment=production

# Update tunnel
gh workflow run cloudflare-tunnel-deploy.yml -f action=update -f environment=production

# Remove tunnel
gh workflow run cloudflare-tunnel-deploy.yml -f action=remove -f environment=production
```

### Method 2: Manual Script Deployment

Use the setup script for local deployment:

```bash
# Make script executable
chmod +x scripts/setup-cloudflare-tunnel.sh

# Run setup
./scripts/setup-cloudflare-tunnel.sh
```

### Method 3: Direct Kubernetes Apply

Apply the deployment directly:

```bash
# Apply the deployment with Cloudflare sidecar
kubectl apply -f k8s/manifests/deployment-with-cloudflare.yaml

# Verify deployment
kubectl rollout status deployment/fortinet-app -n fortinet
```

## Configuration

### Tunnel Token

The tunnel token is embedded in the deployment configuration:
```yaml
args:
- tunnel
- --no-autoupdate
- run
- --token
- <YOUR_TUNNEL_TOKEN>
```

### Resource Allocation

The Cloudflare tunnel container is configured with minimal resources:
- Memory: 128Mi (request) / 256Mi (limit)
- CPU: 50m (request) / 100m (limit)

## Monitoring

### Check Tunnel Status

```bash
# Get pod name
POD_NAME=$(kubectl get pods -n fortinet -l app=fortinet -o jsonpath="{.items[0].metadata.name}")

# View tunnel logs
kubectl logs $POD_NAME -c cloudflare-tunnel -n fortinet

# Follow logs in real-time
kubectl logs -f $POD_NAME -c cloudflare-tunnel -n fortinet
```

### Health Checks

The tunnel container includes health check endpoints:
- Liveness: http://localhost:2000/ready
- Readiness: http://localhost:2000/ready

## Troubleshooting

### Common Issues

1. **Tunnel not connecting**
   - Check the tunnel token is valid
   - Verify network connectivity from the cluster
   - Check Cloudflare dashboard for tunnel status

2. **502 Bad Gateway**
   - Ensure the main application is running
   - Verify the tunnel is configured to connect to localhost:7777
   - Check application logs

3. **Resource constraints**
   - Monitor container resource usage
   - Adjust limits if needed

### Debug Commands

```bash
# Check pod status
kubectl describe pod -n fortinet -l app=fortinet

# Check events
kubectl get events -n fortinet --sort-by='.lastTimestamp'

# Test connectivity from tunnel container
kubectl exec -it $POD_NAME -c cloudflare-tunnel -n fortinet -- wget -O- http://localhost:7777/api/health
```

## Security Considerations

1. **Token Security**
   - Store tunnel tokens as Kubernetes secrets (when not in gitignored files)
   - Rotate tokens periodically
   - Use different tokens for different environments

2. **Network Policies**
   - The tunnel only needs outbound HTTPS (443) to Cloudflare
   - No inbound ports need to be exposed

3. **Access Control**
   - Configure Cloudflare Access policies as needed
   - Use Cloudflare WAF rules for additional protection

## Integration with CI/CD

The Cloudflare tunnel is automatically deployed as part of the main deployment pipeline when:
1. The deployment manifest includes the sidecar configuration
2. The kustomization.yaml references deployment-with-cloudflare.yaml

To enable in the main pipeline:
```bash
# Update kustomization.yaml
sed -i 's/- deployment.yaml/- deployment-with-cloudflare.yaml/' k8s/manifests/kustomization.yaml

# Commit and push
git add k8s/manifests/
git commit -m "feat: Enable Cloudflare tunnel in deployment"
git push
```

## Rollback

To remove the Cloudflare tunnel and revert to standard deployment:

```bash
# Revert kustomization.yaml
sed -i 's/- deployment-with-cloudflare.yaml/- deployment.yaml/' k8s/manifests/kustomization.yaml

# Apply standard deployment
kubectl apply -f k8s/manifests/deployment.yaml

# Or trigger via GitHub Actions
gh workflow run cloudflare-tunnel-deploy.yml -f action=remove -f environment=production
```