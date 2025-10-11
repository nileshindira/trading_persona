"""
Pattern Detector Module
------------------------
Detects behavioral and performance patterns from pre-paired trading data
Adapted for new trade file format (Buy/Sell in single row)
"""

import pandas as pd
import numpy as np
from typing import Dict
import logging


class TradingPatternDetector:
    """Detect trading patterns and behavioral traits (works on paired data)"""

    def __init__(self, config: Dict):
        self.config = config
        self.min_trades = config['analysis'].get('min_trades_for_pattern', 3)
        self.logger = logging.getLogger(__name__)

    # ==========================================================
    # MAIN ENTRY
    # ==========================================================
    def detect_all_patterns(self, df: pd.DataFrame) -> Dict:
        """Detect all major trading patterns from paired trade data"""
        patterns = {}

        df = df.copy()

        # Ensure compatibility fields
        if 'trade_date' not in df.columns:
            df['trade_date'] = df['sell_date']

        # Handle missing columns
        if 'pnl' not in df.columns:
            df['pnl'] = 0.0
        if 'trade_type' not in df.columns:
            df['trade_type'] = 'Unknown'

        # --- Compute behavioral and style patterns ---
        patterns['overtrading'] = self.detect_overtrading(df)
        patterns['revenge_trading'] = self.detect_revenge_trading(df)
        patterns['scalping'] = self.detect_scalping(df)
        patterns['holding_behavior'] = self.detect_holding_behavior(df)
        patterns['focus_bias'] = self.detect_focus_bias(df)
        # patterns['timing_preference'] = self.detect_timing_preference(df)

        return patterns

    # ==========================================================
    # PATTERN DETECTION METHODS
    # ==========================================================
    def detect_overtrading(self, df: pd.DataFrame) -> Dict:
        """Detect if trader trades excessively per day"""
        if 'trade_date' not in df.columns:
            return {'detected': False}

        daily_trades = df.groupby(df['trade_date'].dt.date).size()
        excessive_threshold = 20  # can tweak

        overtrading_days = (daily_trades > excessive_threshold).sum()
        total_days = len(daily_trades)

        return {
            'detected': overtrading_days > total_days * 0.3 if total_days > 0 else False,
            'overtrading_days': int(overtrading_days),
            'avg_trades_per_day': float(daily_trades.mean()) if total_days > 0 else 0.0,
            'max_trades_per_day': int(daily_trades.max()) if total_days > 0 else 0,
            'severity': (
                'HIGH' if overtrading_days > total_days * 0.5
                else 'MEDIUM' if overtrading_days > total_days * 0.3
                else 'LOW'
            )
        }

    def detect_revenge_trading(self, df: pd.DataFrame) -> Dict:
        """Detect revenge trading — large trade after loss within short duration"""
        if 'pnl' not in df.columns or 'trade_date' not in df.columns:
            return {'detected': False, 'count': 0, 'percentage': 0}

        df_sorted = df.sort_values('trade_date')
        revenge_trades = 0

        for i in range(1, len(df_sorted)):
            prev = df_sorted.iloc[i - 1]
            curr = df_sorted.iloc[i]
            time_gap = (curr['trade_date'] - prev['trade_date']).total_seconds() / 60

            if prev['pnl'] < 0 and time_gap < 30:
                if curr.get('quantity', 0) > prev.get('quantity', 0):
                    revenge_trades += 1

        return {
            'detected': revenge_trades > self.min_trades,
            'count': int(revenge_trades),
            'percentage': float(revenge_trades / len(df) * 100) if len(df) else 0
        }

    def detect_scalping(self, df: pd.DataFrame) -> Dict:
        """Detect scalping — extremely short duration trades"""
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

    def detect_holding_behavior(self, df: pd.DataFrame) -> Dict:
        """Classify holding tendencies — intraday, short-term, long-term"""
        if 'holding_days' not in df.columns:
            return {'distribution': {}}

        bins = [0, 1, 7, 30, 90, 365, np.inf]
        labels = ['Intraday', 'Short-term', 'Weekly', 'Monthly', 'Quarterly', 'Long-term']
        df['holding_category'] = pd.cut(df['holding_days'], bins=bins, labels=labels, right=False)

        distribution = df['holding_category'].value_counts(normalize=True) * 100

        return {
            'distribution': distribution.to_dict(),
            'dominant_category': distribution.idxmax() if not distribution.empty else None
        }

    def detect_focus_bias(self, df: pd.DataFrame) -> Dict:
        """Detect concentration towards few instruments"""
        if 'symbol' not in df.columns:
            return {}

        top_symbols = df['symbol'].value_counts().head(5)
        concentration_ratio = top_symbols.sum() / len(df) if len(df) else 0

        return {
            'top_symbols': top_symbols.to_dict(),
            'focus_ratio': round(concentration_ratio * 100, 2),
            'detected': concentration_ratio > 0.5
        }

    def detect_timing_preference(self, df: pd.DataFrame) -> Dict:
        """Identify morning vs afternoon bias based on buy time"""
        if 'buy_date' not in df.columns:
            return {'detected': False}

        df['buy_hour'] = df['buy_date'].dt.hour
        morning_trades = len(df[df['buy_hour'] < 12])
        afternoon_trades = len(df[df['buy_hour'] >= 12])

        preference = 'Morning Trader' if morning_trades > afternoon_trades else 'Afternoon Trader'

        return {
            'detected': True,
            'morning_trades': int(morning_trades),
            'afternoon_trades': int(afternoon_trades),
            'preference': preference
        }
