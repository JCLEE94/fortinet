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

# Start the real FortiGate Nextrade application
echo "🔧 Starting FortiGate Nextrade Application..."
echo "📍 Current directory: $(pwd)"
echo "📁 Files in /app: $(ls -la /app/)"

# Start real application
cd /app/src && exec python main.py --web