# ArgoCD Repository Authentication Guide

## Overview
ArgoCD needs authentication to access private GitHub repositories. This guide explains how to configure repository credentials.

## Current Repository Status

### Configured Repositories
- **fortinet**: https://github.com/JCLEE94/fortinet.git (Public - No auth needed)
- **blacklist**: https://github.com/JCLEE94/blacklist.git (Status: Check required)
- **safework**: https://github.com/JCLEE94/safework.git (Status: Authentication error)

## Authentication Methods

### 1. GitHub Personal Access Token (Recommended)

#### Create a Token
1. Visit https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Name: "ArgoCD Access"
4. Required scopes:
   - `repo` (Full control of private repositories)
   - `workflow` (Optional - for GitHub Actions)
5. Generate and copy token

#### Configure ArgoCD

##### Option A: Using the Setup Script
```bash
# Run the provided setup script
./setup-argocd-repo-auth.sh

# Follow prompts to enter:
# - GitHub username
# - GitHub token
```

##### Option B: Manual Configuration
```bash
# Add repository with credentials
argocd repo add https://github.com/JCLEE94/safework.git \
  --username JCLEE94 \
  --password <your-github-token>

# Verify access
argocd repo list
```

### 2. SSH Key Authentication

#### Generate SSH Key
```bash
# Generate new SSH key for ArgoCD
ssh-keygen -t ed25519 -f ~/.ssh/argocd_github -C "argocd@jclee.me"

# Add to GitHub account
cat ~/.ssh/argocd_github.pub
# Copy and add to https://github.com/settings/keys
```

#### Configure ArgoCD with SSH
```bash
# Add SSH repository
argocd repo add git@github.com:JCLEE94/safework.git \
  --ssh-private-key-path ~/.ssh/argocd_github
```

## Environment Variables

### Set GitHub Token Permanently
```bash
# Add to ~/.bashrc or ~/.zshrc
export GITHUB_TOKEN="ghp_your_token_here"
export GITHUB_USERNAME="JCLEE94"

# Reload shell
source ~/.bashrc
```

## ArgoCD CLI Commands

### Repository Management
```bash
# List all repositories
argocd repo list

# Add repository with token
argocd repo add <repo-url> --username <user> --password <token>

# Remove repository
argocd repo rm <repo-url>

# Get repository details
argocd repo get <repo-url>
```

### Credential Templates
```bash
# Add credential template for all GitHub repos
argocd repocreds add https://github.com/JCLEE94 \
  --username JCLEE94 \
  --password <token>

# List credential templates
argocd repocreds list

# Remove credential template
argocd repocreds rm https://github.com/JCLEE94
```

## Troubleshooting

### Common Issues

#### 1. Authentication Required Error
```
ComparisonError: authentication required: Repository not found
```
**Solution**: Add repository with valid credentials

#### 2. Token Expired
```
401 Unauthorized
```
**Solution**: Generate new token and update credentials

#### 3. Insufficient Permissions
```
403 Forbidden
```
**Solution**: Ensure token has `repo` scope

### Verify Repository Access
```bash
# Test specific repository
argocd repo get <repo-url>

# Check application sync status
argocd app get <app-name>

# Force refresh
argocd app get <app-name> --refresh
```

## Security Best Practices

1. **Use Personal Access Tokens** instead of passwords
2. **Limit token scope** to minimum required permissions
3. **Rotate tokens regularly** (every 90 days)
4. **Store tokens securely** in environment variables or secret managers
5. **Use different tokens** for different environments
6. **Enable SSO** if using GitHub Enterprise

## Quick Reference

### Check Current Authentication
```bash
# ArgoCD login status
argocd account get-user-info

# Repository status
argocd repo list

# GitHub CLI status
gh auth status
```

### Update Repository Credentials
```bash
# Remove old repo
argocd repo rm https://github.com/JCLEE94/safework.git

# Add with new credentials
argocd repo add https://github.com/JCLEE94/safework.git \
  --username JCLEE94 \
  --password <new-token>
```

## Related Documentation
- [ArgoCD Repository Docs](https://argo-cd.readthedocs.io/en/stable/user-guide/private-repositories/)
- [GitHub Personal Access Tokens](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token)
- [ArgoCD CLI Reference](https://argo-cd.readthedocs.io/en/stable/user-guide/commands/argocd/)