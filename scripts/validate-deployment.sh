#!/bin/bash
# FortiGate Nextrade 배포 검증 스크립트
# 배포 전/후 환경 검증 및 헬스체크

set -e
export TZ=Asia/Seoul

# 색상 코드
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

show_help() {
    cat << EOF
FortiGate Nextrade 배포 검증 스크립트

사용법:
  $0 [명령] [옵션]

명령:
  pre-deploy     배포 전 환경 검증
  post-deploy    배포 후 검증 및 헬스체크
  system-check   시스템 요구사항 검증
  app-check      애플리케이션 상태 검증
  full-check     전체 검증 (시스템 + 애플리케이션)

옵션:
  --host HOST    대상 호스트 (기본값: localhost)
  --port PORT    애플리케이션 포트 (기본값: 7777)
  --timeout SEC  타임아웃 (기본값: 30초)
  --verbose      상세 출력
  --help         도움말 표시

예제:
  $0 pre-deploy
  $0 post-deploy --host 192.168.1.100
  $0 full-check --verbose
  
EOF
}

# 시스템 요구사항 검증
check_system_requirements() {
    log_info "시스템 요구사항 검증 중..."
    
    local errors=0
    
    # OS 확인
    if [[ -f /etc/os-release ]]; then
        source /etc/os-release
        log_info "OS: $PRETTY_NAME"
        
        # 지원되는 OS 확인
        case $ID in
            ubuntu|debian|centos|rhel|fedora)
                log_success "지원되는 OS입니다"
                ;;
            *)
                log_warning "테스트되지 않은 OS입니다: $ID"
                ;;
        esac
    else
        log_warning "OS 정보를 확인할 수 없습니다"
    fi
    
    # RAM 확인
    local ram_gb=$(free -g | awk '/^Mem:/{print $2}')
    log_info "RAM: ${ram_gb}GB"
    if [[ $ram_gb -lt 4 ]]; then
        log_error "RAM이 부족합니다. 최소 4GB 필요 (현재: ${ram_gb}GB)"
        ((errors++))
    else
        log_success "RAM 요구사항 충족"
    fi
    
    # 디스크 공간 확인
    local disk_gb=$(df -BG . | awk 'NR==2 {print $4}' | sed 's/G//')
    log_info "사용 가능한 디스크: ${disk_gb}GB"
    if [[ $disk_gb -lt 20 ]]; then
        log_error "디스크 공간이 부족합니다. 최소 20GB 필요 (현재: ${disk_gb}GB)"
        ((errors++))
    else
        log_success "디스크 공간 요구사항 충족"
    fi
    
    # Docker 확인
    if command -v docker &> /dev/null; then
        local docker_version=$(docker --version | awk '{print $3}' | sed 's/,//')
        log_info "Docker: $docker_version"
        
        # Docker 서비스 상태 확인
        if systemctl is-active docker &> /dev/null; then
            log_success "Docker 서비스 실행 중"
        else
            log_error "Docker 서비스가 실행되지 않습니다"
            ((errors++))
        fi
        
        # Docker 권한 확인
        if docker ps &> /dev/null; then
            log_success "Docker 권한 확인됨"
        else
            log_warning "Docker 권한이 없습니다. sudo 또는 docker 그룹에 추가 필요"
        fi
    else
        log_error "Docker가 설치되지 않았습니다"
        ((errors++))
    fi
    
    # 포트 사용 확인
    if ss -tlnp | grep ":${APP_PORT:-7777}" &> /dev/null; then
        local process=$(ss -tlnp | grep ":${APP_PORT:-7777}" | awk '{print $6}' | head -1)
        log_warning "포트 ${APP_PORT:-7777}이 사용 중입니다: $process"
    else
        log_success "포트 ${APP_PORT:-7777} 사용 가능"
    fi
    
    # 네트워크 연결 확인 (선택사항)
    if [[ "$VERBOSE" == "true" ]]; then
        if ping -c 1 8.8.8.8 &> /dev/null; then
            log_info "외부 네트워크 연결 가능 (오프라인 모드에서는 필요 없음)"
        else
            log_info "외부 네트워크 연결 없음 (오프라인 모드에 적합)"
        fi
    fi
    
    return $errors
}

# 애플리케이션 상태 검증
check_application_status() {
    local host=${1:-localhost}
    local port=${2:-7777}
    local timeout=${3:-30}
    
    log_info "애플리케이션 상태 검증 중: ${host}:${port}"
    
    local errors=0
    
    # 컨테이너 상태 확인
    if docker ps --filter "name=fortigate-nextrade" --format "table {{.Names}}\t{{.Status}}" | grep -q "fortigate-nextrade"; then
        local status=$(docker ps --filter "name=fortigate-nextrade" --format "{{.Status}}")
        log_success "컨테이너 실행 중: $status"
    else
        log_error "FortiGate Nextrade 컨테이너가 실행되지 않습니다"
        ((errors++))
        return $errors
    fi
    
    # 포트 리스닝 확인
    if ss -tlnp | grep ":${port}" &> /dev/null; then
        log_success "포트 ${port} 리스닝 중"
    else
        log_error "포트 ${port}에서 리스닝하지 않습니다"
        ((errors++))
    fi
    
    # HTTP 응답 확인
    log_info "HTTP 응답 확인 중..."
    local http_code=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout $timeout "http://${host}:${port}/" || echo "000")
    
    if [[ "$http_code" == "200" ]]; then
        log_success "HTTP 응답 정상: $http_code"
    else
        log_error "HTTP 응답 비정상: $http_code"
        ((errors++))
    fi
    
    # 헬스체크 엔드포인트 확인
    log_info "헬스체크 엔드포인트 확인 중..."
    local health_code=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout $timeout "http://${host}:${port}/api/health" || echo "000")
    
    if [[ "$health_code" == "200" ]]; then
        log_success "헬스체크 통과: $health_code"
        
        # 헬스체크 응답 내용 확인
        if [[ "$VERBOSE" == "true" ]]; then
            local health_response=$(curl -s --connect-timeout $timeout "http://${host}:${port}/api/health")
            log_info "헬스체크 응답: $health_response"
        fi
    else
        log_error "헬스체크 실패: $health_code"
        ((errors++))
    fi
    
    # 주요 엔드포인트 확인
    local endpoints=("/api/settings" "/api/devices" "/api/fortimanager/health")
    
    for endpoint in "${endpoints[@]}"; do
        local endpoint_code=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 10 "http://${host}:${port}${endpoint}" || echo "000")
        
        if [[ "$endpoint_code" =~ ^[2-3][0-9][0-9]$ ]]; then
            log_success "엔드포인트 응답 정상: $endpoint ($endpoint_code)"
        else
            log_warning "엔드포인트 응답 확인 필요: $endpoint ($endpoint_code)"
        fi
    done
    
    return $errors
}

# 배포 전 검증
pre_deploy_check() {
    log_info "🔍 배포 전 환경 검증 시작"
    echo ""
    
    local total_errors=0
    
    # 시스템 요구사항 검증
    check_system_requirements
    total_errors=$((total_errors + $?))
    
    echo ""
    
    # 필수 파일 확인
    log_info "필수 파일 확인 중..."
    local required_files=("Dockerfile.offline" "docker-compose.yml" "requirements_minimal.txt" "src/main.py")
    
    for file in "${required_files[@]}"; do
        if [[ -f "$file" ]]; then
            log_success "파일 존재: $file"
        else
            log_error "필수 파일 없음: $file"
            ((total_errors++))
        fi
    done
    
    echo ""
    
    # 설정 파일 확인
    log_info "설정 파일 확인 중..."
    if [[ -f "data/config.json" ]]; then
        log_success "설정 파일 존재: data/config.json"
        
        # JSON 유효성 검증
        if jq empty data/config.json 2>/dev/null; then
            log_success "설정 파일 JSON 형식 유효"
        else
            log_error "설정 파일 JSON 형식 오류"
            ((total_errors++))
        fi
    else
        log_warning "설정 파일 없음: data/config.json (런타임에 생성됨)"
    fi
    
    echo ""
    
    if [[ $total_errors -eq 0 ]]; then
        log_success "🎉 배포 전 검증 통과! 배포를 진행할 수 있습니다."
        return 0
    else
        log_error "❌ 배포 전 검증 실패: ${total_errors}개 오류 발견"
        return 1
    fi
}

# 배포 후 검증
post_deploy_check() {
    local host=${HOST:-localhost}
    local port=${PORT:-7777}
    local timeout=${TIMEOUT:-30}
    
    log_info "🔍 배포 후 검증 시작: ${host}:${port}"
    echo ""
    
    local total_errors=0
    
    # 애플리케이션 시작 대기
    log_info "애플리케이션 시작 대기 중..."
    sleep 10
    
    # 애플리케이션 상태 검증
    check_application_status "$host" "$port" "$timeout"
    total_errors=$((total_errors + $?))
    
    echo ""
    
    # 로그 확인
    log_info "컨테이너 로그 확인 중..."
    if docker logs fortigate-nextrade --tail=10 2>/dev/null | grep -q "Running on"; then
        log_success "애플리케이션 정상 시작 확인"
    else
        log_warning "애플리케이션 시작 로그 확인 필요"
        if [[ "$VERBOSE" == "true" ]]; then
            echo ""
            log_info "최근 로그 (마지막 10줄):"
            docker logs fortigate-nextrade --tail=10 2>/dev/null || echo "로그를 가져올 수 없습니다"
        fi
    fi
    
    echo ""
    
    # 리소스 사용량 확인
    if [[ "$VERBOSE" == "true" ]]; then
        log_info "리소스 사용량 확인 중..."
        local stats=$(docker stats fortigate-nextrade --no-stream --format "table {{.CPUPerc}}\t{{.MemUsage}}" 2>/dev/null)
        if [[ -n "$stats" ]]; then
            echo "$stats"
        else
            log_warning "리소스 사용량을 확인할 수 없습니다"
        fi
        echo ""
    fi
    
    if [[ $total_errors -eq 0 ]]; then
        log_success "🎉 배포 후 검증 통과! 애플리케이션이 정상 작동합니다."
        echo ""
        log_info "📋 접속 정보:"
        log_info "  - 웹 인터페이스: http://${host}:${port}"
        log_info "  - 헬스체크: http://${host}:${port}/api/health"
        log_info "  - API 문서: http://${host}:${port}/api/docs (개발 모드)"
        return 0
    else
        log_error "❌ 배포 후 검증 실패: ${total_errors}개 오류 발견"
        echo ""
        log_info "🔧 트러블슈팅 명령:"
        log_info "  docker logs fortigate-nextrade --tail=50"
        log_info "  docker exec -it fortigate-nextrade bash"
        log_info "  docker ps -a"
        return 1
    fi
}

# 전체 검증
full_check() {
    log_info "🔍 전체 시스템 검증 시작"
    echo ""
    
    local total_errors=0
    
    # 시스템 검증
    check_system_requirements
    total_errors=$((total_errors + $?))
    
    echo ""
    
    # 애플리케이션 검증 (실행 중인 경우)
    if docker ps --filter "name=fortigate-nextrade" --format "{{.Names}}" | grep -q "fortigate-nextrade"; then
        check_application_status "${HOST:-localhost}" "${PORT:-7777}" "${TIMEOUT:-30}"
        total_errors=$((total_errors + $?))
    else
        log_info "애플리케이션이 실행되지 않음 (시스템 검증만 수행)"
    fi
    
    echo ""
    
    if [[ $total_errors -eq 0 ]]; then
        log_success "🎉 전체 검증 통과!"
        return 0
    else
        log_error "❌ 전체 검증 실패: ${total_errors}개 오류 발견"
        return 1
    fi
}

# 메인 함수
main() {
    local command=${1:-"full-check"}
    
    case $command in
        pre-deploy)
            pre_deploy_check
            ;;
        post-deploy)
            post_deploy_check
            ;;
        system-check)
            check_system_requirements
            ;;
        app-check)
            check_application_status "${HOST:-localhost}" "${PORT:-7777}" "${TIMEOUT:-30}"
            ;;
        full-check)
            full_check
            ;;
        help|--help)
            show_help
            ;;
        *)
            log_error "알 수 없는 명령: $command"
            show_help
            exit 1
            ;;
    esac
}

# 인자 파싱
COMMAND=""
HOST=""
PORT=""
TIMEOUT=30
VERBOSE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        pre-deploy|post-deploy|system-check|app-check|full-check)
            COMMAND=$1
            shift
            ;;
        --host)
            HOST="$2"
            shift 2
            ;;
        --port)
            PORT="$2"
            shift 2
            ;;
        --timeout)
            TIMEOUT="$2"
            shift 2
            ;;
        --verbose)
            VERBOSE=true
            shift
            ;;
        --help)
            show_help
            exit 0
            ;;
        *)
            log_error "알 수 없는 옵션: $1"
            show_help
            exit 1
            ;;
    esac
done

# 명령이 지정되지 않은 경우 기본값 설정
if [[ -z "$COMMAND" ]]; then
    COMMAND="full-check"
fi

# 메인 함수 실행
main "$COMMAND"