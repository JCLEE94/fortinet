#!/bin/bash
# Continuous Health Monitoring for GitOps Deployment
# 지속적인 헬스 모니터링 및 자동 복구

set -euo pipefail

# Configuration
HEALTH_URL="http://192.168.50.110:30777/api/health"
EXTERNAL_URL="https://fortinet.jclee.me/api/health"
CHECK_INTERVAL=30
FAILURE_THRESHOLD=3
SUCCESS_THRESHOLD=2
LOG_FILE="/tmp/health-monitor.log"

# State tracking
consecutive_failures=0
consecutive_successes=0
last_status="unknown"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log() {
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    local message="[$timestamp] $1"
    echo -e "${BLUE}$message${NC}"
    echo "$message" >> "$LOG_FILE"
}

success() {
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    local message="[$timestamp] ✅ $1"
    echo -e "${GREEN}$message${NC}"
    echo "$message" >> "$LOG_FILE"
}

warning() {
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    local message="[$timestamp] ⚠️  $1"
    echo -e "${YELLOW}$message${NC}"
    echo "$message" >> "$LOG_FILE"
}

error() {
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    local message="[$timestamp] ❌ $1"
    echo -e "${RED}$message${NC}"
    echo "$message" >> "$LOG_FILE"
}

# Health check function
check_health() {
    local url=$1
    local name=$2
    
    local response
    local status_code
    local health_status
    
    # Try to get response with timeout
    if response=$(curl -s -f -m 10 "$url" 2>/dev/null); then
        status_code=200
        health_status=$(echo "$response" | jq -r '.status // "unknown"' 2>/dev/null || echo "unknown")
    else
        status_code=$(curl -s -o /dev/null -w "%{http_code}" -m 10 "$url" 2>/dev/null || echo "000")
        health_status="unreachable"
    fi
    
    echo "$status_code:$health_status:$response"
}

# Get deployment info
get_deployment_info() {
    kubectl get deployment fortinet -n fortinet -o json 2>/dev/null | jq -r '{
        replicas: .spec.replicas,
        readyReplicas: .status.readyReplicas // 0,
        availableReplicas: .status.availableReplicas // 0,
        image: .spec.template.spec.containers[0].image,
        conditions: [.status.conditions[]? | select(.type=="Available" or .type=="Progressing")]
    }' 2>/dev/null || echo '{"replicas":0,"readyReplicas":0,"availableReplicas":0}'
}

# Auto-recovery function
trigger_recovery() {
    local failure_type=$1
    
    error "Triggering auto-recovery for: $failure_type"
    
    case $failure_type in
        "health_failure")
            log "Attempting to restart pods..."
            kubectl rollout restart deployment/fortinet -n fortinet
            kubectl rollout status deployment/fortinet -n fortinet --timeout=300s
            ;;
        "deployment_issue")
            log "Triggering ArgoCD sync..."
            argocd app sync fortinet --grpc-web --prune --force
            kubectl rollout status deployment/fortinet -n fortinet --timeout=300s
            ;;
        *)
            warning "Unknown failure type: $failure_type"
            ;;
    esac
    
    log "Recovery action completed, waiting for stabilization..."
    sleep 60
}

# Generate status report
generate_status_report() {
    local health_result=$1
    local deployment_info=$2
    
    local timestamp=$(date -Iseconds)
    local status_code=$(echo "$health_result" | cut -d':' -f1)
    local health_status=$(echo "$health_result" | cut -d':' -f2)
    local health_response=$(echo "$health_result" | cut -d':' -f3-)
    
    cat << EOF
{
    "timestamp": "$timestamp",
    "health": {
        "status_code": $status_code,
        "health_status": "$health_status",
        "response": $health_response
    },
    "deployment": $deployment_info,
    "monitoring": {
        "consecutive_failures": $consecutive_failures,
        "consecutive_successes": $consecutive_successes,
        "last_status": "$last_status",
        "failure_threshold": $FAILURE_THRESHOLD,
        "success_threshold": $SUCCESS_THRESHOLD
    }
}
EOF
}

# Main monitoring loop
monitor_health() {
    log "Starting continuous health monitoring..."
    log "Health URL: $HEALTH_URL"
    log "Check interval: ${CHECK_INTERVAL}s"
    log "Failure threshold: $FAILURE_THRESHOLD"
    log "Log file: $LOG_FILE"
    
    while true; do
        # Check internal health
        local internal_health
        internal_health=$(check_health "$HEALTH_URL" "internal")
        
        local status_code=$(echo "$internal_health" | cut -d':' -f1)
        local health_status=$(echo "$internal_health" | cut -d':' -f2)
        
        # Get deployment info
        local deployment_info
        deployment_info=$(get_deployment_info)
        
        # Analyze health status
        if [ "$status_code" = "200" ] && [ "$health_status" = "healthy" ]; then
            # Health check passed
            consecutive_failures=0
            consecutive_successes=$((consecutive_successes + 1))
            
            if [ "$last_status" != "healthy" ]; then
                success "Application health restored"
            elif [ $((consecutive_successes % 10)) -eq 0 ]; then
                success "Health check passed ($consecutive_successes consecutive)"
            fi
            
            last_status="healthy"
            
        else
            # Health check failed
            consecutive_successes=0
            consecutive_failures=$((consecutive_failures + 1))
            
            error "Health check failed (attempt $consecutive_failures/$FAILURE_THRESHOLD)"
            error "Status: $status_code, Health: $health_status"
            
            # Check deployment status
            local ready_replicas=$(echo "$deployment_info" | jq -r '.readyReplicas')
            local total_replicas=$(echo "$deployment_info" | jq -r '.replicas')
            
            log "Deployment status: $ready_replicas/$total_replicas ready"
            
            # Trigger recovery if threshold reached
            if [ $consecutive_failures -ge $FAILURE_THRESHOLD ]; then
                if [ "$ready_replicas" != "$total_replicas" ]; then
                    trigger_recovery "deployment_issue"
                else
                    trigger_recovery "health_failure"
                fi
                
                # Reset failure counter after recovery attempt
                consecutive_failures=0
            fi
            
            last_status="unhealthy"
        fi
        
        # Generate and save status report
        local report
        report=$(generate_status_report "$internal_health" "$deployment_info")
        echo "$report" > "/tmp/health-status-latest.json"
        
        # Wait before next check
        sleep $CHECK_INTERVAL
    done
}

# Signal handlers for graceful shutdown
cleanup() {
    log "Received termination signal, stopping health monitor..."
    success "Health monitor stopped gracefully"
    exit 0
}

trap cleanup SIGTERM SIGINT

# Main execution
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    # Create log directory if needed
    mkdir -p "$(dirname "$LOG_FILE")"
    
    # Start monitoring
    monitor_health
fi