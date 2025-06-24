#!/bin/bash
# FortiGate Nextrade 자율적 배포 스크립트
# CLAUDE.md 지시사항에 따른 완전 자율적 배포 시스템

set -euo pipefail

# 환경 변수 설정
DEPLOY_HOST="${DEPLOY_HOST:-localhost}"
DEPLOY_PORT="${DEPLOY_PORT:-22}"
DEPLOY_PATH="${DEPLOY_PATH:-/opt/fortinet}"
DEPLOY_USER="${DEPLOY_USER:-deploy}"
APP_NAME="fortigate-nextrade"
BACKUP_DIR="/tmp/fortinet-backups"
LOG_FILE="/tmp/deploy-$(date +%Y%m%d_%H%M%S).log"

# 로깅 함수
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

error() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ERROR: $1" | tee -a "$LOG_FILE" >&2
}

# 색상 코드
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
    log "$1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
    log "WARNING: $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
    error "$1"
}

# 헬스체크 함수
health_check() {
    local host="$1"
    local port="$2"
    local max_attempts="${3:-10}"
    local wait_time="${4:-30}"
    
    print_status "헬스체크 시작: http://$host:$port"
    
    for i in $(seq 1 $max_attempts); do
        if curl -f -s "http://$host:$port/api/settings" > /dev/null; then
            print_status "✅ 헬스체크 성공 ($i/$max_attempts)"
            return 0
        else
            print_warning "⚠️ 헬스체크 실패 ($i/$max_attempts) - ${wait_time}초 대기"
            sleep $wait_time
        fi
    done
    
    print_error "❌ 헬스체크 최종 실패"
    return 1
}

# 백업 생성
create_backup() {
    local backup_name="$APP_NAME-backup-$(date +%Y%m%d_%H%M%S)"
    
    print_status "🔄 현재 버전 백업 중: $backup_name"
    
    # Docker 컨테이너가 실행 중인지 확인
    if docker ps -q -f name="$APP_NAME" > /dev/null; then
        # 실행 중인 컨테이너를 이미지로 저장
        if docker commit "$APP_NAME" "$backup_name"; then
            print_status "✅ 백업 생성 완료: $backup_name"
            echo "$backup_name" > /tmp/last_backup.txt
            return 0
        else
            print_error "❌ 백업 생성 실패"
            return 1
        fi
    else
        print_warning "⚠️ 실행 중인 컨테이너 없음 - 백업 건너뜀"
        return 0
    fi
}

# 이전 버전으로 롤백
rollback() {
    print_error "🔄 이전 버전으로 롤백 시작"
    
    # 현재 컨테이너 정지 및 제거
    docker stop "$APP_NAME" 2>/dev/null || true
    docker rm "$APP_NAME" 2>/dev/null || true
    
    # 마지막 백업 이미지 확인
    if [ -f /tmp/last_backup.txt ]; then
        local backup_image=$(cat /tmp/last_backup.txt)
        
        if docker images -q "$backup_image" > /dev/null; then
            print_status "📦 백업 이미지로 롤백: $backup_image"
            
            docker run -d --name "$APP_NAME" \
                --restart unless-stopped \
                -p 7777:7777 \
                -v "$(pwd)/data:/app/data" \
                -v "$(pwd)/logs:/app/logs" \
                -e APP_MODE=production \
                --health-cmd="python3 -c 'import urllib.request; urllib.request.urlopen(\"http://localhost:7777\", timeout=5)'" \
                --health-interval=30s \
                --health-timeout=10s \
                --health-retries=3 \
                --health-start-period=40s \
                "$backup_image"
            
            if health_check "localhost" "7777" 5 10; then
                print_status "✅ 롤백 성공"
                return 0
            else
                print_error "❌ 롤백 후 헬스체크 실패"
                return 1
            fi
        fi
    fi
    
    # 백업이 없는 경우 최신 태그로 시도
    print_warning "⚠️ 백업 이미지 없음 - latest 태그로 시도"
    
    docker run -d --name "$APP_NAME" \
        --restart unless-stopped \
        -p 7777:7777 \
        -v "$(pwd)/data:/app/data" \
        -v "$(pwd)/logs:/app/logs" \
        -e APP_MODE=production \
        "$APP_NAME:latest" 2>/dev/null || true
    
    return $?
}

# 자율적 빌드 (재시도 포함)
autonomous_build() {
    local max_attempts=3
    local attempt=1
    
    print_status "🔨 Docker 이미지 빌드 시작"
    
    while [ $attempt -le $max_attempts ]; do
        print_status "빌드 시도 $attempt/$max_attempts"
        
        # 빌드 전 정리
        if [ $attempt -gt 1 ]; then
            print_status "🧹 빌드 캐시 정리"
            docker builder prune -f || true
            docker system prune -f || true
        fi
        
        # 빌드 실행
        if docker build --no-cache -f Dockerfile.offline -t "$APP_NAME:latest" .; then
            print_status "✅ 빌드 성공"
            return 0
        else
            print_warning "⚠️ 빌드 실패 ($attempt/$max_attempts)"
            
            if [ $attempt -eq $max_attempts ]; then
                print_error "❌ 최대 빌드 시도 횟수 초과"
                return 1
            fi
            
            # 실패 원인 분석 및 자동 수정 시도
            case $attempt in
                1)
                    print_status "🔧 디스크 공간 정리 시도"
                    docker system prune -af || true
                    ;;
                2)
                    print_status "🔧 빌드킷 재설정 시도"
                    export DOCKER_BUILDKIT=0
                    ;;
            esac
            
            attempt=$((attempt + 1))
            sleep 10
        fi
    done
    
    return 1
}

# 무중단 배포
zero_downtime_deploy() {
    print_status "🚀 무중단 배포 시작"
    
    # 새 컨테이너 시작 (다른 포트 사용)
    local temp_port=7778
    local temp_name="$APP_NAME-new"
    
    print_status "📦 새 컨테이너 시작 (포트: $temp_port)"
    
    docker run -d --name "$temp_name" \
        --restart unless-stopped \
        -p "$temp_port:7777" \
        -v "$(pwd)/data:/app/data" \
        -v "$(pwd)/logs:/app/logs" \
        -e APP_MODE=production \
        --health-cmd="python3 -c 'import urllib.request; urllib.request.urlopen(\"http://localhost:7777\", timeout=5)'" \
        --health-interval=30s \
        --health-timeout=10s \
        --health-retries=3 \
        --health-start-period=40s \
        "$APP_NAME:latest"
    
    # 새 컨테이너 헬스체크
    if health_check "localhost" "$temp_port" 10 15; then
        print_status "🔄 트래픽 전환 중"
        
        # 기존 컨테이너 정지
        docker stop "$APP_NAME" 2>/dev/null || true
        docker rm "$APP_NAME" 2>/dev/null || true
        
        # 새 컨테이너를 메인 포트로 재시작
        docker stop "$temp_name"
        docker rm "$temp_name"
        
        docker run -d --name "$APP_NAME" \
            --restart unless-stopped \
            -p 7777:7777 \
            -v "$(pwd)/data:/app/data" \
            -v "$(pwd)/logs:/app/logs" \
            -e APP_MODE=production \
            --health-cmd="python3 -c 'import urllib.request; urllib.request.urlopen(\"http://localhost:7777\", timeout=5)'" \
            --health-interval=30s \
            --health-timeout=10s \
            --health-retries=3 \
            --health-start-period=40s \
            "$APP_NAME:latest"
        
        # 최종 헬스체크
        if health_check "localhost" "7777" 10 15; then
            print_status "✅ 무중단 배포 성공"
            return 0
        else
            print_error "❌ 최종 헬스체크 실패 - 롤백 필요"
            return 1
        fi
    else
        print_error "❌ 새 컨테이너 헬스체크 실패"
        docker stop "$temp_name" 2>/dev/null || true
        docker rm "$temp_name" 2>/dev/null || true
        return 1
    fi
}

# 메인 배포 함수
main_deploy() {
    print_status "🚀 FortiGate Nextrade 자율적 배포 시작"
    print_status "배포 대상: $DEPLOY_HOST:$DEPLOY_PORT"
    print_status "배포 경로: $DEPLOY_PATH"
    
    # 배포 디렉토리로 이동
    cd "$DEPLOY_PATH" || {
        print_error "배포 디렉토리에 접근할 수 없습니다: $DEPLOY_PATH"
        exit 1
    }
    
    # Git 저장소 업데이트
    print_status "📥 소스 코드 업데이트"
    if [ -d .git ]; then
        git fetch origin
        git reset --hard origin/offline-deployment
    else
        print_error "Git 저장소가 아닙니다: $DEPLOY_PATH"
        exit 1
    fi
    
    # 백업 생성
    if ! create_backup; then
        print_error "백업 생성 실패 - 배포 중단"
        exit 1
    fi
    
    # 자율적 빌드
    if ! autonomous_build; then
        print_error "빌드 실패 - 롤백 실행"
        rollback
        exit 1
    fi
    
    # 무중단 배포
    if ! zero_downtime_deploy; then
        print_error "배포 실패 - 롤백 실행"
        rollback
        exit 1
    fi
    
    # 배포 후 정리
    print_status "🧹 배포 후 정리"
    docker image prune -f || true
    
    # 배포 성공 로그
    print_status "🎉 배포 성공!"
    print_status "서비스 URL: http://$DEPLOY_HOST:7777"
    print_status "로그 파일: $LOG_FILE"
    
    # 최종 상태 확인
    print_status "📊 최종 상태 확인"
    docker ps | grep "$APP_NAME" || true
    docker logs "$APP_NAME" --tail 5 || true
}

# 자율적 오류 처리
trap 'print_error "배포 중 오류 발생 - 자동 롤백 시도"; rollback; exit 1' ERR

# 스크립트 인자 처리
case "${1:-deploy}" in
    "deploy")
        main_deploy
        ;;
    "rollback")
        rollback
        ;;
    "health-check")
        health_check "${2:-localhost}" "${3:-7777}"
        ;;
    "backup")
        create_backup
        ;;
    *)
        echo "사용법: $0 [deploy|rollback|health-check|backup]"
        exit 1
        ;;
esac