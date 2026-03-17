#!/usr/bin/env bash
# First-time setup for new users
set -e

cd "$(dirname "$0")"

echo "=== Causal Sentiment — First Time Setup ==="
echo ""

# Check prerequisites
for cmd in docker docker-compose python3 node npm; do
  if ! command -v $cmd &>/dev/null; then
    echo "ERROR: $cmd is not installed. Please install it first."
    exit 1
  fi
done
echo "Prerequisites OK (docker, python3, node, npm)"

# .env file
if [ ! -f .env ]; then
  cp .env.example .env
  echo ""
  echo "Created .env from .env.example"
  echo ">>> IMPORTANT: Edit .env and add your ANTHROPIC_API_KEY <<<"
  echo ""
else
  echo ".env already exists, skipping"
fi

# Start DB + Redis
echo "Starting DB + Redis..."
docker-compose up db redis -d

echo "Waiting for DB to be ready..."
DB_CONTAINER=$(docker-compose ps -q db)
until docker exec "$DB_CONTAINER" pg_isready -U cs_user -q 2>/dev/null; do
  sleep 1
done
echo "DB ready"

# Backend
echo "Setting up backend..."
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt -q
cd ..
echo "Backend dependencies installed"

# Frontend
echo "Setting up frontend..."
cd frontend
npm install --silent
cd ..
echo "Frontend dependencies installed"

echo ""
echo "=== Setup complete ==="
echo "Run ./start.sh to launch"
echo ""
echo "Make sure to set ANTHROPIC_API_KEY in .env before running analysis!"
