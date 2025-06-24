#!/bin/bash
# SSH 배포 환경 설정 스크립트
# SSH 키 생성, 배포, 원격 서버 설정

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
SSH 배포 환경 설정 스크립트

사용법:
  $0 [명령] [옵션]

명령:
  generate-key        SSH 키 쌍 생성
  deploy-key          공개 키를 원격 서버에 배포
  test-connection     SSH 연결 테스트
  setup-server        원격 서버 환경 설정
  install-docker      원격 서버에 Docker 설치
  setup-all           전체 설정 (키 생성 + 배포 + 서버 설정)

옵션:
  --key-path PATH     SSH 키 경로 (기본값: ~/.ssh/fortigate_deploy)
  --key-type TYPE     키 타입 (rsa, ed25519) (기본값: ed25519)
  --key-bits BITS     키 비트 수 (rsa만 해당) (기본값: 4096)
  --servers FILE      서버 목록 파일 또는 HOST1,HOST2,HOST3
  --user USER         SSH 사용자명 (기본값: admin)
  --port PORT         SSH 포트 (기본값: 22)
  --password PASS     SSH 비밀번호 (초기 설정용)
  --help              도움말 표시

예제:
  $0 generate-key --key-type ed25519
  $0 deploy-key --servers "192.168.1.100,192.168.1.101" --user admin
  $0 setup-server --servers config/servers.txt
  $0 setup-all --servers "prod1.company.com,prod2.company.com"

환경 변수:
  DEPLOY_SSH_KEY      SSH 키 경로
  DEPLOY_USER         SSH 사용자명
  DEPLOY_PASSWORD     SSH 비밀번호
  
EOF
}

# SSH 키 쌍 생성
generate_ssh_key() {
    local key_path=${SSH_KEY_PATH:-~/.ssh/fortigate_deploy}
    local key_type=${SSH_KEY_TYPE:-ed25519}
    local key_bits=${SSH_KEY_BITS:-4096}
    
    log_info "SSH 키 쌍 생성 중..."
    log_info "키 타입: $key_type"
    log_info "키 경로: $key_path"
    
    # 기존 키 백업
    if [[ -f "$key_path" ]]; then
        log_warning "기존 키가 존재합니다. 백업 중..."
        mv "$key_path" "${key_path}.backup.$(date +%Y%m%d-%H%M%S)"
        mv "${key_path}.pub" "${key_path}.pub.backup.$(date +%Y%m%d-%H%M%S)" 2>/dev/null || true
    fi
    
    # SSH 키 생성
    case $key_type in
        ed25519)
            ssh-keygen -t ed25519 -f "$key_path" -N "" -C "fortigate-deploy-$(date +%Y%m%d)"
            ;;
        rsa)
            ssh-keygen -t rsa -b "$key_bits" -f "$key_path" -N "" -C "fortigate-deploy-$(date +%Y%m%d)"
            ;;
        *)
            log_error "지원하지 않는 키 타입: $key_type"
            exit 1
            ;;
    esac
    
    # 키 권한 설정
    chmod 600 "$key_path"
    chmod 644 "${key_path}.pub"
    
    log_success "SSH 키 생성 완료"
    log_info "개인 키: $key_path"
    log_info "공개 키: ${key_path}.pub"
    
    # 공개 키 내용 표시
    echo ""
    log_info "생성된 공개 키:"
    cat "${key_path}.pub"
    echo ""
}

# 서버 목록 파싱
parse_servers() {
    local servers_input=$1
    
    if [[ -f "$servers_input" ]]; then
        # 파일에서 서버 목록 읽기
        grep -v '^#' "$servers_input" | grep -v '^$' | tr '\n' ','
    else
        # 콤마로 구분된 서버 목록
        echo "$servers_input"
    fi
}

# SSH 공개 키 배포
deploy_ssh_key() {
    local key_path=${SSH_KEY_PATH:-~/.ssh/fortigate_deploy}
    local servers_input=${SERVERS:-""}
    local user=${SSH_USER:-admin}
    local port=${SSH_PORT:-22}
    local password=${SSH_PASSWORD:-""}
    
    if [[ -z "$servers_input" ]]; then
        log_error "서버 목록이 지정되지 않았습니다 (--servers 옵션 사용)"
        exit 1
    fi
    
    if [[ ! -f "${key_path}.pub" ]]; then
        log_error "공개 키를 찾을 수 없습니다: ${key_path}.pub"
        log_info "먼저 'generate-key' 명령을 실행하세요"
        exit 1
    fi
    
    local servers=$(parse_servers "$servers_input")
    IFS=',' read -ra server_array <<< "$servers"
    
    log_info "SSH 공개 키 배포 중..."
    log_info "공개 키: ${key_path}.pub"
    log_info "대상 서버: ${#server_array[@]}개"
    
    for server in "${server_array[@]}"; do
        server=$(echo "$server" | xargs) # 공백 제거
        [[ -z "$server" ]] && continue
        
        log_info "키 배포 중: ${user}@${server}:${port}"
        
        if [[ -n "$password" ]]; then
            # 비밀번호를 사용한 키 배포
            sshpass -p "$password" ssh-copy-id -i "${key_path}.pub" -p "$port" "${user}@${server}" 2>/dev/null || {
                log_warning "자동 배포 실패. 수동으로 키를 복사하세요:"
                echo "ssh-copy-id -i ${key_path}.pub -p $port ${user}@${server}"
                continue
            }
        else
            # 대화형 키 배포
            ssh-copy-id -i "${key_path}.pub" -p "$port" "${user}@${server}" || {
                log_warning "키 배포 실패: $server"
                continue
            }
        fi
        
        # 연결 테스트
        if ssh -i "$key_path" -p "$port" -o ConnectTimeout=5 -o BatchMode=yes \
            "${user}@${server}" "echo 'SSH 키 배포 성공'" >/dev/null 2>&1; then
            log_success "키 배포 성공: $server"
        else
            log_error "키 배포 실패: $server"
        fi
    done
}

# SSH 연결 테스트
test_ssh_connections() {
    local key_path=${SSH_KEY_PATH:-~/.ssh/fortigate_deploy}
    local servers_input=${SERVERS:-""}
    local user=${SSH_USER:-admin}
    local port=${SSH_PORT:-22}
    
    if [[ -z "$servers_input" ]]; then
        log_error "서버 목록이 지정되지 않았습니다"
        exit 1
    fi
    
    local servers=$(parse_servers "$servers_input")
    IFS=',' read -ra server_array <<< "$servers"
    
    log_info "SSH 연결 테스트 중..."
    log_info "대상 서버: ${#server_array[@]}개"
    
    local success_count=0
    local total_count=${#server_array[@]}
    
    for server in "${server_array[@]}"; do
        server=$(echo "$server" | xargs)
        [[ -z "$server" ]] && continue
        
        log_info "연결 테스트: ${user}@${server}:${port}"
        
        if ssh -i "$key_path" -p "$port" -o ConnectTimeout=10 -o BatchMode=yes \
            "${user}@${server}" "
                echo '=== 시스템 정보 ==='
                echo \"호스트명: \$(hostname)\"
                echo \"OS: \$(cat /etc/os-release | grep PRETTY_NAME | cut -d'=' -f2 | tr -d '\"')\"
                echo \"커널: \$(uname -r)\"
                echo \"CPU: \$(nproc) cores\"
                echo \"메모리: \$(free -h | grep Mem | awk '{print \$2}')\"
                echo \"디스크: \$(df -h / | tail -1 | awk '{print \$4}') 사용 가능\"
                echo \"Docker: \$(docker --version 2>/dev/null || echo 'Not installed')\"
                echo \"=== 연결 성공 ===\"
            " 2>/dev/null; then
            log_success "연결 성공: $server"
            ((success_count++))
        else
            log_error "연결 실패: $server"
        fi
        echo ""
    done
    
    log_info "연결 테스트 결과: ${success_count}/${total_count} 성공"
    
    if [[ $success_count -eq $total_count ]]; then
        log_success "모든 서버 연결 성공"
        return 0
    else
        log_warning "일부 서버 연결 실패"
        return 1
    fi
}

# 원격 서버 환경 설정
setup_remote_server() {
    local key_path=${SSH_KEY_PATH:-~/.ssh/fortigate_deploy}
    local servers_input=${SERVERS:-""}
    local user=${SSH_USER:-admin}
    local port=${SSH_PORT:-22}
    
    if [[ -z "$servers_input" ]]; then
        log_error "서버 목록이 지정되지 않았습니다"
        exit 1
    fi
    
    local servers=$(parse_servers "$servers_input")
    IFS=',' read -ra server_array <<< "$servers"
    
    log_info "원격 서버 환경 설정 중..."
    
    for server in "${server_array[@]}"; do
        server=$(echo "$server" | xargs)
        [[ -z "$server" ]] && continue
        
        log_info "서버 설정 중: $server"
        
        ssh -i "$key_path" -p "$port" "${user}@${server}" "
            set -e
            
            echo '=== 시스템 업데이트 ==='
            sudo apt update && sudo apt upgrade -y
            
            echo '=== 필수 패키지 설치 ==='
            sudo apt install -y curl wget git jq unzip htop
            
            echo '=== 배포 디렉토리 생성 ==='
            mkdir -p ~/app/fortigate-nextrade
            mkdir -p ~/app/backups
            mkdir -p ~/app/logs
            
            echo '=== Docker Compose 설치 ==='
            if ! command -v docker-compose &> /dev/null; then
                sudo curl -L \"https://github.com/docker/compose/releases/download/v2.20.2/docker-compose-\$(uname -s)-\$(uname -m)\" -o /usr/local/bin/docker-compose
                sudo chmod +x /usr/local/bin/docker-compose
            fi
            
            echo '=== 방화벽 설정 ==='
            sudo ufw allow 22/tcp   # SSH
            sudo ufw allow 7777/tcp # FortiGate Nextrade
            sudo ufw --force enable
            
            echo '=== 로그 로테이션 설정 ==='
            sudo tee /etc/logrotate.d/fortigate-nextrade > /dev/null << 'LOGROTATE_EOF'
~/app/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 $user $user
}
LOGROTATE_EOF
            
            echo '=== crontab 설정 ==='
            (crontab -l 2>/dev/null; echo '0 2 * * * docker system prune -f') | crontab -
            
            echo '서버 설정 완료: $server'
        " || {
            log_error "서버 설정 실패: $server"
            continue
        }
        
        log_success "서버 설정 완료: $server"
    done
}

# Docker 설치
install_docker() {
    local key_path=${SSH_KEY_PATH:-~/.ssh/fortigate_deploy}
    local servers_input=${SERVERS:-""}
    local user=${SSH_USER:-admin}
    local port=${SSH_PORT:-22}
    
    if [[ -z "$servers_input" ]]; then
        log_error "서버 목록이 지정되지 않았습니다"
        exit 1
    fi
    
    local servers=$(parse_servers "$servers_input")
    IFS=',' read -ra server_array <<< "$servers"
    
    log_info "Docker 설치 중..."
    
    for server in "${server_array[@]}"; do
        server=$(echo "$server" | xargs)
        [[ -z "$server" ]] && continue
        
        log_info "Docker 설치 중: $server"
        
        ssh -i "$key_path" -p "$port" "${user}@${server}" "
            set -e
            
            # Docker 설치 확인
            if command -v docker &> /dev/null; then
                echo 'Docker가 이미 설치되어 있습니다.'
                docker --version
                exit 0
            fi
            
            echo '=== Docker 저장소 설정 ==='
            sudo apt update
            sudo apt install -y ca-certificates curl gnupg lsb-release
            
            sudo mkdir -p /etc/apt/keyrings
            curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
            
            echo \"deb [arch=\$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \$(lsb_release -cs) stable\" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
            
            echo '=== Docker 설치 ==='
            sudo apt update
            sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
            
            echo '=== Docker 서비스 시작 ==='
            sudo systemctl start docker
            sudo systemctl enable docker
            
            echo '=== 사용자를 docker 그룹에 추가 ==='
            sudo usermod -aG docker $user
            
            echo '=== Docker 설정 ==='
            sudo tee /etc/docker/daemon.json > /dev/null << 'DOCKER_CONFIG_EOF'
{
    \"log-driver\": \"json-file\",
    \"log-opts\": {
        \"max-size\": \"100m\",
        \"max-file\": \"3\"
    },
    \"storage-driver\": \"overlay2\"
}
DOCKER_CONFIG_EOF
            
            sudo systemctl restart docker
            
            echo '=== Docker 설치 확인 ==='
            docker --version
            docker compose version
            
            echo 'Docker 설치 완료. 재로그인 후 docker 명령을 사용할 수 있습니다.'
        " || {
            log_error "Docker 설치 실패: $server"
            continue
        }
        
        log_success "Docker 설치 완료: $server"
    done
}

# 전체 설정
setup_all() {
    log_info "🚀 SSH 배포 환경 전체 설정 시작"
    
    # 1. SSH 키 생성
    if [[ ! -f "${SSH_KEY_PATH:-~/.ssh/fortigate_deploy}" ]]; then
        generate_ssh_key
        echo ""
    fi
    
    # 2. SSH 키 배포
    deploy_ssh_key
    echo ""
    
    # 3. 연결 테스트
    test_ssh_connections
    echo ""
    
    # 4. 서버 환경 설정
    setup_remote_server
    echo ""
    
    # 5. Docker 설치
    install_docker
    echo ""
    
    log_success "🎉 전체 설정 완료"
    
    # 설정 요약 출력
    echo ""
    log_info "📋 설정 요약:"
    log_info "  - SSH 키: ${SSH_KEY_PATH:-~/.ssh/fortigate_deploy}"
    log_info "  - 대상 서버: $(parse_servers "${SERVERS:-""}" | tr ',' ' ')"
    log_info "  - SSH 사용자: ${SSH_USER:-admin}"
    log_info "  - SSH 포트: ${SSH_PORT:-22}"
    
    echo ""
    log_info "🔧 다음 단계:"
    log_info "  1. 환경 변수 설정: export DEPLOY_SSH_KEY=${SSH_KEY_PATH:-~/.ssh/fortigate_deploy}"
    log_info "  2. 배포 설정 파일 수정: config/deploy-config.json"
    log_info "  3. 원격 배포 실행: ./remote-deploy.sh production --registry-push"
}

# 메인 함수
main() {
    local command=${1:-"help"}
    
    case $command in
        generate-key)
            generate_ssh_key
            ;;
        deploy-key)
            deploy_ssh_key
            ;;
        test-connection)
            test_ssh_connections
            ;;
        setup-server)
            setup_remote_server
            ;;
        install-docker)
            install_docker
            ;;
        setup-all)
            setup_all
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
SSH_KEY_PATH=""
SSH_KEY_TYPE="ed25519"
SSH_KEY_BITS=4096
SERVERS=""
SSH_USER="admin"
SSH_PORT=22
SSH_PASSWORD=""

while [[ $# -gt 0 ]]; do
    case $1 in
        generate-key|deploy-key|test-connection|setup-server|install-docker|setup-all)
            COMMAND=$1
            shift
            ;;
        --key-path)
            SSH_KEY_PATH="$2"
            shift 2
            ;;
        --key-type)
            SSH_KEY_TYPE="$2"
            shift 2
            ;;
        --key-bits)
            SSH_KEY_BITS="$2"
            shift 2
            ;;
        --servers)
            SERVERS="$2"
            shift 2
            ;;
        --user)
            SSH_USER="$2"
            shift 2
            ;;
        --port)
            SSH_PORT="$2"
            shift 2
            ;;
        --password)
            SSH_PASSWORD="$2"
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

# 환경 변수에서 값 가져오기
SSH_KEY_PATH=${SSH_KEY_PATH:-$DEPLOY_SSH_KEY}
SSH_USER=${SSH_USER:-$DEPLOY_USER}
SSH_PASSWORD=${SSH_PASSWORD:-$DEPLOY_PASSWORD}

# 명령이 지정되지 않은 경우 도움말 표시
if [[ -z "$COMMAND" ]]; then
    show_help
    exit 0
fi

# 메인 함수 실행
main "$COMMAND"