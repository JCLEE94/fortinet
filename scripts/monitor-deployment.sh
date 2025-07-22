#!/bin/bash
# monitor-deployment.sh - 배포 모니터링 스크립트

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

log_monitor() {
    echo -e "${CYAN}[MONITOR]${NC} $1"
}

# 설정
GITHUB_REPO="JCLEE94/fortinet"
ARGOCD_SERVER="argo.jclee.me"
CHECK_INTERVAL=30
MAX_WAIT_TIME=1800  # 30분

# 환경별 설정
declare -A ENV_APPS=(
    ["production"]="fortinet"
    ["staging"]="fortinet-staging"
    ["development"]="fortinet-development"
)

declare -A ENV_URLS=(
    ["production"]="https://fortinet.jclee.me"
    ["staging"]="https://fortinet-staging.jclee.me"
    ["development"]="https://fortinet-development.jclee.me"
)

declare -A ENV_NODEPORTS=(
    ["production"]="30777"
    ["staging"]="30779"
    ["development"]="30778"
)

# 사용법 표시
show_usage() {
    cat <<EOF
Usage: $0 [OPTIONS] [MODE]

배포 모니터링 스크립트 - CI/CD 파이프라인 및 ArgoCD 배포 상태 모니터링

MODES:
    github          GitHub Actions 워크플로우 상태 모니터링 (기본값)
    argocd          ArgoCD 애플리케이션 상태 모니터링
    health          애플리케이션 헬스 체크 모니터링
    all             모든 모드 통합 모니터링

OPTIONS:
    -h, --help      이 도움말 표시
    -i, --interval  체크 간격 (초, 기본값: 30)
    -t, --timeout   최대 대기 시간 (초, 기본값: 1800)
    -w, --workflow  특정 워크플로우 모니터링 (ci-parallel, deploy-manual)
    -e, --env       특정 환경 모니터링 (production, staging, development)
    --once          한 번만 체크하고 종료
    --follow        실시간 로그 팔로우 모드

예제:
    $0                              # GitHub Actions 모니터링
    $0 argocd                       # ArgoCD 상태 모니터링
    $0 all --interval 60            # 모든 상태를 60초 간격으로 모니터링
    $0 github --workflow ci-parallel # 특정 워크플로우 모니터링
    $0 health --env production      # 프로덕션 헬스 체크만 모니터링
    $0 --once                       # 현재 상태만 한 번 체크
EOF
}

# GitHub CLI 설치 확인
check_github_cli() {
    if ! command -v gh &> /dev/null; then
        log_error "GitHub CLI not found. Please install gh CLI first."
        log_info "Install: curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg"
        return 1
    fi
    
    # GitHub 인증 상태 확인
    if ! gh auth status >/dev/null 2>&1; then
        log_error "Not authenticated with GitHub. Run: gh auth login"
        return 1
    fi
    
    return 0
}

# ArgoCD CLI 설치 확인
check_argocd_cli() {
    if ! command -v argocd &> /dev/null; then
        log_warning "ArgoCD CLI not found. Installing..."
        curl -sSL -o /tmp/argocd https://github.com/argoproj/argo-cd/releases/latest/download/argocd-linux-amd64
        chmod +x /tmp/argocd
        sudo mv /tmp/argocd /usr/local/bin/argocd
        log_success "ArgoCD CLI installed"
    fi
    
    # ArgoCD 로그인
    log_info "Logging in to ArgoCD..."
    if argocd login "$ARGOCD_SERVER" \
        --username admin \
        --password bingogo1 \
        --insecure \
        --grpc-web >/dev/null 2>&1; then
        log_success "ArgoCD login successful"
        return 0
    else
        log_error "ArgoCD login failed"
        return 1
    fi
}

# GitHub Actions 워크플로우 모니터링
monitor_github_workflows() {
    local workflow_filter="$1"
    
    log_monitor "Monitoring GitHub Actions workflows..."
    
    while true; do
        echo -e "\n$(date +'%Y-%m-%d %H:%M:%S') - GitHub Actions Status"
        echo "=================================="
        
        # 최근 워크플로우 실행 조회
        if [ -n "$workflow_filter" ]; then
            gh run list --repo "$GITHUB_REPO" --workflow "$workflow_filter" --limit 5
        else
            gh run list --repo "$GITHUB_REPO" --limit 10
        fi
        
        # 진행 중인 워크플로우 상세 정보
        local running_runs=$(gh run list --repo "$GITHUB_REPO" --status "in_progress" --json id --jq '.[].id')
        
        if [ -n "$running_runs" ]; then
            echo -e "\n🔄 Running Workflows:"
            for run_id in $running_runs; do
                echo "  Run ID: $run_id"
                gh run view "$run_id" --repo "$GITHUB_REPO" | head -20
            done
        else
            echo -e "\n✅ No workflows currently running"
        fi
        
        if [ "$ONCE_MODE" = "true" ]; then
            break
        fi
        
        sleep "$CHECK_INTERVAL"
    done
}

# ArgoCD 애플리케이션 모니터링
monitor_argocd_applications() {
    local env_filter="$1"
    
    log_monitor "Monitoring ArgoCD applications..."
    
    while true; do
        echo -e "\n$(date +'%Y-%m-%d %H:%M:%S') - ArgoCD Applications Status"
        echo "=================================="
        
        if [ -n "$env_filter" ]; then
            local app_name=${ENV_APPS[$env_filter]}
            if [ -n "$app_name" ]; then
                argocd app get "$app_name" --show-params
            else
                log_error "Invalid environment: $env_filter"
                return 1
            fi
        else
            # 모든 애플리케이션 상태
            argocd app list -o wide
            
            echo -e "\n📊 Application Details:"
            for env in "${!ENV_APPS[@]}"; do
                local app_name=${ENV_APPS[$env]}
                echo -e "\n🎯 $env ($app_name):"
                argocd app get "$app_name" --show-params 2>/dev/null | head -15 || echo "  ❌ Application not found"
            done
        fi
        
        if [ "$ONCE_MODE" = "true" ]; then
            break
        fi
        
        sleep "$CHECK_INTERVAL"
    done
}

# 애플리케이션 헬스 체크 모니터링
monitor_health_checks() {
    local env_filter="$1"
    
    log_monitor "Monitoring application health checks..."
    
    while true; do
        echo -e "\n$(date +'%Y-%m-%d %H:%M:%S') - Health Check Status"
        echo "=================================="
        
        if [ -n "$env_filter" ]; then
            check_single_environment_health "$env_filter"
        else
            # 모든 환경 헬스 체크
            for env in "${!ENV_URLS[@]}"; do
                check_single_environment_health "$env"
            done
        fi
        
        if [ "$ONCE_MODE" = "true" ]; then
            break
        fi
        
        sleep "$CHECK_INTERVAL"
    done
}

# 단일 환경 헬스 체크
check_single_environment_health() {
    local env="$1"
    local url="${ENV_URLS[$env]}"
    local nodeport="${ENV_NODEPORTS[$env]}"
    local fallback_url="http://192.168.50.110:$nodeport"
    
    echo -e "\n🌍 $env Environment:"
    
    # Primary URL 체크
    if curl -s --max-time 10 "$url/api/health" >/dev/null 2>&1; then
        local response=$(curl -s --max-time 10 "$url/api/health")
        if echo "$response" | grep -q "healthy"; then
            log_success "  Primary URL: $url ✅"
        else
            log_warning "  Primary URL: $url ⚠️ (Response: $response)"
        fi
    else
        log_error "  Primary URL: $url ❌"
        
        # Fallback URL 체크
        if curl -s --max-time 10 "$fallback_url/api/health" >/dev/null 2>&1; then
            local fallback_response=$(curl -s --max-time 10 "$fallback_url/api/health")
            if echo "$fallback_response" | grep -q "healthy"; then
                log_success "  Fallback URL: $fallback_url ✅"
            else
                log_warning "  Fallback URL: $fallback_url ⚠️"
            fi
        else
            log_error "  Fallback URL: $fallback_url ❌"
        fi
    fi
    
    # Kubernetes Pod 상태 확인
    local namespace=""
    case "$env" in
        "production") namespace="fortinet" ;;
        "staging") namespace="fortinet-staging" ;;
        "development") namespace="fortinet-dev" ;;
    esac
    
    if [ -n "$namespace" ]; then
        local pods=$(kubectl get pods -n "$namespace" -l app=fortinet --no-headers 2>/dev/null || echo "")
        if [ -n "$pods" ]; then
            local ready_pods=$(echo "$pods" | awk '{print $2}' | grep -c "1/1" || echo "0")
            local total_pods=$(echo "$pods" | wc -l)
            echo "  Pods: $ready_pods/$total_pods ready"
        else
            echo "  Pods: No pods found in namespace $namespace"
        fi
    fi
}

# 통합 모니터링
monitor_all() {
    local env_filter="$1"
    local workflow_filter="$2"
    
    log_monitor "Starting comprehensive monitoring..."
    
    while true; do
        clear
        echo "🚀 FortiGate Nextrade - Deployment Monitoring Dashboard"
        echo "========================================================"
        echo "Time: $(date +'%Y-%m-%d %H:%M:%S')"
        echo "Refresh Interval: ${CHECK_INTERVAL}s"
        echo ""
        
        # GitHub Actions 상태
        echo "🔄 GitHub Actions Status:"
        echo "-------------------------"
        if [ -n "$workflow_filter" ]; then
            gh run list --repo "$GITHUB_REPO" --workflow "$workflow_filter" --limit 3 2>/dev/null || echo "No workflows found"
        else
            gh run list --repo "$GITHUB_REPO" --limit 5 2>/dev/null || echo "Cannot access GitHub API"
        fi
        
        # ArgoCD 애플리케이션 상태
        echo -e "\n📱 ArgoCD Applications:"
        echo "----------------------"
        if command -v argocd &> /dev/null; then
            argocd app list -o wide 2>/dev/null || echo "Cannot connect to ArgoCD"
        else
            echo "ArgoCD CLI not available"
        fi
        
        # 헬스 체크 상태
        echo -e "\n🏥 Health Check Status:"
        echo "----------------------"
        if [ -n "$env_filter" ]; then
            check_single_environment_health "$env_filter"
        else
            for env in production staging development; do
                if [[ " ${!ENV_URLS[@]} " =~ " $env " ]]; then
                    check_single_environment_health "$env"
                fi
            done
        fi
        
        # 시스템 리소스 (Kubernetes)
        echo -e "\n💾 System Resources:"
        echo "-------------------"
        if command -v kubectl &> /dev/null; then
            echo "Nodes:"
            kubectl get nodes --no-headers 2>/dev/null | awk '{print "  "$1": "$2}' || echo "  Cannot access cluster"
            echo ""
            echo "Namespaces:"
            kubectl get ns -l managed-by=fortinet-cicd --no-headers 2>/dev/null | awk '{print "  "$1": "$2}' || echo "  No managed namespaces found"
        else
            echo "kubectl not available"
        fi
        
        if [ "$ONCE_MODE" = "true" ]; then
            break
        fi
        
        echo -e "\n⏱️  Next refresh in ${CHECK_INTERVAL} seconds... (Press Ctrl+C to stop)"
        sleep "$CHECK_INTERVAL"
    done
}

# 실시간 로그 팔로우
follow_logs() {
    local env_filter="$1"
    
    log_monitor "Following real-time logs..."
    
    if [ -n "$env_filter" ]; then
        local namespace=""
        case "$env_filter" in
            "production") namespace="fortinet" ;;
            "staging") namespace="fortinet-staging" ;;
            "development") namespace="fortinet-dev" ;;
        esac
        
        if [ -n "$namespace" ]; then
            log_info "Following logs for $env_filter environment ($namespace namespace)"
            kubectl logs -n "$namespace" -l app=fortinet -f --tail=100
        else
            log_error "Invalid environment: $env_filter"
            return 1
        fi
    else
        log_info "Following logs for all environments..."
        # 여러 네임스페이스 로그를 동시에 팔로우 (백그라운드)
        for env in "${!ENV_APPS[@]}"; do
            local namespace=""
            case "$env" in
                "production") namespace="fortinet" ;;
                "staging") namespace="fortinet-staging" ;;  
                "development") namespace="fortinet-dev" ;;
            esac
            
            if [ -n "$namespace" ]; then
                kubectl logs -n "$namespace" -l app=fortinet -f --tail=10 --prefix=true &
            fi
        done
        
        # 모든 백그라운드 프로세스 대기
        wait
    fi
}

# 메인 함수
main() {
    # 기본값 설정
    local MODE="github"
    local ENV_FILTER=""
    local WORKFLOW_FILTER=""
    ONCE_MODE=false
    FOLLOW_MODE=false
    
    # 인수 파싱
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_usage
                exit 0
                ;;
            -i|--interval)
                CHECK_INTERVAL="$2"
                shift 2
                ;;
            -t|--timeout)
                MAX_WAIT_TIME="$2"
                shift 2
                ;;
            -w|--workflow)
                WORKFLOW_FILTER="$2"
                shift 2
                ;;
            -e|--env)
                ENV_FILTER="$2"
                shift 2
                ;;
            --once)
                ONCE_MODE=true
                shift
                ;;
            --follow)
                FOLLOW_MODE=true
                shift
                ;;
            github|argocd|health|all)
                MODE="$1"
                shift
                ;;
            *)
                log_error "Unknown option: $1"
                show_usage
                exit 1
                ;;
        esac
    done
    
    log_info "🚀 FortiGate Nextrade Deployment Monitor"
    log_info "Mode: $MODE"
    log_info "Check Interval: ${CHECK_INTERVAL}s"
    if [ -n "$ENV_FILTER" ]; then
        log_info "Environment Filter: $ENV_FILTER"
    fi
    if [ -n "$WORKFLOW_FILTER" ]; then
        log_info "Workflow Filter: $WORKFLOW_FILTER"
    fi
    if [ "$ONCE_MODE" = "true" ]; then
        log_info "Single check mode enabled"
    fi
    if [ "$FOLLOW_MODE" = "true" ]; then
        log_info "Follow logs mode enabled"
    fi
    echo ""
    
    # 팔로우 모드
    if [ "$FOLLOW_MODE" = "true" ]; then
        follow_logs "$ENV_FILTER"
        exit 0
    fi
    
    # 필수 도구 확인 및 설치
    case "$MODE" in
        "github"|"all")
            check_github_cli || exit 1
            ;;
    esac
    
    case "$MODE" in
        "argocd"|"all")
            check_argocd_cli || exit 1
            ;;
    esac
    
    # 모니터링 시작
    case "$MODE" in
        "github")
            monitor_github_workflows "$WORKFLOW_FILTER"
            ;;
        "argocd")
            monitor_argocd_applications "$ENV_FILTER"
            ;;
        "health")
            monitor_health_checks "$ENV_FILTER"
            ;;
        "all")
            monitor_all "$ENV_FILTER" "$WORKFLOW_FILTER"
            ;;
        *)
            log_error "Invalid mode: $MODE"
            show_usage
            exit 1
            ;;
    esac
}

# 스크립트 실행
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi