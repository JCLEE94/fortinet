#!/bin/bash
# ArgoCD 설치 스크립트

set -e

echo "🚀 Installing ArgoCD on Kubernetes..."

# 1. ArgoCD 네임스페이스 생성
echo "📦 Creating argocd namespace..."
kubectl create namespace argocd --dry-run=client -o yaml | kubectl apply -f -

# 2. ArgoCD 설치
echo "📥 Installing ArgoCD..."
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

# 3. 설치 완료 대기
echo "⏳ Waiting for ArgoCD to be ready..."
kubectl wait --for=condition=available --timeout=600s deployment/argocd-server -n argocd

# 4. ArgoCD 서버를 LoadBalancer로 변경 (옵션)
echo "🔧 Patching ArgoCD server service..."
kubectl patch svc argocd-server -n argocd -p '{"spec": {"type": "LoadBalancer"}}'

# 5. 초기 관리자 비밀번호 가져오기
echo "🔑 Getting initial admin password..."
sleep 10
ARGOCD_PASSWORD=$(kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d)
echo "Initial admin password: $ARGOCD_PASSWORD"
echo "Please save this password and change it after first login!"

# 6. ArgoCD CLI 설치 안내
echo ""
echo "📌 To install ArgoCD CLI:"
echo "curl -sSL -o /usr/local/bin/argocd https://github.com/argoproj/argo-cd/releases/latest/download/argocd-linux-amd64"
echo "chmod +x /usr/local/bin/argocd"

# 7. 접속 정보
echo ""
echo "✅ ArgoCD installation completed!"
echo "🌐 Access ArgoCD:"
echo "   - Port Forward: kubectl port-forward svc/argocd-server -n argocd 8080:443"
echo "   - URL: https://localhost:8080"
echo "   - Username: admin"
echo "   - Password: $ARGOCD_PASSWORD"