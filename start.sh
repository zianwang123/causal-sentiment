#!/usr/bin/env bash
# Quick launch — assumes everything is installed
set -e

cd "$(dirname "$0")"

echo "Starting DB + Redis..."
docker-compose up db redis -d

echo "Waiting for DB to be ready..."
until docker exec causal-sentiment-db-1 pg_isready -U cs_user -q 2>/dev/null; do
  sleep 1
done

echo "Starting backend..."
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload --port 8000 &
BACKEND_PID=$!
cd ..

echo "Starting frontend..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "=== All services running ==="
echo "Frontend:  http://localhost:3000"
echo "Backend:   http://localhost:8000"
echo "Health:    http://localhost:8000/api/health"
echo ""
echo "To stop everything:  ./stop.sh"

# Wait for either process to exit
wait $BACKEND_PID $FRONTEND_PID
