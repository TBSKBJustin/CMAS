#!/bin/bash
# Start script for Church Media Automation System

echo "🚀 Starting Church Media Automation System..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run setup first:"
    echo "   python3 -m venv venv"
    echo "   source venv/bin/activate"
    echo "   pip install -r requirements.txt"
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Check dependencies
echo "📋 Checking dependencies..."
python utils/dependency_manager.py check --quiet

# Start API server in background
echo "🔧 Starting API server on port 5000..."
uvicorn api_server:app --host 0.0.0.0 --port 5000 &
API_PID=$!

# Wait for API to be ready
sleep 2

# Start frontend
echo "🎨 Starting frontend on port 3000..."
cd frontend
npm run dev &
FRONTEND_PID=$!

echo ""
echo "✅ System started!"
echo "📱 Web interface: http://localhost:3000"
echo "🔌 API server: http://localhost:5000"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for Ctrl+C
trap "echo 'Stopping services...'; kill $API_PID $FRONTEND_PID; exit" INT
wait
