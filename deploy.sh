#!/bin/bash
# ── Stock Analysis Platform — Docker Deploy Script ───────────────────────────
set -e

echo "🐳 Building and starting Stock Analysis Platform..."

# Stop any running containers
docker compose down --remove-orphans 2>/dev/null || true

# Build images (no cache for clean build)
echo "📦 Building Docker images..."
docker compose build --no-cache

# Start services
echo "🚀 Starting services..."
docker compose up -d

# Wait for health checks
echo "⏳ Waiting for services to be healthy..."
sleep 10

# Show status
docker compose ps

echo ""
echo "✅ Deployment complete!"
echo "   FastAPI  → http://localhost:8000"
echo "   API Docs → http://localhost:8000/docs"
echo "   Streamlit → http://localhost:8501"
echo ""
echo "📋 View logs: docker compose logs -f"
echo "🛑 Stop:      docker compose down"
