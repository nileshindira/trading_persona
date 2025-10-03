import pandas as pd
import numpy as np
from typing import Dict, Tuple
from scipy import stats


class TradingMetricsCalculator:
    ###Calculate comprehensive trading metrics###

    def __init__(self, config: Dict):
        self.config = config
        self.risk_free_rate = config['metrics']['risk_free_rate']
        self.trading_days = config['metrics']['trading_days_per_year']

    def calculate_all_metrics(self, df: pd.DataFrame) -> Dict:
        ###Calculate all trading metrics###
        metrics = {}

        # Basic metrics
        metrics.update(self.calculate_basic_metrics(df))

        # Performance metrics
        metrics.update(self.calculate_performance_metrics(df))

        # Risk metrics
        metrics.update(self.calculate_risk_metrics(df))

        # Trading behavior metrics
        metrics.update(self.calculate_behavior_metrics(df))

        return metrics

    def calculate_basic_metrics(self, df: pd.DataFrame) -> Dict:
        ###Calculate basic trading statistics###
        total_trades = len(df)
        total_days = (df['trade_date'].max() - df['trade_date'].min()).days

        return {
            'total_trades': total_trades,
            'total_days': total_days,
            'avg_trades_per_day': total_trades / max(total_days, 1),
            'total_trade_value': df['trade_value'].sum(),
            'avg_trade_value': df['trade_value'].mean(),
            'unique_symbols': df['symbol'].nunique(),
            'date_range': f"{df['trade_date'].min().date()} to {df['trade_date'].max().date()}"
        }

    def calculate_performance_metrics(self, df: pd.DataFrame) -> Dict:
        ###Calculate performance-related metrics###
        total_pnl = df['pnl'].sum()
        winning_trades = df[df['pnl'] > 0]
        losing_trades = df[df['pnl'] < 0]

        win_rate = len(winning_trades) / len(df) if len(df) > 0 else 0

        avg_win = winning_trades['pnl'].mean() if len(winning_trades) > 0 else 0
        avg_loss = losing_trades['pnl'].mean() if len(losing_trades) > 0 else 0

        profit_factor = abs(winning_trades['pnl'].sum() / losing_trades['pnl'].sum()) if losing_trades[
                                                                                             'pnl'].sum() != 0 else 0

        return {
            'total_pnl': total_pnl,
            'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades),
            'win_rate': win_rate * 100,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'largest_win': winning_trades['pnl'].max() if len(winning_trades) > 0 else 0,
            'largest_loss': losing_trades['pnl'].min() if len(losing_trades) > 0 else 0,
            'profit_factor': profit_factor,
            'expectancy': (win_rate * avg_win) + ((1 - win_rate) * avg_loss)
        }

    def calculate_risk_metrics(self, df: pd.DataFrame) -> Dict:
        # ###Calculate risk-related metrics###
        daily_returns = df.groupby(df['trade_date'].dt.date)['pnl'].sum()

        if len(daily_returns) > 1:
            sharpe_ratio = self.calculate_sharpe_ratio(daily_returns)
            max_drawdown, max_drawdown_pct = self.calculate_max_drawdown(daily_returns)
            sortino_ratio = self.calculate_sortino_ratio(daily_returns)
        else:
            sharpe_ratio = 0
            max_drawdown = 0
            max_drawdown_pct = 0
            sortino_ratio = 0

        return {
            'volatility': daily_returns.std(),
            'sharpe_ratio': sharpe_ratio,
            'sortino_ratio': sortino_ratio,
            'max_drawdown': max_drawdown,
            'max_drawdown_pct': max_drawdown_pct,
            'daily_var_95': np.percentile(daily_returns, 5),
            'calmar_ratio': abs(daily_returns.mean() / max_drawdown) if max_drawdown != 0 else 0
        }

    def calculate_behavior_metrics(self, df: pd.DataFrame) -> Dict:
        # ###Calculate trading behavior metrics###
        # Holding period analysis
        avg_holding_period = df['holding_period_minutes'].mean()

        # Time of day analysis
        hour_distribution = df['trade_hour'].value_counts().to_dict()
        most_active_hour = df['trade_hour'].mode()[0] if len(df) > 0 else 0

        # Position sizing analysis
        avg_lot_size = df['quantity'].mean()
        max_lot_size = df['quantity'].max()

        # Instrument preference
        top_symbols = df['symbol'].value_counts().head(5).to_dict()

        return {
            'avg_holding_period_minutes': avg_holding_period,
            'most_active_hour': most_active_hour,
            'hour_distribution': hour_distribution,
            'avg_lot_size': avg_lot_size,
            'max_lot_size': max_lot_size,
            'position_size_std': df['quantity'].std(),
            'top_traded_symbols': top_symbols
        }

    def calculate_sharpe_ratio(self, returns: pd.Series) -> float:
        # ###Calculate Sharpe Ratio###
        excess_returns = returns - (self.risk_free_rate / self.trading_days)
        if excess_returns.std() == 0:
            return 0
        return np.sqrt(self.trading_days) * (excess_returns.mean() / excess_returns.std())

    def calculate_sortino_ratio(self, returns: pd.Series) -> float:
        # ###Calculate Sortino Ratio###
        excess_returns = returns - (self.risk_free_rate / self.trading_days)
        downside_returns = returns[returns < 0]

        if len(downside_returns) == 0 or downside_returns.std() == 0:
            return 0

        return np.sqrt(self.trading_days) * (excess_returns.mean() / downside_returns.std())

    def calculate_max_drawdown(self, returns: pd.Series) -> Tuple[float, float]:
        # ###Calculate Maximum Drawdown###
        cumulative = (1 + returns).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max

        max_dd = drawdown.min()
        max_dd_value = (cumulative.min() - running_max.max())

        return max_dd_value, max_dd * 100