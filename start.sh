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

# Debug mode - use simple server first
echo "🔧 Starting Simple Python Server (debug mode)..."
echo "📍 Current directory: $(pwd)"
echo "📁 Files in /app: $(ls -la /app/)"

# Start simple server for debugging
cd /app && exec python simple_server.py