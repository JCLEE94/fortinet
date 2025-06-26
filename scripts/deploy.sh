#!/bin/bash
# =============================================================================
# FortiGate Nextrade - Production Deployment Script
# =============================================================================

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
DOCKER_REGISTRY="${DOCKER_REGISTRY:-registry.jclee.me}"
DOCKER_IMAGE_NAME="${DOCKER_IMAGE_NAME:-fortinet}"
DOCKER_TAG="${DOCKER_TAG:-latest}"
CONTAINER_NAME="${CONTAINER_NAME:-fortinet}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Help function
show_help() {
    cat << EOF
FortiGate Nextrade Deployment Script

Usage: $0 [OPTIONS] [COMMAND]

Commands:
    deploy          Full deployment (default)
    build           Build Docker image only
    push            Push Docker image to registry
    pull            Pull Docker image from registry
    start           Start containers
    stop            Stop containers
    restart         Restart containers
    logs            Show container logs
    status          Show container status
    cleanup         Cleanup old images and containers
    troubleshoot    Run troubleshooting checks

Options:
    -h, --help      Show this help message
    -t, --tag TAG   Docker image tag (default: latest)
    -n, --name NAME Container name (default: fortinet)
    -e, --env ENV   Environment file (default: .env)
    -f, --force     Force rebuild/redeploy
    -v, --verbose   Verbose output
    --no-cache      Build without cache
    --dry-run       Show what would be done without executing

Examples:
    $0 deploy                    # Full deployment
    $0 build --no-cache          # Build without cache
    $0 start -e .env.production  # Start with specific env file
    $0 troubleshoot              # Run diagnostics
EOF
}

# Parse command line arguments
COMMAND="deploy"
ENV_FILE=".env"
FORCE=false
VERBOSE=false
NO_CACHE=false
DRY_RUN=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -t|--tag)
            DOCKER_TAG="$2"
            shift 2
            ;;
        -n|--name)
            CONTAINER_NAME="$2"
            shift 2
            ;;
        -e|--env)
            ENV_FILE="$2"
            shift 2
            ;;
        -f|--force)
            FORCE=true
            shift
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        --no-cache)
            NO_CACHE=true
            shift
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        deploy|build|push|pull|start|stop|restart|logs|status|cleanup|troubleshoot)
            COMMAND="$1"
            shift
            ;;
        *)
            error "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Change to project directory
cd "$PROJECT_DIR"

# Check prerequisites
check_prerequisites() {
    log "Checking prerequisites..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        error "Docker is not installed or not in PATH"
        exit 1
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        error "Docker Compose is not installed"
        exit 1
    fi
    
    # Check environment file
    if [[ ! -f "$ENV_FILE" ]] && [[ "$COMMAND" != "build" ]]; then
        warning "Environment file '$ENV_FILE' not found. Creating from template..."
        if [[ -f ".env.example" ]]; then
            cp .env.example "$ENV_FILE"
            warning "Please edit '$ENV_FILE' with your configuration"
        else
            error "No environment template found"
            exit 1
        fi
    fi
    
    success "Prerequisites check passed"
}

# Build Docker image
build_image() {
    log "Building Docker image..."
    
    local build_args=(
        --file "Dockerfile.production"
        --tag "${DOCKER_REGISTRY}/${DOCKER_IMAGE_NAME}:${DOCKER_TAG}"
        --build-arg "BUILD_DATE=$(date -u +'%Y-%m-%dT%H:%M:%SZ')"
        --build-arg "GIT_COMMIT=$(git rev-parse HEAD 2>/dev/null || echo 'unknown')"
        --build-arg "GIT_BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo 'unknown')"
        --build-arg "VERSION=${DOCKER_TAG}"
    )
    
    if [[ "$NO_CACHE" == true ]]; then
        build_args+=(--no-cache)
    fi
    
    if [[ "$VERBOSE" == true ]]; then
        build_args+=(--progress=plain)
    fi
    
    if [[ "$DRY_RUN" == true ]]; then
        log "Would run: docker build ${build_args[*]} ."
        return 0
    fi
    
    docker build "${build_args[@]}" .
    success "Docker image built successfully"
}

# Push image to registry
push_image() {
    log "Pushing image to registry..."
    
    if [[ "$DRY_RUN" == true ]]; then
        log "Would run: docker push ${DOCKER_REGISTRY}/${DOCKER_IMAGE_NAME}:${DOCKER_TAG}"
        return 0
    fi
    
    # Login to registry if credentials are available
    if [[ -n "${DOCKER_USERNAME:-}" ]] && [[ -n "${DOCKER_PASSWORD:-}" ]]; then
        echo "$DOCKER_PASSWORD" | docker login "$DOCKER_REGISTRY" -u "$DOCKER_USERNAME" --password-stdin
    fi
    
    docker push "${DOCKER_REGISTRY}/${DOCKER_IMAGE_NAME}:${DOCKER_TAG}"
    success "Image pushed successfully"
}

# Pull image from registry
pull_image() {
    log "Pulling image from registry..."
    
    if [[ "$DRY_RUN" == true ]]; then
        log "Would run: docker pull ${DOCKER_REGISTRY}/${DOCKER_IMAGE_NAME}:${DOCKER_TAG}"
        return 0
    fi
    
    # Login to registry if credentials are available
    if [[ -n "${DOCKER_USERNAME:-}" ]] && [[ -n "${DOCKER_PASSWORD:-}" ]]; then
        echo "$DOCKER_PASSWORD" | docker login "$DOCKER_REGISTRY" -u "$DOCKER_USERNAME" --password-stdin
    fi
    
    docker pull "${DOCKER_REGISTRY}/${DOCKER_IMAGE_NAME}:${DOCKER_TAG}"
    success "Image pulled successfully"
}

# Start containers
start_containers() {
    log "Starting containers..."
    
    local compose_args=(
        --env-file "$ENV_FILE"
        --file "docker-compose.production.yml"
    )
    
    if [[ "$DRY_RUN" == true ]]; then
        log "Would run: docker-compose ${compose_args[*]} up -d"
        return 0
    fi
    
    # Export variables for docker-compose
    export DOCKER_REGISTRY DOCKER_IMAGE_NAME DOCKER_TAG CONTAINER_NAME
    
    docker-compose "${compose_args[@]}" up -d
    
    # Wait for health check
    log "Waiting for container to be healthy..."
    local timeout=60
    while [[ $timeout -gt 0 ]]; do
        if docker inspect --format='{{.State.Health.Status}}' "$CONTAINER_NAME" 2>/dev/null | grep -q "healthy"; then
            success "Container is healthy"
            break
        fi
        sleep 2
        timeout=$((timeout-2))
    done
    
    if [[ $timeout -le 0 ]]; then
        error "Container health check failed"
        show_logs
        exit 1
    fi
    
    success "Containers started successfully"
}

# Stop containers
stop_containers() {
    log "Stopping containers..."
    
    if [[ "$DRY_RUN" == true ]]; then
        log "Would run: docker-compose --file docker-compose.production.yml down"
        return 0
    fi
    
    docker-compose --file "docker-compose.production.yml" down
    success "Containers stopped successfully"
}

# Show logs
show_logs() {
    log "Showing container logs..."
    
    if docker ps -q -f name="$CONTAINER_NAME" &> /dev/null; then
        docker logs --tail 50 --follow "$CONTAINER_NAME"
    else
        error "Container '$CONTAINER_NAME' is not running"
        exit 1
    fi
}

# Show status
show_status() {
    log "Container status:"
    
    # Show container status
    if docker ps -a -f name="$CONTAINER_NAME" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep -q "$CONTAINER_NAME"; then
        docker ps -a -f name="$CONTAINER_NAME" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    else
        warning "Container '$CONTAINER_NAME' not found"
    fi
    
    # Show health status
    if docker ps -q -f name="$CONTAINER_NAME" &> /dev/null; then
        local health_status
        health_status=$(docker inspect --format='{{.State.Health.Status}}' "$CONTAINER_NAME" 2>/dev/null || echo "no-healthcheck")
        log "Health status: $health_status"
    fi
    
    # Show resource usage
    if docker ps -q -f name="$CONTAINER_NAME" &> /dev/null; then
        log "Resource usage:"
        docker stats --no-stream "$CONTAINER_NAME" 2>/dev/null || true
    fi
}

# Cleanup old images and containers
cleanup() {
    log "Cleaning up old images and containers..."
    
    if [[ "$DRY_RUN" == true ]]; then
        log "Would run cleanup commands"
        return 0
    fi
    
    # Remove stopped containers
    if docker ps -aq -f status=exited | head -n 5; then
        docker ps -aq -f status=exited | head -n 5 | xargs docker rm
    fi
    
    # Remove dangling images
    if docker images -q -f dangling=true | head -n 10; then
        docker images -q -f dangling=true | head -n 10 | xargs docker rmi
    fi
    
    # Clean up Docker system
    docker system prune -f
    
    success "Cleanup completed"
}

# Troubleshooting function
troubleshoot() {
    log "Running troubleshooting checks..."
    
    echo "=== System Information ==="
    echo "OS: $(uname -a)"
    echo "Docker Version: $(docker --version)"
    echo "Docker Compose Version: $(docker-compose --version 2>/dev/null || docker compose version)"
    echo "Available Memory: $(free -h | grep Mem | awk '{print $2}')"
    echo "Available Disk: $(df -h . | tail -1 | awk '{print $4}')"
    
    echo -e "\n=== Docker Status ==="
    docker system df
    
    echo -e "\n=== Network Status ==="
    docker network ls | grep fortinet || echo "No fortinet networks found"
    
    echo -e "\n=== Volume Status ==="
    docker volume ls | grep fortinet || echo "No fortinet volumes found"
    
    echo -e "\n=== Image Status ==="
    docker images | grep "$DOCKER_IMAGE_NAME" || echo "No fortinet images found"
    
    echo -e "\n=== Container Status ==="
    docker ps -a | grep fortinet || echo "No fortinet containers found"
    
    echo -e "\n=== Port Status ==="
    netstat -tlnp 2>/dev/null | grep ":7777" || echo "Port 7777 not in use"
    
    echo -e "\n=== Recent Logs ==="
    if docker ps -q -f name="$CONTAINER_NAME" &> /dev/null; then
        docker logs --tail 20 "$CONTAINER_NAME"
    else
        echo "Container not running"
    fi
    
    echo -e "\n=== Environment Check ==="
    if [[ -f "$ENV_FILE" ]]; then
        echo "Environment file exists: $ENV_FILE"
        echo "Non-sensitive variables:"
        grep -E "^[A-Z_]+=" "$ENV_FILE" | grep -v -E "(PASSWORD|SECRET|KEY|TOKEN)" | head -10
    else
        echo "Environment file not found: $ENV_FILE"
    fi
}

# Full deployment
deploy() {
    log "Starting full deployment..."
    
    if [[ "$FORCE" == true ]] || [[ ! $(docker images -q "${DOCKER_REGISTRY}/${DOCKER_IMAGE_NAME}:${DOCKER_TAG}") ]]; then
        build_image
    else
        log "Image exists, skipping build (use --force to rebuild)"
    fi
    
    # Stop existing containers
    if docker ps -q -f name="$CONTAINER_NAME" &> /dev/null; then
        log "Stopping existing container..."
        stop_containers
    fi
    
    start_containers
    
    # Show final status
    show_status
    
    success "Deployment completed successfully!"
    log "Application URL: http://localhost:${WEB_APP_PORT:-7777}"
}

# Main execution
main() {
    log "FortiGate Nextrade Deployment Script"
    log "Command: $COMMAND"
    
    check_prerequisites
    
    case "$COMMAND" in
        deploy)
            deploy
            ;;
        build)
            build_image
            ;;
        push)
            push_image
            ;;
        pull)
            pull_image
            ;;
        start)
            start_containers
            ;;
        stop)
            stop_containers
            ;;
        restart)
            stop_containers
            start_containers
            ;;
        logs)
            show_logs
            ;;
        status)
            show_status
            ;;
        cleanup)
            cleanup
            ;;
        troubleshoot)
            troubleshoot
            ;;
        *)
            error "Unknown command: $COMMAND"
            show_help
            exit 1
            ;;
    esac
}

# Execute main function
main "$@"