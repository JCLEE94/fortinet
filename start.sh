#!/bin/bash
echo "🚀 Starting FortiGate Nextrade Production Server..."
echo "📍 Mode: ${APP_MODE}"
echo "🌐 Host: ${WEB_APP_HOST}:${WEB_APP_PORT}"
echo "💾 Data Dir: /app/data"
echo "📁 Logs Dir: /app/logs"

# Environment variable validation
if [ -z "$APP_MODE" ]; then
    echo "⚠️ APP_MODE not set, using default: production"
    export APP_MODE="production"
fi

# Set PYTHONPATH to include src directory
export PYTHONPATH=/app:/app/src:$PYTHONPATH

# Start the server
echo "🔧 Starting Flask Development Server (simple mode)..."
echo "📍 PYTHONPATH: $PYTHONPATH"

# Simple approach - direct execution
cd /app/src && exec python main.py --web