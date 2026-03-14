#!/usr/bin/env bash
# Kill everything — backend, frontend, Docker services
set -e

cd "$(dirname "$0")"

echo "Stopping backend (uvicorn)..."
pkill -f "uvicorn app.main:app" 2>/dev/null && echo "  killed" || echo "  not running"

echo "Stopping frontend (next-server)..."
pkill -f "next-server" 2>/dev/null && echo "  killed" || echo "  not running"
pkill -f "next dev" 2>/dev/null || true

echo "Stopping Docker services..."
docker-compose down

echo ""
echo "=== Everything stopped ==="
