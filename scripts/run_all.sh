#!/bin/bash

echo "🚀 Starting QCYIS System..."

# Activate virtual environment
source .venv/bin/activate

# Start backend server
echo "🔧 Starting backend server..."
python backend/app/main.py &
BACKEND_PID=$!

# Wait for backend to start
sleep 3

# Start MCP server
echo "🤖 Starting MCP server..."
python mcp-server/server.py &
MCP_PID=$!

# Wait for MCP server to start
sleep 2

# Start simple HTTP server for frontend
echo "🌐 Starting frontend server..."
cd frontend
python -m http.server 3000 &
FRONTEND_PID=$!
cd ..

echo "✅ All services started!"
echo ""
echo "🔗 Access URLs:"
echo "  - Frontend: http://localhost:3000"
echo "  - Backend API: http://localhost:8000"
echo "  - MCP Server: http://localhost:8033"
echo ""
echo "📱 Instructions:"
echo "1. Open http://localhost:3000 in your browser"
echo "2. Click 'Start Camera' and allow permissions"
echo "3. Click 'Start Pose Detection' to begin"
echo "4. Chat with the AI assistant for yoga guidance"
echo ""
echo "🛑 To stop all services: Ctrl+C"

# Wait for user interrupt
trap 'kill $BACKEND_PID $MCP_PID $FRONTEND_PID; echo "🛑 All services stopped."; exit' INT
wait
#!/bin/bash

echo "🚀 Starting QCYIS System..."

# Activate virtual environment
source .venv/bin/activate

# Start backend server
echo "🔧 Starting backend server..."
python backend/app/main.py &
BACKEND_PID=$!

# Wait for backend to start
sleep 3

# Start MCP server
echo "🤖 Starting MCP server..."
python mcp-server/server.py &
MCP_PID=$!

# Wait for MCP server to start
sleep 2

# Start simple HTTP server for frontend
echo "🌐 Starting frontend server..."
cd frontend
python -m http.server 3000 &
FRONTEND_PID=$!
cd ..

echo "✅ All services started!"
echo ""
echo "🔗 Access URLs:"
echo "  - Frontend: http://localhost:3000"
echo "  - Backend API: http://localhost:8000"
echo "  - MCP Server: http://localhost:8033"
echo ""
echo "📱 Instructions:"
echo "1. Open http://localhost:3000 in your browser"
echo "2. Click 'Start Camera' and allow permissions"
echo "3. Click 'Start Pose Detection' to begin"
echo "4. Chat with the AI assistant for yoga guidance"
echo ""
echo "🛑 To stop all services: Ctrl+C"

# Wait for user interrupt
trap 'kill $BACKEND_PID $MCP_PID $FRONTEND_PID; echo "🛑 All services stopped."; exit' INT
wait
