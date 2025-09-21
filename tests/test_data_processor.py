"""
Tests for data processor module
"""

import pytest
import pandas as pd
from src.data_processor import TradingDataProcessor

@pytest.fixture
def config():
    return {
        'data': {
            'required_columns': ['trade_date', 'symbol', 'transaction_type', 'quantity', 'price'],
            'date_format': '%Y-%m-%d',
            'datetime_format': '%Y-%m-%d %H:%M:%S'
        }
    }

@pytest.fixture
def sample_data():
    return pd.DataFrame({
        'trade_date': ['2025-09-10 09:33:02', '2025-09-10 09:29:37'],
        'symbol': ['NIFTY CALL', 'NIFTY CALL'],
        'transaction_type': ['SELL', 'BUY'],
        'quantity': [75, 75],
        'price': [44.2, 44.35]
    })

def test_validate_data(config, sample_data):
    processor = TradingDataProcessor(config)
    is_valid, missing = processor.validate_data(sample_data)
    assert is_valid is True
    assert len(missing) == 0

def test_clean_data(config, sample_data):
    processor = TradingDataProcessor(config)
    cleaned = processor.clean_data(sample_data)
    
    assert 'trade_hour' in cleaned.columns
    assert 'trade_day_of_week' in cleaned.columns
    assert 'trade_value' in cleaned.columns
    assert len(cleaned) == 2

def test_pair_trades(config, sample_data):
    processor = TradingDataProcessor(config)
    cleaned = processor.clean_data(sample_data)
    paired = processor.pair_trades(cleaned)
    
    assert 'pnl' in paired.columns
    assert 'holding_period_minutes' in paired.columns
