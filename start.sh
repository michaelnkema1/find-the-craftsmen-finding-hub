#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# Find Platform — Start Script
# Usage:  ./start.sh
# Starts the FastAPI backend (port 8000) + frontend server (port 3000)
# ─────────────────────────────────────────────────────────────────────────────

AMBER='\033[0;33m'; GREEN='\033[0;32m'; RED='\033[0;31m'; BLUE='\033[0;34m'; NC='\033[0m'
BOLD='\033[1m'

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
BACKEND_DIR="$SCRIPT_DIR/backend"
FRONTEND_DIR="$SCRIPT_DIR/frontend"
VENV="$BACKEND_DIR/.venv"
BACKEND_PORT=8000
FRONTEND_PORT=3000

echo ""
echo -e "${AMBER}${BOLD}╔══════════════════════════════════════════╗${NC}"
echo -e "${AMBER}${BOLD}║        Find Platform — Starting Up        ║${NC}"
echo -e "${AMBER}${BOLD}╚══════════════════════════════════════════╝${NC}"
echo ""

# ── Trap Ctrl+C ───────────────────────────────────────────────────────────────
cleanup() {
  echo ""
  echo -e "${RED}Shutting down…${NC}"
  [ -n "$BACKEND_PID" ]  && kill "$BACKEND_PID"  2>/dev/null
  [ -n "$FRONTEND_PID" ] && kill "$FRONTEND_PID" 2>/dev/null
  exit 0
}
trap cleanup INT TERM

# ── Check .env ────────────────────────────────────────────────────────────────
if [ ! -f "$BACKEND_DIR/.env" ]; then
  echo -e "${RED}✗  Missing backend/.env${NC}"
  echo -e "   Copy the example: ${BLUE}cp backend/.env.example backend/.env${NC}"
  echo -e "   Then fill in your DATABASE_URL, SECRET_KEY, and AES_KEY."
  exit 1
fi
echo -e "${GREEN}✓${NC}  .env found"

# ── Create venv if missing ────────────────────────────────────────────────────
if [ ! -d "$VENV" ]; then
  echo -e "${BLUE}→${NC}  Creating Python virtual environment…"
  python3 -m venv "$VENV"
fi
echo -e "${GREEN}✓${NC}  Virtual environment ready"

# ── Install / sync dependencies ───────────────────────────────────────────────
echo -e "${BLUE}→${NC}  Checking Python dependencies…"
"$VENV/bin/pip" install -r "$BACKEND_DIR/requirements.txt" -q --disable-pip-version-check
echo -e "${GREEN}✓${NC}  Dependencies up to date"

# ── Clear ports if already in use ────────────────────────────────────────────
clear_port() {
  local port=$1
  local pids
  pids=$(lsof -ti tcp:"$port" 2>/dev/null)
  if [ -n "$pids" ]; then
    echo -e "${AMBER}⚠${NC}  Port $port in use — stopping existing process…"
    echo "$pids" | xargs kill -TERM 2>/dev/null
    for i in 1 2 3; do
      sleep 1
      lsof -ti tcp:"$port" &>/dev/null || break
    done
    pids=$(lsof -ti tcp:"$port" 2>/dev/null)
    if [ -n "$pids" ]; then
      echo "$pids" | xargs kill -9 2>/dev/null
    fi
  fi
}
clear_port "$BACKEND_PORT"
clear_port "$FRONTEND_PORT"

# ── Start backend ─────────────────────────────────────────────────────────────
echo ""
echo -e "${BLUE}→${NC}  Starting backend on ${BOLD}http://localhost:$BACKEND_PORT${NC}"
cd "$BACKEND_DIR"
"$VENV/bin/uvicorn" main:app --reload --port "$BACKEND_PORT" --log-level warning &
BACKEND_PID=$!

# Give uvicorn a moment to boot before starting frontend
sleep 2

# Confirm backend is up
if kill -0 "$BACKEND_PID" 2>/dev/null; then
  echo -e "${GREEN}✓${NC}  Backend running (PID $BACKEND_PID)"
else
  echo -e "${RED}✗  Backend failed to start. Check your DATABASE_URL in backend/.env${NC}"
  exit 1
fi

# ── Start frontend ────────────────────────────────────────────────────────────
echo -e "${BLUE}→${NC}  Starting frontend on ${BOLD}http://localhost:$FRONTEND_PORT${NC}"
cd "$FRONTEND_DIR"
python3 -m http.server "$FRONTEND_PORT" 2>/dev/null &
FRONTEND_PID=$!
sleep 1

if kill -0 "$FRONTEND_PID" 2>/dev/null; then
  echo -e "${GREEN}✓${NC}  Frontend running (PID $FRONTEND_PID)"
else
  echo -e "${RED}✗  Frontend failed to start (port $FRONTEND_PORT may still be in use — wait a moment and retry)${NC}"
  kill "$BACKEND_PID" 2>/dev/null
  exit 1
fi

# ── Ready ─────────────────────────────────────────────────────────────────────
echo ""
echo -e "${AMBER}${BOLD}╔══════════════════════════════════════════╗${NC}"
echo -e "${AMBER}${BOLD}║  ✅  Find Platform is live!               ║${NC}"
echo -e "${AMBER}${BOLD}║                                           ║${NC}"
echo -e "${AMBER}${BOLD}║  🌐  Frontend:  http://localhost:3000     ║${NC}"
echo -e "${AMBER}${BOLD}║  ⚙️   Backend:   http://localhost:8000     ║${NC}"
echo -e "${AMBER}${BOLD}║  📖  API Docs:  http://localhost:8000/docs║${NC}"
echo -e "${AMBER}${BOLD}║                                           ║${NC}"
echo -e "${AMBER}${BOLD}║  Demo password (all accounts): demo1234   ║${NC}"
echo -e "${AMBER}${BOLD}║                                           ║${NC}"
echo -e "${AMBER}${BOLD}║  Press Ctrl+C to stop                     ║${NC}"
echo -e "${AMBER}${BOLD}╚══════════════════════════════════════════╝${NC}"
echo ""

# Keep script alive
wait "$BACKEND_PID" "$FRONTEND_PID"
