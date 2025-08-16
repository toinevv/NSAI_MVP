#!/bin/bash

# NewSystem.AI Development Startup Script
# Starts both frontend and backend services for local development
# Mission: Save 1,000,000 operator hours monthly through intelligent automation

set -e

echo "🚀 Starting NewSystem.AI Development Environment"
echo "Mission: Saving 1,000,000 operator hours monthly"
echo "=================================================="

# Check if required tools are installed
check_requirements() {
    echo "📋 Checking requirements..."
    
    if ! command -v node &> /dev/null; then
        echo "❌ Node.js is not installed. Please install Node.js 18+ and try again."
        exit 1
    fi
    
    if ! command -v python3 &> /dev/null; then
        echo "❌ Python 3 is not installed. Please install Python 3.11+ and try again."
        exit 1
    fi
    
    echo "✅ Requirements check passed"
}

# Function to kill existing processes
cleanup() {
    echo "🧹 Cleaning up existing processes..."
    pkill -f "vite" 2>/dev/null || true
    pkill -f "uvicorn" 2>/dev/null || true
    pkill -f "python -m app.main" 2>/dev/null || true
    sleep 2
}

# Setup backend
setup_backend() {
    echo "🔧 Setting up backend..."
    cd backend
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        echo "Creating Python virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment and install dependencies
    source venv/bin/activate
    pip install -q -r requirements.txt
    
    echo "✅ Backend setup complete"
    cd ..
}

# Setup frontend
setup_frontend() {
    echo "🎨 Setting up frontend..."
    cd frontend
    
    # Install dependencies if node_modules doesn't exist
    if [ ! -d "node_modules" ]; then
        echo "Installing frontend dependencies..."
        npm install
    fi
    
    echo "✅ Frontend setup complete"
    cd ..
}

# Start services
start_services() {
    echo "🚀 Starting services..."
    
    # Start backend in background
    echo "Starting FastAPI backend on http://localhost:8000..."
    cd backend
    source venv/bin/activate
    python -m app.main &
    BACKEND_PID=$!
    cd ..
    
    # Wait a moment for backend to start
    sleep 3
    
    # Start frontend in background
    echo "Starting React frontend on http://localhost:5173..."
    cd frontend
    npm run dev &
    FRONTEND_PID=$!
    cd ..
    
    echo ""
    echo "🎉 NewSystem.AI Development Environment Started!"
    echo "=================================================="
    echo "📱 Frontend:  http://localhost:5173"
    echo "🔧 Backend:   http://localhost:8000"
    echo "📚 API Docs:  http://localhost:8000/docs"
    echo ""
    echo "📊 Status Dashboard: Check frontend for connection status"
    echo "💡 Focus: Email → WMS workflow automation for logistics"
    echo ""
    echo "Press Ctrl+C to stop all services"
    echo "=================================================="
    
    # Store PIDs for cleanup
    echo $BACKEND_PID > .backend.pid
    echo $FRONTEND_PID > .frontend.pid
    
    # Wait for interrupt
    trap 'cleanup_and_exit' INT
    wait
}

cleanup_and_exit() {
    echo ""
    echo "🛑 Shutting down NewSystem.AI development environment..."
    
    # Kill background processes
    if [ -f .backend.pid ]; then
        kill $(cat .backend.pid) 2>/dev/null || true
        rm .backend.pid
    fi
    
    if [ -f .frontend.pid ]; then
        kill $(cat .frontend.pid) 2>/dev/null || true
        rm .frontend.pid
    fi
    
    cleanup
    echo "✅ Development environment stopped"
    echo "Ready to save 1,000,000 operator hours monthly! 🚀"
    exit 0
}

# Main execution
main() {
    check_requirements
    cleanup
    setup_backend
    setup_frontend
    start_services
}

# Run if executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi