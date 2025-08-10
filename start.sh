#!/bin/bash
# =============================================================================
# FortiGate Nextrade - Production Startup Script
# =============================================================================

set -e

echo "🚀 FortiGate Nextrade - Production Mode"
echo "=============================================="

# Check build information
if [ -f "/app/build-info.txt" ]; then
    echo "📋 Build Information:"
    cat /app/build-info.txt
fi

# Environment validation
echo "🔧 Environment Configuration:"
echo "APP_MODE: ${APP_MODE:-production}"
echo "WEB_APP_HOST: ${WEB_APP_HOST:-0.0.0.0}"
echo "WEB_APP_PORT: ${WEB_APP_PORT:-7777}"
echo "PYTHONPATH: ${PYTHONPATH}"

# Create necessary directories
mkdir -p /app/data /app/logs /app/temp

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

# Start the application with production settings
if [ "${FLASK_ENV}" = "production" ] && command -v gunicorn >/dev/null 2>&1; then
    echo "🌟 Starting with Gunicorn (Production)"
    exec gunicorn \
        --bind ${WEB_APP_HOST:-0.0.0.0}:${WEB_APP_PORT:-7777} \
        --workers ${WORKERS:-4} \
        --worker-class ${WORKER_CLASS:-gevent} \
        --worker-connections ${WORKER_CONNECTIONS:-1000} \
        --max-requests ${MAX_REQUESTS:-1000} \
        --max-requests-jitter ${MAX_REQUESTS_JITTER:-100} \
        --timeout ${TIMEOUT:-120} \
        --keepalive ${KEEPALIVE:-5} \
        --access-logfile - \
        --error-logfile - \
        --log-level info \
        --preload \
        --chdir /app/src \
        main:app
else
    echo "🔧 Starting with Flask Dev Server"
    cd /app/src
    exec python3 main.py --web
fi