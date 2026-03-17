#!/usr/bin/env bash
# Quick launch — assumes everything is installed
set -e

cd "$(dirname "$0")"

# Check for port conflicts before starting
check_port() {
  local port=$1 service=$2
  if ss -tlnp 2>/dev/null | grep -q ":${port} " || lsof -i :"${port}" -sTCP:LISTEN >/dev/null 2>&1; then
    echo "ERROR: Port ${port} is already in use (needed by ${service})."
    echo "  Find what's using it:  ss -tlnp | grep :${port}"
    echo "  Or:                    sudo lsof -i :${port}"
    echo "  Then stop that process and re-run ./start.sh"
    exit 1
  fi
}

echo "Checking for port conflicts..."
check_port 5432 "PostgreSQL"
check_port 6379 "Redis"
check_port 8000 "Backend (uvicorn)"
check_port 3000 "Frontend (Next.js)"
echo "  All ports available"

echo "Starting DB + Redis..."
docker-compose up db redis -d

echo "Waiting for DB to be ready..."
DB_CONTAINER=$(docker-compose ps -q db)
until docker exec "$DB_CONTAINER" pg_isready -U cs_user -q 2>/dev/null; do
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
