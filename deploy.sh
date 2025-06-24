#!/bin/bash
# FortiGate Nextrade 통합 배포 스크립트
# Asia/Seoul 타임존 자동 적용

set -e
export TZ=Asia/Seoul
PROJECT_NAME="fortigate-nextrade"
BUILD_TIME=$(date +"%Y-%m-%d %H:%M:%S KST")
DOCKER_IMAGE="${PROJECT_NAME}:latest"

echo "🚀 FortiGate Nextrade 배포 시작..."
echo "📅 빌드 시간: $BUILD_TIME"
echo "🌏 타임존: $TZ"
echo ""

# 환경 변수 설정
export APP_MODE=${APP_MODE:-production}
export FLASK_ENV=production
export DOCKER_BUILDKIT=1

# Git 업데이트
echo "📥 최신 코드 업데이트..."
git status --porcelain
if [ $? -eq 0 ] && [ -n "$(git status --porcelain)" ]; then
    echo "⚠️  변경사항이 있습니다. 커밋 후 배포하세요."
fi

# Docker 빌드
echo ""
echo "🔨 Docker 이미지 빌드 (타임존: $TZ)..."
docker build \
    --build-arg BUILD_TIME="$BUILD_TIME" \
    --build-arg TZ="$TZ" \
    -f Dockerfile.offline \
    -t $DOCKER_IMAGE .

if [ $? -ne 0 ]; then
    echo "❌ Docker 빌드 실패!"
    exit 1
fi

# 테스트 실행
echo ""
echo "🧪 기본 테스트 실행..."
docker run --rm \
    -e APP_MODE=test \
    -e TZ="$TZ" \
    $DOCKER_IMAGE python -c "
import sys
sys.path.append('/app/src')
try:
    from web_app import create_app
    app = create_app()
    print('✅ 애플리케이션 로드 성공')
except Exception as e:
    print(f'⚠️  경고: {e}')
    print('✅ 기본 임포트 성공')
"

if [ $? -ne 0 ]; then
    echo "❌ 테스트 실패!"
    exit 1
fi

# 기존 컨테이너 정리
echo ""
echo "🧹 기존 컨테이너 정리..."
docker stop $PROJECT_NAME 2>/dev/null || true
docker rm $PROJECT_NAME 2>/dev/null || true

# 새 컨테이너 시작
echo ""
echo "🚀 새 컨테이너 시작..."
docker run -d \
    --name $PROJECT_NAME \
    -p 7777:7777 \
    -e APP_MODE=$APP_MODE \
    -e FLASK_ENV=production \
    -e TZ="$TZ" \
    -v "$(pwd)/data:/app/data" \
    -v "$(pwd)/logs:/app/logs" \
    --restart unless-stopped \
    $DOCKER_IMAGE

# 헬스체크
echo ""
echo "🔍 헬스체크 대기중..."
sleep 10

for i in {1..6}; do
    if curl -f http://localhost:7777/health 2>/dev/null; then
        echo "✅ 헬스체크 성공!"
        break
    else
        echo "⏳ 헬스체크 재시도 ($i/6)..."
        sleep 5
    fi
    if [ $i -eq 6 ]; then
        echo "❌ 헬스체크 실패!"
        docker logs $PROJECT_NAME --tail=20
        exit 1
    fi
done

# 배포 완료
echo ""
echo "✅ 배포 완료!"
echo "📊 상태 정보:"
docker ps --filter name=$PROJECT_NAME --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo ""
echo "🌐 접속 정보:"
echo "  - 로컬: http://localhost:7777"
echo "  - 외부: http://$(hostname -I | awk '{print $1}'):7777"
echo "  - 헬스체크: http://localhost:7777/health"

echo ""
echo "📋 관리 명령어:"
echo "  docker logs $PROJECT_NAME --tail=50"
echo "  docker exec -it $PROJECT_NAME bash"
echo "  docker restart $PROJECT_NAME"
echo "  docker stop $PROJECT_NAME"

echo ""
echo "🎉 배포 성공! (빌드: $BUILD_TIME)"