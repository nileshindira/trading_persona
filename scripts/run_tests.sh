#!/bin/bash

# Run tests script

set -e

echo "🧪 Running tests..."
echo ""

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Run flake8 linting
echo "📝 Running flake8 linting..."
flake8 src/ --count --select=E9,F63,F7,F82 --show-source --statistics
flake8 src/ --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
echo "   ✓ Linting passed"

# Run tests with pytest
echo "📝 Running pytest..."
pytest tests/ -v --cov=src --cov-report=term-missing
echo "   ✓ Tests passed"

echo ""
echo "✅ All checks passed!"
