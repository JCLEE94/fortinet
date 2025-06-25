#!/bin/bash
# =============================================================================
# FortiGate Nextrade - CI/CD Pipeline Validation Script
# =============================================================================

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
GITHUB_REPO="JCLEE94/fortinet"
DOCKER_REGISTRY="registry.jclee.me"
DOCKER_IMAGE_NAME="fortinet"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Logging functions
log() { echo -e "${BLUE}[INFO]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1" >&2; }
success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
header() { echo -e "${CYAN}=== $1 ===${NC}"; }

# Help function
show_help() {
    cat << EOF
FortiGate Nextrade CI/CD Validation Script

Usage: $0 [OPTIONS] [CHECK]

Available Checks:
    all             Run all validations (default)
    github          GitHub Actions workflow validation
    docker          Docker build and registry validation
    secrets         GitHub secrets validation
    deployment      Deployment process validation
    pipeline        Full pipeline simulation
    troubleshoot    Common CI/CD issues diagnosis

Options:
    -h, --help      Show this help message
    -v, --verbose   Verbose output
    --fix           Attempt to fix issues automatically
    --simulate      Simulate pipeline without actual deployment

Examples:
    $0                      # Run all validations
    $0 github docker        # Check GitHub and Docker only
    $0 --simulate pipeline  # Simulate full pipeline
    $0 troubleshoot         # Diagnose common issues
EOF
}

# Global variables
VERBOSE=false
AUTO_FIX=false
SIMULATE=false
ISSUES_FOUND=0

# Parse arguments
CHECKS=()
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        --fix)
            AUTO_FIX=true
            shift
            ;;
        --simulate)
            SIMULATE=true
            shift
            ;;
        all|github|docker|secrets|deployment|pipeline|troubleshoot)
            CHECKS+=("$1")
            shift
            ;;
        *)
            error "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Default to all checks
if [[ ${#CHECKS[@]} -eq 0 ]]; then
    CHECKS=("all")
fi

cd "$PROJECT_DIR"

# Issue tracking
add_issue() {
    local severity="$1"
    local component="$2"
    local description="$3"
    local fix="${4:-}"
    
    ((ISSUES_FOUND++))
    
    case "$severity" in
        "ERROR") error "[$component] $description" ;;
        "WARNING") warning "[$component] $description" ;;
        "INFO") log "[$component] $description" ;;
    esac
    
    if [[ -n "$fix" ]] && [[ "$AUTO_FIX" == true ]]; then
        log "Attempting fix: $fix"
        if eval "$fix"; then
            success "Issue fixed automatically"
        else
            error "Auto-fix failed"
        fi
    fi
}

# GitHub Actions validation
check_github() {
    header "GitHub Actions Workflow Validation"
    
    # Check workflow file exists
    if [[ ! -f ".github/workflows/ci-cd.yml" ]]; then
        add_issue "ERROR" "GITHUB" "CI/CD workflow file not found" "mkdir -p .github/workflows && cp scripts/ci-cd.yml.template .github/workflows/ci-cd.yml"
        return 1
    fi
    
    success "GitHub Actions workflow file found"
    
    # Validate workflow syntax
    if command -v yq &> /dev/null; then
        if yq eval '.jobs' .github/workflows/ci-cd.yml &> /dev/null; then
            success "Workflow YAML syntax is valid"
        else
            add_issue "ERROR" "GITHUB" "Invalid YAML syntax in workflow file"
        fi
    else
        warning "yq not available - cannot validate YAML syntax"
    fi
    
    # Check required jobs
    local required_jobs=("test" "security" "build")
    for job in "${required_jobs[@]}"; do
        if grep -q "^  $job:" .github/workflows/ci-cd.yml; then
            success "Job '$job' found in workflow"
        else
            add_issue "WARNING" "GITHUB" "Job '$job' not found in workflow"
        fi
    done
    
    # Check environment variables
    local required_env_vars=("REGISTRY" "IMAGE_NAME" "PYTHON_VERSION")
    for var in "${required_env_vars[@]}"; do
        if grep -q "$var:" .github/workflows/ci-cd.yml; then
            success "Environment variable '$var' configured"
        else
            add_issue "WARNING" "GITHUB" "Environment variable '$var' not configured"
        fi
    done
    
    # Check for hardcoded values
    if grep -E "(registry\.jclee\.me|fortinet|qws941|bingogo1)" .github/workflows/ci-cd.yml &> /dev/null; then
        add_issue "WARNING" "GITHUB" "Potential hardcoded values found in workflow"
    fi
    
    # Check GitHub CLI availability
    if command -v gh &> /dev/null; then
        success "GitHub CLI is available"
        
        # Check authentication
        if gh auth status &> /dev/null; then
            success "GitHub CLI is authenticated"
        else
            add_issue "WARNING" "GITHUB" "GitHub CLI not authenticated" "gh auth login"
        fi
    else
        add_issue "WARNING" "GITHUB" "GitHub CLI not available" "curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo gpg --dearmor -o /usr/share/keyrings/githubcli-archive-keyring.gpg"
    fi
}

# Docker validation
check_docker() {
    header "Docker Build and Registry Validation"
    
    # Check Dockerfile exists
    if [[ ! -f "Dockerfile.production" ]]; then
        add_issue "ERROR" "DOCKER" "Production Dockerfile not found"
        return 1
    fi
    
    success "Production Dockerfile found"
    
    # Validate Dockerfile syntax
    if docker build --dry-run -f Dockerfile.production . &> /dev/null; then
        success "Dockerfile syntax is valid"
    else
        add_issue "ERROR" "DOCKER" "Dockerfile syntax errors"
    fi
    
    # Check for hardcoded values in Dockerfile
    if grep -E "(registry\.jclee\.me|7777|fortinet)" Dockerfile.production | grep -v "ENV\|ARG" &> /dev/null; then
        add_issue "WARNING" "DOCKER" "Potential hardcoded values in Dockerfile"
    fi
    
    # Test registry connectivity
    log "Testing Docker registry connectivity..."
    if ping -c 1 "$(echo $DOCKER_REGISTRY | sed 's/.*\/\///' | cut -d'/' -f1)" &> /dev/null; then
        success "Registry host is reachable"
    else
        add_issue "ERROR" "DOCKER" "Cannot reach registry host: $DOCKER_REGISTRY"
    fi
    
    # Test registry authentication
    if [[ -n "${DOCKER_USERNAME:-}" ]] && [[ -n "${DOCKER_PASSWORD:-}" ]]; then
        if echo "$DOCKER_PASSWORD" | docker login "$DOCKER_REGISTRY" -u "$DOCKER_USERNAME" --password-stdin &> /dev/null; then
            success "Registry authentication successful"
            docker logout "$DOCKER_REGISTRY" &> /dev/null
        else
            add_issue "ERROR" "DOCKER" "Registry authentication failed"
        fi
    else
        add_issue "WARNING" "DOCKER" "Docker credentials not available in environment"
    fi
    
    # Check Docker Compose file
    if [[ -f "docker-compose.production.yml" ]]; then
        success "Production Docker Compose file found"
        
        # Validate compose syntax
        if docker-compose -f docker-compose.production.yml config &> /dev/null; then
            success "Docker Compose syntax is valid"
        else
            add_issue "ERROR" "DOCKER" "Docker Compose syntax errors"
        fi
    else
        add_issue "ERROR" "DOCKER" "docker-compose.production.yml not found"
    fi
}

# GitHub secrets validation
check_secrets() {
    header "GitHub Secrets Validation"
    
    if ! command -v gh &> /dev/null; then
        add_issue "ERROR" "SECRETS" "GitHub CLI not available for secrets check"
        return 1
    fi
    
    if ! gh auth status &> /dev/null; then
        add_issue "ERROR" "SECRETS" "GitHub CLI not authenticated"
        return 1
    fi
    
    # Required secrets
    local required_secrets=(
        "DOCKER_USERNAME"
        "DOCKER_PASSWORD"
    )
    
    log "Checking required GitHub secrets..."
    for secret in "${required_secrets[@]}"; do
        if gh secret list | grep -q "$secret"; then
            success "Secret '$secret' is configured"
        else
            add_issue "ERROR" "SECRETS" "Required secret '$secret' not found" "gh secret set $secret"
        fi
    done
    
    # Optional but recommended secrets
    local optional_secrets=(
        "DEPLOY_SSH_KEY"
        "DEPLOY_HOST"
        "DEPLOY_USER"
    )
    
    log "Checking optional GitHub secrets..."
    for secret in "${optional_secrets[@]}"; do
        if gh secret list | grep -q "$secret"; then
            success "Optional secret '$secret' is configured"
        else
            warning "Optional secret '$secret' not configured"
        fi
    done
    
    # Check variables
    local required_vars=(
        "DOCKER_REGISTRY"
        "DOCKER_IMAGE_NAME"
    )
    
    log "Checking GitHub variables..."
    for var in "${required_vars[@]}"; do
        if gh variable list | grep -q "$var"; then
            success "Variable '$var' is configured"
        else
            add_issue "WARNING" "SECRETS" "Variable '$var' not configured" "gh variable set $var"
        fi
    done
}

# Deployment validation
check_deployment() {
    header "Deployment Process Validation"
    
    # Check deployment scripts
    local deploy_scripts=("scripts/deploy.sh" "scripts/troubleshoot.sh")
    for script in "${deploy_scripts[@]}"; do
        if [[ -f "$script" ]]; then
            if [[ -x "$script" ]]; then
                success "Script '$script' is executable"
            else
                add_issue "ERROR" "DEPLOYMENT" "Script '$script' is not executable" "chmod +x $script"
            fi
        else
            add_issue "ERROR" "DEPLOYMENT" "Deployment script '$script' not found"
        fi
    done
    
    # Check environment templates
    local env_templates=(".env.example" ".env.production.template")
    for template in "${env_templates[@]}"; do
        if [[ -f "$template" ]]; then
            success "Environment template '$template' found"
        else
            add_issue "WARNING" "DEPLOYMENT" "Environment template '$template' not found"
        fi
    done
    
    # Check required directories
    local required_dirs=("scripts" "data" "logs")
    for dir in "${required_dirs[@]}"; do
        if [[ -d "$dir" ]]; then
            success "Directory '$dir' exists"
        else
            add_issue "WARNING" "DEPLOYMENT" "Directory '$dir' not found" "mkdir -p $dir"
        fi
    done
    
    # Check volume configuration
    if grep -q "fortinet-data:" docker-compose.production.yml; then
        success "Named volumes configured in Docker Compose"
    else
        add_issue "WARNING" "DEPLOYMENT" "Named volumes not properly configured"
    fi
    
    # Test deployment script syntax
    if bash -n scripts/deploy.sh 2>/dev/null; then
        success "Deploy script syntax is valid"
    else
        add_issue "ERROR" "DEPLOYMENT" "Deploy script has syntax errors"
    fi
}

# Pipeline simulation
simulate_pipeline() {
    header "CI/CD Pipeline Simulation"
    
    if [[ "$SIMULATE" != true ]]; then
        log "Skipping simulation (use --simulate to enable)"
        return 0
    fi
    
    log "Simulating CI/CD pipeline steps..."
    
    # Simulate test stage
    log "Step 1: Running tests..."
    if [[ -f "requirements.txt" ]]; then
        success "✓ Dependencies check"
    else
        add_issue "WARNING" "PIPELINE" "requirements.txt not found"
    fi
    
    # Simulate security scan
    log "Step 2: Security scan..."
    if command -v bandit &> /dev/null; then
        success "✓ Security tools available"
    else
        warning "Security tools not available locally"
    fi
    
    # Simulate Docker build
    log "Step 3: Docker build..."
    if docker build --dry-run -f Dockerfile.production . &> /dev/null; then
        success "✓ Docker build validation"
    else
        add_issue "ERROR" "PIPELINE" "Docker build would fail"
    fi
    
    # Simulate registry push
    log "Step 4: Registry push..."
    if ping -c 1 "$(echo $DOCKER_REGISTRY | sed 's/.*\/\///' | cut -d'/' -f1)" &> /dev/null; then
        success "✓ Registry connectivity"
    else
        add_issue "ERROR" "PIPELINE" "Registry push would fail"
    fi
    
    # Simulate deployment
    log "Step 5: Deployment..."
    if [[ -f "docker-compose.production.yml" ]] && [[ -x "scripts/deploy.sh" ]]; then
        success "✓ Deployment configuration ready"
    else
        add_issue "ERROR" "PIPELINE" "Deployment would fail"
    fi
    
    success "Pipeline simulation completed"
}

# Troubleshoot common issues
troubleshoot_common() {
    header "Common CI/CD Issues Diagnosis"
    
    log "Checking for common CI/CD issues..."
    
    # Check for rate limiting
    if gh api rate_limit &> /dev/null; then
        local remaining
        remaining=$(gh api rate_limit | jq -r '.rate.remaining')
        if [[ $remaining -lt 100 ]]; then
            add_issue "WARNING" "GITHUB" "Low GitHub API rate limit remaining: $remaining"
        else
            success "GitHub API rate limit OK: $remaining remaining"
        fi
    fi
    
    # Check Docker daemon
    if ! docker info &> /dev/null; then
        add_issue "ERROR" "DOCKER" "Docker daemon not running" "sudo systemctl start docker"
    fi
    
    # Check disk space
    local disk_usage
    disk_usage=$(df . | tail -1 | awk '{print $5}' | sed 's/%//')
    if [[ $disk_usage -gt 80 ]]; then
        add_issue "WARNING" "SYSTEM" "High disk usage: ${disk_usage}%" "docker system prune -f"
    fi
    
    # Check for conflicting processes
    if netstat -tlnp 2>/dev/null | grep ":7777" &> /dev/null; then
        local process
        process=$(netstat -tlnp 2>/dev/null | grep ":7777" | awk '{print $7}')
        add_issue "WARNING" "DEPLOYMENT" "Port 7777 in use by: $process"
    fi
    
    # Check Git configuration
    if ! git config user.name &> /dev/null; then
        add_issue "WARNING" "GIT" "Git user.name not configured" "git config --global user.name 'Your Name'"
    fi
    
    if ! git config user.email &> /dev/null; then
        add_issue "WARNING" "GIT" "Git user.email not configured" "git config --global user.email 'your@email.com'"
    fi
    
    # Check for uncommitted changes
    if ! git diff --quiet 2>/dev/null; then
        add_issue "WARNING" "GIT" "Uncommitted changes in working directory"
    fi
    
    # Check branch status
    if command -v git &> /dev/null && git status &> /dev/null; then
        local branch
        branch=$(git rev-parse --abbrev-ref HEAD)
        log "Current branch: $branch"
        
        if [[ "$branch" != "main" ]] && [[ "$branch" != "master" ]]; then
            warning "Not on main/master branch - deployment may not trigger"
        fi
    fi
}

# Generate recommendations
generate_recommendations() {
    header "Recommendations"
    
    echo "Based on the validation results, here are the recommendations:"
    echo ""
    
    if [[ $ISSUES_FOUND -eq 0 ]]; then
        success "🎉 All validations passed! Your CI/CD pipeline is ready."
        echo ""
        echo "Next steps:"
        echo "1. Push changes to trigger the pipeline: git push origin main"
        echo "2. Monitor the GitHub Actions: gh run list"
        echo "3. Check deployment status: ./scripts/deploy.sh status"
    else
        echo "Issues found that should be addressed:"
        echo ""
        echo "Priority actions:"
        echo "1. Fix all ERROR level issues before deploying"
        echo "2. Address WARNING level issues for optimal operation"
        echo "3. Re-run validation after fixes: $0"
        echo ""
        echo "Quick fixes:"
        echo "- Set missing GitHub secrets: gh secret set DOCKER_USERNAME"
        echo "- Fix file permissions: chmod +x scripts/*.sh"
        echo "- Update environment: cp .env.example .env"
        echo "- Test locally: ./scripts/deploy.sh build"
    fi
    
    echo ""
    echo "Useful commands:"
    echo "- Monitor pipeline: gh run watch"
    echo "- Check logs: gh run view --log"
    echo "- Local deployment: ./scripts/deploy.sh"
    echo "- Troubleshooting: ./scripts/troubleshoot.sh"
}

# Main execution
main() {
    log "FortiGate Nextrade CI/CD Validation"
    log "Checks to run: ${CHECKS[*]}"
    
    for check in "${CHECKS[@]}"; do
        case "$check" in
            all)
                check_github
                check_docker
                check_secrets
                check_deployment
                simulate_pipeline
                ;;
            github)
                check_github
                ;;
            docker)
                check_docker
                ;;
            secrets)
                check_secrets
                ;;
            deployment)
                check_deployment
                ;;
            pipeline)
                simulate_pipeline
                ;;
            troubleshoot)
                troubleshoot_common
                ;;
            *)
                error "Unknown check: $check"
                exit 1
                ;;
        esac
    done
    
    generate_recommendations
    
    # Exit with error if issues found
    if [[ $ISSUES_FOUND -gt 0 ]]; then
        exit 1
    fi
}

main "$@"