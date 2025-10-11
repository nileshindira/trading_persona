"""
EMA Allocation Calculator Module (PostgreSQL Caching)
Calculates EMA-based allocation scores for stocks and indices using TradingView data.
Caches results in PostgreSQL to avoid redundant network calls.
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional, Tuple
from datetime import datetime
import logging
import psycopg2
from psycopg2.extras import RealDictCursor

try:
    from tvDatafeed import TvDatafeed, Interval
except ImportError:
    raise ImportError("Please install tvDatafeed: pip install tvDatafeed")


class EMACalculator:
    """Calculate and cache EMA allocation scores using PostgreSQL"""

    def __init__(self, config: Dict):
        self.config = config
        self.logger = logging.getLogger(__name__)

        # Initialize TradingView connection
        try:
            self.tv = TvDatafeed()
            self.logger.info("TradingView datafeed initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize TradingView datafeed: {str(e)}")
            raise

        # PostgreSQL setup
        pg_cfg = config.get("postgres", {})
        try:
            self.conn = psycopg2.connect(
                host=pg_cfg["host"],
                database=pg_cfg["database"],
                user=pg_cfg["user"],
                password=pg_cfg["password"],
                port=pg_cfg.get("port", 5432)
            )
            self.conn.autocommit = True
            self.logger.info("Connected to PostgreSQL successfully")
        except Exception as e:
            self.logger.error(f"Failed to connect to PostgreSQL: {str(e)}")
            raise

        self._ensure_table_exists()

    # ----------------------------------------------------------------------
    def _ensure_table_exists(self):
        """Ensure ema_values table exists with unique constraint."""
        query = """
        CREATE TABLE IF NOT EXISTS ema_values (
            id SERIAL PRIMARY KEY,
            symbol TEXT NOT NULL,
            exchange TEXT DEFAULT 'NSE' NOT NULL,
            date DATE NOT NULL,
            close DOUBLE PRECISION,
            ema21 DOUBLE PRECISION,
            ema50 DOUBLE PRECISION,
            ema100 DOUBLE PRECISION,
            score INT,
            last_updated TIMESTAMP DEFAULT NOW(),
            UNIQUE(symbol, exchange, date)
        );
        """
        with self.conn.cursor() as cur:
            cur.execute(query)
        self.logger.info("Ensured ema_values table exists in PostgreSQL with unique constraint")

    # ----------------------------------------------------------------------
    def calculate_ema(self, prices: pd.Series, period: int) -> pd.Series:
        """Compute Exponential Moving Average"""
        return prices.ewm(span=period, adjust=False).mean()

    def calculate_ema_score(self, close: float, ema21: float, ema50: float, ema100: float) -> int:
        """Compute EMA strength score between -6 and +6"""
        score = 0
        score += 1 if close > ema21 else -1
        score += 1 if close > ema50 else -1
        score += 1 if close > ema100 else -1
        score += 1 if ema21 > ema50 else -1
        score += 1 if ema21 > ema100 else -1
        score += 1 if ema50 > ema100 else -1
        return score

    # ----------------------------------------------------------------------
    def fetch_from_db(self, symbol: str, exchange: str, date: datetime) -> Optional[Dict]:
        """Fetch cached EMA record from PostgreSQL."""
        date_str = date.strftime("%Y-%m-%d")
        query = """
            SELECT * FROM ema_values
            WHERE symbol = %s AND exchange = %s AND date = %s
        """
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query, (symbol, exchange, date_str))
            return cur.fetchone()

    def save_to_db(self, symbol: str, exchange: str, date: datetime, data: Dict):
        """Insert or update EMA record."""
        def to_native(v):
            if isinstance(v, np.generic):
                return v.item()
            return v

        query = """
            INSERT INTO ema_values (symbol, exchange, date, close, ema21, ema50, ema100, score, last_updated)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,NOW())
            ON CONFLICT (symbol, exchange, date)
            DO UPDATE SET
                close = EXCLUDED.close,
                ema21 = EXCLUDED.ema21,
                ema50 = EXCLUDED.ema50,
                ema100 = EXCLUDED.ema100,
                score = EXCLUDED.score,
                last_updated = NOW();
        """
        try:
            with self.conn.cursor() as cur:
                cur.execute(query, (
                    symbol,
                    exchange,
                    date.strftime("%Y-%m-%d"),
                    to_native(data.get("close")),
                    to_native(data.get("ema21")),
                    to_native(data.get("ema50")),
                    to_native(data.get("ema100")),
                    int(to_native(data.get("score") or 0))
                ))
            self.logger.debug(f"Saved EMA for {symbol} ({date.date()})")
        except Exception as e:
            self.logger.error(f"DB insert failed for {symbol} ({date.date()}): {str(e)}")

    # ----------------------------------------------------------------------
    def get_historical_data(self, symbol: str, exchange: str = 'NSE', n_bars: int = 200,
                            interval: Interval = Interval.in_daily) -> Optional[pd.DataFrame]:
        """Fetch OHLC data from TradingView."""
        try:
            df = self.tv.get_hist(symbol=symbol, exchange=exchange, interval=interval, n_bars=n_bars)
            if df is None or df.empty:
                self.logger.warning(f"No data received for {symbol}")
                return None
            return df
        except Exception as e:
            self.logger.error(f"Error fetching data for {symbol}: {str(e)}")
            return None

    # ----------------------------------------------------------------------
    def calculate_emas_for_symbol(self, symbol: str, exchange: str = 'NSE',
                                  target_date: Optional[datetime] = None) -> Tuple[Optional[int], Dict]:
        """Calculate EMA score and store in DB (with caching)."""
        if not target_date:
            target_date = datetime.today()

        # Step 1: Try cache
        cached = self.fetch_from_db(symbol, exchange, target_date)
        if cached:
            self.logger.info(f"Loaded cached EMA for {symbol} ({target_date.date()})")
            return cached["score"], cached

        # Step 2: Fetch fresh data
        df = self.get_historical_data(symbol, exchange)
        if df is None or len(df) < 100:
            self.logger.warning(f"Insufficient data for {symbol}")
            return None, {}

        # Step 3: Calculate EMAs
        df["EMA21"] = self.calculate_ema(df["close"], 21)
        df["EMA50"] = self.calculate_ema(df["close"], 50)
        df["EMA100"] = self.calculate_ema(df["close"], 100)

        df = df[df.index < target_date]
        if df.empty:
            self.logger.warning(f"No valid data before {target_date.date()} for {symbol}")
            return None, {}

        latest = df.iloc[-1]
        score = self.calculate_ema_score(latest["close"], latest["EMA21"], latest["EMA50"], latest["EMA100"])

        ema_data = {
            "close": float(latest["close"]),
            "ema21": float(latest["EMA21"]),
            "ema50": float(latest["EMA50"]),
            "ema100": float(latest["EMA100"]),
            "score": int(score)
        }

        # Step 4: Cache in DB
        self.save_to_db(symbol, exchange, target_date, ema_data)
        self.logger.info(f"✅ Cached EMA for {symbol} ({target_date.date()}): {score}/6")
        return score, ema_data

    # ----------------------------------------------------------------------
    def extract_base_symbol(self, trading_symbol: str) -> str:
        """Clean and normalize symbol name."""
        try:
            trading_symbol = str(trading_symbol).strip()
            if trading_symbol.isdigit():
                return trading_symbol
            return trading_symbol.split()[0].upper().replace("&", "").replace("-", "")
        except Exception:
            return str(trading_symbol)

    # ----------------------------------------------------------------------
    def add_ema_scores_to_trades(self, df: pd.DataFrame) -> pd.DataFrame:
        """Attach EMA scores to each trade using DB caching."""
        df = df.copy()
        df["ema_score_stock"] = None
        df["ema_score_nifty"] = None
        df["ema_score_midcap"] = None

        score_cache = {}
        unique_symbols = df["symbol"].unique()
        self.logger.info(f"Calculating EMA scores for {len(unique_symbols)} symbols...")

        for idx, row in df.iterrows():
            trade_date = row["trade_date"]
            symbol = self.extract_base_symbol(row["symbol"])

            for cache_key, name in [
                (f"{symbol}_{trade_date.date()}", symbol),
                (f"NIFTY_{trade_date.date()}", "NIFTY"),
                (f"NIFTYMIDCAP150_{trade_date.date()}", "NIFTYMIDCAP150")
            ]:
                if cache_key not in score_cache:
                    try:
                        score, _ = self.calculate_emas_for_symbol(name, "NSE", trade_date)
                        score_cache[cache_key] = score
                    except Exception as e:
                        self.logger.warning(f"EMA calc failed for {name}: {e}")
                        score_cache[cache_key] = None

            df.at[idx, "ema_score_stock"] = score_cache[f"{symbol}_{trade_date.date()}"]
            df.at[idx, "ema_score_nifty"] = score_cache[f"NIFTY_{trade_date.date()}"]
            df.at[idx, "ema_score_midcap"] = score_cache[f"NIFTYMIDCAP150_{trade_date.date()}"]

        self.logger.info("✅ EMA scores added to all trades")
        return df

    # ----------------------------------------------------------------------
    def get_ema_summary_stats(self, df: pd.DataFrame) -> Dict:
        """Summarize EMA scores."""
        def safe_stats(series):
            return series.describe().to_dict() if series.notna().any() else {}

        return {
            "stock_ema": safe_stats(df["ema_score_stock"]),
            "nifty_ema": safe_stats(df["ema_score_nifty"]),
            "midcap_ema": safe_stats(df["ema_score_midcap"])
        }
