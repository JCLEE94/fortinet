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
gh api repos/$REPO_OWNER/$REPO_NAME/hooks \
  --method POST \
  -H "Accept: application/vnd.github+json" \
  -f "config[url]=$WEBHOOK_URL" \
  -f "config[content_type]=json" \
  -f "config[secret]=$WEBHOOK_SECRET" \
  -f "config[insecure_ssl]=1" \
  -f "events[]=push" \
  -f "events[]=pull_request" \
  --field "active=true"

if [ $? -eq 0 ]; then
    echo "✅ GitHub Webhook 생성 완료!"
    echo ""
    echo "📋 Webhook 정보:"
    echo "   URL: $WEBHOOK_URL"
    echo "   Secret: $WEBHOOK_SECRET"
    echo ""
    echo "💡 다음 단계:"
    echo "   1. ArgoCD에 Webhook Secret 설정 필요"
    echo "   2. Push 이벤트 시 즉시 동기화됨"
else
    echo "❌ Webhook 생성 실패!"
fi

# 3. 현재 Webhook 목록 확인
echo ""
echo "📋 현재 설정된 Webhook 목록:"
gh api repos/$REPO_OWNER/$REPO_NAME/hooks --jq '.[].config.url'