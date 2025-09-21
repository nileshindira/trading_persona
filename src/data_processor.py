"""
Data Processor Module
Handles data loading, cleaning, and preparation for analysis
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
import logging

class TradingDataProcessor:
    """Process and clean trading data from various sources"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
    def load_data(self, filepath: str, source_type: str = "csv") -> pd.DataFrame:
        """Load trading data from file"""
        try:
            if source_type == "csv":
                df = pd.read_csv(filepath)
            elif source_type == "excel":
                df = pd.read_excel(filepath)
            elif source_type == "json":
                df = pd.read_json(filepath)
            else:
                raise ValueError(f"Unsupported source type: {source_type}")
            
            self.logger.info(f"Loaded {len(df)} records from {filepath}")
            return df
        except Exception as e:
            self.logger.error(f"Error loading data: {str(e)}")
            raise
    
    def validate_data(self, df: pd.DataFrame) -> Tuple[bool, List[str]]:
        """Validate data has required columns and structure"""
        required_cols = self.config['data']['required_columns']
        missing_cols = [col for col in required_cols if col not in df.columns]
        
        if missing_cols:
            return False, missing_cols
        return True, []
    
    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and preprocess trading data"""
        df = df.copy()
        
        # Convert dates
        df['trade_date'] = pd.to_datetime(df['trade_date'])
        
        # Handle missing values
        df = df.dropna(subset=['symbol', 'price', 'quantity'])
        
        # Add derived columns
        df['trade_hour'] = df['trade_date'].dt.hour
        df['trade_day_of_week'] = df['trade_date'].dt.dayofweek
        df['trade_month'] = df['trade_date'].dt.month
        
        # Calculate trade value if not present
        if 'trade_value' not in df.columns:
            df['trade_value'] = df['price'] * df['quantity']
        
        # Sort by date
        df = df.sort_values('trade_date').reset_index(drop=True)
        
        self.logger.info(f"Cleaned data: {len(df)} records")
        return df
    
    def pair_trades(self, df: pd.DataFrame) -> pd.DataFrame:
        """Pair buy/sell trades to calculate P&L"""
        df = df.copy()
        df['paired_trade_id'] = None
        df['pnl'] = 0.0
        df['holding_period_minutes'] = 0
        
        # Group by symbol
        for symbol in df['symbol'].unique():
            symbol_df = df[df['symbol'] == symbol].copy()
            
            buys = symbol_df[symbol_df['transaction_type'] == 'BUY'].copy()
            sells = symbol_df[symbol_df['transaction_type'] == 'SELL'].copy()
            
            # Match trades using FIFO
            for idx, buy_row in buys.iterrows():
                remaining_qty = buy_row['quantity']
                
                for sidx, sell_row in sells.iterrows():
                    if remaining_qty <= 0:
                        break
                    
                    if sell_row['trade_date'] > buy_row['trade_date']:
                        matched_qty = min(remaining_qty, sell_row['quantity'])
                        
                        # Calculate P&L
                        buy_value = matched_qty * buy_row['price']
                        sell_value = matched_qty * sell_row['price']
                        pnl = sell_value - buy_value
                        
                        # Calculate holding period
                        holding_period = (sell_row['trade_date'] - buy_row['trade_date']).total_seconds() / 60
                        
                        # Update dataframe
                        df.loc[idx, 'pnl'] += pnl
                        df.loc[idx, 'holding_period_minutes'] = holding_period
                        
                        remaining_qty -= matched_qty
        
        return df
    
    def aggregate_daily_stats(self, df: pd.DataFrame) -> pd.DataFrame:
        """Aggregate trades by day"""
        daily_stats = df.groupby(df['trade_date'].dt.date).agg({
            'trade_value': 'sum',
            'pnl': 'sum',
            'symbol': 'count',
            'quantity': 'sum'
        }).rename(columns={'symbol': 'num_trades'})
        
        return daily_stats
