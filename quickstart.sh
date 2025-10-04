#!/bin/bash

# Quick Start Script for Trading Analysis System
# This script helps you get started quickly

echo "========================================"
echo "Trading Analysis System - Quick Start"
echo "========================================"
echo ""

# Check Python version
echo "1. Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "   Found: Python $python_version"

if ! command -v python3 &> /dev/null; then
    echo "   ❌ Python 3 is not installed!"
    exit 1
fi
echo "   ✅ Python 3 is available"
echo ""

# Check if virtual environment exists
echo "2. Checking virtual environment..."
if [ ! -d "venv" ]; then
    echo "   Creating virtual environment..."
    python3 -m venv venv
    echo "   ✅ Virtual environment created"
else
    echo "   ✅ Virtual environment exists"
fi
echo ""

# Activate virtual environment
echo "3. Activating virtual environment..."
source venv/bin/activate
echo "   ✅ Virtual environment activated"
echo ""

# Install dependencies
echo "4. Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt
echo "   ✅ Dependencies installed"
echo ""

# Check Ollama (optional)
echo "5. Checking Ollama (optional for AI analysis)..."
if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "   ✅ Ollama is running"
    models=$(curl -s http://localhost:11434/api/tags | grep -o '"name":"[^"]*"' | head -3)
    echo "   Available models: $models"
else
    echo "   ⚠️  Ollama is not running (AI analysis will be skipped)"
    echo "   To install: curl https://ollama.ai/install.sh | sh"
    echo "   Then run: ollama pull llama2:13b"
fi
echo ""

# Run integration tests
echo "6. Running integration tests..."
python tests/test_integration.py
test_result=$?

if [ $test_result -eq 0 ]; then
    echo ""
    echo "========================================"
    echo "✅ ALL SYSTEMS READY!"
    echo "========================================"
    echo ""
    echo "Quick commands to try:"
    echo ""
    echo "  # Test with sample data (no AI):"
    echo "  python main.py data/sample_trades.csv --trader-name 'Sample' --no-ema"
    echo ""
    echo "  # Full analysis with AI (requires Ollama):"
    echo "  python main.py data/sample_trades.csv --trader-name 'Sample'"
    echo ""
    echo "  # Analyze your own data:"
    echo "  python main.py /path/to/your/trades.csv --trader-name 'YourName'"
    echo ""
    echo "Reports will be saved in: data/reports/"
    echo ""
else
    echo ""
    echo "========================================"
    echo "❌ Tests failed - please check errors above"
    echo "========================================"
    exit 1
fi
