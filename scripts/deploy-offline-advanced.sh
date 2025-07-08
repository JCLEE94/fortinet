#!/bin/bash

# =============================================================================
# Advanced Offline Deployment Script for FortiGate Nextrade
# =============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
NAMESPACE="fortinet"
APP_NAME="fortinet-app"
DEFAULT_PORT="7777"
IMAGE_NAME="fortinet:latest"

# Banner
print_banner() {
    echo -e "${CYAN}"
    echo "╔═══════════════════════════════════════════════════════════╗"
    echo "║          FortiGate Nextrade Offline Deployment            ║"
    echo "║                    Version 2.0                            ║"
    echo "╚═══════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

# Function to check prerequisites
check_prerequisites() {
    echo -e "${BLUE}Checking prerequisites...${NC}"
    
    local missing=()
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        missing+=("docker")
    fi
    
    # Check if Docker daemon is running
    if command -v docker &> /dev/null && ! docker info &> /dev/null; then
        echo -e "${RED}Docker daemon is not running${NC}"
        echo "Please start Docker service and try again"
        exit 1
    fi
    
    # Check kubectl (optional)
    KUBECTL_AVAILABLE=false
    if command -v kubectl &> /dev/null; then
        KUBECTL_AVAILABLE=true
        echo -e "${GREEN}✓ kubectl found${NC}"
    else
        echo -e "${YELLOW}⚠ kubectl not found (Kubernetes deployment unavailable)${NC}"
    fi
    
    # Check for required files
    if [ ! -f "fortinet-image.tar" ]; then
        echo -e "${RED}fortinet-image.tar not found in current directory${NC}"
        exit 1
    fi
    
    if [ ${#missing[@]} -ne 0 ]; then
        echo -e "${RED}Missing required tools: ${missing[*]}${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✓ All prerequisites met${NC}"
}

# Function to load Docker image
load_docker_image() {
    echo -e "${BLUE}Loading Docker image...${NC}"
    
    # Check if image already exists
    if docker images | grep -q "$IMAGE_NAME"; then
        echo -e "${YELLOW}Image already exists. Overwriting...${NC}"
    fi
    
    # Load image with progress
    docker load -i fortinet-image.tar | while read line; do
        echo -e "${CYAN}  $line${NC}"
    done
    
    echo -e "${GREEN}✓ Docker image loaded successfully${NC}"
    
    # Verify image
    echo -e "${BLUE}Verifying image...${NC}"
    docker images | grep fortinet
}

# Function to deploy with Docker
deploy_docker() {
    echo -e "${BLUE}=== Docker Deployment ===${NC}"
    
    # Check if container already exists
    if docker ps -a | grep -q "$APP_NAME"; then
        echo -e "${YELLOW}Container $APP_NAME already exists${NC}"
        read -p "Remove existing container? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            docker stop $APP_NAME 2>/dev/null || true
            docker rm $APP_NAME 2>/dev/null || true
        else
            echo -e "${RED}Deployment cancelled${NC}"
            return 1
        fi
    fi
    
    # Get deployment parameters
    read -p "Port to expose (default: $DEFAULT_PORT): " PORT
    PORT=${PORT:-$DEFAULT_PORT}
    
    read -p "Data directory (default: ./data): " DATA_DIR
    DATA_DIR=${DATA_DIR:-./data}
    
    read -p "Logs directory (default: ./logs): " LOGS_DIR
    LOGS_DIR=${LOGS_DIR:-./logs}
    
    # Create directories
    mkdir -p "$DATA_DIR" "$LOGS_DIR"
    
    # Deploy container
    echo -e "${BLUE}Starting container...${NC}"
    docker run -d \
        --name $APP_NAME \
        -p ${PORT}:7777 \
        -v "$(pwd)/${DATA_DIR}:/app/data" \
        -v "$(pwd)/${LOGS_DIR}:/app/logs" \
        -e APP_MODE=production \
        -e OFFLINE_MODE=true \
        -e WEB_APP_PORT=7777 \
        --restart unless-stopped \
        $IMAGE_NAME
    
    # Wait for container to start
    echo -e "${BLUE}Waiting for application to start...${NC}"
    sleep 5
    
    # Check container status
    if docker ps | grep -q $APP_NAME; then
        echo -e "${GREEN}✓ Container started successfully${NC}"
        echo -e "${CYAN}Application URL: http://localhost:${PORT}${NC}"
        
        # Show logs
        echo -e "\n${BLUE}Recent logs:${NC}"
        docker logs --tail 20 $APP_NAME
    else
        echo -e "${RED}Container failed to start${NC}"
        echo -e "${YELLOW}Checking logs...${NC}"
        docker logs $APP_NAME
        return 1
    fi
}

# Function to deploy with Kubernetes
deploy_kubernetes() {
    echo -e "${BLUE}=== Kubernetes Deployment ===${NC}"
    
    if [ "$KUBECTL_AVAILABLE" != "true" ]; then
        echo -e "${RED}kubectl is not available${NC}"
        return 1
    fi
    
    # Check cluster connection
    if ! kubectl cluster-info &> /dev/null; then
        echo -e "${RED}Cannot connect to Kubernetes cluster${NC}"
        echo -e "${YELLOW}Please check your kubeconfig${NC}"
        return 1
    fi
    
    # Create namespace if needed
    if ! kubectl get namespace $NAMESPACE &> /dev/null; then
        echo -e "${BLUE}Creating namespace $NAMESPACE...${NC}"
        kubectl create namespace $NAMESPACE
    fi
    
    # Tag image for local registry
    read -p "Local registry URL (e.g., localhost:5000): " REGISTRY
    if [ -n "$REGISTRY" ]; then
        echo -e "${BLUE}Tagging image for local registry...${NC}"
        docker tag $IMAGE_NAME $REGISTRY/fortinet:latest
        
        echo -e "${BLUE}Pushing to local registry...${NC}"
        docker push $REGISTRY/fortinet:latest
        
        # Update kustomization
        sed -i "s|registry.jclee.me/fortinet|$REGISTRY/fortinet|g" k8s/manifests/kustomization.yaml
    fi
    
    # Deploy
    echo -e "${BLUE}Applying Kubernetes manifests...${NC}"
    kubectl apply -k k8s/manifests/
    
    # Wait for deployment
    echo -e "${BLUE}Waiting for pods to be ready...${NC}"
    kubectl wait --for=condition=ready pod -l app=fortinet -n $NAMESPACE --timeout=300s
    
    # Get pod status
    echo -e "${GREEN}✓ Deployment successful${NC}"
    kubectl get all -n $NAMESPACE
    
    # Get service information
    echo -e "\n${CYAN}Service Information:${NC}"
    kubectl get svc -n $NAMESPACE
}

# Function to deploy with Docker Compose
deploy_compose() {
    echo -e "${BLUE}=== Docker Compose Deployment ===${NC}"
    
    if ! command -v docker-compose &> /dev/null; then
        echo -e "${RED}docker-compose is not installed${NC}"
        return 1
    fi
    
    # Create docker-compose.yml
    cat > docker-compose.yml << EOF
version: '3.8'

services:
  fortinet:
    image: fortinet:latest
    container_name: fortinet-app
    ports:
      - "${DEFAULT_PORT}:7777"
    environment:
      - APP_MODE=production
      - OFFLINE_MODE=true
      - WEB_APP_PORT=7777
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:7777/api/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  redis:
    image: redis:alpine
    container_name: fortinet-redis
    command: redis-server --appendonly yes
    volumes:
      - ./redis-data:/data
    restart: unless-stopped

volumes:
  data:
  logs:
  redis-data:
EOF
    
    echo -e "${BLUE}Starting services...${NC}"
    docker-compose up -d
    
    echo -e "${GREEN}✓ Docker Compose deployment complete${NC}"
    docker-compose ps
}

# Function to verify deployment
verify_deployment() {
    echo -e "\n${BLUE}=== Verifying Deployment ===${NC}"
    
    local PORT=${1:-$DEFAULT_PORT}
    local MAX_ATTEMPTS=30
    local ATTEMPT=0
    
    echo -e "${BLUE}Checking application health...${NC}"
    
    while [ $ATTEMPT -lt $MAX_ATTEMPTS ]; do
        if curl -s -f "http://localhost:${PORT}/api/health" > /dev/null 2>&1; then
            echo -e "${GREEN}✓ Application is healthy${NC}"
            
            # Get health details
            HEALTH=$(curl -s "http://localhost:${PORT}/api/health")
            echo -e "${CYAN}Health Status:${NC}"
            echo "$HEALTH" | jq . 2>/dev/null || echo "$HEALTH"
            
            return 0
        fi
        
        ATTEMPT=$((ATTEMPT + 1))
        echo -ne "${YELLOW}Waiting for application to be ready... ($ATTEMPT/$MAX_ATTEMPTS)\r${NC}"
        sleep 2
    done
    
    echo -e "\n${RED}Application health check failed${NC}"
    return 1
}

# Function to show post-deployment information
show_info() {
    echo -e "\n${GREEN}╔═══════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║            Deployment Complete!                           ║${NC}"
    echo -e "${GREEN}╚═══════════════════════════════════════════════════════════╝${NC}"
    
    echo -e "\n${CYAN}Access Information:${NC}"
    echo -e "  URL: ${YELLOW}http://localhost:${PORT:-$DEFAULT_PORT}${NC}"
    echo -e "  Username: ${YELLOW}admin${NC}"
    echo -e "  Password: ${YELLOW}Check data/config.json${NC}"
    
    echo -e "\n${CYAN}Useful Commands:${NC}"
    echo -e "  View logs:     ${YELLOW}docker logs -f $APP_NAME${NC}"
    echo -e "  Stop app:      ${YELLOW}docker stop $APP_NAME${NC}"
    echo -e "  Start app:     ${YELLOW}docker start $APP_NAME${NC}"
    echo -e "  Remove app:    ${YELLOW}docker rm -f $APP_NAME${NC}"
    
    echo -e "\n${CYAN}Configuration:${NC}"
    echo -e "  Config file:   ${YELLOW}./data/config.json${NC}"
    echo -e "  Log files:     ${YELLOW}./logs/${NC}"
}

# Main menu
main_menu() {
    echo -e "\n${BLUE}Select deployment method:${NC}"
    echo "1) Docker Standalone"
    echo "2) Docker Compose"
    if [ "$KUBECTL_AVAILABLE" = "true" ]; then
        echo "3) Kubernetes"
    fi
    echo "4) Verify existing deployment"
    echo "5) Exit"
    
    read -p "Enter choice: " choice
    
    case $choice in
        1)
            deploy_docker && verify_deployment && show_info
            ;;
        2)
            deploy_compose && verify_deployment && show_info
            ;;
        3)
            if [ "$KUBECTL_AVAILABLE" = "true" ]; then
                deploy_kubernetes
            else
                echo -e "${RED}Kubernetes not available${NC}"
            fi
            ;;
        4)
            read -p "Port to check (default: $DEFAULT_PORT): " CHECK_PORT
            CHECK_PORT=${CHECK_PORT:-$DEFAULT_PORT}
            verify_deployment $CHECK_PORT
            ;;
        5)
            echo -e "${BLUE}Exiting...${NC}"
            exit 0
            ;;
        *)
            echo -e "${RED}Invalid choice${NC}"
            ;;
    esac
}

# Main execution
main() {
    print_banner
    check_prerequisites
    load_docker_image
    
    while true; do
        main_menu
        echo -e "\n${YELLOW}Press Enter to continue...${NC}"
        read
    done
}

# Run main function
main "$@"