#!/bin/bash

# =============================================================================
# Complete Cloudflare Deployment Script
# Handles DNS registration, tunnel setup, and Kubernetes deployment
# =============================================================================

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Configuration
DOMAIN="jclee.me"
SUBDOMAIN="fortinet"
CF_API_TOKEN="19OuO8pBp83XDkJsUf2TRmDPKd6ZySIXrGJbh5Uk"
TUNNEL_TOKEN="eyJhIjoiYThkOWM2N2Y1ODZhY2RkMTVlZWJjYzY1Y2EzYWE1YmIiLCJ0IjoiOGVhNzg5MDYtMWEwNS00NGZiLWExYmItZTUxMjE3MmNiNWFiIiwicyI6Ill6RXlZVEUwWWpRdC0yZXlNUzAwWmpRMExXSTVaR0V0WkdNM09UY3pOV1ExT1RGbSJ9"

echo -e "${CYAN}╔═══════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║        FortiGate Cloudflare Complete Deployment           ║${NC}"
echo -e "${CYAN}╚═══════════════════════════════════════════════════════════╝${NC}"

# Step 1: Setup DNS
echo -e "\n${BLUE}[1/4] Setting up Cloudflare DNS...${NC}"
if [ -f "scripts/cloudflare-dns-manager.sh" ]; then
    ./scripts/cloudflare-dns-manager.sh setup --domain "$DOMAIN" --subdomain "$SUBDOMAIN"
else
    echo -e "${YELLOW}DNS manager script not found, skipping DNS setup${NC}"
fi

# Step 2: Create Kubernetes secret
echo -e "\n${BLUE}[2/4] Creating Kubernetes secret...${NC}"
kubectl create secret generic cloudflare-tunnel-token \
  --from-literal=token="$TUNNEL_TOKEN" \
  --namespace=fortinet \
  --dry-run=client -o yaml | kubectl apply -f -
echo -e "${GREEN}✓ Secret created/updated${NC}"

# Step 3: Update and apply deployment
echo -e "\n${BLUE}[3/4] Deploying to Kubernetes...${NC}"

# Ensure we're using the Cloudflare-enabled deployment
if [ -f "k8s/manifests/kustomization.yaml" ]; then
    # Backup original
    cp k8s/manifests/kustomization.yaml k8s/manifests/kustomization.yaml.bak
    
    # Update to use Cloudflare deployment
    sed -i 's/- deployment.yaml/- deployment-with-cloudflare.yaml/' k8s/manifests/kustomization.yaml
    echo -e "${GREEN}✓ Kustomization updated${NC}"
fi

# Apply deployment
kubectl apply -k k8s/manifests/
echo -e "${GREEN}✓ Kubernetes deployment applied${NC}"

# Step 4: Wait and verify
echo -e "\n${BLUE}[4/4] Verifying deployment...${NC}"

# Wait for pods
echo "Waiting for pods to be ready..."
kubectl wait --for=condition=ready pod -l app=fortinet -n fortinet --timeout=300s || {
    echo -e "${YELLOW}Warning: Pods not ready after 5 minutes${NC}"
}

# Check pod status
echo -e "\n${BLUE}Pod Status:${NC}"
kubectl get pods -n fortinet -l app=fortinet

# Check Cloudflare tunnel logs
echo -e "\n${BLUE}Cloudflare Tunnel Status:${NC}"
POD=$(kubectl get pods -n fortinet -l app=fortinet -o jsonpath="{.items[0].metadata.name}" 2>/dev/null)
if [ -n "$POD" ]; then
    kubectl logs "$POD" -c cloudflare-tunnel -n fortinet --tail=5 2>/dev/null || echo "Waiting for tunnel container..."
fi

# Final summary
echo -e "\n${GREEN}╔═══════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                  Deployment Complete!                     ║${NC}"
echo -e "${GREEN}╚═══════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "🌐 URL: ${CYAN}https://${SUBDOMAIN}.${DOMAIN}${NC}"
echo -e "📊 Status: Check deployment with:"
echo -e "   ${YELLOW}kubectl get all -n fortinet${NC}"
echo -e "   ${YELLOW}./scripts/cloudflare-dns-manager.sh verify --domain ${DOMAIN}${NC}"
echo ""
echo -e "⏱️  DNS propagation may take 1-2 minutes"
echo -e "🔍 Monitor tunnel: ${YELLOW}kubectl logs -f deployment/fortinet-app -c cloudflare-tunnel -n fortinet${NC}"