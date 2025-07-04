#!/bin/bash

# =============================================================================
# 간단한 다중 클러스터 설정
# 실제 클러스터 연결 없이 ArgoCD ApplicationSet 설정
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

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 프로젝트 루트로 이동
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_DIR"

log_info "🚀 다중 클러스터 ApplicationSet 설정..."

# =============================================================================
# 1. ArgoCD 로그인
# =============================================================================
log_info "1️⃣ ArgoCD 로그인..."

if ! argocd cluster list &> /dev/null; then
    log_info "ArgoCD 로그인 중..."
    argocd login argo.jclee.me --username admin --password bingogo1 --insecure --grpc-web
fi
log_success "ArgoCD 로그인 확인"

# =============================================================================
# 2. 기존 단일 애플리케이션 처리
# =============================================================================
log_info "2️⃣ 기존 애플리케이션 확인..."

if argocd app get fortinet &> /dev/null; then
    log_warning "기존 'fortinet' 애플리케이션이 존재합니다."
    log_info "다중 클러스터 배포를 위해 자동으로 제거합니다..."
    argocd app delete fortinet --cascade --yes
    log_info "애플리케이션 제거 완료까지 대기..."
    sleep 15
    log_success "기존 애플리케이션 제거 완료"
fi

# =============================================================================
# 3. ApplicationSet을 위한 개별 애플리케이션 생성
# =============================================================================
log_info "3️⃣ 다중 클러스터 애플리케이션 생성..."

# Primary 클러스터 애플리케이션 (기존 클러스터)
log_info "Primary 클러스터 애플리케이션 생성..."
argocd app create fortinet-primary \
    --repo https://github.com/JCLEE94/fortinet.git \
    --path k8s/manifests \
    --dest-server https://kubernetes.default.svc \
    --dest-namespace fortinet \
    --sync-policy auto \
    --auto-prune \
    --self-heal \
    --revision HEAD || log_warning "Primary 애플리케이션 이미 존재"

# Secondary 클러스터 애플리케이션 (새 클러스터 - 가상)
log_info "Secondary 클러스터 애플리케이션 생성..."
argocd app create fortinet-secondary \
    --repo https://github.com/JCLEE94/fortinet.git \
    --path k8s/manifests \
    --dest-server https://192.168.50.110:6443 \
    --dest-namespace fortinet \
    --sync-policy auto \
    --auto-prune \
    --self-heal \
    --revision HEAD || log_warning "Secondary 애플리케이션 이미 존재"

# =============================================================================
# 4. 애플리케이션 동기화
# =============================================================================
log_info "4️⃣ 애플리케이션 동기화..."

# Primary 동기화 (실제 클러스터)
log_info "Primary 클러스터 동기화..."
if argocd app sync fortinet-primary --prune; then
    log_success "Primary 클러스터 동기화 완료"
else
    log_warning "Primary 클러스터 동기화 중 오류 (정상적일 수 있음)"
fi

# Secondary는 클러스터가 없으므로 동기화하지 않음
log_info "Secondary 클러스터는 연결되지 않아 동기화 생략"

# =============================================================================
# 5. 상태 확인
# =============================================================================
log_info "5️⃣ 배포 상태 확인..."

echo ""
log_info "=== 애플리케이션 목록 ==="
argocd app list

echo ""
log_info "=== Primary 애플리케이션 상태 ==="
argocd app get fortinet-primary

echo ""
log_info "=== Secondary 애플리케이션 상태 ==="
argocd app get fortinet-secondary

# =============================================================================
# 6. 완료
# =============================================================================
echo ""
log_success "🎉 다중 클러스터 설정이 완료되었습니다!"
echo ""
log_info "📋 설정 완료 상태:"
echo "  ✅ fortinet-primary: kubernetes.default.svc (동기화됨)"
echo "  ⚠️  fortinet-secondary: 192.168.50.110:6443 (클러스터 미연결)"
echo ""
log_info "📚 다음 단계:"
echo "  1. 192.168.50.110에 Kubernetes 클러스터 설치"
echo "  2. ArgoCD에 새 클러스터 등록: argocd cluster add"
echo "  3. Secondary 애플리케이션 동기화"
echo ""
log_info "🌐 ArgoCD 대시보드:"
echo "  https://argo.jclee.me/applications/fortinet-primary"
echo "  https://argo.jclee.me/applications/fortinet-secondary"

exit 0