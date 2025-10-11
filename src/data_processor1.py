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

    import os

    def pair_trades(self, df: pd.DataFrame, filepath: str = None) -> pd.DataFrame:
        """
        Pair BUY and SELL trades using FIFO method (per-symbol basis).
        Since each file belongs to a single client, client_id is derived from filename if missing.
        """
        self.logger.info("Pairing BUY and SELL trades (single-client FIFO)...")

        df = df.copy()
        df['trade_date'] = pd.to_datetime(df['trade_date'])
        df = df.sort_values(['symbol', 'trade_date']).reset_index(drop=True)

        # Derive client_id from filename if not in data
        if filepath:
            base_name = os.path.basename(filepath)
            client_id = os.path.splitext(base_name)[0].replace("trade_", "").replace(".csv", "").upper()
            df['client_id'] = client_id
        else:
            client_id = df['client_id'].iloc[0] if 'client_id' in df.columns else 'UNKNOWN'

        paired_trades = []

        # --- Process symbol-wise trades for this client ---
        for symbol, group in df.groupby('symbol'):
            buys = group[group['transaction_type'].str.upper() == 'BUY'].copy()
            sells = group[group['transaction_type'].str.upper() == 'SELL'].copy()

            while not buys.empty and not sells.empty:
                buy = buys.iloc[0]
                sell = sells.iloc[0]
                qty = min(buy['quantity'], sell['quantity'])

                pnl = (sell['price'] - buy['price']) * qty - (buy.get('charges', 0) + sell.get('charges', 0))
                holding_period = (sell['trade_date'] - buy['trade_date']).total_seconds() / 60
                trade_value = (buy['price'] * qty + sell['price'] * qty) / 2

                paired_trades.append({
                    'client_id': client_id,
                    'symbol': symbol,
                    'buy_date': buy['trade_date'],
                    'sell_date': sell['trade_date'],
                    'quantity': qty,
                    'buy_price': buy['price'],
                    'sell_price': sell['price'],
                    'pnl': pnl,
                    'holding_period_minutes': holding_period,
                    'trade_value': trade_value,
                    'charges_total': buy.get('charges', 0) + sell.get('charges', 0)
                })

                # Adjust remaining quantities
                buys.at[buy.name, 'quantity'] -= qty
                sells.at[sell.name, 'quantity'] -= qty

                if buys.at[buy.name, 'quantity'] <= 0:
                    buys = buys.drop(buy.name)
                if sells.at[sell.name, 'quantity'] <= 0:
                    sells = sells.drop(sell.name)

        paired_df = pd.DataFrame(paired_trades)

        if paired_df.empty:
            self.logger.warning(f"No BUY/SELL pairs found for {client_id}. Returning empty DataFrame.")
            df['pnl'] = 0.0
            df['holding_period_minutes'] = 0.0
            return df

        paired_df['trade_date'] = paired_df['sell_date']
        self.logger.info(
            f"Paired {len(paired_df)} trades for client {client_id} across {df['symbol'].nunique()} symbols.")
        return paired_df

    def aggregate_daily_stats(self, df: pd.DataFrame) -> pd.DataFrame:
        """Aggregate trades by day"""
        daily_stats = df.groupby(df['trade_date'].dt.date).agg({
            'trade_value': 'sum',
            'pnl': 'sum',
            'symbol': 'count',
            'quantity': 'sum'
        }).rename(columns={'symbol': 'num_trades'})

        return daily_stats
