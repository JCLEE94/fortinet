#!/bin/bash

# MSA 배포 스크립트
set -e

echo "🚀 FortiGate Nextrade MSA 배포 시작..."

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 함수 정의
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_dependencies() {
    log_info "의존성 확인 중..."
    
    # Docker 확인
    if ! command -v docker &> /dev/null; then
        log_error "Docker가 설치되지 않았습니다."
        exit 1
    fi
    
    # Docker Compose 확인
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose가 설치되지 않았습니다."
        exit 1
    fi
    
    # jq 확인 (JSON 파싱용)
    if ! command -v jq &> /dev/null; then
        log_warn "jq가 설치되지 않았습니다. 설치 중..."
        if [[ "$OSTYPE" == "linux-gnu"* ]]; then
            sudo apt-get update && sudo apt-get install -y jq
        elif [[ "$OSTYPE" == "darwin"* ]]; then
            brew install jq
        fi
    fi
    
    log_info "의존성 확인 완료"
}

setup_environment() {
    log_info "환경 설정 중..."
    
    # .env 파일 생성
    if [ ! -f .env ]; then
        cat > .env << EOF
# MSA Environment Configuration
COMPOSE_PROJECT_NAME=fortinet-msa
KONG_DATABASE=postgres
KONG_PG_HOST=kong-database
KONG_PG_USER=kong
KONG_PG_PASSWORD=kongpass
KONG_PG_DATABASE=kong

# RabbitMQ Configuration
RABBITMQ_DEFAULT_USER=fortinet
RABBITMQ_DEFAULT_PASS=fortinet123

# Redis Configuration
REDIS_PASSWORD=

# JWT Configuration
JWT_SECRET=fortinet-msa-secret-key-$(date +%s)
JWT_EXPIRY_HOURS=24

# Service URLs
AUTH_SERVICE_URL=http://auth-service:8081
FORTIMANAGER_SERVICE_URL=http://fortimanager-service:8082
ITSM_SERVICE_URL=http://itsm-service:8083
MONITORING_SERVICE_URL=http://monitoring-service:8084
SECURITY_SERVICE_URL=http://security-service:8085
ANALYSIS_SERVICE_URL=http://analysis-service:8086
CONFIG_SERVICE_URL=http://config-service:8087

# Database URLs
FORTIMANAGER_DB_URL=postgresql://fortimanager:fm123@fortimanager-db:5432/fortimanager
ITSM_DB_URL=postgresql://itsm:itsm123@itsm-db:5432/itsm
ANALYSIS_DB_URL=postgresql://analysis:analysis123@analysis-db:5432/analysis

# External Services
CONSUL_URL=http://consul:8500
RABBITMQ_URL=amqp://fortinet:fortinet123@rabbitmq:5672/
REDIS_URL=redis://redis:6379
INFLUXDB_URL=http://influxdb:8086
MONGODB_URL=mongodb://security:sec123@mongodb:27017/security
ETCD_URL=http://etcd:2379
EOF
        log_info ".env 파일 생성 완료"
    fi
    
    # 로그 디렉토리 생성
    mkdir -p logs/services
    mkdir -p data/prometheus
    mkdir -p data/grafana
    
    log_info "환경 설정 완료"
}

build_services() {
    log_info "서비스 이미지 빌드 중..."
    
    # 병렬 빌드로 속도 향상
    docker-compose -f docker-compose.msa.yml build --parallel
    
    log_info "서비스 이미지 빌드 완료"
}

start_infrastructure() {
    log_info "인프라 컴포넌트 시작 중..."
    
    # 1단계: 데이터베이스와 메시지 큐 시작
    docker-compose -f docker-compose.msa.yml up -d \
        kong-database \
        fortimanager-db \
        itsm-db \
        analysis-db \
        mongodb \
        influxdb \
        redis \
        rabbitmq \
        consul \
        etcd
    
    log_info "데이터베이스 시작 대기 중..."
    sleep 30
    
    # Kong 마이그레이션 실행
    log_info "Kong 마이그레이션 실행 중..."
    docker-compose -f docker-compose.msa.yml run --rm kong-migrations
    
    # 2단계: Kong API Gateway 시작
    docker-compose -f docker-compose.msa.yml up -d kong
    
    log_info "Kong 시작 대기 중..."
    sleep 20
    
    log_info "인프라 컴포넌트 시작 완료"
}

start_services() {
    log_info "마이크로서비스 시작 중..."
    
    # 핵심 서비스부터 순차 시작
    docker-compose -f docker-compose.msa.yml up -d \
        auth-service \
        config-service
    
    log_info "핵심 서비스 시작 대기 중..."
    sleep 15
    
    # 나머지 서비스 시작
    docker-compose -f docker-compose.msa.yml up -d \
        fortimanager-service \
        itsm-service \
        monitoring-service \
        security-service \
        analysis-service
    
    log_info "모든 마이크로서비스 시작 대기 중..."
    sleep 30
    
    log_info "마이크로서비스 시작 완료"
}

start_monitoring() {
    log_info "모니터링 스택 시작 중..."
    
    docker-compose -f docker-compose.msa.yml up -d \
        prometheus \
        grafana
    
    log_info "모니터링 스택 시작 완료"
}

setup_kong_routes() {
    log_info "Kong API Gateway 라우팅 설정 중..."
    
    # Kong이 준비될 때까지 대기
    local retry_count=0
    local max_retries=12
    
    while [ $retry_count -lt $max_retries ]; do
        if curl -s http://localhost:8001/status > /dev/null 2>&1; then
            log_info "Kong Admin API 준비 완료"
            break
        fi
        
        log_info "Kong Admin API 대기 중... ($((retry_count + 1))/$max_retries)"
        sleep 10
        retry_count=$((retry_count + 1))
    done
    
    if [ $retry_count -eq $max_retries ]; then
        log_error "Kong Admin API 연결 실패"
        exit 1
    fi
    
    # Kong 라우팅 스크립트 실행
    if [ -f scripts/setup-kong-routes.sh ]; then
        chmod +x scripts/setup-kong-routes.sh
        ./scripts/setup-kong-routes.sh
    else
        log_warn "Kong 라우팅 스크립트를 찾을 수 없습니다."
    fi
    
    log_info "Kong API Gateway 설정 완료"
}

verify_deployment() {
    log_info "배포 검증 중..."
    
    # 서비스 헬스체크
    local services=(
        "auth:8000/auth/health"
        "fortimanager:8000/fortimanager/health"
        "itsm:8000/itsm/health"
        "kong-admin:8001/status"
        "grafana:3000/api/health"
        "prometheus:9090/-/healthy"
    )
    
    local failed_services=()
    
    for service_info in "${services[@]}"; do
        IFS=':' read -r service_name service_endpoint <<< "$service_info"
        
        log_info "Testing $service_name..."
        
        if curl -s -f "http://localhost:$service_endpoint" > /dev/null; then
            log_info "✅ $service_name: OK"
        else
            log_error "❌ $service_name: FAILED"
            failed_services+=("$service_name")
        fi
    done
    
    if [ ${#failed_services[@]} -eq 0 ]; then
        log_info "🎉 모든 서비스가 정상적으로 배포되었습니다!"
    else
        log_error "❌ 다음 서비스들에서 문제가 발생했습니다: ${failed_services[*]}"
        return 1
    fi
}

show_service_info() {
    log_info "서비스 접근 정보:"
    echo ""
    echo "🌐 API Gateway (Kong):"
    echo "  - Proxy: http://localhost:8000"
    echo "  - Admin API: http://localhost:8001"
    echo "  - Admin GUI: http://localhost:8002"
    echo ""
    echo "🔐 서비스 엔드포인트 (through API Gateway):"
    echo "  - 인증: http://localhost:8000/auth"
    echo "  - FortiManager: http://localhost:8000/fortimanager"
    echo "  - ITSM: http://localhost:8000/itsm"
    echo "  - 모니터링: http://localhost:8000/monitoring"
    echo "  - 보안: http://localhost:8000/security"
    echo "  - 분석: http://localhost:8000/analysis"
    echo "  - 설정: http://localhost:8000/config"
    echo ""
    echo "📊 모니터링 & 관리:"
    echo "  - Grafana: http://localhost:3000 (admin/admin123)"
    echo "  - Prometheus: http://localhost:9090"
    echo "  - RabbitMQ Management: http://localhost:15672 (fortinet/fortinet123)"
    echo "  - Consul: http://localhost:8500"
    echo ""
    echo "🧪 테스트 명령:"
    echo "  python tests/msa/test_service_communication.py"
    echo ""
}

cleanup_on_error() {
    log_error "배포 중 오류 발생. 정리 중..."
    docker-compose -f docker-compose.msa.yml down
    exit 1
}

# 메인 실행
main() {
    # 오류 시 정리 함수 등록
    trap cleanup_on_error ERR
    
    # 단계별 실행
    check_dependencies
    setup_environment
    build_services
    start_infrastructure
    start_services
    start_monitoring
    setup_kong_routes
    
    # 배포 검증
    if verify_deployment; then
        show_service_info
        log_info "🚀 MSA 배포가 성공적으로 완료되었습니다!"
    else
        log_error "배포 검증 실패"
        exit 1
    fi
}

# 스크립트 인자 처리
case "${1:-deploy}" in
    "deploy")
        main
        ;;
    "stop")
        log_info "MSA 서비스 중지 중..."
        docker-compose -f docker-compose.msa.yml down
        log_info "MSA 서비스 중지 완료"
        ;;
    "restart")
        log_info "MSA 서비스 재시작 중..."
        docker-compose -f docker-compose.msa.yml down
        sleep 5
        main
        ;;
    "logs")
        service_name=${2:-}
        if [ -n "$service_name" ]; then
            docker-compose -f docker-compose.msa.yml logs -f "$service_name"
        else
            docker-compose -f docker-compose.msa.yml logs -f
        fi
        ;;
    "status")
        verify_deployment
        ;;
    "help")
        echo "사용법: $0 [deploy|stop|restart|logs|status|help]"
        echo "  deploy  - MSA 전체 배포 (기본값)"
        echo "  stop    - MSA 서비스 중지"
        echo "  restart - MSA 서비스 재시작"
        echo "  logs    - 서비스 로그 확인 (서비스명 선택 가능)"
        echo "  status  - 배포 상태 확인"
        echo "  help    - 도움말 출력"
        ;;
    *)
        log_error "알 수 없는 명령: $1"
        echo "사용법: $0 [deploy|stop|restart|logs|status|help]"
        exit 1
        ;;
esac