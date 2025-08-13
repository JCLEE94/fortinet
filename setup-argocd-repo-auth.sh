#!/bin/bash

# ArgoCD Repository Authentication Setup Script
# This script helps configure repository credentials for ArgoCD

echo "ArgoCD Repository Authentication Setup"
echo "======================================"
echo ""

# Check if ArgoCD is logged in
if ! argocd account get-user-info &>/dev/null; then
    echo "❌ Please login to ArgoCD first:"
    echo "   argocd login argo.jclee.me"
    exit 1
fi

echo "✅ ArgoCD login verified"
echo ""

# List current repositories
echo "Current repositories:"
argocd repo list
echo ""

# Function to add repository with credentials
add_repo_with_creds() {
    local repo_url=$1
    local username=$2
    local token=$3
    
    echo "Adding repository: $repo_url"
    
    # Remove existing repo if present
    argocd repo rm "$repo_url" 2>/dev/null
    
    # Add repository with credentials
    if [ -n "$token" ]; then
        argocd repo add "$repo_url" \
            --username "$username" \
            --password "$token" \
            --insecure-skip-server-verification=false
    else
        argocd repo add "$repo_url"
    fi
    
    if [ $? -eq 0 ]; then
        echo "✅ Repository added successfully"
    else
        echo "❌ Failed to add repository"
        return 1
    fi
}

# Check for GitHub token
if [ -z "$GITHUB_TOKEN" ]; then
    echo "⚠️  No GITHUB_TOKEN environment variable found"
    echo ""
    echo "To create a GitHub Personal Access Token:"
    echo "1. Go to https://github.com/settings/tokens"
    echo "2. Click 'Generate new token (classic)'"
    echo "3. Give it a name (e.g., 'ArgoCD Access')"
    echo "4. Select scopes: 'repo' (full control of private repositories)"
    echo "5. Generate token and copy it"
    echo ""
    read -p "Enter your GitHub username: " github_username
    read -s -p "Enter your GitHub token: " github_token
    echo ""
else
    github_username=${GITHUB_USERNAME:-"JCLEE94"}
    github_token=$GITHUB_TOKEN
    echo "Using GITHUB_TOKEN from environment"
fi

# Add/Update repositories
repositories=(
    "https://github.com/JCLEE94/fortinet.git"
    "https://github.com/JCLEE94/safework.git"
    "https://github.com/JCLEE94/blacklist.git"
)

echo ""
echo "Configuring repositories..."
echo ""

for repo in "${repositories[@]}"; do
    add_repo_with_creds "$repo" "$github_username" "$github_token"
    echo ""
done

# Verify all repositories
echo "Final repository status:"
argocd repo list
echo ""

# Test repository access
echo "Testing repository access..."
for repo in "${repositories[@]}"; do
    echo -n "Testing $repo ... "
    if argocd repo get "$repo" | grep -q "Successful"; then
        echo "✅ OK"
    else
        echo "❌ Failed"
    fi
done

echo ""
echo "Repository authentication setup complete!"
echo ""
echo "Tips:"
echo "- To save credentials permanently, export GITHUB_TOKEN in your ~/.bashrc"
echo "- For private repos, ensure your token has 'repo' scope"
echo "- To update credentials, run this script again"