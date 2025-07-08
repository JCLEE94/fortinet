#!/bin/bash

# 빠른 Cloudflare 터널 배포 스크립트 (환경변수 사용)

set -e

# 색상
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}=== FortiGate Nextrade Cloudflare 터널 배포 ===${NC}"

# 환경변수 체크
if [ -z "$CLOUDFLARE_TUNNEL_TOKEN" ]; then
    echo -e "${RED}Error: CLOUDFLARE_TUNNEL_TOKEN 환경변수가 설정되지 않았습니다${NC}"
    echo "다음과 같이 설정하세요:"
    echo "export CLOUDFLARE_TUNNEL_TOKEN='your-tunnel-token'"
    exit 1
fi

# 1. 시크릿 생성
echo -e "${BLUE}1. Kubernetes 시크릿 생성 중...${NC}"
kubectl create secret generic cloudflare-tunnel-token \
  --from-literal=token="$CLOUDFLARE_TUNNEL_TOKEN" \
  --namespace=fortinet \
  --dry-run=client -o yaml | kubectl apply -f -

echo -e "${GREEN}✓ 시크릿 생성 완료${NC}"

# 2. Kustomization 업데이트
echo -e "${BLUE}2. Kustomization 업데이트 중...${NC}"
sed -i 's/- deployment.yaml/- deployment-with-cloudflare.yaml/' k8s/manifests/kustomization.yaml
echo -e "${GREEN}✓ Kustomization 업데이트 완료${NC}"

# 3. 배포
echo -e "${BLUE}3. Kubernetes 배포 중...${NC}"
kubectl apply -k k8s/manifests/
echo -e "${GREEN}✓ 배포 완료${NC}"

# 4. 상태 확인
echo -e "${BLUE}4. 배포 상태 확인 중...${NC}"
kubectl wait --for=condition=ready pod -l app=fortinet -n fortinet --timeout=300s

# 5. 로그 확인
echo -e "${BLUE}5. Cloudflare 터널 로그:${NC}"
POD=$(kubectl get pods -n fortinet -l app=fortinet -o jsonpath="{.items[0].metadata.name}")
kubectl logs $POD -c cloudflare-tunnel -n fortinet --tail=10

echo -e "${GREEN}=== 배포 완료! ===${NC}"
echo -e "${YELLOW}Cloudflare 대시보드에서 터널 상태를 확인하세요.${NC}"