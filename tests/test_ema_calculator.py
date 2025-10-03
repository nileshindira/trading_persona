"""
Unit tests for EMA Calculator module
"""

import unittest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock

import sys
sys.path.append('..')

from src.ema_calculator import EMACalculator


class TestEMACalculator(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures"""
        self.config = {
            'data': {'required_columns': []},
            'ollama': {'model': 'test'}
        }
        
    @patch('src.ema_calculator.TvDatafeed')
    def test_ema_calculator_initialization(self, mock_tvdatafeed):
        """Test EMA calculator initialization"""
        calculator = EMACalculator(self.config)
        self.assertIsNotNone(calculator)
        self.assertEqual(calculator.config, self.config)
    
    def test_calculate_ema(self):
        """Test EMA calculation"""
        # Create sample price data
        prices = pd.Series([100, 102, 101, 103, 105, 104, 106, 108, 107, 109])
        
        with patch('src.ema_calculator.TvDatafeed'):
            calculator = EMACalculator(self.config)
            ema = calculator.calculate_ema(prices, period=3)
            
            # EMA should be a series of same length
            self.assertEqual(len(ema), len(prices))
            
            # EMA values should be numeric
            self.assertTrue(all(isinstance(x, (int, float, np.number)) for x in ema))
    
    def test_calculate_ema_score_bullish(self):
        """Test EMA score calculation for bullish scenario"""
        with patch('src.ema_calculator.TvDatafeed'):
            calculator = EMACalculator(self.config)
            
            # Strongly bullish: price above all EMAs, EMAs aligned
            score = calculator.calculate_ema_score(
                close_price=110,
                ema21=108,
                ema50=105,
                ema100=100
            )
            
            # Should be maximum score: +6
            self.assertEqual(score, 6)
    
    def test_calculate_ema_score_bearish(self):
        """Test EMA score calculation for bearish scenario"""
        with patch('src.ema_calculator.TvDatafeed'):
            calculator = EMACalculator(self.config)
            
            # Strongly bearish: price below all EMAs, EMAs reverse aligned
            score = calculator.calculate_ema_score(
                close_price=90,
                ema21=92,
                ema50=95,
                ema100=100
            )
            
            # Should be minimum score: -6
            self.assertEqual(score, -6)
    
    def test_calculate_ema_score_neutral(self):
        """Test EMA score calculation for neutral scenario"""
        with patch('src.ema_calculator.TvDatafeed'):
            calculator = EMACalculator(self.config)
            
            # Mixed signals
            score = calculator.calculate_ema_score(
                close_price=100,
                ema21=99,    # price > ema21 (+1)
                ema50=98,    # price > ema50 (+1)
                ema100=101   # price < ema100 (-1)
                            # ema21 < ema100 (-1)
                            # ema21 > ema50 (+1)
                            # ema50 < ema100 (-1)
            )
            
            # Score should be 0 (3 positive, 3 negative)
            self.assertEqual(score, 0)
    
    def test_extract_base_symbol_nifty(self):
        """Test symbol extraction for NIFTY options"""
        with patch('src.ema_calculator.TvDatafeed'):
            calculator = EMACalculator(self.config)
            
            symbol = calculator.extract_base_symbol('NIFTY 16 SEP 25200 CALL')
            self.assertEqual(symbol, 'NIFTY')
            
            symbol = calculator.extract_base_symbol('NIFTY 30 OCT 24800 PUT')
            self.assertEqual(symbol, 'NIFTY')
    
    def test_extract_base_symbol_banknifty(self):
        """Test symbol extraction for BANKNIFTY options"""
        with patch('src.ema_calculator.TvDatafeed'):
            calculator = EMACalculator(self.config)
            
            symbol = calculator.extract_base_symbol('BANKNIFTY 30 SEP 54300 PUT')
            self.assertEqual(symbol, 'BANKNIFTY')
    
    def test_extract_base_symbol_stock(self):
        """Test symbol extraction for stocks"""
        with patch('src.ema_calculator.TvDatafeed'):
            calculator = EMACalculator(self.config)
            
            symbol = calculator.extract_base_symbol('RELIANCE')
            self.assertEqual(symbol, 'RELIANCE')
            
            symbol = calculator.extract_base_symbol('TCS')
            self.assertEqual(symbol, 'TCS')
    
    @patch('src.ema_calculator.TvDatafeed')
    def test_get_historical_data(self, mock_tvdatafeed):
        """Test historical data fetching"""
        # Mock TradingView data
        mock_df = pd.DataFrame({
            'close': [100, 102, 101, 103, 105],
            'open': [99, 101, 100, 102, 104],
            'high': [101, 103, 102, 104, 106],
            'low': [98, 100, 99, 101, 103],
            'volume': [1000, 1100, 900, 1200, 1300]
        })
        
        mock_tv_instance = Mock()
        mock_tv_instance.get_hist.return_value = mock_df
        mock_tvdatafeed.return_value = mock_tv_instance
        
        calculator = EMACalculator(self.config)
        result = calculator.get_historical_data('RELIANCE', 'NSE')
        
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 5)
        self.assertIn('close', result.columns)
    
    @patch('src.ema_calculator.TvDatafeed')
    def test_calculate_emas_for_symbol(self, mock_tvdatafeed):
        """Test complete EMA calculation for a symbol"""
        # Create mock data with sufficient history
        dates = pd.date_range(end=datetime.now(), periods=150, freq='D')
        mock_df = pd.DataFrame({
            'close': np.random.uniform(100, 110, 150)
        }, index=dates)
        
        mock_tv_instance = Mock()
        mock_tv_instance.get_hist.return_value = mock_df
        mock_tvdatafeed.return_value = mock_tv_instance
        
        calculator = EMACalculator(self.config)
        score, ema_values = calculator.calculate_emas_for_symbol('RELIANCE', 'NSE')
        
        # Should return a valid score
        self.assertIsNotNone(score)
        self.assertIsInstance(score, int)
        self.assertGreaterEqual(score, -6)
        self.assertLessEqual(score, 6)
        
        # Should return EMA values
        self.assertIn('close', ema_values)
        self.assertIn('ema21', ema_values)
        self.assertIn('ema50', ema_values)
        self.assertIn('ema100', ema_values)
    
    @patch('src.ema_calculator.TvDatafeed')
    def test_add_ema_scores_to_trades(self, mock_tvdatafeed):
        """Test adding EMA scores to trading dataframe"""
        # Create sample trading data
        df = pd.DataFrame({
            'trade_date': pd.date_range(start='2025-09-01', periods=5, freq='D'),
            'symbol': ['NIFTY 25200 CALL'] * 5,
            'price': [100, 102, 101, 103, 105],
            'quantity': [75, 75, 75, 75, 75],
            'transaction_type': ['BUY', 'SELL', 'BUY', 'SELL', 'BUY']
        })
        
        # Mock historical data
        dates = pd.date_range(end=datetime.now(), periods=150, freq='D')
        mock_df = pd.DataFrame({
            'close': np.random.uniform(100, 110, 150)
        }, index=dates)
        
        mock_tv_instance = Mock()
        mock_tv_instance.get_hist.return_value = mock_df
        mock_tvdatafeed.return_value = mock_tv_instance
        
        calculator = EMACalculator(self.config)
        result_df = calculator.add_ema_scores_to_trades(df)
        
        # Check new columns are added
        self.assertIn('ema_score_stock', result_df.columns)
        self.assertIn('ema_score_nifty', result_df.columns)
        self.assertIn('ema_score_midcap', result_df.columns)
        
        # Check all rows have been processed
        self.assertEqual(len(result_df), len(df))
    
    @patch('src.ema_calculator.TvDatafeed')
    def test_get_ema_summary_stats(self, mock_tvdatafeed):
        """Test EMA summary statistics generation"""
        # Create dataframe with EMA scores
        df = pd.DataFrame({
            'ema_score_stock': [3, 4, 2, 5, 3],
            'ema_score_nifty': [2, 3, 2, 4, 3],
            'ema_score_midcap': [1, 2, 0, 3, 1]
        })
        
        mock_tvdatafeed.return_value = Mock()
        calculator = EMACalculator(self.config)
        stats = calculator.get_ema_summary_stats(df)
        
        # Check structure
        self.assertIn('stock_ema', stats)
        self.assertIn('nifty_ema', stats)
        self.assertIn('midcap_ema', stats)
        
        # Check stock stats
        self.assertAlmostEqual(stats['stock_ema']['mean'], 3.4)
        self.assertEqual(stats['stock_ema']['min'], 2)
        self.assertEqual(stats['stock_ema']['max'], 5)
        
        # Check nifty stats
        self.assertAlmostEqual(stats['nifty_ema']['mean'], 2.8)
        self.assertEqual(stats['nifty_ema']['min'], 2)
        self.assertEqual(stats['nifty_ema']['max'], 4)
    
    def test_ema_score_range(self):
        """Test that EMA scores are always within valid range"""
        with patch('src.ema_calculator.TvDatafeed'):
            calculator = EMACalculator(self.config)
            
            # Test various combinations
            test_cases = [
                (110, 108, 105, 100),  # All bullish
                (90, 92, 95, 100),      # All bearish
                (100, 100, 100, 100),   # Neutral
                (105, 100, 102, 101),   # Mixed
            ]
            
            for close, ema21, ema50, ema100 in test_cases:
                score = calculator.calculate_ema_score(close, ema21, ema50, ema100)
                self.assertGreaterEqual(score, -6)
                self.assertLessEqual(score, 6)


class TestEMAScoreLogic(unittest.TestCase):
    """Test the detailed scoring logic"""
    
    def setUp(self):
        """Set up calculator instance"""
        with patch('src.ema_calculator.TvDatafeed'):
            self.calculator = EMACalculator({})
    
    def test_price_above_all_emas(self):
        """Test when price is above all EMAs"""
        score = self.calculator.calculate_ema_score(
            close_price=120,
            ema21=110,
            ema50=105,
            ema100=100
        )
        # Price above all: +3, EMAs aligned: +3 = +6
        self.assertEqual(score, 6)
    
    def test_price_below_all_emas(self):
        """Test when price is below all EMAs"""
        score = self.calculator.calculate_ema_score(
            close_price=80,
            ema21=90,
            ema50=95,
            ema100=100
        )
        # Price below all: -3, EMAs reverse aligned: -3 = -6
        self.assertEqual(score, -6)
    
    def test_price_between_emas(self):
        """Test when price is between EMAs"""
        score = self.calculator.calculate_ema_score(
            close_price=103,
            ema21=105,
            ema50=102,
            ema100=100
        )
        # Price < EMA21 (-1), Price > EMA50 (+1), Price > EMA100 (+1)
        # EMA21 > EMA100 (+1), EMA21 > EMA50 (+1), EMA50 > EMA100 (+1)
        # Total: +3
        self.assertEqual(score, 3)


if __name__ == '__main__':
    unittest.main()
