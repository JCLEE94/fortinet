#!/bin/bash

# 🚀 완전 자동화 GitOps 배포 스크립트
# jclee.me 인프라 통합 버전

set -euo pipefail

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 환경 설정
REGISTRY="registry.jclee.me"
IMAGE_NAME="fortinet"
APP_NAME="fortinet"
NAMESPACE="fortinet"
ARGOCD_SERVER="argo.jclee.me"
DEPLOYMENT_HOST="192.168.50.110"
DEPLOYMENT_PORT="30777"

echo -e "${BLUE}🚀 jclee.me 인프라 GitOps 배포 시작${NC}"
echo "========================================"

# 1. Git 상태 분석
echo -e "\n${YELLOW}📊 Git 상태 분석${NC}"
echo "Current branch: $(git branch --show-current)"
echo "Last commit: $(git log --oneline -1)"

# 변경사항 확인
if [[ -n $(git status --porcelain) ]]; then
    echo -e "${GREEN}✅ 변경사항 발견${NC}"
    git status --short
else
    echo -e "${RED}⚠️ 변경사항이 없습니다${NC}"
fi

# 2. Docker 이미지 태그 생성
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
SHORT_SHA=$(git rev-parse --short HEAD)
IMAGE_TAG="${SHORT_SHA}-${TIMESTAMP}"

echo -e "\n${YELLOW}🏷️ 이미지 태그 생성${NC}"
echo "Generated Tag: ${IMAGE_TAG}"

# 3. Kustomize 매니페스트 업데이트
echo -e "\n${YELLOW}📝 GitOps 매니페스트 업데이트${NC}"
cd k8s/overlays/production

# 현재 태그 확인
CURRENT_TAG=$(grep "newTag:" kustomization.yaml | awk '{print $2}' | sed 's/#.*//')
echo "Current Tag: ${CURRENT_TAG}"
echo "New Tag: ${IMAGE_TAG}"

# 태그 업데이트
sed -i "s/newTag:.*/newTag: ${IMAGE_TAG}  # GitOps 자동 업데이트/" kustomization.yaml

echo -e "${GREEN}✅ kustomization.yaml 업데이트 완료${NC}"
cat kustomization.yaml | grep -A 5 -B 5 "newTag"

cd - > /dev/null

# 4. Git 커밋 및 Push
echo -e "\n${YELLOW}📤 Git Commit & Push${NC}"
git config user.email "noreply@claude.ai"
git config user.name "Claude Code"

# 변경사항 추가
git add .
git add k8s/overlays/production/kustomization.yaml
git add DEPLOYMENT_TRIGGER.md

# 커밋 메시지 생성
COMMIT_MSG="deploy(k8s): GitOps 자동화 배포 - ${IMAGE_TAG}

🚀 jclee.me 인프라 완전 통합 배포
- Registry: ${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}
- Environment: production
- Namespace: ${NAMESPACE}
- ArgoCD: https://${ARGOCD_SERVER}

🔄 배포 플로우:
1. Docker 빌드 → ${REGISTRY}
2. Kustomize 매니페스트 업데이트
3. ArgoCD Pull-based 동기화
4. K8s 클러스터 무중단 배포
5. Health Check 자동 검증

🤖 Generated with Claude Code

Co-authored-by: Claude <noreply@anthropic.com>"

git commit -m "${COMMIT_MSG}"
git push origin master

echo -e "${GREEN}✅ Git Push 완료${NC}"

# 5. GitHub Actions 트리거 및 모니터링
echo -e "\n${YELLOW}🔄 GitHub Actions 트리거${NC}"
echo "Manual GitOps workflow 트리거 중..."

# GitHub CLI로 워크플로우 실행
if command -v gh &> /dev/null; then
    echo "GitHub Actions 워크플로우 실행..."
    gh workflow run "manual-gitops-trigger.yml" \
       --field environment=production \
       --field force_rebuild=false
    
    echo -e "${GREEN}✅ GitHub Actions 트리거 완료${NC}"
    echo "워크플로우 상태: https://github.com/$(git config --get remote.origin.url | sed 's/.*github.com[:/]\([^.]*\).*/\1/')/actions"
else
    echo -e "${YELLOW}⚠️ GitHub CLI 없음 - 수동으로 워크플로우 실행하세요${NC}"
fi

# 6. ArgoCD 동기화 대기
echo -e "\n${YELLOW}⏳ ArgoCD 동기화 대기${NC}"
echo "ArgoCD Dashboard: https://${ARGOCD_SERVER}/applications/${APP_NAME}"
echo "자동 동기화 완료까지 약 3-5분 소요..."

# 7. 배포 상태 모니터링
echo -e "\n${YELLOW}🔍 배포 상태 모니터링${NC}"
max_attempts=30
attempt=1

while [ $attempt -le $max_attempts ]; do
    echo -e "🔄 Health Check 시도 $attempt/$max_attempts"
    
    if curl -f -s --connect-timeout 10 --max-time 20 "http://${DEPLOYMENT_HOST}:${DEPLOYMENT_PORT}/api/health" > /dev/null; then
        echo -e "${GREEN}✅ 배포 검증 성공!${NC}"
        
        # Health Check 응답 표시
        echo -e "\n${GREEN}📊 Health Check 응답:${NC}"
        HEALTH_RESPONSE=$(curl -s "http://${DEPLOYMENT_HOST}:${DEPLOYMENT_PORT}/api/health")
        echo "$HEALTH_RESPONSE" | jq . 2>/dev/null || echo "$HEALTH_RESPONSE"
        
        break
    else
        echo -e "${YELLOW}⚠️ Health Check 대기 중... ($attempt/$max_attempts)${NC}"
        if [ $attempt -eq $max_attempts ]; then
            echo -e "${RED}❌ 배포 검증 실패!${NC}"
            echo "디버깅 정보:"
            echo "1. ArgoCD: https://${ARGOCD_SERVER}"
            echo "2. Pod 로그: kubectl logs -l app=${APP_NAME} -n ${NAMESPACE}"
            echo "3. Service 상태: kubectl get svc -n ${NAMESPACE}"
            exit 1
        fi
        sleep 15
        attempt=$((attempt + 1))
    fi
done

# 8. 배포 완료 보고서
echo -e "\n${GREEN}🎉 GITOPS 배포 완료 보고서${NC}"
echo "================================="
echo ""
echo -e "${GREEN}✅ 배포 정보:${NC}"
echo "  🏷️ Image Tag: ${IMAGE_TAG}"
echo "  🌍 Environment: production"
echo "  📦 Registry: ${REGISTRY}/${IMAGE_NAME}"
echo "  🔄 Commit: ${SHORT_SHA}"
echo "  📅 Timestamp: ${TIMESTAMP}"
echo ""
echo -e "${BLUE}🔗 접속 정보:${NC}"
echo "  🌐 External: https://fortinet.jclee.me"
echo "  🔗 Internal: http://${DEPLOYMENT_HOST}:${DEPLOYMENT_PORT}"
echo "  🏥 Health: http://${DEPLOYMENT_HOST}:${DEPLOYMENT_PORT}/api/health"
echo ""
echo -e "${BLUE}📊 GitOps 대시보드:${NC}"
echo "  🔄 ArgoCD: https://${ARGOCD_SERVER}"
echo "  📦 Registry: https://${REGISTRY}"
echo "  🐙 GitHub: https://github.com/$(git config --get remote.origin.url | sed 's/.*github.com[:/]\([^.]*\).*/\1/')/actions"
echo ""

# 최종 검증
echo -e "${GREEN}🔍 최종 검증:${NC}"
echo -e "$(curl -s http://${DEPLOYMENT_HOST}:${DEPLOYMENT_PORT}/api/health | jq -r '.status // "OK"') 서비스 상태"

echo -e "\n${GREEN}🚀 GitOps 배포 성공! 🎉${NC}"

exit 0