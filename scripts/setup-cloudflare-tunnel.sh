#!/bin/bash

# =============================================================================
# Cloudflare Tunnel Setup for FortiGate Nextrade
# =============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
NAMESPACE="fortinet"
SECRET_NAME="cloudflare-tunnel-token"
TEMPLATE_FILE="k8s/templates/cloudflare-tunnel-token.yaml.template"

# Default token (이미 설정됨)
DEFAULT_TOKEN="eyJhIjoiYThkOWM2N2Y1ODZhY2RkMTVlZWJjYzY1Y2EzYWE1YmIiLCJ0IjoiOGVhNzg5MDYtMWEwNS00NGZiLWExYmItZTUxMjE3MmNiNWFiIiwicyI6Ill6RXlZVEUwWWpRdE1tVXlNUzAwWmpRMExXSTVaR0V0WkdNM09UY3pOV1ExT1RGbSJ9"

# Parse command line arguments
USE_TOKEN=false
TUNNEL_TOKEN=""
while [[ $# -gt 0 ]]; do
    case $1 in
        --token)
            TUNNEL_TOKEN="$2"
            USE_TOKEN=true
            shift 2
            ;;
        --help)
            echo "Usage: $0 [--token TOKEN]"
            echo "  --token TOKEN  Cloudflare tunnel token (optional, will use environment variable if not provided)"
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

echo -e "${BLUE}=== Cloudflare Tunnel Setup ===${NC}"
echo "Setting up Cloudflare tunnel for FortiGate Nextrade..."

# Function to check if kubectl is available
check_kubectl() {
    if ! command -v kubectl &> /dev/null; then
        echo -e "${RED}kubectl could not be found. Please install kubectl first.${NC}"
        exit 1
    fi
}

# Function to create or update secret
manage_secret() {
    echo -e "${BLUE}Managing Cloudflare tunnel secret...${NC}"
    
    # Get token from environment or command line
    if [ "$USE_TOKEN" = true ]; then
        TOKEN="$TUNNEL_TOKEN"
    elif [ -n "$CLOUDFLARE_TUNNEL_TOKEN" ]; then
        TOKEN="$CLOUDFLARE_TUNNEL_TOKEN"
        echo -e "${GREEN}Using token from CLOUDFLARE_TUNNEL_TOKEN environment variable${NC}"
    else
        # Use default token
        TOKEN="$DEFAULT_TOKEN"
        echo -e "${GREEN}Using default configured token${NC}"
    fi
    
    # Check if secret already exists
    if kubectl get secret $SECRET_NAME -n $NAMESPACE &> /dev/null; then
        echo -e "${YELLOW}Secret already exists. Updating...${NC}"
        kubectl delete secret $SECRET_NAME -n $NAMESPACE
    fi
    
    # Create secret from template
    echo -e "${BLUE}Creating secret from template...${NC}"
    cat $TEMPLATE_FILE | sed "s/CLOUDFLARE_TUNNEL_TOKEN_PLACEHOLDER/$TOKEN/" | kubectl apply -f -
    
    echo -e "${GREEN}Secret created/updated successfully!${NC}"
}

# Function to check if namespace exists
check_namespace() {
    if ! kubectl get namespace $NAMESPACE &> /dev/null; then
        echo -e "${YELLOW}Namespace $NAMESPACE does not exist. Creating...${NC}"
        kubectl create namespace $NAMESPACE
    fi
}

# Function to apply the deployment
apply_deployment() {
    echo -e "${BLUE}Applying Cloudflare tunnel deployment...${NC}"
    
    # Check if the deployment with cloudflare exists
    if [ -f "k8s/manifests/deployment-with-cloudflare.yaml" ]; then
        kubectl apply -f k8s/manifests/deployment-with-cloudflare.yaml
        echo -e "${GREEN}Deployment with Cloudflare tunnel applied successfully!${NC}"
    else
        echo -e "${RED}deployment-with-cloudflare.yaml not found!${NC}"
        exit 1
    fi
}

# Function to update kustomization
update_kustomization() {
    echo -e "${BLUE}Updating kustomization.yaml...${NC}"
    
    # Check if deployment-with-cloudflare.yaml is already in kustomization
    if ! grep -q "deployment-with-cloudflare.yaml" k8s/manifests/kustomization.yaml; then
        # Replace deployment.yaml with deployment-with-cloudflare.yaml
        sed -i 's/- deployment.yaml/- deployment-with-cloudflare.yaml/' k8s/manifests/kustomization.yaml
        echo -e "${GREEN}Kustomization updated!${NC}"
    else
        echo -e "${YELLOW}Kustomization already includes deployment-with-cloudflare.yaml${NC}"
    fi
}

# Function to verify tunnel status
verify_tunnel() {
    echo -e "${BLUE}Verifying Cloudflare tunnel status...${NC}"
    
    # Wait for pods to be ready
    echo "Waiting for pods to be ready..."
    kubectl wait --for=condition=ready pod -l app=fortinet -n $NAMESPACE --timeout=300s
    
    # Check pod status
    kubectl get pods -n $NAMESPACE -l app=fortinet
    
    # Check logs of cloudflare tunnel container
    echo -e "${BLUE}Cloudflare tunnel logs:${NC}"
    POD_NAME=$(kubectl get pods -n $NAMESPACE -l app=fortinet -o jsonpath="{.items[0].metadata.name}")
    kubectl logs $POD_NAME -c cloudflare-tunnel -n $NAMESPACE --tail=20
}

# Main execution
main() {
    echo -e "${BLUE}Starting Cloudflare Tunnel setup...${NC}"
    
    check_kubectl
    check_namespace
    manage_secret
    update_kustomization
    apply_deployment
    verify_tunnel
    
    echo -e "${GREEN}=== Cloudflare Tunnel Setup Complete ===${NC}"
    echo -e "${BLUE}Your application should now be accessible via Cloudflare tunnel${NC}"
    echo -e "${BLUE}Check the tunnel status in Cloudflare dashboard${NC}"
}

# Run main function
main "$@"