#!/usr/bin/env python3
"""
Dhan Data Extraction Example
Shows how to extract trading data from Dhan API
"""

from extractors.dhan import DhanExtractor
import os

# Your Dhan credentials
ACCESS_TOKEN = os.getenv('DHAN_ACCESS_TOKEN', 'YOUR_ACCESS_TOKEN_HERE')

# Initialize extractor
extractor = DhanExtractor(access_token=ACCESS_TOKEN)

# Extract trades
print("Extracting trades from Dhan...")
trades = extractor.extract_trades(
    from_date="2025-04-01",
    to_date="2025-09-21",
    output_file="data/raw/dhan_trades.csv"
)

print(f"\n✅ Extracted {len(trades)} trades")
print(f"\nFirst 5 trades:")
print(trades.head())

print(f"\nTrade summary:")
print(f"Total trade value: ₹{trades['trade_value'].sum():,.2f}")
print(f"Unique symbols: {trades['symbol'].nunique()}")
print(f"Date range: {trades['trade_date'].min()} to {trades['trade_date'].max()}")
