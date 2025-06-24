#!/bin/bash
# Docker Registry 설정 스크립트
# 로컬 또는 원격 Docker Registry 설정

set -e

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
Docker Registry 설정 스크립트

사용법:
  $0 [모드] [옵션]

모드:
  local       로컬 Docker Registry 설정 (기본값)
  remote      원격 Docker Registry 설정
  aws         AWS ECR 설정
  harbor      Harbor Registry 설정

옵션:
  --port PORT         Registry 포트 (기본값: 5000)
  --host HOST         Registry 호스트 (기본값: localhost)
  --ssl               SSL/TLS 활성화
  --auth              인증 활성화
  --data-dir DIR      데이터 디렉토리 지정
  --help              도움말 표시

예제:
  $0 local --port 5000
  $0 remote --host registry.company.com --ssl --auth
  $0 aws --region ap-northeast-2

환경 변수:
  DOCKER_REGISTRY_URL     Registry URL
  REGISTRY_USERNAME       Registry 사용자명
  REGISTRY_PASSWORD       Registry 비밀번호
  AWS_REGION             AWS 리전
  
EOF
}

# 로컬 Registry 설정
setup_local_registry() {
    local port=${REGISTRY_PORT:-5000}
    local data_dir=${REGISTRY_DATA_DIR:-"$HOME/docker-registry"}
    
    log_info "로컬 Docker Registry 설정 중..."
    log_info "포트: $port"
    log_info "데이터 디렉토리: $data_dir"
    
    # 데이터 디렉토리 생성
    mkdir -p "$data_dir"
    
    # 기존 Registry 컨테이너 제거
    docker stop registry 2>/dev/null || true
    docker rm registry 2>/dev/null || true
    
    # Registry 컨테이너 시작
    if [[ "$ENABLE_SSL" == "true" ]]; then
        setup_local_registry_with_ssl "$port" "$data_dir"
    else
        docker run -d \
            --name registry \
            --restart unless-stopped \
            -p "${port}:5000" \
            -v "${data_dir}:/var/lib/registry" \
            -e REGISTRY_STORAGE_DELETE_ENABLED=true \
            registry:2
    fi
    
    # Registry 시작 확인
    sleep 5
    if curl -s "http://localhost:${port}/v2/" >/dev/null; then
        log_success "로컬 Docker Registry 시작 완료"
        log_info "Registry URL: http://localhost:${port}"
        
        # Docker insecure-registries 설정
        setup_insecure_registry "localhost:${port}"
    else
        log_error "Registry 시작 실패"
        exit 1
    fi
}

# SSL이 활성화된 로컬 Registry 설정
setup_local_registry_with_ssl() {
    local port=$1
    local data_dir=$2
    local cert_dir="${data_dir}/certs"
    
    log_info "SSL 인증서 생성 중..."
    
    mkdir -p "$cert_dir"
    
    # 자체 서명 인증서 생성
    openssl req -newkey rsa:4096 -nodes -sha256 \
        -keyout "${cert_dir}/domain.key" \
        -x509 -days 365 \
        -out "${cert_dir}/domain.crt" \
        -subj "/C=KR/ST=Seoul/L=Seoul/O=FortiGate/OU=IT/CN=localhost"
    
    # SSL이 활성화된 Registry 시작
    docker run -d \
        --name registry \
        --restart unless-stopped \
        -p "${port}:5000" \
        -v "${data_dir}:/var/lib/registry" \
        -v "${cert_dir}:/certs" \
        -e REGISTRY_HTTP_TLS_CERTIFICATE=/certs/domain.crt \
        -e REGISTRY_HTTP_TLS_KEY=/certs/domain.key \
        -e REGISTRY_STORAGE_DELETE_ENABLED=true \
        registry:2
    
    log_info "SSL 인증서 위치: ${cert_dir}/domain.crt"
}

# insecure-registries 설정
setup_insecure_registry() {
    local registry_url=$1
    local docker_config="/etc/docker/daemon.json"
    
    log_info "Docker insecure-registries 설정 중..."
    
    # 기존 설정 백업
    if [[ -f "$docker_config" ]]; then
        sudo cp "$docker_config" "${docker_config}.backup"
    fi
    
    # daemon.json 생성/수정
    if [[ -f "$docker_config" ]]; then
        # 기존 설정에 insecure-registries 추가
        sudo jq ". + {\"insecure-registries\": [\"${registry_url}\"]}" "$docker_config" > /tmp/daemon.json
        sudo mv /tmp/daemon.json "$docker_config"
    else
        # 새 설정 파일 생성
        echo "{\"insecure-registries\": [\"${registry_url}\"]}" | sudo tee "$docker_config" > /dev/null
    fi
    
    # Docker 서비스 재시작
    log_info "Docker 서비스 재시작 중..."
    sudo systemctl restart docker
    
    # Docker 서비스 시작 확인
    sleep 5
    if sudo systemctl is-active docker >/dev/null; then
        log_success "Docker 서비스 재시작 완료"
    else
        log_error "Docker 서비스 재시작 실패"
        exit 1
    fi
}

# 원격 Registry 설정
setup_remote_registry() {
    local registry_host=${REGISTRY_HOST:-"registry.company.com"}
    local registry_port=${REGISTRY_PORT:-443}
    
    log_info "원격 Docker Registry 설정 중..."
    log_info "호스트: $registry_host:$registry_port"
    
    # Registry 연결 테스트
    if [[ "$ENABLE_SSL" == "true" ]]; then
        local registry_url="https://${registry_host}:${registry_port}"
    else
        local registry_url="http://${registry_host}:${registry_port}"
    fi
    
    log_info "Registry 연결 테스트: $registry_url"
    
    if curl -s "${registry_url}/v2/" >/dev/null; then
        log_success "원격 Registry 연결 성공"
    else
        log_error "원격 Registry 연결 실패"
        exit 1
    fi
    
    # 인증 설정
    if [[ "$ENABLE_AUTH" == "true" ]]; then
        setup_registry_auth "$registry_host:$registry_port"
    fi
}

# Registry 인증 설정
setup_registry_auth() {
    local registry_url=$1
    
    log_info "Registry 인증 설정 중..."
    
    if [[ -z "$REGISTRY_USERNAME" ]] || [[ -z "$REGISTRY_PASSWORD" ]]; then
        log_error "REGISTRY_USERNAME 및 REGISTRY_PASSWORD 환경 변수가 필요합니다"
        exit 1
    fi
    
    # Docker 로그인
    echo "$REGISTRY_PASSWORD" | docker login --username "$REGISTRY_USERNAME" --password-stdin "$registry_url"
    
    if [[ $? -eq 0 ]]; then
        log_success "Registry 인증 완료"
    else
        log_error "Registry 인증 실패"
        exit 1
    fi
}

# AWS ECR 설정
setup_aws_ecr() {
    local region=${AWS_REGION:-"ap-northeast-2"}
    local repository_name="fortigate-nextrade"
    
    log_info "AWS ECR 설정 중..."
    log_info "리전: $region"
    
    # AWS CLI 설치 확인
    if ! command -v aws &> /dev/null; then
        log_error "AWS CLI가 설치되지 않았습니다"
        exit 1
    fi
    
    # ECR 리포지토리 생성 (이미 있으면 무시)
    aws ecr create-repository \
        --repository-name "$repository_name" \
        --region "$region" \
        --image-scanning-configuration scanOnPush=true \
        2>/dev/null || true
    
    # ECR 로그인
    aws ecr get-login-password --region "$region" | \
        docker login --username AWS --password-stdin \
        "$(aws sts get-caller-identity --query Account --output text).dkr.ecr.${region}.amazonaws.com"
    
    if [[ $? -eq 0 ]]; then
        local ecr_url="$(aws sts get-caller-identity --query Account --output text).dkr.ecr.${region}.amazonaws.com"
        log_success "AWS ECR 설정 완료"
        log_info "ECR URL: ${ecr_url}/${repository_name}"
        
        # 환경 변수 설정
        export DOCKER_REGISTRY_URL="${ecr_url}"
        echo "export DOCKER_REGISTRY_URL=\"${ecr_url}\"" >> ~/.bashrc
    else
        log_error "AWS ECR 로그인 실패"
        exit 1
    fi
}

# Harbor Registry 설정
setup_harbor_registry() {
    local harbor_host=${REGISTRY_HOST:-"harbor.company.com"}
    local harbor_port=${REGISTRY_PORT:-443}
    local project_name="fortigate"
    
    log_info "Harbor Registry 설정 중..."
    log_info "Harbor URL: https://${harbor_host}:${harbor_port}"
    
    # Harbor 연결 테스트
    if curl -s "https://${harbor_host}:${harbor_port}/api/v2.0/health" >/dev/null; then
        log_success "Harbor Registry 연결 성공"
    else
        log_error "Harbor Registry 연결 실패"
        exit 1
    fi
    
    # Harbor 인증
    if [[ -n "$REGISTRY_USERNAME" ]] && [[ -n "$REGISTRY_PASSWORD" ]]; then
        echo "$REGISTRY_PASSWORD" | docker login --username "$REGISTRY_USERNAME" --password-stdin "${harbor_host}:${harbor_port}"
        
        if [[ $? -eq 0 ]]; then
            log_success "Harbor 인증 완료"
            log_info "Harbor Project: ${project_name}"
            
            # 환경 변수 설정
            export DOCKER_REGISTRY_URL="${harbor_host}:${harbor_port}/${project_name}"
            echo "export DOCKER_REGISTRY_URL=\"${harbor_host}:${harbor_port}/${project_name}\"" >> ~/.bashrc
        else
            log_error "Harbor 인증 실패"
            exit 1
        fi
    else
        log_error "REGISTRY_USERNAME 및 REGISTRY_PASSWORD가 필요합니다"
        exit 1
    fi
}

# Registry 정리
cleanup_registry() {
    log_info "Registry 정리 중..."
    
    # 로컬 Registry 컨테이너 제거
    docker stop registry 2>/dev/null || true
    docker rm registry 2>/dev/null || true
    
    # 사용하지 않는 이미지 정리
    docker system prune -f
    
    log_success "Registry 정리 완료"
}

# Registry 상태 확인
check_registry_status() {
    local registry_url=${DOCKER_REGISTRY_URL:-"localhost:5000"}
    
    log_info "Registry 상태 확인: $registry_url"
    
    # HTTP/HTTPS 자동 감지
    if [[ "$registry_url" == *"443"* ]] || [[ "$registry_url" == "harbor"* ]]; then
        local protocol="https"
    else
        local protocol="http"
    fi
    
    if curl -s "${protocol}://${registry_url}/v2/" >/dev/null; then
        log_success "Registry 연결 성공"
        
        # 저장된 이미지 목록 조회
        if curl -s "${protocol}://${registry_url}/v2/_catalog" >/dev/null; then
            log_info "저장된 이미지 목록:"
            curl -s "${protocol}://${registry_url}/v2/_catalog" | jq -r '.repositories[]' 2>/dev/null || echo "  (없음)"
        fi
    else
        log_error "Registry 연결 실패"
        exit 1
    fi
}

# 메인 함수
main() {
    local mode=${1:-"local"}
    
    log_info "🐳 Docker Registry 설정 시작"
    log_info "모드: $mode"
    echo ""
    
    case $mode in
        local)
            setup_local_registry
            ;;
        remote)
            setup_remote_registry
            ;;
        aws)
            setup_aws_ecr
            ;;
        harbor)
            setup_harbor_registry
            ;;
        cleanup)
            cleanup_registry
            ;;
        status)
            check_registry_status
            ;;
        *)
            log_error "알 수 없는 모드: $mode"
            show_help
            exit 1
            ;;
    esac
    
    log_success "🎉 Docker Registry 설정 완료"
}

# 인자 파싱
MODE=""
REGISTRY_PORT=5000
REGISTRY_HOST=""
ENABLE_SSL=false
ENABLE_AUTH=false
REGISTRY_DATA_DIR=""

while [[ $# -gt 0 ]]; do
    case $1 in
        local|remote|aws|harbor|cleanup|status)
            MODE=$1
            shift
            ;;
        --port)
            REGISTRY_PORT="$2"
            shift 2
            ;;
        --host)
            REGISTRY_HOST="$2"
            shift 2
            ;;
        --ssl)
            ENABLE_SSL=true
            shift
            ;;
        --auth)
            ENABLE_AUTH=true
            shift
            ;;
        --data-dir)
            REGISTRY_DATA_DIR="$2"
            shift 2
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

# 기본 모드 설정
if [[ -z "$MODE" ]]; then
    MODE="local"
fi

# 메인 함수 실행
main "$MODE"