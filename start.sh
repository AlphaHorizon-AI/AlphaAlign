#!/bin/bash
echo "========================================================"
echo "Starting AlphaAlign"
echo "========================================================"

# Start backend in background
echo "Starting Backend Server (port 8000)..."
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000 &
BACKEND_PID=$!
cd ..

sleep 3

# Start frontend in background
echo "Starting Frontend Development Server (port 5173)..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

sleep 3

# Open browser
if command -v xdg-open &> /dev/null; then
    xdg-open http://localhost:5173
elif command -v open &> /dev/null; then
    open http://localhost:5173
fi

echo ""
echo "Both servers are running in the background."
echo "Browser opened to http://localhost:5173"
echo "Press Ctrl+C to stop both servers."

# Wait for user interrupt to kill both processes
trap "kill $BACKEND_PID $FRONTEND_PID; exit" SIGINT SIGTERM
wait
