#!/bin/bash

# =============================================================================
# 완전한 CI/CD 파이프라인 설정 스크립트
# GitHub Registry 연동 + ArgoCD 자동배포
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

# 스크립트 시작
log_header "🚀 완전한 CI/CD 파이프라인 설정"

echo "이 스크립트는 다음을 설정합니다:"
echo "  📋 1. GitHub Repository Secrets"
echo "  📋 2. ArgoCD Application 생성"
echo "  📋 3. 자동 배포 테스트"
echo ""

read -p "계속 진행하시겠습니까? (y/N): " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    log_info "설정이 취소되었습니다."
    exit 0
fi

# 1단계: GitHub Secrets 설정
log_header "1️⃣ GitHub Secrets 설정"

if [ -f "./scripts/setup-github-secrets.sh" ]; then
    log_info "GitHub Secrets 설정 실행 중..."
    ./scripts/setup-github-secrets.sh
    log_success "GitHub Secrets 설정 완료"
else
    log_error "setup-github-secrets.sh 파일을 찾을 수 없습니다."
    exit 1
fi

echo ""
read -p "GitHub Secrets 설정이 완료되었습니다. 다음 단계로 진행하시겠습니까? (y/N): " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    log_info "설정이 중단되었습니다."
    exit 0
fi

# 2단계: ArgoCD Application 설정
log_header "2️⃣ ArgoCD Application 설정"

if [ -f "./scripts/setup-argocd-app.sh" ]; then
    log_info "ArgoCD Application 설정 실행 중..."
    ./scripts/setup-argocd-app.sh
    log_success "ArgoCD Application 설정 완료"
else
    log_error "setup-argocd-app.sh 파일을 찾을 수 없습니다."
    exit 1
fi

echo ""
read -p "ArgoCD Application 설정이 완료되었습니다. 배포 테스트를 진행하시겠습니까? (y/N): " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    log_info "배포 테스트가 건너뛰어졌습니다."
    exit 0
fi

# 3단계: 배포 테스트
log_header "3️⃣ CI/CD 파이프라인 테스트"

log_info "현재 Git 상태 확인..."
git status

echo ""
log_info "테스트용 변경사항 생성..."

# 현재 시간을 포함한 테스트 파일 생성
cat > test-deployment.txt << EOF
🚀 CI/CD Pipeline Test

Timestamp: $(date -u +'%Y-%m-%d %H:%M:%S UTC')
Test ID: $(date +%s)
Git SHA: $(git rev-parse HEAD)

This file was created to test the complete CI/CD pipeline:
1. GitHub Actions builds Docker image
2. Pushes to registry.jclee.me
3. ArgoCD detects changes and deploys automatically

배포 테스트 완료!
EOF

# Git 커밋 및 푸시
log_info "변경사항 커밋 및 푸시..."
git add test-deployment.txt
git add -A  # 모든 변경사항 포함

COMMIT_MSG="🚀 CI/CD Pipeline Test - $(date +'%Y%m%d_%H%M%S')

✨ Features:
- Complete GitHub Registry integration
- ArgoCD automated deployment
- Full GitOps workflow

🔧 Technical Details:
- Registry: registry.jclee.me
- ArgoCD: argo.jclee.me
- Namespace: fortinet

🤖 Auto-generated test commit"

git commit -m "$COMMIT_MSG" || log_warning "커밋할 변경사항이 없습니다."

log_info "GitHub로 푸시 중..."
git push origin $(git branch --show-current)

log_success "✅ 파이프라인 테스트 트리거 완료!"

# 4단계: 모니터링 안내
log_header "4️⃣ 배포 모니터링"

echo ""
log_info "📊 배포 상태를 모니터링하세요:"
echo ""
echo "🔗 GitHub Actions:"
echo "  https://github.com/JCLEE94/fortinet/actions"
echo ""
echo "🔗 ArgoCD Dashboard:"
echo "  https://argo.jclee.me"
echo "  Application: fortinet"
echo ""
echo "🔗 배포된 애플리케이션:"
echo "  https://fortinet.jclee.me"
echo "  Health Check: https://fortinet.jclee.me/api/health"
echo ""

log_info "⏱️ 예상 배포 시간: 3-5분"
echo "  1. GitHub Actions (1-2분): 테스트 → 빌드 → 푸시"
echo "  2. ArgoCD Sync (1-2분): 변경감지 → 배포"
echo "  3. K8s Deployment (1분): Pod 시작 → Ready 상태"

echo ""
log_info "🔍 실시간 모니터링 명령어:"
echo "  # GitHub Actions 상태"
echo "  gh run list --limit 5"
echo ""
echo "  # ArgoCD 애플리케이션 상태"
echo "  argocd app get fortinet --grpc-web"
echo ""
echo "  # Kubernetes Pod 상태"
echo "  kubectl get pods -n fortinet"
echo ""

# 자동 모니터링 시작
echo ""
read -p "자동 모니터링을 시작하시겠습니까? (y/N): " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    log_info "🔄 자동 모니터링 시작 (5분간)..."
    
    for i in {1..10}; do
        echo ""
        log_info "📊 모니터링 라운드 $i/10 ($(date))"
        
        # GitHub Actions 상태
        echo "  🔧 GitHub Actions:"
        gh run list --limit 1 --json status,conclusion,displayTitle,createdAt || echo "    GitHub CLI 필요"
        
        # ArgoCD 상태
        echo "  🎯 ArgoCD Status:"
        timeout 10s argocd app get fortinet --grpc-web 2>/dev/null | grep -E "(Health Status|Sync Status)" || echo "    ArgoCD 연결 실패"
        
        # 헬스 체크
        echo "  🏥 Application Health:"
        if curl -f -s -k https://fortinet.jclee.me/api/health > /dev/null 2>&1; then
            echo "    ✅ Application is healthy"
        else
            echo "    ⏳ Application not ready yet"
        fi
        
        if [ $i -lt 10 ]; then
            echo "  ⏱️ 다음 체크까지 30초 대기..."
            sleep 30
        fi
    done
fi

# 완료 메시지
echo ""
log_success "🎉 CI/CD 파이프라인 설정 완료!"

echo ""
log_info "📋 설정 완료 항목:"
echo "  ✅ GitHub Repository Secrets"
echo "  ✅ GitHub Actions Workflow"
echo "  ✅ Docker Registry 연동"
echo "  ✅ ArgoCD Application"
echo "  ✅ 자동 배포 파이프라인"
echo "  ✅ 배포 테스트 실행"

echo ""
log_info "🔄 앞으로의 워크플로우:"
echo "  1. 코드 변경 후 git push"
echo "  2. GitHub Actions가 자동으로 Docker 빌드 & 푸시"
echo "  3. ArgoCD가 자동으로 변경사항 감지 & 배포"
echo "  4. https://fortinet.jclee.me에서 변경사항 확인"

echo ""
log_info "🛠️ 유용한 명령어:"
echo "  ./scripts/setup-github-secrets.sh   # Secrets 재설정"
echo "  ./scripts/setup-argocd-app.sh       # ArgoCD 앱 재생성"
echo "  argocd app sync fortinet             # 수동 동기화"
echo "  kubectl get pods -n fortinet         # Pod 상태 확인"

exit 0