#!/bin/bash
set -euo pipefail

# Watchtower 기반 자동 배포 스크립트
# registry.jclee.me에서 새 이미지를 감지하면 자동으로 컨테이너를 업데이트

REGISTRY="registry.jclee.me"
IMAGE_NAME="fortinet"
CONTAINER_NAME="fortinet-app"

echo "🔍 Watchtower 자동 배포 설정..."

# 기존 watchtower 컨테이너 정리
echo "🧹 기존 Watchtower 정리..."
docker stop watchtower 2>/dev/null || true
docker rm watchtower 2>/dev/null || true

# Watchtower 실행 (30초마다 체크)
echo "🚀 Watchtower 시작..."
docker run -d \
  --name watchtower \
  --restart unless-stopped \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -e WATCHTOWER_POLL_INTERVAL=30 \
  -e WATCHTOWER_CLEANUP=true \
  -e WATCHTOWER_INCLUDE_RESTARTING=true \
  -e WATCHTOWER_ROLLING_RESTART=true \
  -e WATCHTOWER_NOTIFICATIONS=shoutrrr \
  -e WATCHTOWER_NOTIFICATION_URL="logger://" \
  -e WATCHTOWER_DEBUG=true \
  containrrr/watchtower \
  $CONTAINER_NAME

echo "✅ Watchtower 설정 완료!"
echo ""
echo "📊 Watchtower 상태:"
docker ps --filter "name=watchtower" --format "table {{.Names}}\t{{.Status}}\t{{.Image}}"
echo ""
echo "🔄 자동 배포 활성화됨:"
echo "  - 30초마다 $REGISTRY/$IMAGE_NAME:latest 체크"
echo "  - 새 이미지 발견 시 $CONTAINER_NAME 자동 업데이트"
echo "  - 무중단 롤링 업데이트"
echo ""
echo "📋 Watchtower 로그 확인:"
echo "  docker logs watchtower -f"
echo ""
echo "🛑 Watchtower 중지:"
echo "  docker stop watchtower && docker rm watchtower"