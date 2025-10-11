"""
Data Processor Module
Handles data loading, cleaning, and preparation for analysis
"""
import os
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
        """Clean and normalize pre-paired trade data"""
        df = df.copy()

        # Standardize column names (strip spaces)
        df.columns = [c.strip() for c in df.columns]

        # Rename to internal standard names
        rename_map = {
            'Scrip Name': 'symbol',
            'ISIN': 'isin',
            'Quantity': 'quantity',
            'Buy Date': 'buy_date',
            'Buy Rate': 'buy_price',
            'Buy Value': 'buy_value',
            'Sell Date': 'sell_date',
            'Sell Rate': 'sell_price',
            'Sell Value': 'sell_value',
            'Holding Days': 'holding_days',
            'Profit(+) / Loss(-)': 'pnl',
            'Trade Type': 'trade_type'
        }
        df = df.rename(columns=rename_map)

        # Convert dates and numeric fields
        for col in ['buy_date', 'sell_date']:
            df[col] = pd.to_datetime(df[col], errors='coerce')

        for col in ['quantity', 'buy_price', 'sell_price', 'pnl', 'buy_value', 'sell_value']:
            df[col] = pd.to_numeric(df[col], errors='coerce')

        # Drop empty rows
        df = df.dropna(subset=['symbol', 'buy_date', 'sell_date'])

        # Add derived columns for compatibility
        df['trade_date'] = df['sell_date']
        df['trade_value'] = (df['buy_value'] + df['sell_value']) / 2
        df['holding_period_minutes'] = df['holding_days'] * 1440  # 1 day = 1440 mins

        # Add profit flag
        df['pnl_flag'] = np.where(df['pnl'] > 0, 'WIN', 'LOSS')

        self.logger.info(f"✅ Cleaned data: {len(df)} paired trades loaded.")
        return df

    def pair_trades(self, df: pd.DataFrame, filepath: str = None) -> pd.DataFrame:
        """Bypass pairing — data already paired"""
        self.logger.info("Skipping BUY/SELL pairing (data already aggregated)")
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
