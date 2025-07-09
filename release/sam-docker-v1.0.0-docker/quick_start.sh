#!/bin/bash
# SAM Docker Quick Start Script

set -e

echo "🐳 SAM Docker Quick Start"
echo "========================="

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    echo "   Windows: Install Docker Desktop from https://docs.docker.com/desktop/windows/"
    echo "   Linux: Visit https://docs.docker.com/engine/install/"
    echo "   macOS: Install Docker Desktop from https://docs.docker.com/desktop/mac/"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    echo "   Note: Docker Desktop includes Docker Compose"
    echo "   Visit: https://docs.docker.com/compose/install/"
    exit 1
fi

echo "✅ Docker and Docker Compose found"

# Pull images
echo "📥 Pulling SAM Docker images..."
docker-compose pull

# Start services
echo "🚀 Starting SAM services..."
docker-compose up -d

echo "⏳ Waiting for services to start..."
sleep 15

# Check if services are running
if docker-compose ps | grep -q "Up"; then
    echo "✅ SAM is now running!"
    echo ""
    echo "🌟 Access SAM at:"
    echo "   Main Interface:     http://localhost:8502"
    echo "   Memory Center:      http://localhost:8501"
    echo "   Setup Page:         http://localhost:8503"
    echo ""
    echo "📚 For more information, see DOCKER_DEPLOYMENT_GUIDE.md"
    echo "🛠️  For management commands, use: ./manage_sam.sh"
else
    echo "❌ Failed to start SAM services"
    echo "📋 Checking logs..."
    docker-compose logs
    exit 1
fi
