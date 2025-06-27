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

# Ensure directories exist with proper permissions
echo "📦 Checking directory permissions..."
if [ ! -d "/app/data" ]; then
    echo "❌ Error: /app/data directory not found"
    exit 1
fi

if [ ! -d "/app/logs" ]; then
    echo "❌ Error: /app/logs directory not found"
    exit 1
fi

# Start the server
echo "🔧 Starting Flask Development Server (temporary)..."
echo "⚠️ Note: Production deployment pending Gunicorn fix"

exec python src/main.py --web