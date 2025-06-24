#!/bin/bash
# FortiGate Nextrade Docker Compose Startup Script

set -e

echo "🚀 Starting FortiGate Nextrade with Docker Compose..."

# Check if Docker is running
if ! docker info >/dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Login to private registry
echo "🔑 Logging into private registry..."
echo "bingogo1l7!" | docker login registry.jclee.me -u qws941 --password-stdin

# Pull latest image
echo "📥 Pulling latest image..."
docker pull registry.jclee.me/fortinet:latest

# Start services
echo "🐳 Starting services..."
docker-compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 10

# Check service status
echo "📊 Service Status:"
docker-compose ps

# Show logs
echo "📋 Recent logs:"
docker-compose logs --tail=20

echo "✅ FortiGate Nextrade is running!"
echo "🌐 Access at: http://localhost:7777"
echo "📊 Health check: http://localhost:7777/api/health"