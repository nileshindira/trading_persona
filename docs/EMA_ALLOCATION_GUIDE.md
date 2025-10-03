# EMA Allocation Score Feature

## Overview
The EMA Allocation Score feature adds market context to trading analysis by calculating Exponential Moving Average (EMA) based allocation scores for stocks and indices.

## What is EMA Allocation Score?

The EMA allocation score is a quantitative measure (ranging from -6 to +6) that indicates the strength of a bullish or bearish trend based on the relationship between price and three key EMAs (21, 50, and 100).

### Scoring System

The score is calculated using 6 components:

#### Price vs EMAs (3 points)
- If Current Price > EMA21 → +1, else -1
- If Current Price > EMA50 → +1, else -1
- If Current Price > EMA100 → +1, else -1

#### EMA Relationships (3 points)
- If EMA21 > EMA100 → +1, else -1
- If EMA21 > EMA50 → +1, else -1
- If EMA50 > EMA100 → +1, else -1

### Score Interpretation

| Score Range | Interpretation | Allocation Suggestion |
|-------------|---------------|----------------------|
| +6 | Extremely Bullish | Maximum allocation |
| +4 to +5 | Strong Bullish | High allocation |
| +1 to +3 | Moderately Bullish | Medium allocation |
| 0 | Neutral | Cautious allocation |
| -1 to -3 | Moderately Bearish | Low allocation |
| -4 to -5 | Strong Bearish | Minimal allocation |
| -6 | Extremely Bearish | No allocation |

## Features

### Three-Level Market Context

The feature calculates EMA scores at three levels for each trade:

1. **Stock EMA Score (`ema_score_stock`)**: Score for the specific stock being traded
2. **Nifty EMA Score (`ema_score_nifty`)**: Score for the Nifty 50 index (broad market)
3. **Midcap EMA Score (`ema_score_midcap`)**: Score for the Nifty Midcap index (mid-cap segment)

### Key Benefits

- **Market Context**: Understand if you're trading with or against market trends
- **Risk Assessment**: Identify trades taken in adverse market conditions
- **Pattern Recognition**: Spot tendencies to trade in specific market conditions
- **Performance Attribution**: Analyze if your losses/profits correlate with market trends

## Usage

### Basic Usage

```bash
# Run analysis with EMA scores (default)
python main.py data/sample_trades.csv --trader-name "John"

# Skip EMA calculation if needed
python main.py data/sample_trades.csv --trader-name "John" --no-ema
```

### Output Files

The analysis generates:

1. **Standard Reports**: JSON and HTML reports (as before)
2. **Enriched CSV**: `{trader_name}_trades_with_ema.csv` containing all original data plus three EMA score columns

### Example Output

```
EMA ALLOCATION SCORES
==================================================
Stock EMA (Avg): 3.45
Nifty EMA (Avg): 2.80
Midcap EMA (Avg): 1.20
```

## Technical Implementation

### Data Source

The feature uses [tvDatafeed](https://github.com/rongardF/tvdatafeed) to fetch historical price data from TradingView. This provides:

- Real-time and historical data for NSE/BSE stocks
- Index data (Nifty, Midcap, etc.)
- No API key required for basic usage
- Daily OHLC data for EMA calculation

### EMA Calculation

EMAs are calculated using the pandas exponential weighted moving average:

```python
EMA = prices.ewm(span=period, adjust=False).mean()
```

### Symbol Extraction

The system intelligently extracts base symbols from complex trading symbols:

- `NIFTY 16 SEP 25200 CALL` → `NIFTY`
- `BANKNIFTY 30 SEP 54300 PUT` → `BANKNIFTY`
- `RELIANCE` → `RELIANCE`

### Caching

To optimize performance and reduce API calls:
- Scores are cached by symbol and date
- Each unique symbol-date combination is calculated only once
- Reduces redundant calculations for multiple trades on the same day

## Configuration

No additional configuration needed! The feature automatically:
- Detects symbol types (stock, index, derivatives)
- Uses appropriate exchanges (NSE by default)
- Calculates scores up to t-1 (previous day's close)

## Error Handling

The implementation includes robust error handling:

- If tvDatafeed fails to initialize, analysis continues without EMA scores
- If data is unavailable for a symbol, that trade gets `None` for EMA score
- Errors are logged but don't stop the analysis pipeline

## Performance Considerations

- **Initial Run**: May take 2-5 minutes for datasets with many unique symbols
- **Subsequent Runs**: Faster due to caching
- **API Limits**: TradingView has rate limits; excessive requests may fail
- **Recommendation**: Use `--no-ema` flag for quick iterations during development

## Example Analysis

### Sample Trade
```
Symbol: NIFTY 16 SEP 25200 CALL
Date: 2025-09-10
Transaction: SELL
Price: 44.2
Quantity: 75

EMA Scores:
- ema_score_stock: 4    (Strong bullish - NIFTY in uptrend)
- ema_score_nifty: 4    (Market is bullish)
- ema_score_midcap: 2   (Midcaps moderately bullish)
```

### Interpretation
This is a SELL trade in a strong bullish market (score +4), indicating the trader might be going against the trend. This could be:
- A contrarian position
- A hedge against other positions
- Risk of trading against the trend

## Use Cases

### 1. Trend Alignment Analysis
Identify what percentage of your trades align with market trends:
```python
# Trades with market (both positive)
aligned = df[(df['ema_score_stock'] > 0) & (df['ema_score_nifty'] > 0)]

# Trades against market
contrarian = df[(df['ema_score_stock'] < 0) & (df['ema_score_nifty'] > 0)]
```

### 2. Performance Attribution
Analyze if your winning/losing trades correlate with market conditions:
```python
# Winning trades in bullish conditions
wins_in_bull = df[(df['pnl'] > 0) & (df['ema_score_nifty'] > 3)]

# Losing trades in bearish conditions
loss_in_bear = df[(df['pnl'] < 0) & (df['ema_score_nifty'] < -3)]
```

### 3. Risk Management
Set position sizing rules based on market conditions:
```python
# Example: Reduce position size when market EMA is negative
if ema_score_nifty < 0:
    position_size = base_size * 0.5  # 50% position in bearish market
else:
    position_size = base_size
```

## API Reference

### EMACalculator Class

```python
from src.ema_calculator import EMACalculator

# Initialize
calculator = EMACalculator(config)

# Calculate score for a symbol
score, ema_values = calculator.calculate_emas_for_symbol(
    symbol='RELIANCE',
    exchange='NSE',
    target_date=datetime(2025, 9, 10)
)

# Add scores to dataframe
df_with_ema = calculator.add_ema_scores_to_trades(df)

# Get summary statistics
stats = calculator.get_ema_summary_stats(df_with_ema)
```

### Key Methods

#### `calculate_ema_score(close_price, ema21, ema50, ema100)`
Calculates the EMA allocation score based on price and EMA values.

**Parameters:**
- `close_price` (float): Current market price
- `ema21` (float): 21-period EMA value
- `ema50` (float): 50-period EMA value  
- `ema100` (float): 100-period EMA value

**Returns:** int (score from -6 to +6)

#### `add_ema_scores_to_trades(df)`
Adds EMA scores to trading dataframe.

**Parameters:**
- `df` (pd.DataFrame): Trading dataframe with 'trade_date' and 'symbol' columns

**Returns:** pd.DataFrame with three additional columns:
- `ema_score_stock`
- `ema_score_nifty`
- `ema_score_midcap`

#### `get_ema_summary_stats(df)`
Generates summary statistics for EMA scores.

**Returns:** dict with mean, min, max for each EMA score type

## Troubleshooting

### Common Issues

#### 1. tvDatafeed import error
```
ImportError: No module named 'tvDatafeed'
```
**Solution:** 
```bash
pip install tvDatafeed
```

#### 2. No data for symbol
```
WARNING: No data received for SYMBOL
```
**Solution:** 
- Check if symbol exists on TradingView
- Verify exchange is correct (NSE/BSE)
- Symbol might be delisted or inactive

#### 3. Rate limit errors
```
ERROR: Too many requests
```
**Solution:**
- Add delays between requests
- Reduce number of unique symbols
- Use `--no-ema` flag temporarily

#### 4. All EMA scores are None
**Solution:**
- Check internet connectivity
- Verify tvDatafeed is properly installed
- Check logs for specific error messages

## Future Enhancements

Potential improvements for future versions:

1. **Custom EMA Periods**: Allow users to configure EMA periods (currently 21, 50, 100)
2. **Multiple Timeframes**: Add intraday EMA scores (15-min, hourly)
3. **More Indices**: Support for sector indices (Bank Nifty, IT, Pharma, etc.)
4. **Visual Dashboard**: Charts showing EMA trends alongside trades
5. **Alert System**: Warn when trading against strong trends
6. **Historical Backtesting**: Compare strategies in different EMA regimes

## Contributing

To contribute to this feature:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This feature is part of the trade_analysis_dhan project and follows the same license (MIT).

## Support

For issues or questions:
- Open an issue on GitHub
- Check existing documentation
- Review the code in `src/ema_calculator.py`

## Changelog

### Version 1.0.0 (2025-10-03)
- Initial release
- Support for stock, Nifty, and Midcap EMA scores
- Integration with main analysis pipeline
- Summary statistics in reports
- Enriched CSV export
