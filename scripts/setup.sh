#!/bin/bash

echo "🚀 Setting up QCYIS Project..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv .venv

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source .venv/bin/activate

# Install backend dependencies
echo "📚 Installing backend dependencies..."
pip install -r backend/requirements.txt

# Install MCP server dependencies
echo "🔧 Installing MCP server dependencies..."
pip install -r mcp-server/requirements.txt

# Check if Ollama is installed
if ! command -v ollama &> /dev/null; then
    echo "🤖 Installing Ollama..."
    curl -fsSL https://ollama.com/install.sh | sh
else
    echo "✅ Ollama already installed"
fi

# Pull Llama model
echo "🧠 Downloading Llama 3.1 model (this may take a while)..."
ollama pull llama3.1

# Create necessary directories
echo "📁 Creating project directories..."
mkdir -p data/sessions
mkdir -p logs

# Set permissions for scripts
echo "🔐 Setting script permissions..."
chmod +x scripts/*.sh

echo "✅ Setup complete!"
echo ""
echo "🎯 Next steps:"
echo "1. Run: ./scripts/run_all.sh"
echo "2. Open browser to: http://localhost:3000"
echo "3. Allow camera permissions when prompted"
echo ""
echo "🔗 Service URLs:"
echo "  - Frontend: http://localhost:3000"
echo "  - Backend: http://localhost:8000"
echo "  - MCP Server: http://localhost:8033"
