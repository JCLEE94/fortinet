# ArgoCD GitOps Setup for FortiGate Nextrade

## 🚀 Quick Start

### 1. Install ArgoCD
```bash
./argocd/install-argocd.sh
```

### 2. Access ArgoCD UI
```bash
kubectl port-forward svc/argocd-server -n argocd 8080:443
```
- URL: https://localhost:8080
- Username: admin
- Password: (shown during installation)

### 3. Create ArgoCD Application
```bash
kubectl apply -f argocd/applications/fortinet-app.yaml
```

## 📁 Directory Structure

```
argocd/
├── applications/          # ArgoCD Application manifests
│   └── fortinet-app.yaml # Main application
├── environments/         # Kustomize environments
│   ├── base/            # Base manifests
│   │   ├── deployment.yaml
│   │   ├── service.yaml
│   │   ├── configmap.yaml
│   │   ├── pvc.yaml
│   │   └── kustomization.yaml
│   └── production/      # Production overrides
│       ├── deployment-patch.yaml
│       └── kustomization.yaml
├── install-argocd.sh    # ArgoCD installation script
└── setup-argocd-app.sh  # Application setup script
```

## 🔄 GitOps Workflow

1. **Developer pushes code** → GitHub
2. **GitHub Actions CI** → Build Docker image
3. **CI updates** → `argocd/environments/production/kustomization.yaml`
4. **ArgoCD detects change** → Syncs to K8s cluster
5. **K8s pulls new image** → Rolling update

## 🛠️ Manual Operations

### Sync Application
```bash
argocd app sync fortinet
```

### Check Status
```bash
argocd app get fortinet
kubectl get pods -n fortinet
```

### Rollback
```bash
argocd app rollback fortinet <revision>
```

## 🔧 Configuration

### Update Image Tag Manually
Edit `argocd/environments/production/kustomization.yaml`:
```yaml
images:
  - name: registry.jclee.me/fortinet
    newTag: <new-tag>
```

### Environment Variables
Edit `argocd/environments/production/kustomization.yaml`:
```yaml
configMapGenerator:
  - name: fortinet-config
    behavior: merge
    literals:
      - KEY=value
```

## 📊 Monitoring

### ArgoCD Dashboard
- Applications health status
- Sync status
- Resource tree view
- Deployment history

### Kubernetes
```bash
kubectl logs -n fortinet -l app=fortinet
kubectl describe pod -n fortinet
```