#!/bin/bash
# validate-pipeline.sh - CI/CD 파이프라인 검증 스크립트

set -euo pipefail

# 색깔 출력
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
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

log_check() {
    echo -e "${CYAN}[CHECK]${NC} $1"
}

# 전역 변수
ERRORS=()
WARNINGS=()
SUCCESS_COUNT=0
TOTAL_CHECKS=0

# 체크 함수 wrapper
run_check() {
    local check_name="$1"
    local check_function="$2"
    
    ((TOTAL_CHECKS++))
    log_check "Running: $check_name"
    
    if $check_function; then
        log_success "$check_name"
        ((SUCCESS_COUNT++))
        return 0
    else
        log_error "$check_name"
        ERRORS+=("$check_name")
        return 1
    fi
}

# 1. GitHub Actions 워크플로우 검증
check_github_workflows() {
    local workflow_dir=".github/workflows"
    local required_workflows=("ci-parallel.yml" "deploy-manual.yml" "offline-tar.yml")
    local missing_workflows=()
    
    if [ ! -d "$workflow_dir" ]; then
        echo "GitHub workflows directory not found"
        return 1
    fi
    
    for workflow in "${required_workflows[@]}"; do
        if [ ! -f "$workflow_dir/$workflow" ]; then
            missing_workflows+=("$workflow")
        fi
    done
    
    if [ ${#missing_workflows[@]} -gt 0 ]; then
        echo "Missing workflows: ${missing_workflows[*]}"
        return 1
    fi
    
    # 워크플로우 문법 검증 (기본적인 YAML 검증)
    for workflow in "${required_workflows[@]}"; do
        if ! python3 -c "import yaml; yaml.safe_load(open('$workflow_dir/$workflow'))" 2>/dev/null; then
            echo "Invalid YAML syntax in $workflow"
            return 1
        fi
    done
    
    return 0
}

# 2. Docker 환경 검증
check_docker_environment() {
    if ! docker --version >/dev/null 2>&1; then
        echo "Docker not installed or not accessible"
        return 1
    fi
    
    if ! docker buildx version >/dev/null 2>&1; then
        echo "Docker Buildx not available"
        return 1
    fi
    
    # Registry 접근 테스트
    if ! docker login registry.jclee.me -u admin -p bingogo1 >/dev/null 2>&1; then
        echo "Cannot login to Docker registry"
        return 1
    fi
    
    return 0
}

# 3. Kubernetes 클러스터 연결 검증
check_kubernetes_access() {
    if ! kubectl version --client >/dev/null 2>&1; then
        echo "kubectl not installed or not accessible"
        return 1
    fi
    
    if ! kubectl cluster-info >/dev/null 2>&1; then
        echo "Cannot connect to Kubernetes cluster"
        return 1
    fi
    
    # 필요한 네임스페이스 확인
    local namespaces=("argocd" "fortinet" "fortinet-staging" "fortinet-dev")
    for ns in "${namespaces[@]}"; do
        if ! kubectl get namespace "$ns" >/dev/null 2>&1; then
            echo "Namespace $ns not found"
            WARNINGS+=("Namespace $ns not found - will be created during deployment")
        fi
    done
    
    return 0
}

# 4. ArgoCD 접근 검증
check_argocd_access() {
    if ! command -v argocd &> /dev/null; then
        echo "ArgoCD CLI not installed"
        return 1
    fi
    
    if ! argocd login argo.jclee.me --username admin --password bingogo1 --insecure --grpc-web >/dev/null 2>&1; then
        echo "Cannot login to ArgoCD"
        return 1
    fi
    
    # ArgoCD 애플리케이션 확인
    local apps=("fortinet")
    for app in "${apps[@]}"; do
        if ! argocd app get "$app" >/dev/null 2>&1; then
            echo "ArgoCD application $app not found"
            WARNINGS+=("ArgoCD application $app not found - will be created during deployment")
        fi
    done
    
    return 0
}

# 5. Registry 및 ChartMuseum 접근 검증
check_registries() {
    # Docker Registry 테스트
    if ! curl -u admin:bingogo1 -s https://registry.jclee.me/v2/_catalog >/dev/null; then
        echo "Cannot access Docker registry API"
        return 1
    fi
    
    # ChartMuseum 테스트
    if ! curl -u admin:bingogo1 -s https://charts.jclee.me/api/charts >/dev/null; then
        echo "Cannot access ChartMuseum API"
        return 1
    fi
    
    return 0
}

# 6. Helm 환경 검증
check_helm_environment() {
    if ! helm version >/dev/null 2>&1; then
        echo "Helm not installed or not accessible"
        return 1
    fi
    
    # Helm Chart 디렉토리 확인
    if [ ! -d "helm/fortinet" ]; then
        echo "Helm chart directory not found"
        return 1
    fi
    
    # Chart 문법 검증
    if ! helm lint helm/fortinet >/dev/null 2>&1; then
        echo "Helm chart has syntax errors"
        return 1
    fi
    
    # ChartMuseum 저장소 추가
    if ! helm repo add chartmuseum https://charts.jclee.me --username admin --password bingogo1 >/dev/null 2>&1; then
        echo "Cannot add ChartMuseum repository to Helm"
        return 1
    fi
    
    return 0
}

# 7. Python 환경 및 테스트 검증
check_python_environment() {
    if ! python3 --version | grep -q "3.11" >/dev/null 2>&1; then
        echo "Python 3.11 not found"
        return 1
    fi
    
    # 필수 패키지 확인
    local packages=("pytest" "pytest-cov" "black" "flake8" "mypy")
    for package in "${packages[@]}"; do
        if ! python3 -c "import $package" >/dev/null 2>&1; then
            echo "Python package $package not installed"
            WARNINGS+=("Python package $package not installed - will be installed during CI")
        fi
    done
    
    # 테스트 디렉토리 확인
    if [ ! -d "tests" ]; then
        echo "Tests directory not found"
        WARNINGS+=("Tests directory not found - basic test will be created during CI")
    fi
    
    return 0
}

# 8. 프로젝트 구조 검증
check_project_structure() {
    local required_files=(
        "src/main.py"
        "src/web_app.py"
        "Dockerfile.production"
        "helm/fortinet/Chart.yaml"
        "k8s/manifests/deployment.yaml"
        "argocd/fortinet-app.yaml"
    )
    
    local missing_files=()
    for file in "${required_files[@]}"; do
        if [ ! -f "$file" ]; then
            missing_files+=("$file")
        fi
    done
    
    if [ ${#missing_files[@]} -gt 0 ]; then
        echo "Missing required files: ${missing_files[*]}"
        return 1
    fi
    
    return 0
}

# 9. 환경 변수 및 설정 검증
check_environment_config() {
    # GitHub Actions에서 필요한 환경 변수들이 설정되어 있는지 확인
    local github_secrets=(
        "Registry credentials should be set in GitHub repository secrets"
        "ChartMuseum credentials should be set in GitHub repository secrets"
    )
    
    # 로컬 환경 설정 확인
    if [ ! -f "$HOME/.kube/config" ]; then
        echo "Kubernetes config not found"
        WARNINGS+=("Kubernetes config not found in ~/.kube/config")
    fi
    
    # Docker 로그인 상태 확인
    if ! docker info | grep -q "registry.jclee.me" 2>/dev/null; then
        echo "Not logged into Docker registry"
        WARNINGS+=("Docker registry login may be required")
    fi
    
    return 0
}

# 10. 네트워크 연결 검증
check_network_connectivity() {
    local urls=(
        "https://k8s.jclee.me:443"
        "https://argo.jclee.me"
        "https://registry.jclee.me"
        "https://charts.jclee.me"
        "https://fortinet.jclee.me"
    )
    
    local failed_urls=()
    for url in "${urls[@]}"; do
        if ! curl -s --connect-timeout 5 "$url" >/dev/null 2>&1; then
            failed_urls+=("$url")
        fi
    done
    
    if [ ${#failed_urls[@]} -gt 0 ]; then
        echo "Cannot connect to: ${failed_urls[*]}"
        return 1
    fi
    
    return 0
}

# 스크립트 실행 권한 검증
check_script_permissions() {
    local scripts=(
        "scripts/setup-multi-env.sh"
        "scripts/deploy-parallel.sh"
        "scripts/validate-pipeline.sh"
    )
    
    for script in "${scripts[@]}"; do
        if [ -f "$script" ] && [ ! -x "$script" ]; then
            echo "Script $script is not executable"
            return 1
        fi
    done
    
    return 0
}

# 보고서 생성
generate_report() {
    echo ""
    echo "====================================="
    echo "🔍 PIPELINE VALIDATION REPORT"
    echo "====================================="
    echo "Timestamp: $(date -u +'%Y-%m-%d %H:%M:%S UTC')"
    echo "Total Checks: $TOTAL_CHECKS"
    echo "Successful: $SUCCESS_COUNT"
    echo "Failed: $((TOTAL_CHECKS - SUCCESS_COUNT))"
    echo "Warnings: ${#WARNINGS[@]}"
    echo ""
    
    if [ $SUCCESS_COUNT -eq $TOTAL_CHECKS ]; then
        log_success "✅ ALL CHECKS PASSED!"
        echo "Your CI/CD pipeline is ready for deployment."
    else
        log_error "❌ SOME CHECKS FAILED!"
        echo "Please fix the following issues before deploying:"
        for error in "${ERRORS[@]}"; do
            echo "  • $error"
        done
    fi
    
    if [ ${#WARNINGS[@]} -gt 0 ]; then
        echo ""
        log_warning "⚠️ WARNINGS:"
        for warning in "${WARNINGS[@]}"; do
            echo "  • $warning"
        done
    fi
    
    echo ""
    echo "🔗 Next Steps:"
    if [ $SUCCESS_COUNT -eq $TOTAL_CHECKS ]; then
        echo "  1. Commit and push your changes to trigger CI/CD"
        echo "  2. Monitor deployment: https://github.com/your-repo/actions"
        echo "  3. Check ArgoCD: https://argo.jclee.me"
        echo "  4. Verify application: https://fortinet.jclee.me"
    else
        echo "  1. Fix the failed checks listed above"
        echo "  2. Run this validation script again"
        echo "  3. Ensure all environments are properly configured"
    fi
    echo "====================================="
}

# 메인 함수
main() {
    echo "🚀 Starting CI/CD Pipeline Validation..."
    echo ""
    
    # 모든 검증 실행
    run_check "GitHub Workflows Validation" check_github_workflows
    run_check "Docker Environment Check" check_docker_environment  
    run_check "Kubernetes Access Check" check_kubernetes_access
    run_check "ArgoCD Access Check" check_argocd_access
    run_check "Registry Access Check" check_registries
    run_check "Helm Environment Check" check_helm_environment
    run_check "Python Environment Check" check_python_environment
    run_check "Project Structure Check" check_project_structure
    run_check "Environment Configuration Check" check_environment_config
    run_check "Network Connectivity Check" check_network_connectivity
    run_check "Script Permissions Check" check_script_permissions
    
    # 보고서 생성
    generate_report
    
    # 종료 코드 설정
    exit $((TOTAL_CHECKS - SUCCESS_COUNT))
}

# 사용법 표시
show_usage() {
    cat <<EOF
Usage: $0 [OPTIONS]

CI/CD 파이프라인 검증 스크립트

OPTIONS:
    -h, --help      이 도움말 표시
    -v, --verbose   상세한 출력 표시
    -q, --quiet     오류만 표시

이 스크립트는 다음을 검증합니다:
  • GitHub Actions 워크플로우
  • Docker 및 Registry 접근
  • Kubernetes 클러스터 연결
  • ArgoCD 접근 및 설정
  • Helm 환경 및 차트
  • Python 환경 및 테스트
  • 프로젝트 구조
  • 네트워크 연결
  • 스크립트 권한

EOF
}

# 인수 파싱
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_usage
            exit 0
            ;;
        -v|--verbose)
            set -x
            shift
            ;;
        -q|--quiet)
            # 오류만 표시하도록 로그 함수 재정의
            log_info() { :; }
            log_success() { :; }
            log_check() { :; }
            shift
            ;;
        *)
            echo "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# 스크립트 실행
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi