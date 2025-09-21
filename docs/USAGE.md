# Usage Guide

## Basic Usage

### Analyze Your Trades

```bash
python main.py data/your_trades.csv --trader-name "Your Name"
```

### Command Line Options

```bash
python main.py <data_file> [options]

Options:
  --trader-name TEXT     Name for the report (default: "Trader")
  --config TEXT          Config file path (default: "config.yaml")
  --output-dir TEXT      Output directory (default: "data/reports")
```

## Data Format

Your CSV file should have these columns:

```csv
trade_date,symbol,transaction_type,quantity,price
2025-09-10 09:33:02,NIFTY 25200 CALL,BUY,75,44.35
2025-09-10 09:35:15,NIFTY 25200 CALL,SELL,75,44.20
```

**Required Columns:**
- `trade_date`: Date and time (YYYY-MM-DD HH:MM:SS)
- `symbol`: Trading instrument name
- `transaction_type`: BUY or SELL
- `quantity`: Number of units
- `price`: Price per unit

**Optional Columns:**
- `trade_value`: Total value (calculated if missing)
- `charges`: Brokerage and fees
- `order_id`: Order identifier

## Python API

### Basic Analysis

```python
from trading_persona_analyzer import TradingPersonaAnalyzer

analyzer = TradingPersonaAnalyzer()
report = analyzer.analyze(
    'data/trades.csv',
    trader_name='John Doe'
)

print(f"Risk Score: {report['risk_score']}/100")
```

### Custom Analysis

```python
from src.data_processor import TradingDataProcessor
from src.metrics_calculator import TradingMetricsCalculator

# Load and process data
processor = TradingDataProcessor(config)
df = processor.load_data('trades.csv')
df = processor.clean_data(df)
df = processor.pair_trades(df)

# Calculate metrics
calculator = TradingMetricsCalculator(config)
metrics = calculator.calculate_all_metrics(df)

print(f"Sharpe Ratio: {metrics['sharpe_ratio']:.2f}")
print(f"Win Rate: {metrics['win_rate']:.1f}%")
```

## Extracting Data from Brokers

### Dhan

```python
from extractors.dhan import DhanExtractor

extractor = DhanExtractor(
    access_token="YOUR_ACCESS_TOKEN"
)

trades = extractor.extract_trades(
    from_date="2025-04-01",
    to_date="2025-09-21",
    output_file="data/raw/dhan_trades.csv"
)
```

### Zerodha

```python
from extractors.zerodha import ZerodhaExtractor

extractor = ZerodhaExtractor(
    api_key="YOUR_API_KEY",
    access_token="YOUR_ACCESS_TOKEN"
)

trades = extractor.extract_trades(
    output_file="data/raw/zerodha_trades.csv"
)
```

## Understanding the Report

### Risk Score (0-100)

- **0-30**: Low Risk - Conservative trading
- **31-60**: Medium Risk - Balanced approach
- **61-80**: High Risk - Aggressive trading
- **81-100**: Very High Risk - Dangerous patterns detected

### Trading Patterns

**Overtrading**: More than 10 trades per day consistently
- **Impact**: High transaction costs, reduced profits
- **Fix**: Reduce frequency, focus on quality

**Revenge Trading**: Trading immediately after losses
- **Impact**: Emotional decisions, increased losses
- **Fix**: Take breaks after losses, use daily limits

**Scalping**: Very short holding periods (<30 min)
- **Impact**: High stress, transaction cost erosion
- **Fix**: Extend holding periods, target larger moves

### Key Metrics

**Sharpe Ratio**:
- Above 1.0: Good risk-adjusted returns
- 0.5-1.0: Acceptable performance
- Below 0.5: Poor risk-adjusted returns
- Negative: Losing money

**Win Rate**:
- Above 60%: Strong performance
- 50-60%: Average
- Below 50%: Needs improvement

**Max Drawdown**:
- Below 10%: Good risk management
- 10-20%: Acceptable
- Above 20%: Poor risk control

## Tips for Better Results

1. **Provide Complete Data**: More trades = better analysis
2. **Include Charges**: For accurate P&L calculation
3. **Regular Analysis**: Run monthly to track improvement
4. **Act on Recommendations**: Implement suggested changes
5. **Track Progress**: Compare reports over time

## Batch Processing

```python
import glob
from pathlib import Path

analyzer = TradingPersonaAnalyzer()

for filepath in glob.glob('data/raw/*.csv'):
    trader_name = Path(filepath).stem
    analyzer.analyze(filepath, trader_name)

print("Batch analysis complete!")
```

## Troubleshooting

### "Ollama not responding"

```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Start Ollama if needed
ollama serve
```

### "Invalid date format"

Ensure dates are in format: `YYYY-MM-DD HH:MM:SS`

```python
import pandas as pd

df = pd.read_csv('trades.csv')
df['trade_date'] = pd.to_datetime(df['trade_date'])
df.to_csv('trades_fixed.csv', index=False)
```

### "Missing required columns"

Check your CSV has all required columns:

```python
required = ['trade_date', 'symbol', 'transaction_type', 'quantity', 'price']
df = pd.read_csv('trades.csv')
missing = [col for col in required if col not in df.columns]

if missing:
    print(f"Missing columns: {missing}")
```

## Next Steps

- Review your generated report
- Implement top 3 recommendations
- Re-run analysis after 1 month
- Compare improvement

For advanced features, see [Advanced Usage](ADVANCED.md)
