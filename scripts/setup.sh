#!/bin/bash

# Setup script for Trade Analysis Dhan

set -e

echo "🚀 Setting up Trade Analysis Dhan..."
echo ""

# Check Python version
echo "📌 Checking Python version..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "   Found Python $PYTHON_VERSION"

# Check Ollama
echo "📌 Checking Ollama installation..."
if ! command -v ollama &> /dev/null; then
    echo "⚠️  Ollama is not installed."
    echo "   Please install from: https://ollama.ai/download"
    echo "   Or run: curl https://ollama.ai/install.sh | sh"
else
    echo "   ✓ Ollama is installed"
    
    # Check if Ollama is running
    if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
        echo "   ✓ Ollama is running"
    else
        echo "   ⚠️  Ollama is not running. Start it with: ollama serve"
    fi
fi

# Create virtual environment
echo "📌 Creating virtual environment..."
if [ -d "venv" ]; then
    echo "   Virtual environment already exists"
else
    python3 -m venv venv
    echo "   ✓ Virtual environment created"
fi

# Activate virtual environment
echo "📌 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📌 Installing dependencies..."
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt > /dev/null 2>&1
echo "   ✓ Dependencies installed"

# Create necessary directories
echo "📌 Creating project directories..."
mkdir -p data/{raw,processed,reports}
echo "   ✓ Directories created"

# Download Ollama model (if Ollama is installed)
if command -v ollama &> /dev/null; then
    echo "📌 Checking for Ollama models..."
    if ollama list | grep -q "llama2:13b"; then
        echo "   ✓ Model llama2:13b already exists"
    else
        echo "   Downloading llama2:13b model (this may take a few minutes)..."
        ollama pull llama2:13b
        echo "   ✓ Model downloaded"
    fi
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "  1. Activate virtual environment: source venv/bin/activate"
echo "  2. Add your trading data to data/raw/"
echo "  3. Run analysis: python main.py data/raw/your_trades.csv"
echo "  4. View reports in data/reports/"
echo ""
echo "For help: python main.py --help"
