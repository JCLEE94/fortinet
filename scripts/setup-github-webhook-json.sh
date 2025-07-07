#!/bin/bash

# GitHub Webhook 설정 스크립트
REPO_OWNER="JCLEE94"
REPO_NAME="fortinet"
ARGOCD_URL="https://argo.jclee.me"
WEBHOOK_SECRET="fortinet-webhook-secret-$(date +%s)"

echo "🔗 GitHub Webhook 설정 중..."

# 1. ArgoCD Webhook URL 확인
WEBHOOK_URL="${ARGOCD_URL}/api/webhook"
echo "Webhook URL: $WEBHOOK_URL"

# 2. GitHub에 Webhook 생성
echo "📝 GitHub Webhook 생성..."

WEBHOOK_JSON=$(cat <<EOF
{
  "name": "web",
  "active": true,
  "events": ["push", "pull_request"],
  "config": {
    "url": "${WEBHOOK_URL}",
    "content_type": "json",
    "insecure_ssl": "1",
    "secret": "${WEBHOOK_SECRET}"
  }
}
EOF
)

echo "$WEBHOOK_JSON" | gh api repos/$REPO_OWNER/$REPO_NAME/hooks \
  --method POST \
  --input -

if [ $? -eq 0 ]; then
    echo "✅ GitHub Webhook 생성 완료!"
    echo ""
    echo "📋 Webhook 정보:"
    echo "   URL: $WEBHOOK_URL"
    echo "   Secret: $WEBHOOK_SECRET"
else
    echo "❌ Webhook 생성 실패!"
fi

# 3. 현재 Webhook 목록 확인
echo ""
echo "📋 현재 설정된 Webhook 목록:"
gh api repos/$REPO_OWNER/$REPO_NAME/hooks --jq '.[] | {id: .id, url: .config.url, active: .active}'