"""
Pattern Detector Module
Detects trading patterns and behavioral issues
"""

import pandas as pd
import numpy as np
from typing import Dict, List
import logging

class TradingPatternDetector:
    """Detect trading patterns and behaviors (compatible with paired trades)"""

    def __init__(self, config: Dict):
        self.config = config
        self.min_trades = config['analysis'].get('min_trades_for_pattern', 3)
        self.logger = logging.getLogger(__name__)

    # ==========================================================
    # MAIN ENTRY
    # ==========================================================
    def detect_all_patterns(self, df: pd.DataFrame) -> Dict:
        """Detect all trading patterns from cleaned and paired trade data"""
        patterns = {}

        # --- Ensure required columns exist ---
        df = df.copy()
        if 'pnl' not in df.columns:
            self.logger.warning("No 'pnl' column found — revenge/scalping limited.")
            df['pnl'] = 0.0
        if 'transaction_type' not in df.columns:
            # Derive synthetic transaction_type if missing (based on available columns)
            df['transaction_type'] = np.where(df.get('buy_date').notna(), 'BUY', 'SELL')

        # --- Compute patterns ---
        patterns['overtrading'] = self.detect_overtrading(df)
        patterns['revenge_trading'] = self.detect_revenge_trading(df)
        patterns['pyramiding'] = self.detect_pyramiding(df)
        patterns['scalping'] = self.detect_scalping(df)
        patterns['hedging'] = self.detect_hedging(df)
        patterns['time_patterns'] = self.detect_time_patterns(df)
        patterns['instrument_clustering'] = self.detect_instrument_clustering(df)

        return patterns

    # ==========================================================
    # PATTERN DETECTION METHODS
    # ==========================================================
    def detect_overtrading(self, df: pd.DataFrame) -> Dict:
        """Detect overtrading behavior — too many trades per day"""
        if 'trade_date' not in df.columns:
            return {'detected': False}

        daily_trades = df.groupby(df['trade_date'].dt.date).size()
        excessive_threshold = 10  # trades/day

        overtrading_days = (daily_trades > excessive_threshold).sum()
        total_days = len(daily_trades)

        return {
            'detected': overtrading_days > total_days * 0.3,
            'overtrading_days': int(overtrading_days),
            'avg_trades_per_day': float(daily_trades.mean()),
            'max_trades_per_day': int(daily_trades.max() if len(daily_trades) else 0),
            'severity': (
                'HIGH' if overtrading_days > total_days * 0.5
                else 'MEDIUM' if overtrading_days > total_days * 0.3
                else 'LOW'
            )
        }

    def detect_revenge_trading(self, df: pd.DataFrame) -> Dict:
        """Detect revenge trading — larger trade soon after loss"""
        if 'pnl' not in df.columns or 'trade_date' not in df.columns:
            return {'detected': False, 'count': 0, 'percentage': 0}

        df_sorted = df.sort_values('trade_date')
        revenge_trades = 0

        for i in range(1, len(df_sorted)):
            prev_trade = df_sorted.iloc[i-1]
            curr_trade = df_sorted.iloc[i]
            time_diff = (curr_trade['trade_date'] - prev_trade['trade_date']).total_seconds() / 60

            if prev_trade['pnl'] < 0 and time_diff < 30:
                if curr_trade.get('quantity', 0) > prev_trade.get('quantity', 0):
                    revenge_trades += 1

        return {
            'detected': revenge_trades > self.min_trades,
            'count': int(revenge_trades),
            'percentage': float(revenge_trades / len(df) * 100) if len(df) else 0
        }

    def detect_pyramiding(self, df: pd.DataFrame) -> Dict:
        """Detect pyramiding — repeated buys adding to same position"""
        if 'symbol' not in df.columns:
            return {'detected': False, 'sequences': 0}

        pyramiding_sequences = 0

        for symbol, group in df.groupby('symbol'):
            group = group.sort_values('trade_date')
            consecutive_buys = 0
            for _, trade in group.iterrows():
                ttype = str(trade.get('transaction_type', '')).upper()
                if ttype == 'BUY':
                    consecutive_buys += 1
                else:
                    if consecutive_buys > 1:
                        pyramiding_sequences += 1
                    consecutive_buys = 0

        return {
            'detected': pyramiding_sequences > 3,
            'sequences': int(pyramiding_sequences)
        }

    def detect_scalping(self, df: pd.DataFrame) -> Dict:
        """Detect scalping — trades with very short holding duration"""
        if 'holding_period_minutes' not in df.columns:
            return {'detected': False, 'avg_holding_minutes': None}

        avg_holding = df['holding_period_minutes'].mean()
        scalping_trades = len(df[df['holding_period_minutes'] < 30])

        return {
            'detected': avg_holding < 60 if not np.isnan(avg_holding) else False,
            'avg_holding_minutes': float(avg_holding) if not np.isnan(avg_holding) else None,
            'scalping_trades': int(scalping_trades),
            'scalping_percentage': float(scalping_trades / len(df) * 100) if len(df) else 0
        }

    def detect_hedging(self, df: pd.DataFrame) -> Dict:
        """Detect hedging — simultaneous CALL and PUT trades on same base"""
        if 'symbol' not in df.columns or 'trade_date' not in df.columns:
            return {'detected': False, 'hedged_days': 0}

        df['symbol'] = df['symbol'].astype(str)
        hedged_positions = 0

        for date in df['trade_date'].dt.date.unique():
            day_trades = df[df['trade_date'].dt.date == date].copy()
            day_trades['base_symbol'] = day_trades['symbol'].str.extract(r'([A-Z]+)')[0]

            for base_sym, group in day_trades.groupby('base_symbol'):
                has_call = any('CALL' in s for s in group['symbol'])
                has_put = any('PUT' in s for s in group['symbol'])
                if has_call and has_put:
                    hedged_positions += 1

        return {'detected': hedged_positions > 5, 'hedged_days': int(hedged_positions)}

    def detect_time_patterns(self, df: pd.DataFrame) -> Dict:
        """Detect trading time preferences"""
        if 'trade_hour' not in df.columns:
            return {'most_active_hours': [], 'morning_trader': None}

        hourly_dist = df['trade_hour'].value_counts()
        morning_trades = len(df[df['trade_hour'] < 12])
        afternoon_trades = len(df[df['trade_hour'] >= 12])

        return {
            'most_active_hours': hourly_dist.head(3).index.tolist(),
            'morning_trader': morning_trades > afternoon_trades,
            'morning_trades': int(morning_trades),
            'afternoon_trades': int(afternoon_trades)
        }

    def detect_instrument_clustering(self, df: pd.DataFrame) -> Dict:
        """Detect focus bias (NIFTY/BANKNIFTY/CALL/PUT dominance)"""
        if 'symbol' not in df.columns:
            return {}

        nifty_trades = len(df[df['symbol'].str.contains('NIFTY', na=False)])
        banknifty_trades = len(df[df['symbol'].str.contains('BANKNIFTY', na=False)])
        call_trades = len(df[df['symbol'].str.contains('CALL', na=False)])
        put_trades = len(df[df['symbol'].str.contains('PUT', na=False)])

        return {
            'nifty_percentage': round(nifty_trades / len(df) * 100, 2) if len(df) else 0,
            'banknifty_percentage': round(banknifty_trades / len(df) * 100, 2) if len(df) else 0,
            'call_percentage': round(call_trades / len(df) * 100, 2) if len(df) else 0,
            'put_percentage': round(put_trades / len(df) * 100, 2) if len(df) else 0
        }
