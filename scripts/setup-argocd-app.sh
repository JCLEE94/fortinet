#!/bin/bash

# =============================================================================
# ArgoCD Application 자동 생성 및 GitHub 연동 스크립트
# =============================================================================

set -e

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }
log_header() { echo -e "${CYAN}=== $1 ===${NC}"; }

# 환경 변수
ARGOCD_SERVER="argo.jclee.me"
ARGOCD_TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJhcmdvY2QiLCJzdWIiOiJhZG1pbjphcGlLZXkiLCJuYmYiOjE3NTE1ODkwMTAsImlhdCI6MTc1MTU4OTAxMCwianRpIjoiNjg0Y2NhYmQtMWUwNi00M2E1LTlkMGEtMzRlNzE4NGMzNDUzIn0.0wNIBxenEi2_ALlhjzkmlMyWtid7gfsJj8no2CEjI"
APP_NAME="fortinet"
REPO_URL="https://github.com/JCLEE94/fortinet.git"
NAMESPACE="fortinet"
REGISTRY_URL="registry.jclee.me"

log_header "ArgoCD Application 설정 시작"

# ArgoCD CLI 확인
if ! command -v argocd &> /dev/null; then
    log_error "ArgoCD CLI가 설치되지 않았습니다."
    echo "설치 방법:"
    echo "  curl -sSL -o argocd https://github.com/argoproj/argo-cd/releases/latest/download/argocd-linux-amd64"
    echo "  chmod +x argocd && sudo mv argocd /usr/local/bin/"
    exit 1
fi

# ArgoCD 서버 연결 테스트
log_info "ArgoCD 서버 연결 테스트..."
if ! curl -k -s --connect-timeout 10 "https://$ARGOCD_SERVER/api/version" > /dev/null; then
    log_error "ArgoCD 서버($ARGOCD_SERVER)에 연결할 수 없습니다."
    exit 1
fi
log_success "ArgoCD 서버 연결 확인"

# ArgoCD 로그인 (API 토큰 사용)
log_info "ArgoCD 로그인 중..."
export ARGOCD_AUTH_TOKEN="$ARGOCD_TOKEN"
export ARGOCD_SERVER="$ARGOCD_SERVER"
export ARGOCD_OPTS="--grpc-web"

if argocd cluster list > /dev/null 2>&1; then
    log_success "ArgoCD 인증 성공"
else
    log_error "ArgoCD 인증 실패"
    exit 1
fi

# 기존 애플리케이션 정리
log_info "기존 애플리케이션 정리..."
argocd app delete $APP_NAME --cascade --yes 2>/dev/null || true
argocd app delete fortinet-primary --cascade --yes 2>/dev/null || true
argocd app delete fortinet-secondary --cascade --yes 2>/dev/null || true
sleep 5

# ArgoCD Application 생성
log_header "ArgoCD Application 생성"

log_info "새 애플리케이션 생성: $APP_NAME"
argocd app create $APP_NAME \
    --repo $REPO_URL \
    --path k8s/manifests \
    --dest-namespace $NAMESPACE \
    --dest-server https://kubernetes.default.svc \
    --sync-policy automated \
    --sync-option CreateNamespace=true \
    --sync-option PrunePropagationPolicy=foreground \
    --auto-prune \
    --self-heal \
    --revision HEAD

log_success "ArgoCD Application 생성 완료"

# 초기 동기화
log_info "초기 동기화 실행..."
argocd app sync $APP_NAME --prune

# 애플리케이션 상태 확인
log_header "애플리케이션 상태 확인"
sleep 10

log_info "애플리케이션 상세 정보:"
argocd app get $APP_NAME

echo ""
log_info "애플리케이션 리스트:"
argocd app list

# Git hook 설정 (GitOps 연동)
log_header "GitOps 연동 설정"

# Webhook 설정을 위한 정보 표시
log_info "📋 Webhook 설정 정보:"
echo "  ArgoCD Server: https://$ARGOCD_SERVER"
echo "  Webhook URL: https://$ARGOCD_SERVER/api/webhook"
echo "  Application: $APP_NAME"

# Repository 설정 확인
log_info "Repository 설정 확인..."
argocd repo list | grep -E "(URL|TYPE)" || true
if ! argocd repo list | grep -q "$REPO_URL"; then
    log_info "Repository 추가..."
    argocd repo add $REPO_URL --type git --name fortinet-repo
    log_success "Repository 추가 완료"
fi

# 자동 동기화 설정 확인
log_header "자동 동기화 설정 확인"

# 애플리케이션의 동기화 정책 확인
SYNC_POLICY=$(argocd app get $APP_NAME -o json | jq -r '.spec.syncPolicy.automated // "null"')
if [ "$SYNC_POLICY" != "null" ]; then
    log_success "자동 동기화가 활성화되어 있습니다"
    argocd app get $APP_NAME -o json | jq '.spec.syncPolicy'
else
    log_warning "자동 동기화가 비활성화되어 있습니다"
    log_info "자동 동기화 활성화..."
    argocd app patch $APP_NAME --patch '{"spec":{"syncPolicy":{"automated":{"prune":true,"selfHeal":true},"syncOptions":["CreateNamespace=true","PrunePropagationPolicy=foreground"]}}}'
fi

# Image Updater 설정 (선택사항)
log_header "Image Updater 설정"

# ArgoCD Image Updater annotation 추가
log_info "이미지 자동 업데이트 설정..."
argocd app patch $APP_NAME --patch '{
  "metadata": {
    "annotations": {
      "argocd-image-updater.argoproj.io/image-list": "fortinet='$REGISTRY_URL'/fortinet",
      "argocd-image-updater.argoproj.io/write-back-method": "git:secret:argocd/git-creds",
      "argocd-image-updater.argoproj.io/fortinet.update-strategy": "latest",
      "argocd-image-updater.argoproj.io/fortinet.kustomize.image-name": "'$REGISTRY_URL'/fortinet"
    }
  }
}'

log_success "이미지 자동 업데이트 설정 완료"

# 최종 상태 확인
log_header "최종 설정 확인"

log_info "애플리케이션 상태:"
argocd app get $APP_NAME | grep -E "(Health Status|Sync Status|Last Sync|Repository)"

echo ""
log_success "🎉 ArgoCD Application 설정 완료!"

echo ""
log_info "📋 설정 요약:"
echo "  📱 Application: $APP_NAME"
echo "  🔗 Repository: $REPO_URL"
echo "  📂 Path: k8s/manifests"
echo "  🎯 Namespace: $NAMESPACE"
echo "  🔄 Sync Policy: Automated (prune + self-heal)"
echo "  🖼️  Image Update: Enabled"

echo ""
log_info "📚 다음 단계:"
echo "  1. GitHub에서 코드 변경 후 push"
echo "  2. Docker 이미지 자동 빌드 및 레지스트리 푸시"
echo "  3. ArgoCD가 변경사항 감지 및 자동 배포"
echo "  4. https://fortinet.jclee.me에서 배포 확인"

echo ""
log_info "🔍 모니터링:"
echo "  ArgoCD UI: https://$ARGOCD_SERVER"
echo "  Application: https://$ARGOCD_SERVER/applications/$APP_NAME"

exit 0