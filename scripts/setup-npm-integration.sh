#!/bin/bash

# NPM Integration Setup Script
# This script helps configure Nginx Proxy Manager integration for External-DNS

set -e

echo "🔧 Nginx Proxy Manager Integration Setup"
echo "======================================"

# Configuration
NPM_HOST="${NPM_HOST:-192.168.50.215}"
NPM_PORT="${NPM_PORT:-81}"
NPM_EMAIL="${NPM_EMAIL:-admin@jclee.me}"

# Helper functions
setup_npm_credentials() {
    echo "📋 Step 1: Create NPM Credentials Secret"
    echo ""
    echo "First, get your NPM credentials:"
    echo "1. Login to NPM at http://${NPM_HOST}:${NPM_PORT}"
    echo "2. Default credentials are usually: admin@example.com / changeme"
    echo "3. Update to your secure credentials"
    echo ""
    read -p "Enter NPM admin email [${NPM_EMAIL}]: " input_email
    NPM_EMAIL="${input_email:-$NPM_EMAIL}"
    
    read -s -p "Enter NPM admin password: " NPM_PASSWORD
    echo ""
    
    # Create Kubernetes secret
    echo ""
    echo "Creating Kubernetes secret..."
    kubectl create secret generic npm-credentials \
        --from-literal=npm_host="${NPM_HOST}" \
        --from-literal=npm_port="${NPM_PORT}" \
        --from-literal=npm_email="${NPM_EMAIL}" \
        --from-literal=npm_password="${NPM_PASSWORD}" \
        --from-literal=npm_url="http://${NPM_HOST}:${NPM_PORT}" \
        -n fortinet \
        --dry-run=client -o yaml | kubectl apply -f -
    
    echo "✅ NPM credentials secret created/updated"
}

setup_webhook_provider() {
    echo ""
    echo "📋 Step 2: Deploy Webhook Provider"
    echo ""
    echo "Choose deployment method:"
    echo "1. Webhook Provider (Real-time updates, more complex)"
    echo "2. CronJob Sync (Simple, 5-minute intervals)"
    read -p "Select option [1-2]: " DEPLOY_METHOD
    
    case $DEPLOY_METHOD in
        1)
            echo "Building and deploying Webhook Provider..."
            
            # Build Docker image
            echo "Building npm-webhook-provider image..."
            cd k8s/npm-external-dns
            
            # Check if Docker is available
            if command -v docker &> /dev/null; then
                docker build -t npm-webhook-provider:latest -f Dockerfile.webhook .
                
                # Tag for registry
                REGISTRY="${DOCKER_REGISTRY:-registry.jclee.me}"
                docker tag npm-webhook-provider:latest ${REGISTRY}/npm-webhook-provider:latest
                
                echo "Pushing to registry..."
                docker push ${REGISTRY}/npm-webhook-provider:latest
                
                # Update deployment with registry image
                sed -i "s|image: npm-webhook-provider:latest|image: ${REGISTRY}/npm-webhook-provider:latest|g" webhook-provider-deployment.yaml
            else
                echo "⚠️ Docker not found. Please build the image manually:"
                echo "cd k8s/npm-external-dns"
                echo "docker build -t npm-webhook-provider:latest -f Dockerfile.webhook ."
                echo "docker push your-registry/npm-webhook-provider:latest"
            fi
            
            # Apply webhook provider
            kubectl apply -f webhook-provider-deployment.yaml
            
            # Update External-DNS to use webhook provider
            kubectl apply -f external-dns-npm.yaml
            
            echo "✅ Webhook Provider deployed"
            ;;
        2)
            echo "Deploying CronJob Sync..."
            kubectl apply -f simple-cronjob.yaml
            echo "✅ CronJob deployed (runs every 5 minutes)"
            ;;
        *)
            echo "Invalid option. Exiting."
            exit 1
            ;;
    esac
}

update_ingress_config() {
    echo ""
    echo "📋 Step 3: Update Ingress Annotations"
    echo ""
    echo "Your Ingress resources need NPM-specific annotations."
    echo ""
    echo "Example annotations to add:"
    echo '  annotations:'
    echo '    # NPM specific settings'
    echo '    npm.external-dns.io/ssl-forced: "true"'
    echo '    npm.external-dns.io/http2-support: "true"'
    echo '    npm.external-dns.io/hsts-enabled: "true"'
    echo '    npm.external-dns.io/location: "/"'
    echo ""
    read -p "Update fortinet Ingress now? [y/N]: " UPDATE_INGRESS
    
    if [[ "$UPDATE_INGRESS" =~ ^[Yy]$ ]]; then
        # Check if fortinet ingress exists
        if kubectl get ingress fortinet-ingress -n fortinet &>/dev/null; then
            echo "Updating fortinet-ingress..."
            kubectl annotate ingress fortinet-ingress -n fortinet \
                npm.external-dns.io/ssl-forced="true" \
                npm.external-dns.io/http2-support="true" \
                npm.external-dns.io/hsts-enabled="true" \
                npm.external-dns.io/location="/" \
                --overwrite
            echo "✅ Ingress annotations updated"
        else
            echo "⚠️ fortinet-ingress not found. Please update manually."
        fi
    fi
}

verify_deployment() {
    echo ""
    echo "📋 Step 4: Verify Deployment"
    echo ""
    
    # Check pods
    echo "Checking pods..."
    kubectl get pods -n fortinet | grep -E "(npm-webhook|npm-sync)" || echo "No NPM integration pods found yet"
    
    # Check secret
    echo ""
    echo "Checking secret..."
    kubectl get secret npm-credentials -n fortinet -o jsonpath='{.data}' | jq -r 'keys[]' 2>/dev/null || echo "Secret not found"
    
    echo ""
    echo "🔗 Quick Commands:"
    echo "- Check logs: kubectl logs -n fortinet -l app=npm-webhook-provider -f"
    echo "- Check sync status: ./scripts/npm-sync-monitor.sh"
    echo "- Force sync: kubectl create job --from=cronjob/npm-sync-cronjob npm-sync-manual -n fortinet"
}

# Main execution
echo "This script will help you set up NPM integration for External-DNS"
echo ""
echo "Prerequisites:"
echo "- Nginx Proxy Manager running at ${NPM_HOST}:${NPM_PORT}"
echo "- kubectl configured for your cluster"
echo "- External-DNS already deployed"
echo ""
read -p "Continue? [y/N]: " CONTINUE

if [[ ! "$CONTINUE" =~ ^[Yy]$ ]]; then
    echo "Setup cancelled."
    exit 0
fi

# Run setup steps
setup_npm_credentials
setup_webhook_provider
update_ingress_config
verify_deployment

echo ""
echo "✅ NPM Integration Setup Complete!"
echo ""
echo "Next steps:"
echo "1. Monitor the integration: ./scripts/npm-sync-monitor.sh"
echo "2. Check NPM dashboard for new proxy hosts"
echo "3. Test with: curl -H 'Host: fortinet.jclee.me' http://${NPM_HOST}"
echo ""
echo "Troubleshooting:"
echo "- Logs: kubectl logs -n fortinet -l app=npm-webhook-provider"
echo "- NPM API: curl http://${NPM_HOST}:${NPM_PORT}/api"
echo "- Force sync: kubectl delete pod -n fortinet -l app=npm-webhook-provider"