#!/bin/bash
# Build and push Docker images to private registry

set -e

# Configuration
REGISTRY="registry.jclee.me"
PROJECT="fortinet"
TAG="${1:-latest}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Starting build and push process...${NC}"

# Function to build and push image
build_and_push() {
    local service=$1
    local dockerfile=$2
    local context=$3
    local image="${REGISTRY}/${PROJECT}-${service}:${TAG}"
    
    echo -e "${GREEN}Building ${service}...${NC}"
    docker build -f ${dockerfile} -t ${image} ${context}
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}Successfully built ${image}${NC}"
        
        echo -e "${YELLOW}Pushing ${image} to registry...${NC}"
        docker push ${image}
        
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}Successfully pushed ${image}${NC}"
        else
            echo -e "${RED}Failed to push ${image}${NC}"
            exit 1
        fi
    else
        echo -e "${RED}Failed to build ${image}${NC}"
        exit 1
    fi
}

# Login to registry
echo -e "${YELLOW}Logging in to registry...${NC}"
docker login ${REGISTRY}

# Build and push Redis
echo -e "${YELLOW}Building Redis image...${NC}"
build_and_push "redis" "docker/redis/Dockerfile" "docker/redis"

# Build and push PostgreSQL
echo -e "${YELLOW}Building PostgreSQL image...${NC}"
build_and_push "postgresql" "docker/postgresql/Dockerfile" "docker/postgresql"

# Build and push main application
echo -e "${YELLOW}Building main application image...${NC}"
if [ -f "Dockerfile.production" ]; then
    build_and_push "" "Dockerfile.production" "."
else
    echo -e "${RED}Dockerfile.production not found${NC}"
    exit 1
fi

# Tag latest as additional tags if needed
if [ "${TAG}" != "latest" ]; then
    echo -e "${YELLOW}Creating additional tags...${NC}"
    
    docker tag ${REGISTRY}/${PROJECT}-redis:${TAG} ${REGISTRY}/${PROJECT}-redis:latest
    docker tag ${REGISTRY}/${PROJECT}-postgresql:${TAG} ${REGISTRY}/${PROJECT}-postgresql:latest
    docker tag ${REGISTRY}/${PROJECT}:${TAG} ${REGISTRY}/${PROJECT}:latest
    
    docker push ${REGISTRY}/${PROJECT}-redis:latest
    docker push ${REGISTRY}/${PROJECT}-postgresql:latest
    docker push ${REGISTRY}/${PROJECT}:latest
fi

echo -e "${GREEN}All images built and pushed successfully!${NC}"
echo -e "${GREEN}Images:${NC}"
echo -e "  - ${REGISTRY}/${PROJECT}-redis:${TAG}"
echo -e "  - ${REGISTRY}/${PROJECT}-postgresql:${TAG}"
echo -e "  - ${REGISTRY}/${PROJECT}:${TAG}"