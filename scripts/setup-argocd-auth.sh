#!/bin/bash

# ArgoCD Authentication Setup Script
# This script helps set up ArgoCD authentication for GitHub Actions

set -e

echo "🔐 ArgoCD Authentication Setup"
echo "=============================="

# Configuration
ARGOCD_SERVER="${ARGO_HOST:-https://argo.jclee.me}"
ARGOCD_USER="${ARGO_admin:-admin}"
ARGOCD_PASS="${ARGO_password:-bingogo1}"

# Generate ArgoCD token
echo "📋 Generating ArgoCD API Token..."
echo ""
echo "Run this command to generate a new token:"
echo "argocd login argo.jclee.me --username admin --password bingogo1 --insecure --grpc-web"
echo "argocd account generate-token --account admin --grpc-web"
echo ""
echo "Then add these secrets to your GitHub repository:"
echo "1. Go to: https://github.com/JCLEE94/fortinet/settings/secrets/actions"
echo "2. Add/Update these secrets:"
echo "   - ARGOCD_AUTH_TOKEN: <paste the generated token>"
echo "   - ARGOCD_PASSWORD: bingogo1"
echo ""
echo "3. Ensure these secrets are also set:"
echo "   - REGISTRY_USERNAME: qws9411"
echo "   - REGISTRY_PASSWORD: <your registry password>"
echo ""

# Show current ArgoCD token (for this session)
echo "📌 Current session token (generated now):"
argocd account generate-token --account admin --grpc-web 2>/dev/null || echo "Please login first with: argocd login argo.jclee.me --username admin --password bingogo1 --insecure --grpc-web"

echo ""
echo "✅ Setup instructions complete!"
echo ""
echo "🔗 Quick Links:"
echo "- GitHub Secrets: https://github.com/JCLEE94/fortinet/settings/secrets/actions"
echo "- ArgoCD Dashboard: https://argo.jclee.me"
echo "- Application: https://fortinet.jclee.me"