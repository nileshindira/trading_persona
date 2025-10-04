"""
EMA Allocation Calculator Module
Calculates EMA-based allocation scores for stocks and indices using TradingView data
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional, Tuple
from datetime import datetime, timedelta
import logging

try:
    from tvDatafeed import TvDatafeed, Interval
except ImportError:
    raise ImportError("Please install tvDatafeed: pip install tvDatafeed")


class EMACalculator:
    """Calculate EMA allocation scores for trading analysis"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Initialize TradingView datafeed
        try:
            self.tv = TvDatafeed()
            self.logger.info("TradingView datafeed initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize TradingView datafeed: {str(e)}")
            raise
    
    def calculate_ema(self, prices: pd.Series, period: int) -> pd.Series:
        """Calculate Exponential Moving Average"""
        return prices.ewm(span=period, adjust=False).mean()
    
    def calculate_ema_score(self, close_price: float, ema21: float, ema50: float, ema100: float) -> int:
        """
        Calculate EMA allocation score based on price position relative to EMAs
        
        Scoring System:
        - If price > EMA level → Assign +1
        - If price < EMA level → Assign -1
        - If EMA21 > EMA100 → Assign +1
        - If EMA21 > EMA50 → Assign +1
        - If EMA50 > EMA100 → Assign +1
        - If EMA21 < EMA100 → Assign -1
        - If EMA21 < EMA50 → Assign -1
        - If EMA50 < EMA100 → Assign -1
        
        Score range: -6 to +6
        """
        score = 0
        
        # Price vs EMAs (3 points)
        score += 1 if close_price > ema21 else -1
        score += 1 if close_price > ema50 else -1
        score += 1 if close_price > ema100 else -1
        
        # EMA relationships (3 points)
        score += 1 if ema21 > ema100 else -1
        score += 1 if ema21 > ema50 else -1
        score += 1 if ema50 > ema100 else -1
        
        return score
    
    def get_historical_data(self, symbol: str, exchange: str = 'NSE', 
                           n_bars: int = 200, interval: Interval = Interval.in_daily) -> Optional[pd.DataFrame]:
        """
        Fetch historical data from TradingView
        
        Args:
            symbol: Trading symbol (e.g., 'RELIANCE', 'NIFTY', 'MIDCPNIFTY')
            exchange: Exchange name (NSE, BSE, etc.)
            n_bars: Number of bars to fetch (default 200 for EMA100 calculation)
            interval: Time interval (daily, weekly, etc.)
        """
        try:
            self.logger.info(f"Fetching data for {symbol} from {exchange}")
            df = self.tv.get_hist(symbol=symbol, exchange=exchange, interval=interval, n_bars=n_bars)
            
            if df is None or df.empty:
                self.logger.warning(f"No data received for {symbol}")
                return None
            
            self.logger.info(f"Fetched {len(df)} bars for {symbol}")
            return df
        
        except Exception as e:
            self.logger.error(f"Error fetching data for {symbol}: {str(e)}")
            return None
    
    def calculate_emas_for_symbol(self, symbol: str, exchange: str = 'NSE', 
                                  target_date: Optional[datetime] = None) -> Tuple[Optional[int], Dict]:
        """
        Calculate EMA score for a specific symbol up to target_date (t-1)
        
        Returns:
            Tuple of (ema_score, ema_values_dict)
        """
        try:
            # Fetch historical data
            df = self.get_historical_data(symbol, exchange, n_bars=200)
            
            if df is None or len(df) < 100:
                self.logger.warning(f"Insufficient data for {symbol}")
                return None, {}
            
            # Calculate EMAs
            df['EMA21'] = self.calculate_ema(df['close'], 21)
            df['EMA50'] = self.calculate_ema(df['close'], 50)
            df['EMA100'] = self.calculate_ema(df['close'], 100)
            
            # Get data up to t-1 (yesterday or specified date)
            if target_date:
                df = df[df.index < target_date]
            
            if df.empty:
                self.logger.warning(f"No data available before target date for {symbol}")
                return None, {}
            
            # Get latest values
            latest = df.iloc[-1]
            close_price = latest['close']
            ema21 = latest['EMA21']
            ema50 = latest['EMA50']
            ema100 = latest['EMA100']
            
            # Calculate score
            score = self.calculate_ema_score(close_price, ema21, ema50, ema100)
            
            ema_values = {
                'close': close_price,
                'ema21': ema21,
                'ema50': ema50,
                'ema100': ema100,
                'date': latest.name
            }
            
            self.logger.info(f"EMA score for {symbol}: {score}/6")
            
            return score, ema_values
        
        except Exception as e:
            self.logger.error(f"Error calculating EMA for {symbol}: {str(e)}")
            return None, {}
    
    def extract_base_symbol(self, trading_symbol: str) -> str:
        """
        Extract base stock symbol from trading symbol
        e.g., 'NIFTY 16 SEP 25200 CALL' -> 'NIFTY'
             'BANKNIFTY 30 SEP 54300 PUT' -> 'BANKNIFTY'
             'RELIANCE' -> 'RELIANCE'
        """
        # For options/futures, take the first word
        parts = trading_symbol.split()
        base_symbol = parts[0]
        
        # Handle index names
        if base_symbol == 'NIFTY':
            return 'NIFTY'
        elif base_symbol == 'BANKNIFTY':
            return 'BANKNIFTY'
        elif base_symbol == 'FINNIFTY':
            return 'FINNIFTY'
        else:
            # For stocks, return as is
            return base_symbol
    
    def add_ema_scores_to_trades(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add EMA allocation scores to trading dataframe
        Adds three columns: ema_score_stock, ema_score_nifty, ema_score_midcap
        """
        df = df.copy()
        
        # Initialize columns with None
        df['ema_score_stock'] = None
        df['ema_score_nifty'] = None
        df['ema_score_midcap'] = None
        
        # Get unique dates and symbols
        unique_dates = df['trade_date'].dt.date.unique()
        unique_symbols = df['symbol'].unique()
        
        # Cache for calculated scores to avoid redundant API calls
        score_cache = {}
        
        self.logger.info(f"Calculating EMA scores for {len(unique_symbols)} symbols across {len(unique_dates)} dates")
        
        for idx, row in df.iterrows():
            trade_date = row['trade_date']
            symbol = row['symbol']
            
            # Extract base symbol
            base_symbol = self.extract_base_symbol(symbol)
            
            # Create cache key
            cache_key_stock = f"{base_symbol}_{trade_date.date()}"
            cache_key_nifty = f"NIFTY_{trade_date.date()}"
            cache_key_midcap = f"MIDCPNIFTY_{trade_date.date()}"
            
            # Calculate stock EMA score
            if cache_key_stock not in score_cache:
                score, _ = self.calculate_emas_for_symbol(
                    base_symbol, 
                    exchange='NSE',
                    target_date=trade_date
                )
                score_cache[cache_key_stock] = score
            
            df.at[idx, 'ema_score_stock'] = score_cache[cache_key_stock]
            
            # Calculate NIFTY EMA score
            if cache_key_nifty not in score_cache:
                score, _ = self.calculate_emas_for_symbol(
                    'NIFTY',
                    exchange='NSE',
                    target_date=trade_date
                )
                score_cache[cache_key_nifty] = score
            
            df.at[idx, 'ema_score_nifty'] = score_cache[cache_key_nifty]
            
            # Calculate MIDCAP NIFTY EMA score
            if cache_key_midcap not in score_cache:
                score, _ = self.calculate_emas_for_symbol(
                    'MIDCPNIFTY',
                    exchange='NSE',
                    target_date=trade_date
                )
                score_cache[cache_key_midcap] = score
            
            df.at[idx, 'ema_score_midcap'] = score_cache[cache_key_midcap]
        
        self.logger.info("EMA scores added to all trades")
        
        return df
    
    def get_ema_summary_stats(self, df: pd.DataFrame) -> Dict:
        """
        Generate summary statistics for EMA scores
        """
        stats = {
            'stock_ema': {
                'mean': df['ema_score_stock'].mean() if 'ema_score_stock' in df.columns else None,
                'min': df['ema_score_stock'].min() if 'ema_score_stock' in df.columns else None,
                'max': df['ema_score_stock'].max() if 'ema_score_stock' in df.columns else None,
            },
            'nifty_ema': {
                'mean': df['ema_score_nifty'].mean() if 'ema_score_nifty' in df.columns else None,
                'min': df['ema_score_nifty'].min() if 'ema_score_nifty' in df.columns else None,
                'max': df['ema_score_nifty'].max() if 'ema_score_nifty' in df.columns else None,
            },
            'midcap_ema': {
                'mean': df['ema_score_midcap'].mean() if 'ema_score_midcap' in df.columns else None,
                'min': df['ema_score_midcap'].min() if 'ema_score_midcap' in df.columns else None,
                'max': df['ema_score_midcap'].max() if 'ema_score_midcap' in df.columns else None,
            }
        }
        
        return stats
