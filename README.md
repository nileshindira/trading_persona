# 🚀 Trading Persona Analyzer - Dhan Edition

AI-powered trading analysis system using local LLMs (Ollama) to analyze trading patterns, detect behavioral issues, and provide actionable insights with **EMA-based market context**.

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Ollama](https://img.shields.io/badge/LLM-Ollama-orange.svg)

## 🎯 Features

- 📊 **Comprehensive Metrics**: Sharpe ratio, max drawdown, win rate, and 20+ metrics
- 🔍 **Pattern Detection**: Identifies overtrading, revenge trading, scalping, hedging
- 📈 **EMA Allocation Scores**: Market context with stock, Nifty & Midcap EMA analysis
- 🤖 **AI Analysis**: Uses Ollama (Llama2, Mixtral) for natural language insights
- 📄 **Professional Reports**: Generates HTML, JSON and enriched CSV with EMA scores
- 🔒 **Privacy First**: All analysis runs locally, no data leaves your machine
- 🌐 **Multi-Broker**: Works with Dhan, Zerodha, Upstox, and any broker

## ✨ NEW: EMA Allocation Score Feature

Automatically calculates **EMA-based market trend scores** (-6 to +6) for:
- 📉 **Stock/Index being traded** (ema_score_stock)
- 📊 **Nifty 50 Index** (ema_score_nifty) - Broad market context
- 📈 **Midcap Nifty** (ema_score_midcap) - Mid-cap segment context

This helps you understand:
- Are you trading with or against market trends?
- Do your losses correlate with adverse market conditions?
- What's your performance in different market regimes?

[📖 Read full EMA documentation](docs/EMA_ALLOCATION_GUIDE.md)

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
# Analyze your trades with EMA scores (default)
python main.py data/sample_trades.csv --trader-name "Your Name"

# Skip EMA calculation for faster analysis
python main.py data/sample_trades.csv --trader-name "Your Name" --no-ema

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

==================================================
EMA ALLOCATION SCORES
==================================================
Stock EMA (Avg): 3.45      ← Stock in uptrend
Nifty EMA (Avg): 2.80      ← Market moderately bullish
Midcap EMA (Avg): 1.20     ← Midcaps weakly bullish

Recommendations:
• Reduce trading frequency by 70%
• Implement daily loss limits
• Focus on 2-3 high-conviction trades
• Avoid trading after losses
• Your losses correlate with weak market conditions (EMA < 0)
```

## 📁 Project Structure

```
trade_analysis_dhan/
│
├── src/
│   ├── data_processor.py      # Data loading and cleaning
│   ├── metrics_calculator.py  # Calculate trading metrics
│   ├── pattern_detector.py    # Detect trading patterns
│   ├── ema_calculator.py      # 🆕 EMA allocation scores
│   ├── llm_analyzer.py         # Ollama integration
│   └── report_generator.py    # Generate reports
│
├── data/
│   ├── raw/                    # Your trading data
│   ├── processed/              # Processed data
│   └── reports/                # Generated reports + CSV with EMA
│
├── docs/
│   └── EMA_ALLOCATION_GUIDE.md # 🆕 EMA feature documentation
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

**Output includes additional columns:**
- `ema_score_stock`: EMA score for traded stock/index (-6 to +6)
- `ema_score_nifty`: EMA score for Nifty 50 (-6 to +6)
- `ema_score_midcap`: EMA score for Nifty Midcap (-6 to +6)

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

## 📈 EMA Allocation Usage

### Programmatic Access

```python
from src.ema_calculator import EMACalculator

# Initialize calculator
calculator = EMACalculator(config)

# Calculate EMA score for any symbol
score, ema_values = calculator.calculate_emas_for_symbol(
    symbol='RELIANCE',
    exchange='NSE',
    target_date=datetime(2025, 9, 10)
)

print(f"EMA Score: {score}/6")
print(f"Close: {ema_values['close']}")
print(f"EMA21: {ema_values['ema21']}")

# Add scores to your dataframe
df_with_ema = calculator.add_ema_scores_to_trades(df)

# Get summary statistics
stats = calculator.get_ema_summary_stats(df_with_ema)
```

### Score Interpretation

| Score | Meaning | Action |
|-------|---------|--------|
| +6 | Extremely Bullish | Maximum allocation |
| +4 to +5 | Strong Bullish | High allocation |
| +1 to +3 | Moderately Bullish | Medium allocation |
| 0 | Neutral | Cautious |
| -1 to -3 | Moderately Bearish | Low allocation |
| -4 to -5 | Strong Bearish | Minimal allocation |
| -6 | Extremely Bearish | No allocation |

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

## 🐛 Troubleshooting

### EMA Calculation Issues

If you encounter issues with EMA scores:

```bash
# Check tvDatafeed installation
pip install tvDatafeed

# Run without EMA for testing
python main.py data/sample_trades.csv --no-ema

# Check logs for specific errors
tail -f trade_analysis.log
```

See [EMA Troubleshooting Guide](docs/EMA_ALLOCATION_GUIDE.md#troubleshooting) for more details.

## ⚠️ Disclaimer

This tool provides analytical insights only. Not financial advice. Trade at your own risk.

## 🙏 Acknowledgments

- Ollama team for local LLM infrastructure
- Trading community for patterns and insights
- [tvDatafeed](https://github.com/rongardF/tvdatafeed) for market data access
- Open source contributors

---

**Made with ❤️ for traders who want to improve**

⭐ Star this repo if you find it helpful!

## 📚 Documentation

- [EMA Allocation Guide](docs/EMA_ALLOCATION_GUIDE.md) - Complete guide to EMA features
- [Contributing Guidelines](CONTRIBUTING.md) - How to contribute
- [Changelog](CHANGELOG.md) - Version history
