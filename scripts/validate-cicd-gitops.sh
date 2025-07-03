#!/bin/bash

set -euo pipefail

# CI/CD + ArgoCD GitOps 파이프라인 전체 검증 스크립트
# 사용법: ./scripts/validate-cicd-gitops.sh [component]
# 컴포넌트: all, github, docker, registry, argocd, k8s, health

COMPONENT=${1:-"all"}
REGISTRY="registry.jclee.me"
IMAGE_NAME="fortinet"
NAMESPACE="fortinet"
ARGOCD_SERVER="localhost:30080"

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 로깅 함수
log_info() {
    echo -e "${BLUE}ℹ️ $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️ $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

log_header() {
    echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}🔍 $1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

# GitHub Actions 검증
validate_github_actions() {
    log_header "GitHub Actions 워크플로우 검증"
    
    # 워크플로우 파일 존재 확인
    if [ -f ".github/workflows/ci-cd.yml" ]; then
        log_success "CI/CD 워크플로우 파일 존재함"
    else
        log_error "CI/CD 워크플로우 파일이 없습니다"
        return 1
    fi
    
    if [ -f ".github/workflows/argocd-gitops.yml" ]; then
        log_success "ArgoCD GitOps 워크플로우 파일 존재함"
    else
        log_warning "ArgoCD GitOps 워크플로우 파일이 없습니다"
    fi
    
    # GitHub CLI로 워크플로우 상태 확인
    if command -v gh &> /dev/null; then
        log_info "GitHub Actions 실행 기록 확인 중..."
        gh run list --limit 5 --repo JCLEE94/fortinet || log_warning "GitHub CLI 인증 필요"
    else
        log_warning "GitHub CLI가 설치되지 않음"
    fi
    
    # 필수 secrets 확인 (실제로는 확인할 수 없지만 가이드 제공)
    log_info "필수 GitHub Secrets 확인:"
    echo "  - DOCKER_USERNAME"
    echo "  - DOCKER_PASSWORD"  
    echo "  - REGISTRY_USERNAME"
    echo "  - REGISTRY_PASSWORD"
    echo "  - KUBECONFIG (선택사항)"
    echo "  - ARGOCD_TOKEN (선택사항)"
}

# Docker 빌드 검증
validate_docker() {
    log_header "Docker 빌드 검증"
    
    # Dockerfile 존재 확인
    if [ -f "Dockerfile.production" ]; then
        log_success "Dockerfile.production 존재함"
    else
        log_error "Dockerfile.production이 없습니다"
        return 1
    fi
    
    # Docker 빌드 테스트
    log_info "Docker 빌드 테스트 실행 중..."
    if docker build -f Dockerfile.production -t ${REGISTRY}/${IMAGE_NAME}:test . ; then
        log_success "Docker 빌드 성공"
        
        # 빌드된 이미지 정보
        log_info "빌드된 이미지 정보:"
        docker images ${REGISTRY}/${IMAGE_NAME}:test
        
        # 이미지 정리
        docker rmi ${REGISTRY}/${IMAGE_NAME}:test || true
    else
        log_error "Docker 빌드 실패"
        return 1
    fi
}

# 레지스트리 연결 검증
validate_registry() {
    log_header "Docker Registry 연결 검증"
    
    # 레지스트리 ping 테스트
    log_info "레지스트리 연결 테스트 중..."
    if curl -f -s https://${REGISTRY}/v2/ > /dev/null; then
        log_success "레지스트리 연결 성공"
    else
        log_warning "레지스트리 연결 실패 또는 인증 필요"
    fi
    
    # 이미지 목록 확인 (인증이 필요할 수 있음)
    log_info "기존 이미지 확인 중..."
    if docker pull ${REGISTRY}/${IMAGE_NAME}:latest 2>/dev/null; then
        log_success "기존 이미지 확인됨"
        docker rmi ${REGISTRY}/${IMAGE_NAME}:latest || true
    else
        log_warning "기존 이미지가 없거나 접근 권한 없음"
    fi
}

# ArgoCD 검증
validate_argocd() {
    log_header "ArgoCD 설정 검증"
    
    # ArgoCD CLI 설치 확인
    if command -v argocd &> /dev/null; then
        log_success "ArgoCD CLI 설치됨"
        argocd version --client
    else
        log_warning "ArgoCD CLI가 설치되지 않음"
        log_info "설치 명령어: curl -sSL -o argocd-linux-amd64 https://github.com/argoproj/argo-cd/releases/latest/download/argocd-linux-amd64 && sudo install -m 555 argocd-linux-amd64 /usr/local/bin/argocd"
    fi
    
    # ArgoCD 서버 연결 테스트
    log_info "ArgoCD 서버 연결 테스트 중..."
    if curl -f -s http://${ARGOCD_SERVER} > /dev/null; then
        log_success "ArgoCD 서버 연결 성공"
        
        # ArgoCD 로그인 테스트
        if command -v argocd &> /dev/null; then
            if argocd login ${ARGOCD_SERVER} --username admin --password g0nVB3uL4ccsNiSe --insecure; then
                log_success "ArgoCD 로그인 성공"
                
                # 애플리케이션 목록 확인
                log_info "ArgoCD 애플리케이션 목록:"
                argocd app list || log_warning "애플리케이션 목록 조회 실패"
                
                # fortinet-app 상태 확인
                if argocd app get fortinet-app 2>/dev/null; then
                    log_success "fortinet-app 애플리케이션 존재함"
                else
                    log_warning "fortinet-app 애플리케이션이 없습니다"
                fi
            else
                log_warning "ArgoCD 로그인 실패"
            fi
        fi
    else
        log_warning "ArgoCD 서버에 연결할 수 없습니다"
        log_info "ArgoCD 설치: ./argocd/install-argocd.sh"
    fi
    
    # GitOps 매니페스트 검증
    log_info "GitOps 매니페스트 검증 중..."
    if [ -d "argocd/environments" ]; then
        log_success "ArgoCD 환경 디렉토리 존재함"
        
        # 필수 파일들 확인
        REQUIRED_FILES=(
            "argocd/applications/fortinet-app.yaml"
            "argocd/environments/base/deployment.yaml"
            "argocd/environments/base/service.yaml"
            "argocd/environments/base/kustomization.yaml"
            "argocd/environments/production/kustomization.yaml"
        )
        
        for file in "${REQUIRED_FILES[@]}"; do
            if [ -f "$file" ]; then
                log_success "$file 존재함"
            else
                log_error "$file 없음"
            fi
        done
    else
        log_error "ArgoCD 환경 디렉토리가 없습니다"
    fi
}

# Kubernetes 클러스터 검증
validate_kubernetes() {
    log_header "Kubernetes 클러스터 검증"
    
    # kubectl 설치 확인
    if command -v kubectl &> /dev/null; then
        log_success "kubectl 설치됨"
        kubectl version --client
    else
        log_error "kubectl이 설치되지 않음"
        return 1
    fi
    
    # 클러스터 연결 테스트
    log_info "Kubernetes 클러스터 연결 테스트 중..."
    if kubectl cluster-info 2>/dev/null; then
        log_success "Kubernetes 클러스터 연결 성공"
        
        # 네임스페이스 확인
        if kubectl get namespace ${NAMESPACE} 2>/dev/null; then
            log_success "네임스페이스 ${NAMESPACE} 존재함"
        else
            log_warning "네임스페이스 ${NAMESPACE}가 없습니다"
            log_info "생성 명령어: kubectl create namespace ${NAMESPACE}"
        fi
        
        # ArgoCD 네임스페이스 확인
        if kubectl get namespace argocd 2>/dev/null; then
            log_success "ArgoCD 네임스페이스 존재함"
        else
            log_warning "ArgoCD 네임스페이스가 없습니다"
            log_info "ArgoCD 설치: ./argocd/install-argocd.sh"
        fi
        
        # 배포 상태 확인
        if kubectl get deployment fortinet -n ${NAMESPACE} 2>/dev/null; then
            log_success "fortinet 배포 존재함"
            kubectl get pods -n ${NAMESPACE} -l app=fortinet
        else
            log_warning "fortinet 배포가 없습니다"
        fi
        
    else
        log_error "Kubernetes 클러스터에 연결할 수 없습니다"
        return 1
    fi
}

# 헬스 체크 검증
validate_health() {
    log_header "애플리케이션 헬스 체크"
    
    # 로컬 NodePort 테스트
    log_info "로컬 NodePort 서비스 테스트 중..."
    if curl -f -s http://localhost:30777/api/health > /dev/null; then
        log_success "로컬 NodePort 헬스 체크 성공"
        HEALTH_RESPONSE=$(curl -s http://localhost:30777/api/health)
        echo "응답: $HEALTH_RESPONSE"
    else
        log_warning "로컬 NodePort 헬스 체크 실패"
    fi
    
    # 프로덕션 URL 테스트
    log_info "프로덕션 URL 테스트 중..."
    if curl -f -s https://fortinet.jclee.me/api/health > /dev/null; then
        log_success "프로덕션 헬스 체크 성공"
        HEALTH_RESPONSE=$(curl -s https://fortinet.jclee.me/api/health)
        echo "응답: $HEALTH_RESPONSE"
    else
        log_warning "프로덕션 헬스 체크 실패"
    fi
    
    # Kubernetes 내부 서비스 테스트
    if command -v kubectl &> /dev/null && kubectl get svc fortinet-service -n ${NAMESPACE} 2>/dev/null; then
        log_info "Kubernetes 내부 서비스 테스트 중..."
        CLUSTER_IP=$(kubectl get svc fortinet-service -n ${NAMESPACE} -o jsonpath='{.spec.clusterIP}')
        
        if kubectl run health-check-test --rm -i --restart=Never --image=curlimages/curl -- \
           curl -f http://${CLUSTER_IP}/api/health 2>/dev/null; then
            log_success "Kubernetes 내부 서비스 헬스 체크 성공"
        else
            log_warning "Kubernetes 내부 서비스 헬스 체크 실패"
        fi
    fi
}

# 전체 파이프라인 테스트
validate_pipeline() {
    log_header "전체 CI/CD GitOps 파이프라인 통합 테스트"
    
    log_info "파이프라인 플로우 검증:"
    echo "1. 📝 코드 커밋 → GitHub Repository"
    echo "2. 🚀 GitHub Actions CI/CD 트리거"
    echo "3. 🧪 테스트 및 보안 스캔 실행"
    echo "4. 🐳 Docker 이미지 빌드"
    echo "5. 📦 registry.jclee.me에 이미지 푸시"
    echo "6. 📝 GitOps 매니페스트 업데이트"
    echo "7. 🔄 ArgoCD 자동 동기화"
    echo "8. 🚢 Kubernetes 클러스터 배포"
    echo "9. 🏥 헬스 체크 및 검증"
    
    # 간단한 통합 테스트
    log_info "통합 테스트 시뮬레이션..."
    
    # 1. Git 상태 확인
    log_info "1. Git 저장소 상태:"
    git status --porcelain | head -5
    
    # 2. 최근 커밋 확인
    log_info "2. 최근 커밋:"
    git log --oneline -5
    
    # 3. Docker 이미지 확인
    log_info "3. 로컬 Docker 이미지:"
    docker images ${REGISTRY}/${IMAGE_NAME} 2>/dev/null || log_warning "로컬에 이미지 없음"
    
    # 4. ArgoCD 앱 상태 (가능한 경우)
    if command -v argocd &> /dev/null && argocd app list 2>/dev/null | grep -q fortinet-app; then
        log_info "4. ArgoCD 애플리케이션 상태:"
        argocd app get fortinet-app --output yaml | grep -E "(health|sync)" || true
    fi
    
    # 5. Kubernetes 리소스 상태
    if command -v kubectl &> /dev/null && kubectl get deployment fortinet -n ${NAMESPACE} 2>/dev/null; then
        log_info "5. Kubernetes 배포 상태:"
        kubectl get deployment,service,pods -n ${NAMESPACE} -l app=fortinet
    fi
    
    log_success "파이프라인 검증 완료"
}

# 메인 실행 로직
main() {
    log_header "FortiGate Nextrade CI/CD + ArgoCD GitOps 파이프라인 검증"
    
    case $COMPONENT in
        "github")
            validate_github_actions
            ;;
        "docker")
            validate_docker
            ;;
        "registry")
            validate_registry
            ;;
        "argocd")
            validate_argocd
            ;;
        "k8s"|"kubernetes")
            validate_kubernetes
            ;;
        "health")
            validate_health
            ;;
        "pipeline")
            validate_pipeline
            ;;
        "all")
            validate_github_actions
            validate_docker
            validate_registry
            validate_argocd
            validate_kubernetes
            validate_health
            validate_pipeline
            ;;
        *)
            log_error "알 수 없는 컴포넌트: $COMPONENT"
            log_info "사용법: $0 [github|docker|registry|argocd|k8s|health|pipeline|all]"
            exit 1
            ;;
    esac
    
    log_header "검증 완료"
    log_success "CI/CD + ArgoCD GitOps 파이프라인 검증이 완료되었습니다!"
    
    echo ""
    log_info "📚 유용한 명령어들:"
    echo "# ArgoCD UI 접근"
    echo "http://localhost:30080 (admin / g0nVB3uL4ccsNiSe)"
    echo ""
    echo "# GitHub Actions 모니터링"
    echo "gh run list --repo JCLEE94/fortinet"
    echo "gh run watch"
    echo ""
    echo "# ArgoCD CLI 명령어"
    echo "argocd app list"
    echo "argocd app get fortinet-app"
    echo "argocd app sync fortinet-app"
    echo ""
    echo "# Kubernetes 모니터링"
    echo "kubectl get pods -n fortinet -w"
    echo "kubectl logs -f deployment/fortinet -n fortinet"
    echo ""
    echo "# 헬스 체크"
    echo "curl http://localhost:30777/api/health"
    echo "curl https://fortinet.jclee.me/api/health"
}

# 스크립트 실행
main "$@"