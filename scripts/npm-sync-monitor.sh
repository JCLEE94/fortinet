#!/bin/bash

# NPM Sync Monitoring Script
# 이 스크립트는 NPM과 Kubernetes 간의 동기화 상태를 모니터링합니다

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
NPM_URL="${NPM_URL:-http://192.168.50.215:81}"
NPM_EMAIL="${NPM_EMAIL:-admin@example.com}"
NPM_PASSWORD="${NPM_PASSWORD:-changeme}"

echo -e "${BLUE}🔍 NPM Sync Monitor${NC}"
echo "===================="
echo ""

# 1. Check NPM connectivity
echo -e "${YELLOW}1️⃣ Checking NPM connectivity...${NC}"
if curl -s -f "${NPM_URL}/api" > /dev/null; then
    echo -e "${GREEN}✅ NPM is reachable${NC}"
else
    echo -e "${RED}❌ Cannot reach NPM at ${NPM_URL}${NC}"
    exit 1
fi

# 2. Authenticate with NPM
echo -e "\n${YELLOW}2️⃣ Authenticating with NPM...${NC}"
TOKEN=$(curl -s -X POST "${NPM_URL}/api/tokens" \
    -H "Content-Type: application/json" \
    -d "{\"identity\":\"${NPM_EMAIL}\",\"secret\":\"${NPM_PASSWORD}\"}" \
    | jq -r '.token')

if [ -z "$TOKEN" ] || [ "$TOKEN" = "null" ]; then
    echo -e "${RED}❌ Authentication failed${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Authentication successful${NC}"

# 3. Get Kubernetes Ingresses with external-dns annotation
echo -e "\n${YELLOW}3️⃣ Kubernetes Ingresses with External-DNS:${NC}"
kubectl get ingress -A -o json | jq -r '
    .items[] | 
    select(.metadata.annotations."external-dns.alpha.kubernetes.io/hostname" != null) |
    [.metadata.namespace, .metadata.name, .metadata.annotations."external-dns.alpha.kubernetes.io/hostname"] |
    @tsv' | while IFS=$'\t' read -r namespace name hostname; do
    echo -e "  📌 ${BLUE}$namespace/$name${NC} → $hostname"
done

# 4. Get NPM Proxy Hosts
echo -e "\n${YELLOW}4️⃣ NPM Proxy Hosts (K8s managed):${NC}"
PROXY_HOSTS=$(curl -s -X GET "${NPM_URL}/api/nginx/proxy-hosts" \
    -H "Authorization: Bearer ${TOKEN}")

echo "$PROXY_HOSTS" | jq -r '.[] | select(.meta.k8s_managed == true or .meta.external_dns_managed == true) | 
    "\(.id)\t\(.domain_names | join(","))\t\(.forward_host):\(.forward_port)\t\(.enabled)"' | \
    while IFS=$'\t' read -r id domains target enabled; do
    if [ "$enabled" = "1" ]; then
        status="${GREEN}✅${NC}"
    else
        status="${RED}❌${NC}"
    fi
    echo -e "  $status ID:$id $domains → $target"
done

# 5. Sync Status Check
echo -e "\n${YELLOW}5️⃣ Sync Status:${NC}"

# Get all expected hosts from K8s
EXPECTED_HOSTS=$(kubectl get ingress -A -o json | jq -r '
    .items[] | 
    select(.metadata.annotations."external-dns.alpha.kubernetes.io/hostname" != null) |
    .metadata.annotations."external-dns.alpha.kubernetes.io/hostname"' | sort | uniq)

# Get all actual hosts from NPM
ACTUAL_HOSTS=$(echo "$PROXY_HOSTS" | jq -r '.[] | 
    select(.meta.k8s_managed == true or .meta.external_dns_managed == true) | 
    .domain_names[]' | sort | uniq)

# Compare
echo -e "\n  ${BLUE}Expected hosts (from K8s):${NC}"
echo "$EXPECTED_HOSTS" | while read -r host; do
    echo "    - $host"
done

echo -e "\n  ${BLUE}Actual hosts (in NPM):${NC}"
echo "$ACTUAL_HOSTS" | while read -r host; do
    echo "    - $host"
done

# Find missing hosts
MISSING=$(comm -23 <(echo "$EXPECTED_HOSTS") <(echo "$ACTUAL_HOSTS"))
if [ -n "$MISSING" ]; then
    echo -e "\n  ${RED}⚠️  Missing in NPM:${NC}"
    echo "$MISSING" | while read -r host; do
        echo "    - $host"
    done
fi

# Find extra hosts
EXTRA=$(comm -13 <(echo "$EXPECTED_HOSTS") <(echo "$ACTUAL_HOSTS"))
if [ -n "$EXTRA" ]; then
    echo -e "\n  ${YELLOW}⚠️  Extra in NPM (not in K8s):${NC}"
    echo "$EXTRA" | while read -r host; do
        echo "    - $host"
    done
fi

# 6. CronJob Status (if using simple-cronjob)
echo -e "\n${YELLOW}6️⃣ Sync Job Status:${NC}"
if kubectl get cronjob -n npm-sync npm-sync &>/dev/null; then
    LAST_SCHEDULE=$(kubectl get cronjob -n npm-sync npm-sync -o jsonpath='{.status.lastScheduleTime}')
    ACTIVE=$(kubectl get cronjob -n npm-sync npm-sync -o jsonpath='{.status.active}')
    
    echo -e "  📅 Last run: $LAST_SCHEDULE"
    if [ -n "$ACTIVE" ]; then
        echo -e "  ${GREEN}🏃 Currently running${NC}"
    fi
    
    # Check last job logs
    LAST_JOB=$(kubectl get jobs -n npm-sync --sort-by=.metadata.creationTimestamp -o name | tail -1)
    if [ -n "$LAST_JOB" ]; then
        echo -e "\n  ${BLUE}Last job logs:${NC}"
        kubectl logs -n npm-sync "$LAST_JOB" --tail=10 2>/dev/null || echo "    No logs available"
    fi
else
    echo -e "  ${YELLOW}⚠️  CronJob not found${NC}"
fi

# 7. Health Check
echo -e "\n${YELLOW}7️⃣ Application Health Check:${NC}"
for host in $EXPECTED_HOSTS; do
    echo -n "  Testing $host... "
    if curl -s -f -m 5 "http://$host/api/health" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Healthy${NC}"
    else
        echo -e "${RED}❌ Unreachable${NC}"
    fi
done

echo -e "\n${GREEN}✅ Monitoring complete!${NC}"