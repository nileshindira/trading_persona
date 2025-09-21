# 🚀 Trading Persona Analyzer - Dhan Edition

AI-powered trading analysis system using local LLMs (Ollama) to analyze trading patterns, detect behavioral issues, and provide actionable insights.

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Ollama](https://img.shields.io/badge/LLM-Ollama-orange.svg)

## 🎯 Features

- 📊 **Comprehensive Metrics**: Sharpe ratio, max drawdown, win rate, and 20+ metrics
- 🔍 **Pattern Detection**: Identifies overtrading, revenge trading, scalping, hedging
- 🤖 **AI Analysis**: Uses Ollama (Llama2, Mixtral) for natural language insights
- 📈 **Professional Reports**: Generates HTML and JSON reports
- 🔒 **Privacy First**: All analysis runs locally, no data leaves your machine
- 🌐 **Multi-Broker**: Works with Dhan, Zerodha, Upstox, and any broker

## 🚀 Quick Start

### Prerequisites

1. **Python 3.8+** installed
2. **Ollama** installed and running

### Install Ollama

```bash
# macOS/Linux
curl https://ollama.ai/install.sh | sh

# Windows - Download from https://ollama.ai/download

# Pull a model
ollama pull llama2:13b
```

### Install Trading Analyzer

```bash
# Clone repository
git clone https://github.com/vikkysarswat/trade_analysis_dhan.git
cd trade_analysis_dhan

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Run Analysis

```bash
# Analyze your trades
python main.py data/sample_trades.csv --trader-name "Your Name"

# View report
open data/reports/Your_Name_report.html
```

## 📊 Sample Output

```
=== TRADING PERSONA ANALYSIS ===

Trader Type: High-Frequency Scalper
Risk Level: VERY HIGH
Win Rate: 48.5%
Net P&L: ₹186.52
Sharpe Ratio: -0.15

Detected Patterns:
⚠ Overtrading (12 trades/day average)
⚠ Revenge Trading (15 instances)
⚠ Scalping (avg holding: 25 minutes)

Risk Score: 78/100

Recommendations:
• Reduce trading frequency by 70%
• Implement daily loss limits
• Focus on 2-3 high-conviction trades
• Avoid trading after losses
```

## 📁 Project Structure

```
trade_analysis_dhan/
│
├── src/
│   ├── data_processor.py      # Data loading and cleaning
│   ├── metrics_calculator.py  # Calculate trading metrics
│   ├── pattern_detector.py    # Detect trading patterns
│   ├── llm_analyzer.py         # Ollama integration
│   └── report_generator.py    # Generate reports
│
├── data/
│   ├── raw/                    # Your trading data
│   ├── processed/              # Processed data
│   └── reports/                # Generated reports
│
├── config.yaml                 # Configuration
├── main.py                     # Main application
└── requirements.txt            # Dependencies
```

## 📥 Data Format

Your trading data should be in CSV format:

```csv
trade_date,symbol,transaction_type,quantity,price
2025-09-10 09:33:02,NIFTY 25200 CALL,BUY,75,44.35
2025-09-10 09:35:15,NIFTY 25200 CALL,SELL,75,44.20
```

**Required columns:**
- `trade_date`: Date/time of trade
- `symbol`: Trading instrument
- `transaction_type`: BUY or SELL
- `quantity`: Number of units
- `price`: Price per unit

## 🔌 API Integration

### Extract from Dhan

```python
from extractors import DhanExtractor

extractor = DhanExtractor(access_token="YOUR_TOKEN")
trades = extractor.extract_trades("2025-04-01", "2025-09-21")
```

### Extract from Zerodha

```python
from extractors import ZerodhaExtractor

extractor = ZerodhaExtractor(api_key="YOUR_KEY")
trades = extractor.extract_trades()
```

## 🛠️ Configuration

Edit `config.yaml`:

```yaml
ollama:
  model: "llama2:13b"      # Change model
  temperature: 0.7         # Adjust creativity

analysis:
  min_trades: 20          # Minimum trades required
  risk_free_rate: 0.065   # For Sharpe ratio
```

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## 📝 License

MIT License - see [LICENSE](LICENSE) file

## ⚠️ Disclaimer

This tool provides analytical insights only. Not financial advice. Trade at your own risk.

## 🙏 Acknowledgments

- Ollama team for local LLM infrastructure
- Trading community for patterns and insights
- Open source contributors

---

**Made with ❤️ for traders who want to improve**

⭐ Star this repo if you find it helpful!