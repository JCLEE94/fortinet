#!/bin/bash

set -euo pipefail

# ArgoCD 애플리케이션 설정 스크립트
# 사용법: ./setup-argocd-app.sh [app-name] [repo-url] [branch]

APP_NAME=${1:-"fortinet-app"}
REPO_URL=${2:-"https://github.com/JCLEE94/fortinet.git"}
BRANCH=${3:-"master"}
NAMESPACE="fortinet"
ARGOCD_NAMESPACE="argocd"

echo "🚀 ArgoCD 애플리케이션 설정 시작..."
echo "📱 앱 이름: $APP_NAME"
echo "📦 저장소: $REPO_URL"
echo "🌿 브랜치: $BRANCH"
echo "📁 네임스페이스: $NAMESPACE"

# ArgoCD 로그인
echo "🔐 ArgoCD 로그인 중..."
argocd login localhost:30080 --username admin --password 'g0nVB3uL4ccsNiSe' --insecure

# 대상 네임스페이스 생성
echo "📁 대상 네임스페이스 생성 중..."
kubectl create namespace $NAMESPACE || echo "네임스페이스가 이미 존재합니다."

# ArgoCD 애플리케이션 생성/업데이트
echo "📱 ArgoCD 애플리케이션 생성/업데이트 중..."
argocd app create $APP_NAME \
    --repo $REPO_URL \
    --path argocd/environments/production \
    --dest-server https://kubernetes.default.svc \
    --dest-namespace $NAMESPACE \
    --revision $BRANCH \
    --sync-policy automated \
    --auto-prune \
    --self-heal \
    --allow-empty \
    --upsert

# 애플리케이션 동기화
echo "🔄 애플리케이션 동기화 중..."
argocd app sync $APP_NAME --prune

# 동기화 완료 대기
echo "⏳ 동기화 완료 대기 중..."
argocd app wait $APP_NAME --timeout 300

# 애플리케이션 상태 확인
echo "📊 애플리케이션 상태 확인 중..."
argocd app get $APP_NAME

# Kubernetes 리소스 상태 확인
echo "🔍 Kubernetes 리소스 상태 확인 중..."
echo ""
echo "📦 Deployments:"
kubectl get deployments -n $NAMESPACE

echo ""
echo "🏃 Pods:"
kubectl get pods -n $NAMESPACE

echo ""
echo "🌐 Services:"
kubectl get services -n $NAMESPACE

echo ""
echo "💾 PVCs:"
kubectl get pvc -n $NAMESPACE

# 헬스 체크
echo ""
echo "🏥 헬스 체크 수행 중..."
if kubectl get deployment fortinet -n $NAMESPACE &>/dev/null; then
    kubectl wait --for=condition=available --timeout=180s deployment/fortinet -n $NAMESPACE
    
    # 서비스 엔드포인트 확인
    SERVICE_IP=$(kubectl get svc fortinet-service -n $NAMESPACE -o jsonpath='{.spec.clusterIP}' 2>/dev/null || echo "N/A")
    NODEPORT=$(kubectl get svc fortinet-nodeport -n $NAMESPACE -o jsonpath='{.spec.ports[0].nodePort}' 2>/dev/null || echo "N/A")
    
    echo "✅ 배포 완료!"
    echo "🌐 클러스터 IP: $SERVICE_IP"
    echo "🚪 NodePort: $NODEPORT"
    
    if [ "$NODEPORT" != "N/A" ]; then
        echo "🔗 외부 접근 URL: http://localhost:$NODEPORT"
        echo "🏥 헬스 체크 URL: http://localhost:$NODEPORT/api/health"
    fi
else
    echo "⚠️ Deployment를 찾을 수 없습니다."
fi

echo ""
echo "✅ ArgoCD 애플리케이션 설정 완료!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🌐 ArgoCD UI: http://localhost:30080"
echo "👤 사용자명: admin"
echo "🔑 비밀번호: g0nVB3uL4ccsNiSe"
echo ""
echo "🔧 유용한 명령어들:"
echo "argocd app list                    # 앱 목록 보기"
echo "argocd app get $APP_NAME           # 앱 상태 보기"
echo "argocd app sync $APP_NAME          # 수동 동기화"
echo "argocd app delete $APP_NAME        # 앱 삭제"
echo "argocd app set $APP_NAME --revision HEAD  # 최신 커밋으로 업데이트"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"