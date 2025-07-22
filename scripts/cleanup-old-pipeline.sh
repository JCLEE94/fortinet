#!/bin/bash

# cleanup-old-pipeline.sh - Remove legacy pipeline components after GitOps migration
# This script safely removes old CI/CD components that are no longer needed

set -e

echo "🧹 GitOps Migration Cleanup Script"
echo "=================================="
echo "This script will remove legacy pipeline components"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check if resource exists
check_resource() {
    local resource_type=$1
    local resource_name=$2
    local namespace=$3
    
    if [ -n "$namespace" ]; then
        kubectl get "$resource_type" "$resource_name" -n "$namespace" &>/dev/null
    else
        kubectl get "$resource_type" "$resource_name" &>/dev/null
    fi
}

# Function to delete resource
delete_resource() {
    local resource_type=$1
    local resource_name=$2
    local namespace=$3
    
    echo -n "  Deleting $resource_type/$resource_name... "
    
    if [ -n "$namespace" ]; then
        if kubectl delete "$resource_type" "$resource_name" -n "$namespace" 2>/dev/null; then
            echo -e "${GREEN}✓${NC}"
        else
            echo -e "${YELLOW}Not found${NC}"
        fi
    else
        if kubectl delete "$resource_type" "$resource_name" 2>/dev/null; then
            echo -e "${GREEN}✓${NC}"
        else
            echo -e "${YELLOW}Not found${NC}"
        fi
    fi
}

# Confirmation prompt
echo -e "${YELLOW}⚠️  Warning: This will remove legacy pipeline components${NC}"
echo "Components to be removed:"
echo "- Old ArgoCD applications (if any)"
echo "- Legacy image updater configs"
echo "- Unused secrets"
echo "- Old GitHub workflows (backup only)"
echo ""
read -p "Continue with cleanup? (y/N) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cleanup cancelled."
    exit 0
fi

echo ""
echo "📋 Starting cleanup process..."
echo ""

# 1. Remove old ArgoCD applications
echo "1️⃣ Checking for legacy ArgoCD applications..."
OLD_APPS=("fortinet-old" "fortinet-legacy" "fortinet-basic")
for app in "${OLD_APPS[@]}"; do
    if argocd app get "$app" &>/dev/null; then
        echo -e "  Found legacy app: ${YELLOW}$app${NC}"
        argocd app delete "$app" --cascade --yes
        echo -e "  ${GREEN}✓ Deleted${NC}"
    fi
done

# 2. Remove old image updater annotations
echo ""
echo "2️⃣ Checking for legacy image updater configs..."
# Check if old fortinet app has legacy annotations
if kubectl get application fortinet -n argocd -o yaml 2>/dev/null | grep -q "argocd-image-updater.argoproj.io/image-list"; then
    if ! kubectl get application fortinet -n argocd -o yaml | grep -q "registry-credentials"; then
        echo -e "  ${YELLOW}Legacy image updater config detected${NC}"
        echo "  Please manually update ArgoCD application annotations"
    fi
fi

# 3. Remove unused secrets
echo ""
echo "3️⃣ Checking for unused secrets..."
OLD_SECRETS=("registry-noauth-secret" "fortinet-registry-old" "docker-registry-secret")
for secret in "${OLD_SECRETS[@]}"; do
    delete_resource "secret" "$secret" "fortinet"
done

# 4. Backup old GitHub workflows
echo ""
echo "4️⃣ Backing up old GitHub workflows..."
OLD_WORKFLOWS=(
    ".github/workflows/ci-cd.yml"
    ".github/workflows/docker-build.yml"
    ".github/workflows/deploy.yml"
)

BACKUP_DIR="backup/old-workflows-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$BACKUP_DIR"

for workflow in "${OLD_WORKFLOWS[@]}"; do
    if [ -f "$workflow" ]; then
        echo -e "  Backing up: ${YELLOW}$workflow${NC}"
        cp "$workflow" "$BACKUP_DIR/"
        echo -e "  ${GREEN}✓ Backed up${NC}"
    fi
done

if [ -d "$BACKUP_DIR" ] && [ "$(ls -A $BACKUP_DIR)" ]; then
    echo -e "  Backups saved to: ${GREEN}$BACKUP_DIR${NC}"
fi

# 5. Clean up old kustomization files
echo ""
echo "5️⃣ Checking for old kustomization files..."
OLD_KUSTOMIZATION=(
    "k8s/base/kustomization.yaml.bak"
    "k8s/overlays/production/kustomization.yaml.old"
)

for file in "${OLD_KUSTOMIZATION[@]}"; do
    if [ -f "$file" ]; then
        echo -e "  Removing: ${YELLOW}$file${NC}"
        rm -f "$file"
        echo -e "  ${GREEN}✓ Removed${NC}"
    fi
done

# 6. Clean up Docker registry
echo ""
echo "6️⃣ Cleaning up Docker registry..."
echo "  Note: Old images will be garbage collected automatically"
echo "  Current images:"
curl -s https://registry.jclee.me/v2/fortinet/tags/list 2>/dev/null | jq -r '.tags[]' 2>/dev/null | tail -5 || echo "  Unable to list tags"

# 7. Remove old deployment scripts
echo ""
echo "7️⃣ Backing up old deployment scripts..."
OLD_SCRIPTS=(
    "scripts/deploy-old.sh"
    "scripts/build-and-push.sh"
    "scripts/update-image.sh"
)

for script in "${OLD_SCRIPTS[@]}"; do
    if [ -f "$script" ]; then
        echo -e "  Moving to backup: ${YELLOW}$script${NC}"
        mv "$script" "$BACKUP_DIR/" 2>/dev/null || true
        echo -e "  ${GREEN}✓ Moved${NC}"
    fi
done

# 8. Clean up ArgoCD resources
echo ""
echo "8️⃣ Optimizing ArgoCD resources..."
# Remove old app projects
OLD_PROJECTS=("fortinet-legacy" "default")
for proj in "${OLD_PROJECTS[@]}"; do
    if [ "$proj" != "default" ]; then  # Don't delete default project
        if argocd proj get "$proj" &>/dev/null; then
            echo -e "  Removing project: ${YELLOW}$proj${NC}"
            argocd proj delete "$proj" -y
            echo -e "  ${GREEN}✓ Deleted${NC}"
        fi
    fi
done

# 9. Final validation
echo ""
echo "9️⃣ Running final validation..."
echo -n "  Checking current ArgoCD app... "
if argocd app get fortinet &>/dev/null; then
    echo -e "${GREEN}✓ Active${NC}"
else
    echo -e "${RED}✗ Not found${NC}"
fi

echo -n "  Checking registry secret... "
if kubectl get secret registry-credentials -n fortinet &>/dev/null; then
    echo -e "${GREEN}✓ Present${NC}"
else
    echo -e "${RED}✗ Missing${NC}"
fi

echo -n "  Checking application health... "
if curl -s https://fortinet.jclee.me/api/health | grep -q "healthy"; then
    echo -e "${GREEN}✓ Healthy${NC}"
else
    echo -e "${YELLOW}⚠ Check manually${NC}"
fi

# Summary
echo ""
echo "🎉 Cleanup Summary"
echo "=================="
echo -e "${GREEN}✓${NC} Legacy components removed"
echo -e "${GREEN}✓${NC} Backups created in: $BACKUP_DIR"
echo -e "${GREEN}✓${NC} GitOps pipeline is now the only deployment method"
echo ""
echo "📝 Next steps:"
echo "1. Review and commit these changes:"
echo "   git add -A"
echo "   git commit -m 'chore: remove legacy pipeline components'"
echo "   git push origin master"
echo ""
echo "2. Monitor the deployment:"
echo "   argocd app get fortinet --refresh"
echo ""
echo "3. Delete backups when confident:"
echo "   rm -rf $BACKUP_DIR"
echo ""
echo -e "${GREEN}✅ Cleanup complete!${NC}"