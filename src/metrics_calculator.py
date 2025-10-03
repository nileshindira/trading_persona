"""
Metrics Calculator Module
Calculates comprehensive trading performance metrics
"""

import pandas as pd
import numpy as np
from typing import Dict
import logging

class TradingMetricsCalculator:
    """Calculate comprehensive trading metrics"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.risk_free_rate = config['metrics']['risk_free_rate']
        self.trading_days = config['metrics']['trading_days_per_year']
        self.logger = logging.getLogger(__name__)
    
    def calculate_all_metrics(self, df: pd.DataFrame) -> Dict:
        """Calculate all trading metrics"""
        
        metrics = {
            'total_trades': len(df),
            'total_pnl': self.calculate_total_pnl(df),
            'win_rate': self.calculate_win_rate(df),
            'avg_win': self.calculate_avg_win(df),
            'avg_loss': self.calculate_avg_loss(df),
            'profit_factor': self.calculate_profit_factor(df),
            'sharpe_ratio': self.calculate_sharpe_ratio(df),
            'sortino_ratio': self.calculate_sortino_ratio(df),
            'max_drawdown': self.calculate_max_drawdown(df),
            'max_drawdown_pct': self.calculate_max_drawdown_pct(df),
            'avg_trade_value': self.calculate_avg_trade_value(df),
            'largest_win': self.calculate_largest_win(df),
            'largest_loss': self.calculate_largest_loss(df),
            'consecutive_wins': self.calculate_consecutive_wins(df),
            'consecutive_losses': self.calculate_consecutive_losses(df),
            'avg_holding_period': self.calculate_avg_holding_period(df),
            'avg_trades_per_day': self.calculate_avg_trades_per_day(df),
            'date_range': self.get_date_range(df),
            'trading_days': self.get_trading_days(df)
        }
        
        # Add metrics that may have been added (like EMA)
        if 'ema_allocation' in df.columns or any(col.startswith('ema_score') for col in df.columns):
            metrics['ema_enabled'] = True
        
        return metrics
    
    def calculate_total_pnl(self, df: pd.DataFrame) -> float:
        """Calculate total P&L"""
        return float(df['pnl'].sum())
    
    def calculate_win_rate(self, df: pd.DataFrame) -> float:
        """Calculate win rate percentage"""
        if len(df) == 0:
            return 0.0
        winning_trades = len(df[df['pnl'] > 0])
        return float(winning_trades / len(df) * 100)
    
    def calculate_avg_win(self, df: pd.DataFrame) -> float:
        """Calculate average winning trade"""
        winning_trades = df[df['pnl'] > 0]['pnl']
        return float(winning_trades.mean()) if len(winning_trades) > 0 else 0.0
    
    def calculate_avg_loss(self, df: pd.DataFrame) -> float:
        """Calculate average losing trade"""
        losing_trades = df[df['pnl'] < 0]['pnl']
        return float(losing_trades.mean()) if len(losing_trades) > 0 else 0.0
    
    def calculate_profit_factor(self, df: pd.DataFrame) -> float:
        """Calculate profit factor (gross profit / gross loss)"""
        gross_profit = df[df['pnl'] > 0]['pnl'].sum()
        gross_loss = abs(df[df['pnl'] < 0]['pnl'].sum())
        
        if gross_loss == 0:
            return float('inf') if gross_profit > 0 else 0.0
        
        return float(gross_profit / gross_loss)
    
    def calculate_sharpe_ratio(self, df: pd.DataFrame) -> float:
        """Calculate Sharpe ratio"""
        if len(df) < 2:
            return 0.0
        
        returns = df['pnl'] / df['trade_value']
        
        if returns.std() == 0:
            return 0.0
        
        excess_return = returns.mean() - (self.risk_free_rate / self.trading_days)
        sharpe = excess_return / returns.std() * np.sqrt(self.trading_days)
        
        return float(sharpe)
    
    def calculate_sortino_ratio(self, df: pd.DataFrame) -> float:
        """Calculate Sortino ratio (uses downside deviation)"""
        if len(df) < 2:
            return 0.0
        
        returns = df['pnl'] / df['trade_value']
        
        # Calculate downside deviation
        downside_returns = returns[returns < 0]
        if len(downside_returns) == 0:
            return float('inf') if returns.mean() > 0 else 0.0
        
        downside_std = downside_returns.std()
        if downside_std == 0:
            return 0.0
        
        excess_return = returns.mean() - (self.risk_free_rate / self.trading_days)
        sortino = excess_return / downside_std * np.sqrt(self.trading_days)
        
        return float(sortino)
    
    def calculate_max_drawdown(self, df: pd.DataFrame) -> float:
        """Calculate maximum drawdown in rupees"""
        df_sorted = df.sort_values('trade_date')
        cumulative_pnl = df_sorted['pnl'].cumsum()
        
        running_max = cumulative_pnl.cummax()
        drawdown = cumulative_pnl - running_max
        
        return float(drawdown.min())
    
    def calculate_max_drawdown_pct(self, df: pd.DataFrame) -> float:
        """Calculate maximum drawdown percentage"""
        df_sorted = df.sort_values('trade_date')
        cumulative_pnl = df_sorted['pnl'].cumsum()
        
        running_max = cumulative_pnl.cummax()
        drawdown_pct = ((cumulative_pnl - running_max) / running_max.replace(0, 1)) * 100
        
        return float(drawdown_pct.min())
    
    def calculate_avg_trade_value(self, df: pd.DataFrame) -> float:
        """Calculate average trade value"""
        return float(df['trade_value'].mean())
    
    def calculate_largest_win(self, df: pd.DataFrame) -> float:
        """Calculate largest single win"""
        return float(df['pnl'].max()) if len(df) > 0 else 0.0
    
    def calculate_largest_loss(self, df: pd.DataFrame) -> float:
        """Calculate largest single loss"""
        return float(df['pnl'].min()) if len(df) > 0 else 0.0
    
    def calculate_consecutive_wins(self, df: pd.DataFrame) -> int:
        """Calculate maximum consecutive wins"""
        df_sorted = df.sort_values('trade_date')
        max_consecutive = 0
        current_consecutive = 0
        
        for pnl in df_sorted['pnl']:
            if pnl > 0:
                current_consecutive += 1
                max_consecutive = max(max_consecutive, current_consecutive)
            else:
                current_consecutive = 0
        
        return int(max_consecutive)
    
    def calculate_consecutive_losses(self, df: pd.DataFrame) -> int:
        """Calculate maximum consecutive losses"""
        df_sorted = df.sort_values('trade_date')
        max_consecutive = 0
        current_consecutive = 0
        
        for pnl in df_sorted['pnl']:
            if pnl < 0:
                current_consecutive += 1
                max_consecutive = max(max_consecutive, current_consecutive)
            else:
                current_consecutive = 0
        
        return int(max_consecutive)
    
    def calculate_avg_holding_period(self, df: pd.DataFrame) -> float:
        """Calculate average holding period in minutes"""
        return float(df['holding_period_minutes'].mean()) if 'holding_period_minutes' in df.columns else 0.0
    
    def calculate_avg_trades_per_day(self, df: pd.DataFrame) -> float:
        """Calculate average trades per day"""
        trading_days = df['trade_date'].dt.date.nunique()
        return float(len(df) / trading_days) if trading_days > 0 else 0.0
    
    def get_date_range(self, df: pd.DataFrame) -> str:
        """Get date range of trading data"""
        start_date = df['trade_date'].min().strftime('%Y-%m-%d')
        end_date = df['trade_date'].max().strftime('%Y-%m-%d')
        return f"{start_date} to {end_date}"
    
    def get_trading_days(self, df: pd.DataFrame) -> int:
        """Get number of unique trading days"""
        return int(df['trade_date'].dt.date.nunique())
