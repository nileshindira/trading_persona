#!/usr/bin/env python3
"""
Custom Pattern Detection Example
Shows how to add your own trading patterns
"""

import pandas as pd
from src.pattern_detector import TradingPatternDetector
import yaml

# Load config
with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

class CustomPatternDetector(TradingPatternDetector):
    """Extended pattern detector with custom patterns"""
    
    def detect_fomo_trading(self, df: pd.DataFrame) -> dict:
        """Detect FOMO (Fear of Missing Out) trading"""
        fomo_trades = 0
        
        for idx, trade in df.iterrows():
            # Get previous trades for context
            if idx < 10:
                continue
                
            recent = df.iloc[max(0, idx-10):idx]
            
            if len(recent) > 0:
                recent_high = recent['price'].max()
                recent_low = recent['price'].min()
                
                # Check if buying at high or panic selling at low
                if (trade['transaction_type'] == 'BUY' and 
                    trade['price'] >= recent_high * 0.95):
                    fomo_trades += 1
                elif (trade['transaction_type'] == 'SELL' and 
                      trade['price'] <= recent_low * 1.05):
                    fomo_trades += 1
        
        return {
            'detected': fomo_trades > 5,
            'count': int(fomo_trades),
            'percentage': float(fomo_trades / len(df) * 100) if len(df) > 0 else 0
        }
    
    def detect_martingale(self, df: pd.DataFrame) -> dict:
        """Detect martingale (doubling after loss) pattern"""
        martingale_count = 0
        
        for i in range(1, len(df)):
            prev_trade = df.iloc[i-1]
            curr_trade = df.iloc[i]
            
            if (prev_trade['pnl'] < 0 and 
                curr_trade['quantity'] >= prev_trade['quantity'] * 1.8):
                martingale_count += 1
        
        return {
            'detected': martingale_count > 3,
            'count': int(martingale_count),
            'severity': 'CRITICAL' if martingale_count > 5 else 'HIGH'
        }

# Load and process sample data
from src.data_processor import TradingDataProcessor

processor = TradingDataProcessor(config)
df = processor.load_data('data/sample_trades.csv')
df = processor.clean_data(df)
df = processor.pair_trades(df)

# Use custom detector
detector = CustomPatternDetector(config)

print("Detecting custom patterns...\n")

# Detect FOMO trading
fomo = detector.detect_fomo_trading(df)
print(f"FOMO Trading:")
print(f"  Detected: {fomo['detected']}")
print(f"  Count: {fomo['count']}")
print(f"  Percentage: {fomo['percentage']:.1f}%\n")

# Detect martingale
martingale = detector.detect_martingale(df)
print(f"Martingale Pattern:")
print(f"  Detected: {martingale['detected']}")
print(f"  Count: {martingale['count']}")
print(f"  Severity: {martingale.get('severity', 'N/A')}")

print("\n✅ Custom pattern detection complete!")
