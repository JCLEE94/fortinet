#!/bin/bash

set -euo pipefail

# ArgoCD 설치 및 설정 스크립트
# 사용법: ./install-argocd.sh [namespace]

NAMESPACE=${1:-argocd}
ARGOCD_VERSION=${ARGOCD_VERSION:-"v2.12.4"}

echo "🚀 ArgoCD 설치 시작..."
echo "📦 Namespace: $NAMESPACE"
echo "🏷️ Version: $ARGOCD_VERSION"

# 네임스페이스 생성
echo "📁 네임스페이스 생성 중..."
kubectl create namespace $NAMESPACE || echo "네임스페이스가 이미 존재합니다."

# ArgoCD 설치
echo "📦 ArgoCD 설치 중..."
kubectl apply -n $NAMESPACE -f https://raw.githubusercontent.com/argoproj/argo-cd/$ARGOCD_VERSION/manifests/install.yaml

# ArgoCD 서버 대기
echo "⏳ ArgoCD 서버 시작 대기 중..."
kubectl wait --for=condition=available --timeout=300s deployment/argocd-server -n $NAMESPACE

# ArgoCD CLI 설치
echo "🔧 ArgoCD CLI 설치 중..."
if ! command -v argocd &> /dev/null; then
    curl -sSL -o argocd-linux-amd64 https://github.com/argoproj/argo-cd/releases/download/$ARGOCD_VERSION/argocd-linux-amd64
    sudo install -m 555 argocd-linux-amd64 /usr/local/bin/argocd
    rm argocd-linux-amd64
    echo "✅ ArgoCD CLI 설치 완료"
else
    echo "ℹ️ ArgoCD CLI가 이미 설치되어 있습니다."
fi

# NodePort 서비스 생성 (외부 접근용)
echo "🌐 NodePort 서비스 생성 중..."
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: Service
metadata:
  name: argocd-server-nodeport
  namespace: $NAMESPACE
  labels:
    app.kubernetes.io/component: server
    app.kubernetes.io/name: argocd-server
    app.kubernetes.io/part-of: argocd
spec:
  type: NodePort
  ports:
  - name: http
    port: 80
    protocol: TCP
    targetPort: 8080
    nodePort: 30080
  - name: https
    port: 443
    protocol: TCP
    targetPort: 8080
    nodePort: 30443
  selector:
    app.kubernetes.io/name: argocd-server
EOF

# ArgoCD 서버 설정 업데이트 (insecure 모드 활성화)
echo "⚙️ ArgoCD 서버 설정 업데이트 중..."
kubectl patch configmap argocd-cmd-params-cm -n $NAMESPACE --type merge -p='{"data":{"server.insecure":"true"}}'

# ArgoCD 서버 재시작
echo "🔄 ArgoCD 서버 재시작 중..."
kubectl rollout restart deployment/argocd-server -n $NAMESPACE
kubectl wait --for=condition=available --timeout=300s deployment/argocd-server -n $NAMESPACE

# 초기 admin 비밀번호 가져오기
echo "🔑 초기 admin 비밀번호 가져오기..."
ADMIN_PASSWORD=$(kubectl -n $NAMESPACE get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d)

echo ""
echo "✅ ArgoCD 설치 완료!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🌐 웹 UI URL: http://localhost:30080 또는 https://localhost:30080"
echo "👤 사용자명: admin"
echo "🔑 비밀번호: $ADMIN_PASSWORD"
echo ""
echo "🔧 CLI 로그인 명령어:"
echo "argocd login localhost:30080 --username admin --password '$ADMIN_PASSWORD' --insecure"
echo ""
echo "📝 비밀번호 변경 명령어:"
echo "argocd account update-password --current-password '$ADMIN_PASSWORD' --new-password 'g0nVB3uL4ccsNiSe'"
echo ""
echo "🔗 포트 포워딩 (옵션):"
echo "kubectl port-forward svc/argocd-server -n $NAMESPACE 8080:443"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# 선택적으로 비밀번호를 미리 설정된 값으로 변경
read -p "비밀번호를 'g0nVB3uL4ccsNiSe'로 변경하시겠습니까? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🔄 ArgoCD 서버 로그인 대기 중..."
    sleep 10
    
    echo "🔑 비밀번호 변경 중..."
    argocd login localhost:30080 --username admin --password "$ADMIN_PASSWORD" --insecure
    argocd account update-password --current-password "$ADMIN_PASSWORD" --new-password 'g0nVB3uL4ccsNiSe'
    
    echo "✅ 비밀번호가 성공적으로 변경되었습니다!"
    echo "🔑 새 비밀번호: g0nVB3uL4ccsNiSe"
fi

echo ""
echo "🎉 ArgoCD 설치 및 설정이 완료되었습니다!"