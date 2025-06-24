#!/bin/bash
# GitLab CI/CD 로컬 테스트 스크립트
# GitLab Runner 없이 CI/CD 파이프라인을 로컬에서 테스트

echo "=== GitLab CI/CD 로컬 테스트 ==="
echo ""

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 변수 설정
export APP_MODE="test"
export OFFLINE_MODE="true"
export DOCKER_REGISTRY="localhost"
export DOCKER_IMAGE="fortigate-nextrade:latest"

# Stage 1: Validate
echo -e "${BLUE}[Stage 1/4] Validate - 코드 품질 검사${NC}"
echo "----------------------------------------"

echo "• Black 코드 포맷 검사..."
if command -v black &> /dev/null; then
    black --check src/ 2>/dev/null && echo -e "${GREEN}✓ 코드 포맷 정상${NC}" || echo -e "${YELLOW}⚠ 코드 포맷 필요 (black src/)${NC}"
else
    echo -e "${YELLOW}⚠ Black이 설치되지 않음${NC}"
fi

echo ""

# Stage 2: Build
echo -e "${BLUE}[Stage 2/4] Build - Docker 이미지 빌드${NC}"
echo "----------------------------------------"

if [[ -f "Dockerfile.offline" ]]; then
    echo "• Docker 이미지 빌드 중..."
    if docker build -f Dockerfile.offline -t ${DOCKER_REGISTRY}/${DOCKER_IMAGE} . ; then
        echo -e "${GREEN}✓ Docker 이미지 빌드 성공${NC}"
    else
        echo -e "${RED}✗ Docker 이미지 빌드 실패${NC}"
        exit 1
    fi
else
    echo -e "${RED}✗ Dockerfile.offline 파일이 없습니다${NC}"
    exit 1
fi

echo ""

# Stage 3: Test
echo -e "${BLUE}[Stage 3/4] Test - Mock FortiGate 테스트${NC}"
echo "----------------------------------------"

# 기존 컨테이너 정리
echo "• 기존 테스트 컨테이너 정리..."
docker stop test-fortigate 2>/dev/null
docker rm test-fortigate 2>/dev/null

# 테스트 컨테이너 실행
echo "• 테스트 컨테이너 시작..."
docker run -d --name test-fortigate -p 8888:7777 -e APP_MODE=test ${DOCKER_REGISTRY}/${DOCKER_IMAGE}

# 서비스 시작 대기
echo "• 서비스 시작 대기 (10초)..."
sleep 10

# API 테스트
echo "• API 엔드포인트 테스트..."

# 1. 시스템 상태 확인
if curl -s http://localhost:8888/api/settings | jq -e '.app_mode == "test"' > /dev/null; then
    echo -e "${GREEN}  ✓ 설정 API 정상${NC}"
else
    echo -e "${RED}  ✗ 설정 API 실패${NC}"
fi

# 2. Mock FortiGate 테스트
PACKET_TEST=$(curl -s -X POST http://localhost:8888/api/fortimanager/analyze-packet-path \
    -H "Content-Type: application/json" \
    -d '{"src_ip":"192.168.1.100","dst_ip":"172.16.10.100","port":80,"protocol":"tcp"}' | jq -r '.status')

if [[ "$PACKET_TEST" == "allowed" ]]; then
    echo -e "${GREEN}  ✓ 패킷 분석 API 정상${NC}"
else
    echo -e "${RED}  ✗ 패킷 분석 API 실패${NC}"
fi

# 3. 정책 목록 확인
POLICY_COUNT=$(curl -s http://localhost:8888/api/fortimanager/policies | jq '.policies | length')
if [[ "$POLICY_COUNT" -gt 0 ]]; then
    echo -e "${GREEN}  ✓ 정책 조회 API 정상 (${POLICY_COUNT}개 정책)${NC}"
else
    echo -e "${RED}  ✗ 정책 조회 API 실패${NC}"
fi

# 테스트 컨테이너 정리
echo ""
echo "• 테스트 컨테이너 정리..."
docker stop test-fortigate
docker rm test-fortigate

echo ""

# Stage 4: Package
echo -e "${BLUE}[Stage 4/4] Package - 오프라인 패키지 생성${NC}"
echo "----------------------------------------"

if [[ -f "create-offline-package.sh" ]]; then
    echo "• 오프라인 패키지 생성 중..."
    if ./create-offline-package.sh; then
        echo -e "${GREEN}✓ 오프라인 패키지 생성 성공${NC}"
        ls -lh fortinet-offline-deploy-*.tar.gz | tail -1
    else
        echo -e "${RED}✗ 오프라인 패키지 생성 실패${NC}"
    fi
else
    echo -e "${YELLOW}⚠ create-offline-package.sh 파일이 없습니다${NC}"
fi

echo ""
echo -e "${GREEN}=== 로컬 CI/CD 테스트 완료 ===${NC}"
echo ""
echo "GitLab CI/CD 없이도 다음 작업이 가능합니다:"
echo "1. 코드 품질 검사: black src/ && flake8 src/"
echo "2. Docker 빌드: docker build -f Dockerfile.offline -t fortigate-nextrade ."
echo "3. 로컬 실행: docker run -d -p 7777:7777 -e APP_MODE=test fortigate-nextrade"
echo "4. 패키지 생성: ./create-offline-package.sh"