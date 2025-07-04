#!/bin/bash

# =============================================================================
# 단일 애플리케이션으로 모든 클러스터에 배포
# =============================================================================

set -e

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_info "🚀 단일 애플리케이션으로 다중 클러스터 배포 설정..."

# ArgoCD 로그인
log_info "ArgoCD 로그인..."
argocd login argo.jclee.me --username admin --password bingogo1 --insecure --grpc-web

# 기존 개별 애플리케이션 삭제
log_info "기존 개별 애플리케이션 정리..."
argocd app delete fortinet-primary --cascade --yes 2>/dev/null || true
argocd app delete fortinet-secondary --cascade --yes 2>/dev/null || true
sleep 10

# 단일 애플리케이션 생성 (모든 클러스터 대상)
log_info "단일 fortinet 애플리케이션 생성..."

# ApplicationSet 방식 대신 직접 생성
argocd app create fortinet \
    --repo https://github.com/JCLEE94/fortinet.git \
    --path k8s/manifests \
    --dest-name in-cluster \
    --dest-namespace fortinet \
    --sync-policy auto \
    --auto-prune \
    --self-heal \
    --revision HEAD

log_success "✅ 단일 애플리케이션 생성 완료!"

# 동기화
log_info "애플리케이션 동기화..."
argocd app sync fortinet --prune

# 상태 확인
log_info "배포 상태:"
argocd app get fortinet

echo ""
log_info "📋 참고사항:"
echo "  - 현재는 기본 클러스터(kubernetes.default.svc)에만 배포됩니다"
echo "  - 192.168.50.110 클러스터를 추가하려면:"
echo "    1. 해당 서버에 Kubernetes 설치"
echo "    2. argocd cluster add 명령으로 클러스터 등록"
echo "    3. ApplicationSet 사용하여 자동으로 모든 클러스터에 배포"

exit 0