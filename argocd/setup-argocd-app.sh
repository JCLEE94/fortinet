#!/bin/bash
# ArgoCD Application 설정 스크립트

set -e

echo "🚀 Setting up ArgoCD Application..."

# 1. ArgoCD 설치 확인
if ! kubectl get namespace argocd &> /dev/null; then
    echo "❌ ArgoCD is not installed. Please run install-argocd.sh first."
    exit 1
fi

# 2. ArgoCD CLI 로그인
echo "🔐 Logging into ArgoCD..."
ARGOCD_PASSWORD=$(kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d)
argocd login localhost:8080 --username admin --password $ARGOCD_PASSWORD --insecure

# 3. GitHub Repository 등록
echo "📚 Adding GitHub repository..."
argocd repo add https://github.com/JCLEE94/fortinet --name fortinet-repo

# 4. Application 생성
echo "📱 Creating ArgoCD Application..."
kubectl apply -f argocd/applications/fortinet-app.yaml

# 5. 첫 동기화
echo "🔄 Triggering initial sync..."
argocd app sync fortinet

# 6. Application 상태 확인
echo "📊 Checking application status..."
argocd app get fortinet

echo ""
echo "✅ ArgoCD Application setup completed!"
echo "🌐 View in ArgoCD UI: https://localhost:8080/applications/fortinet"