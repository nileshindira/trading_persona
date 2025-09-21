# Contributing to Trade Analysis Dhan

Thank you for your interest in contributing! This project welcomes contributions from the community.

## How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported in [Issues](https://github.com/vikkysarswat/trade_analysis_dhan/issues)
2. If not, create a new issue with:
   - Clear title and description
   - Steps to reproduce
   - Expected vs actual behavior
   - Python version and OS
   - Sample data (if applicable)

### Suggesting Features

1. Open an issue with `[Feature Request]` in the title
2. Describe the feature and its benefits
3. Provide use cases or examples

### Pull Requests

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```

3. **Make your changes**
   - Follow the existing code style
   - Add tests for new features
   - Update documentation

4. **Test your changes**
   ```bash
   python -m pytest tests/
   flake8 src/
   ```

5. **Commit with clear messages**
   ```bash
   git commit -m "Add feature: description"
   ```

6. **Push and create PR**
   ```bash
   git push origin feature/amazing-feature
   ```

## Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/trade_analysis_dhan.git
cd trade_analysis_dhan

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Development dependencies
```

## Code Style

- Follow PEP 8
- Use type hints
- Write docstrings for functions and classes
- Keep functions focused and small

### Example

```python
def calculate_sharpe_ratio(returns: pd.Series, risk_free_rate: float) -> float:
    """Calculate Sharpe Ratio for given returns.
    
    Args:
        returns: Series of daily returns
        risk_free_rate: Annual risk-free rate
        
    Returns:
        Sharpe ratio value
    """
    excess_returns = returns - (risk_free_rate / 252)
    return np.sqrt(252) * (excess_returns.mean() / excess_returns.std())
```

## Testing

Add tests for new features:

```python
# tests/test_metrics.py
import pytest
from src.metrics_calculator import TradingMetricsCalculator

def test_sharpe_ratio_calculation():
    calculator = TradingMetricsCalculator(config)
    result = calculator.calculate_sharpe_ratio(returns)
    assert result > 0
```

## Areas for Contribution

### High Priority

- [ ] Additional broker integrations (Angel One, Upstox, ICICI)
- [ ] Real-time analysis features
- [ ] More pattern detection algorithms
- [ ] Performance optimizations
- [ ] Better error handling

### Medium Priority

- [ ] Web dashboard interface
- [ ] Mobile app support
- [ ] Advanced visualizations
- [ ] Machine learning predictions
- [ ] Social trading features

### Documentation

- [ ] Video tutorials
- [ ] More code examples
- [ ] Translation to other languages
- [ ] API documentation
- [ ] Best practices guide

## Broker Integration Template

To add a new broker:

```python
# extractors/your_broker.py
class YourBrokerExtractor:
    def __init__(self, credentials):
        self.api_key = credentials['api_key']
        
    def extract_trades(self, from_date, to_date):
        # Implement API calls
        trades = self._fetch_from_api(from_date, to_date)
        
        # Convert to standard format
        df = self._convert_to_standard(trades)
        
        return df
    
    def _convert_to_standard(self, trades):
        return pd.DataFrame({
            'trade_date': ...,
            'symbol': ...,
            'transaction_type': ...,
            'quantity': ...,
            'price': ...
        })
```

## Pattern Detection Template

To add a new pattern:

```python
# src/pattern_detector.py
def detect_your_pattern(self, df: pd.DataFrame) -> Dict:
    """Detect your custom pattern"""
    pattern_count = 0
    
    # Your detection logic
    for idx, trade in df.iterrows():
        if self._is_pattern(trade):
            pattern_count += 1
    
    return {
        'detected': pattern_count > self.min_trades,
        'count': pattern_count,
        'severity': 'HIGH' if pattern_count > 10 else 'MEDIUM'
    }
```

## Release Process

1. Update version in `setup.py`
2. Update CHANGELOG.md
3. Create release tag
4. GitHub Actions will build and publish

## Code of Conduct

### Our Standards

- Be respectful and inclusive
- Accept constructive criticism
- Focus on what's best for the community
- Show empathy towards others

### Unacceptable Behavior

- Harassment or discriminatory language
- Personal attacks
- Publishing others' private information
- Unethical or unprofessional conduct

## Questions?

Feel free to ask questions in:

- [GitHub Discussions](https://github.com/vikkysarswat/trade_analysis_dhan/discussions)
- [Issues](https://github.com/vikkysarswat/trade_analysis_dhan/issues)
- Email: vikky.sarswat@gmail.com

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for making this project better! 🚀
