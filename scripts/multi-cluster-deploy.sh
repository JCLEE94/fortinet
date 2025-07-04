#!/bin/bash

# =============================================================================
# 다중 클러스터 배포 스크립트
# Primary: kubernetes.default.svc
# Secondary: 192.168.50.110
# =============================================================================

set -e

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 로그 함수
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

# 프로젝트 루트 디렉토리로 이동
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_DIR"

log_info "🚀 다중 클러스터 배포 시작..."

# =============================================================================
# 1. 사전 체크
# =============================================================================
log_info "1️⃣ 사전 요구사항 확인..."

# ArgoCD 로그인 확인
if ! argocd cluster list &> /dev/null; then
    log_info "ArgoCD 로그인 중..."
    argocd login argo.jclee.me --username admin --password bingogo1 --insecure --grpc-web
fi

# =============================================================================
# 2. 새 클러스터 추가
# =============================================================================
log_info "2️⃣ 새 클러스터 추가..."

if [ ! -f "./scripts/add-cluster.sh" ]; then
    log_error "add-cluster.sh 스크립트가 없습니다."
    exit 1
fi

log_info "새 클러스터 추가 스크립트 실행..."
./scripts/add-cluster.sh

# =============================================================================
# 3. 기존 단일 애플리케이션 제거
# =============================================================================
log_info "3️⃣ 기존 단일 애플리케이션 확인..."

if argocd app get fortinet &> /dev/null; then
    log_warning "기존 단일 클러스터 애플리케이션 'fortinet'이 존재합니다."
    read -p "제거하고 다중 클러스터로 전환하시겠습니까? (y/N): " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        log_info "기존 애플리케이션 제거 중..."
        argocd app delete fortinet --cascade
        sleep 10
        log_success "기존 애플리케이션 제거 완료"
    else
        log_warning "기존 애플리케이션을 유지합니다. 다중 클러스터 배포가 충돌할 수 있습니다."
    fi
fi

# =============================================================================
# 4. ApplicationSet 배포
# =============================================================================
log_info "4️⃣ ApplicationSet 배포..."

# ApplicationSet 파일 확인
if [ ! -f "./argocd/applicationset.yaml" ]; then
    log_error "ApplicationSet 파일이 없습니다: ./argocd/applicationset.yaml"
    exit 1
fi

# ApplicationSet 적용
log_info "ApplicationSet 적용 중..."
kubectl apply -f ./argocd/applicationset.yaml

log_success "ApplicationSet 적용 완료"

# =============================================================================
# 5. 애플리케이션 생성 대기
# =============================================================================
log_info "5️⃣ 애플리케이션 생성 대기..."

sleep 15

# Primary 클러스터 애플리케이션 확인
log_info "Primary 클러스터 애플리케이션 확인..."
if argocd app get fortinet-primary; then
    log_success "fortinet-primary 애플리케이션 생성됨"
else
    log_warning "fortinet-primary 애플리케이션 생성 중..."
fi

# Secondary 클러스터 애플리케이션 확인
log_info "Secondary 클러스터 애플리케이션 확인..."
if argocd app get fortinet-secondary; then
    log_success "fortinet-secondary 애플리케이션 생성됨"
else
    log_warning "fortinet-secondary 애플리케이션 생성 중..."
fi

# =============================================================================
# 6. 동기화 실행
# =============================================================================
log_info "6️⃣ 애플리케이션 동기화..."

# Primary 동기화
log_info "Primary 클러스터 동기화 중..."
if argocd app sync fortinet-primary --prune; then
    log_success "Primary 클러스터 동기화 완료"
else
    log_warning "Primary 클러스터 동기화 중 오류 발생"
fi

# Secondary 동기화
log_info "Secondary 클러스터 동기화 중..."
if argocd app sync fortinet-secondary --prune; then
    log_success "Secondary 클러스터 동기화 완료"
else
    log_warning "Secondary 클러스터 동기화 중 오류 발생"
fi

# =============================================================================
# 7. 배포 상태 확인
# =============================================================================
log_info "7️⃣ 배포 상태 확인..."

echo ""
log_info "=== Primary 클러스터 상태 ==="
argocd app get fortinet-primary

echo ""
log_info "=== Secondary 클러스터 상태 ==="
argocd app get fortinet-secondary

echo ""
log_info "=== 모든 애플리케이션 목록 ==="
argocd app list

# =============================================================================
# 8. 헬스체크
# =============================================================================
log_info "8️⃣ 헬스체크 실행..."

echo "배포 완료 대기 중..."
sleep 30

# Primary 클러스터 헬스체크
log_info "Primary 클러스터 헬스체크..."
if kubectl get pods -n fortinet 2>/dev/null; then
    log_success "Primary 클러스터 Pod 상태 확인됨"
    kubectl get pods -n fortinet
else
    log_warning "Primary 클러스터 Pod 상태 확인 실패"
fi

# Secondary 클러스터 헬스체크
log_info "Secondary 클러스터 헬스체크..."
if kubectl --context=production-secondary get pods -n fortinet 2>/dev/null; then
    log_success "Secondary 클러스터 Pod 상태 확인됨"
    kubectl --context=production-secondary get pods -n fortinet
else
    log_warning "Secondary 클러스터 Pod 상태 확인 실패"
fi

# =============================================================================
# 9. 완료
# =============================================================================
echo ""
log_success "🎉 다중 클러스터 배포가 완료되었습니다!"
echo ""
log_info "📋 배포 정보:"
echo "  🔸 Primary 클러스터: kubernetes.default.svc (3 replicas)"
echo "  🔸 Secondary 클러스터: 192.168.50.110:6443 (2 replicas)"
echo ""
log_info "📊 모니터링:"
echo "  🌐 ArgoCD: https://argo.jclee.me"
echo "  📱 Primary 앱: kubectl get pods -n fortinet"
echo "  📱 Secondary 앱: kubectl --context=production-secondary get pods -n fortinet"
echo ""
log_info "🔄 다음 배포 시:"
echo "  git push origin master  # 자동으로 두 클러스터에 모두 배포됨"

exit 0