#!/bin/bash
# FortiGate Nextrade 자동 롤백 스크립트
# CLAUDE.md 지시사항에 따른 완전 자율적 롤백 시스템

set -euo pipefail

# 환경 변수 설정
APP_NAME="fortigate-nextrade"
BACKUP_RETENTION_DAYS=7
LOG_FILE="/tmp/rollback-$(date +%Y%m%d_%H%M%S).log"

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
BLUE='\033[0;34m'
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

print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
    log "$1"
}

# 헬스체크 함수
health_check() {
    local max_attempts="${1:-5}"
    local wait_time="${2:-10}"
    
    print_status "헬스체크 시작"
    
    for i in $(seq 1 $max_attempts); do
        if curl -f -s "http://localhost:7777/api/settings" > /dev/null; then
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

# 사용 가능한 백업 이미지 목록 조회
list_backups() {
    print_info "📋 사용 가능한 백업 이미지:"
    docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.CreatedAt}}\t{{.Size}}" | grep -E "$APP_NAME.*backup" || {
        print_warning "⚠️ 사용 가능한 백업 이미지가 없습니다"
        return 1
    }
}

# 가장 최신 백업 이미지 선택
get_latest_backup() {
    local latest_backup
    latest_backup=$(docker images --format "{{.Repository}}:{{.Tag}}" | grep -E "$APP_NAME.*backup" | head -1)
    
    if [ -n "$latest_backup" ]; then
        echo "$latest_backup"
        return 0
    else
        return 1
    fi
}

# 특정 백업으로 롤백
rollback_to_backup() {
    local backup_image="$1"
    
    print_status "🔄 백업 이미지로 롤백 시작: $backup_image"
    
    # 현재 컨테이너 상태 확인 및 정리
    print_info "🛑 현재 컨테이너 정리 중"
    
    if docker ps -q -f name="$APP_NAME" > /dev/null; then
        print_info "기존 컨테이너 정지 중..."
        docker stop "$APP_NAME" --time=30 || true
    fi
    
    if docker ps -aq -f name="$APP_NAME" > /dev/null; then
        print_info "기존 컨테이너 제거 중..."
        docker rm "$APP_NAME" || true
    fi
    
    # 백업 이미지로 새 컨테이너 시작
    print_status "🚀 백업 이미지로 컨테이너 시작"
    
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
    
    # 컨테이너 시작 대기
    print_info "⏳ 컨테이너 시작 대기 (30초)"
    sleep 30
    
    # 헬스체크 실행
    if health_check 5 15; then
        print_status "✅ 롤백 성공!"
        print_info "서비스 URL: http://localhost:7777"
        
        # 롤백 후 상태 확인
        print_info "📊 컨테이너 상태:"
        docker ps | grep "$APP_NAME" || true
        
        print_info "📊 최근 로그:"
        docker logs "$APP_NAME" --tail 10 || true
        
        return 0
    else
        print_error "❌ 롤백 후 헬스체크 실패"
        return 1
    fi
}

# 자동 롤백 (가장 최신 백업 사용)
auto_rollback() {
    print_status "🤖 자동 롤백 시작"
    
    local latest_backup
    if latest_backup=$(get_latest_backup); then
        print_info "🔍 최신 백업 이미지 발견: $latest_backup"
        rollback_to_backup "$latest_backup"
    else
        print_error "❌ 사용 가능한 백업 이미지가 없습니다"
        
        # 백업이 없는 경우 latest 태그로 시도
        print_warning "⚠️ latest 태그로 복구 시도"
        if docker images -q "$APP_NAME:latest" > /dev/null; then
            rollback_to_backup "$APP_NAME:latest"
        else
            print_error "❌ latest 이미지도 없습니다 - 수동 개입 필요"
            return 1
        fi
    fi
}

# 백업 정리 (오래된 백업 제거)
cleanup_old_backups() {
    print_status "🧹 오래된 백업 정리 시작"
    
    # 7일 이상 된 백업 이미지 찾기
    local old_backups
    old_backups=$(docker images --format "{{.Repository}}:{{.Tag}}" | grep -E "$APP_NAME.*backup" | tail -n +4) # 최신 3개 제외
    
    if [ -n "$old_backups" ]; then
        print_info "🗑️ 정리 대상 백업:"
        echo "$old_backups"
        
        echo "$old_backups" | while read -r backup; do
            if [ -n "$backup" ]; then
                print_info "삭제 중: $backup"
                docker rmi "$backup" 2>/dev/null || true
            fi
        done
        
        print_status "✅ 백업 정리 완료"
    else
        print_info "ℹ️ 정리할 오래된 백업이 없습니다"
    fi
}

# 시스템 상태 확인
check_system_status() {
    print_info "📊 시스템 상태 확인"
    
    echo "=== Docker 컨테이너 상태 ==="
    docker ps -a | grep "$APP_NAME" || echo "FortiGate Nextrade 컨테이너 없음"
    
    echo ""
    echo "=== Docker 이미지 상태 ==="
    docker images | grep "$APP_NAME" || echo "FortiGate Nextrade 이미지 없음"
    
    echo ""
    echo "=== 포트 사용 상태 ==="
    netstat -tlnp | grep :7777 || echo "포트 7777 사용 중이지 않음"
    
    echo ""
    echo "=== 디스크 사용량 ==="
    df -h | grep -E "(Filesystem|/dev/)"
    
    echo ""
    echo "=== Docker 시스템 정보 ==="
    docker system df
}

# 비상 복구 (모든 방법 시도)
emergency_recovery() {
    print_error "🚨 비상 복구 모드 시작"
    
    # 1. 자동 롤백 시도
    print_status "1️⃣ 자동 롤백 시도"
    if auto_rollback; then
        print_status "✅ 자동 롤백 성공"
        return 0
    fi
    
    # 2. 컨테이너 재시작 시도
    print_status "2️⃣ 컨테이너 재시작 시도"
    if docker ps -q -f name="$APP_NAME" > /dev/null; then
        docker restart "$APP_NAME" || true
        sleep 30
        if health_check 3 10; then
            print_status "✅ 재시작 성공"
            return 0
        fi
    fi
    
    # 3. 시스템 정리 후 재배포
    print_status "3️⃣ 시스템 정리 후 재배포 시도"
    docker stop "$APP_NAME" 2>/dev/null || true
    docker rm "$APP_NAME" 2>/dev/null || true
    docker system prune -f || true
    
    # latest 이미지로 재시작
    if docker images -q "$APP_NAME:latest" > /dev/null; then
        rollback_to_backup "$APP_NAME:latest"
        return $?
    fi
    
    print_error "❌ 모든 복구 시도 실패 - 수동 개입 필요"
    print_error "다음 단계:"
    print_error "1. Docker 서비스 재시작: sudo systemctl restart docker"
    print_error "2. 수동 이미지 빌드: docker build -f Dockerfile.offline -t $APP_NAME:latest ."
    print_error "3. 수동 컨테이너 시작: ./auto-deploy.sh"
    
    return 1
}

# 메인 함수
main() {
    local action="${1:-auto}"
    
    print_status "🔄 FortiGate Nextrade 롤백 시스템"
    print_info "로그 파일: $LOG_FILE"
    
    case "$action" in
        "auto"|"")
            auto_rollback
            ;;
        "list")
            list_backups
            ;;
        "cleanup")
            cleanup_old_backups
            ;;
        "status")
            check_system_status
            ;;
        "emergency")
            emergency_recovery
            ;;
        "backup")
            if [ -n "${2:-}" ]; then
                rollback_to_backup "$2"
            else
                print_error "❌ 백업 이미지명을 지정해주세요"
                print_info "사용법: $0 backup <backup_image>"
                list_backups
                exit 1
            fi
            ;;
        "help"|"-h"|"--help")
            cat << EOF
FortiGate Nextrade 롤백 스크립트

사용법: $0 [옵션]

옵션:
  auto        자동 롤백 (최신 백업 사용) [기본값]
  list        사용 가능한 백업 목록 표시
  backup <img> 특정 백업 이미지로 롤백
  cleanup     오래된 백업 정리
  status      시스템 상태 확인
  emergency   비상 복구 모드 (모든 방법 시도)
  help        이 도움말 표시

예제:
  $0                              # 자동 롤백
  $0 list                         # 백업 목록 확인
  $0 backup fortigate-nextrade:backup-20231201_140000
  $0 emergency                    # 비상 복구

EOF
            ;;
        *)
            print_error "❌ 알 수 없는 옵션: $action"
            print_info "도움말: $0 help"
            exit 1
            ;;
    esac
}

# 자율적 오류 처리
trap 'print_error "롤백 중 오류 발생 - 비상 복구 시도"; emergency_recovery; exit 1' ERR

# 스크립트 실행
main "$@"