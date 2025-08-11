#!/bin/bash
# =============================================================================
# FortiGate Nextrade - GitOps Production Startup Script
# GitOps 4원칙 준수: 불변 인프라 실행 환경
# =============================================================================

set -e

echo "🚀 FortiGate Nextrade - GitOps Production Mode"
echo "================================================="

# GitOps 불변성 검증: 빌드 정보 표시
if [ -f "/app/build-info.txt" ]; then
    echo "📋 GitOps Immutable Build Information:"
    cat /app/build-info.txt
    echo ""
fi

# GitOps JSON 메타데이터 검증
if [ -f "/app/build-info.json" ]; then
    echo "🔍 GitOps Metadata Validation:"
    if command -v python3 >/dev/null 2>&1; then
        python3 -c "
import json, os
try:
    with open('/app/build-info.json', 'r') as f:
        build_info = json.load(f)
    
    # GitOps 원칙 검증
    gitops = build_info.get('gitops', {})
    if gitops.get('immutable') == True:
        print('  ✅ GitOps Immutable: TRUE')
    else:
        print('  ❌ GitOps Immutable: FALSE')
    
    # 불변 태그 검증
    immutable_tag = build_info.get('build', {}).get('immutable_tag', 'unknown')
    env_tag = os.environ.get('IMMUTABLE_TAG', 'unknown')
    if immutable_tag == env_tag:
        print(f'  ✅ Immutable Tag Verified: {immutable_tag}')
    else:
        print(f'  ⚠️  Tag Mismatch - Build: {immutable_tag}, Env: {env_tag}')
    
    # GitOps 관리 도구 확인
    managed_by = gitops.get('managed_by', 'unknown')
    print(f'  📋 Managed by: {managed_by}')
    
except Exception as e:
    print(f'  ❌ Metadata validation failed: {e}')
"
    fi
    echo ""
fi

# Environment validation
echo "🔧 Environment Configuration:"
echo "APP_MODE: ${APP_MODE:-production}"
echo "WEB_APP_HOST: ${WEB_APP_HOST:-0.0.0.0}"
echo "WEB_APP_PORT: ${WEB_APP_PORT:-7777}"
echo "PYTHONPATH: ${PYTHONPATH}"

# Create necessary directories
mkdir -p /app/data /app/logs /app/temp /app/src/logs

# Pre-flight checks
echo "🔍 Pre-flight Checks:"

# Check Python import paths
echo "  ✓ Checking Python imports..."
cd /app/src
python3 -c "
import sys
sys.path.insert(0, '/app/src')
try:
    import main
    print('  ✓ Main module import successful')
except ImportError as e:
    print(f'  ✗ Main module import failed: {e}')
    sys.exit(1)
" || exit 1

# Check if we're in test/offline mode
if [ "${APP_MODE}" = "test" ]; then
    echo "  🧪 Test mode enabled - using mock services"
    export OFFLINE_MODE=true
fi

# Health check endpoint validation
echo "  ✓ Starting application..."

# GitOps 4원칙 준수: 불변 운영 환경 시작
if [ "${FLASK_ENV}" = "production" ] && command -v gunicorn >/dev/null 2>&1; then
    echo "🌟 Starting GitOps Production Environment with Gunicorn"
    echo "📊 Production Configuration:"
    echo "  Workers: ${WORKERS:-4}"
    echo "  Worker Class: ${WORKER_CLASS:-gevent}"
    echo "  Worker Connections: ${WORKER_CONNECTIONS:-1000}"
    echo "  Max Requests: ${MAX_REQUESTS:-1000}"
    echo "  Timeout: ${TIMEOUT:-120}s"
    echo "  Keep-Alive: ${KEEPALIVE:-5}s"
    echo "  Immutable Tag: ${IMMUTABLE_TAG:-unknown}"
    echo ""
    
    # GitOps 불변 환경에서 Gunicorn 실행
    exec gunicorn \
        --bind ${WEB_APP_HOST:-0.0.0.0}:${WEB_APP_PORT:-7777} \
        --workers ${WORKERS:-4} \
        --worker-class ${WORKER_CLASS:-gevent} \
        --worker-connections ${WORKER_CONNECTIONS:-1000} \
        --max-requests ${MAX_REQUESTS:-1000} \
        --max-requests-jitter ${MAX_REQUESTS_JITTER:-100} \
        --timeout ${TIMEOUT:-120} \
        --keep-alive ${KEEPALIVE:-5} \
        --access-logfile - \
        --error-logfile - \
        --log-level info \
        --preload \
        --enable-stdio-inheritance \
        --capture-output \
        --chdir /app/src \
        --env IMMUTABLE_TAG="${IMMUTABLE_TAG:-unknown}" \
        --env GITOPS_MANAGED="true" \
        web_app:app
else
    echo "🔧 Starting Development Mode with Flask Server"
    echo "⚠️  WARNING: Not using immutable production configuration"
    cd /app/src
    exec python3 main.py --web
fi