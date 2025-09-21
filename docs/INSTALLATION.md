# Installation Guide

## Prerequisites

### 1. Python Installation

**Windows:**
```bash
# Download from https://www.python.org/downloads/
# Make sure to check "Add Python to PATH" during installation
```

**macOS:**
```bash
# Using Homebrew
brew install python@3.11
```

**Linux:**
```bash
sudo apt update
sudo apt install python3.11 python3-pip
```

### 2. Ollama Installation

**macOS/Linux:**
```bash
curl https://ollama.ai/install.sh | sh
```

**Windows:**
1. Download from https://ollama.ai/download
2. Run the installer
3. Verify installation: `ollama --version`

### 3. Pull LLM Model

```bash
# Recommended model (13B parameters)
ollama pull llama2:13b

# Alternative models
ollama pull mixtral:8x7b  # Better quality
ollama pull llama2:7b     # Faster
```

## Project Setup

### 1. Clone Repository

```bash
git clone https://github.com/vikkysarswat/trade_analysis_dhan.git
cd trade_analysis_dhan
```

### 2. Create Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Verify Installation

```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Test the analyzer
python main.py data/sample_trades.csv --trader-name "Test"
```

## Troubleshooting

### Ollama Not Running

**Error:** `Connection refused to localhost:11434`

**Solution:**
```bash
# Start Ollama service
ollama serve

# In another terminal, verify
curl http://localhost:11434/api/tags
```

### Import Errors

**Error:** `ModuleNotFoundError: No module named 'pandas'`

**Solution:**
```bash
# Ensure virtual environment is activated
pip install -r requirements.txt --upgrade
```

### Memory Issues

**Error:** `Out of memory`

**Solution:**
```bash
# Use a smaller model
ollama pull llama2:7b

# Update config.yaml
ollama:
  model: "llama2:7b"
```

## Configuration

Edit `config.yaml` to customize:

```yaml
ollama:
  model: "llama2:13b"  # Change model here
  temperature: 0.7     # Adjust creativity

analysis:
  min_trades: 20      # Minimum trades for analysis
```

## Next Steps

1. Prepare your trading data (CSV format)
2. Run analysis: `python main.py your_trades.csv`
3. View reports in `data/reports/`

For more help, see [Usage Guide](USAGE.md)
