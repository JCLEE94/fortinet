#!/bin/bash

# Self-hosted Runner Setup Script
# This script prepares the self-hosted runner environment for ArgoCD deployment

set -e

echo "🏃 Self-hosted Runner Environment Setup"
echo "======================================"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to install ArgoCD CLI
install_argocd_cli() {
    echo -e "${YELLOW}📦 Installing ArgoCD CLI...${NC}"
    
    # Get latest version
    VERSION=$(curl -s https://api.github.com/repos/argoproj/argo-cd/releases/latest | grep '"tag_name"' | sed -E 's/.*"([^"]+)".*/\1/')
    echo "Latest ArgoCD version: $VERSION"
    
    # Download and install
    curl -sSL -o /tmp/argocd "https://github.com/argoproj/argo-cd/releases/download/$VERSION/argocd-linux-amd64"
    chmod +x /tmp/argocd
    
    # Try to move to /usr/local/bin with sudo, fall back to user's bin
    if sudo mv /tmp/argocd /usr/local/bin/argocd 2>/dev/null; then
        echo -e "${GREEN}✅ ArgoCD CLI installed to /usr/local/bin${NC}"
    else
        mkdir -p "$HOME/.local/bin"
        mv /tmp/argocd "$HOME/.local/bin/argocd"
        echo -e "${GREEN}✅ ArgoCD CLI installed to ~/.local/bin${NC}"
        echo -e "${YELLOW}⚠️  Add ~/.local/bin to PATH if not already done${NC}"
    fi
}

# Function to install kubectl
install_kubectl() {
    echo -e "${YELLOW}📦 Installing kubectl...${NC}"
    
    # Get latest stable version
    VERSION=$(curl -L -s https://dl.k8s.io/release/stable.txt)
    echo "Latest kubectl version: $VERSION"
    
    # Download and install
    curl -LO "https://dl.k8s.io/release/$VERSION/bin/linux/amd64/kubectl"
    chmod +x kubectl
    
    # Try to move to /usr/local/bin with sudo, fall back to user's bin
    if sudo mv kubectl /usr/local/bin/kubectl 2>/dev/null; then
        echo -e "${GREEN}✅ kubectl installed to /usr/local/bin${NC}"
    else
        mkdir -p "$HOME/.local/bin"
        mv kubectl "$HOME/.local/bin/kubectl"
        echo -e "${GREEN}✅ kubectl installed to ~/.local/bin${NC}"
        echo -e "${YELLOW}⚠️  Add ~/.local/bin to PATH if not already done${NC}"
    fi
}

# Function to install jq
install_jq() {
    echo -e "${YELLOW}📦 Installing jq...${NC}"
    
    # Download and install
    curl -L https://github.com/stedolan/jq/releases/download/jq-1.6/jq-linux64 -o /tmp/jq
    chmod +x /tmp/jq
    
    # Try to move to /usr/local/bin with sudo, fall back to user's bin
    if sudo mv /tmp/jq /usr/local/bin/jq 2>/dev/null; then
        echo -e "${GREEN}✅ jq installed to /usr/local/bin${NC}"
    else
        mkdir -p "$HOME/.local/bin"
        mv /tmp/jq "$HOME/.local/bin/jq"
        echo -e "${GREEN}✅ jq installed to ~/.local/bin${NC}"
        echo -e "${YELLOW}⚠️  Add ~/.local/bin to PATH if not already done${NC}"
    fi
}

# Main setup
echo "🔍 Checking environment..."

# Check and install ArgoCD CLI
if command_exists argocd; then
    echo -e "${GREEN}✅ ArgoCD CLI already installed${NC}"
    argocd version --client
else
    install_argocd_cli
fi

# Check and install kubectl
if command_exists kubectl; then
    echo -e "${GREEN}✅ kubectl already installed${NC}"
    kubectl version --client
else
    install_kubectl
fi

# Check and install jq
if command_exists jq; then
    echo -e "${GREEN}✅ jq already installed${NC}"
    jq --version
else
    install_jq
fi

# Check Git
if command_exists git; then
    echo -e "${GREEN}✅ Git already installed${NC}"
    git --version
else
    echo -e "${RED}❌ Git not found. Please install git${NC}"
    exit 1
fi

# Setup PATH if needed
if [[ ! "$PATH" =~ "$HOME/.local/bin" ]]; then
    echo -e "${YELLOW}📝 Adding ~/.local/bin to PATH...${NC}"
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.bashrc"
    export PATH="$HOME/.local/bin:$PATH"
fi

# Create runner work directory
echo -e "${YELLOW}📁 Setting up runner work directory...${NC}"
mkdir -p "$HOME/actions-runner/_work"

# Test ArgoCD connectivity
echo -e "${YELLOW}🔗 Testing ArgoCD connectivity...${NC}"
if curl -k -s -o /dev/null -w "%{http_code}" https://argo.jclee.me/api/version | grep -q "200"; then
    echo -e "${GREEN}✅ ArgoCD server is reachable${NC}"
else
    echo -e "${RED}❌ Cannot reach ArgoCD server${NC}"
fi

# Create environment file for runner
echo -e "${YELLOW}📝 Creating runner environment file...${NC}"
cat > "$HOME/actions-runner/.env" << EOF
# Self-hosted runner environment variables
ARGOCD_SERVER=argo.jclee.me
PATH=$HOME/.local/bin:$PATH
EOF

echo -e "${GREEN}✅ Self-hosted runner setup complete!${NC}"
echo ""
echo "📋 Next steps:"
echo "1. Ensure GitHub secrets are set:"
echo "   - ARGOCD_AUTH_TOKEN"
echo "   - ARGOCD_PASSWORD"
echo "   - REGISTRY_USERNAME"
echo "   - REGISTRY_PASSWORD"
echo ""
echo "2. If you installed tools to ~/.local/bin, restart your shell or run:"
echo "   export PATH=\"\$HOME/.local/bin:\$PATH\""
echo ""
echo "3. Test ArgoCD login:"
echo "   argocd login argo.jclee.me --username admin --password bingogo1 --insecure --grpc-web"