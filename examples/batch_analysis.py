#!/usr/bin/env python3
"""
Batch Analysis Example
Analyze multiple traders at once
"""

import glob
from pathlib import Path
from main import TradingPersonaAnalyzer
import pandas as pd

# Initialize analyzer
analyzer = TradingPersonaAnalyzer()

# Find all CSV files in raw data directory
csv_files = glob.glob('data/raw/*.csv')

if not csv_files:
    print("No CSV files found in data/raw/")
    print("Please add your trading data files there.")
else:
    print(f"Found {len(csv_files)} files to analyze\n")
    
    # Analyze each file
    results = []
    
    for filepath in csv_files:
        trader_name = Path(filepath).stem
        
        try:
            print(f"Analyzing {trader_name}...")
            report = analyzer.analyze(filepath, trader_name)
            
            # Store summary
            results.append({
                'trader': trader_name,
                'trades': report['executive_summary']['total_trades'],
                'pnl': report['executive_summary']['net_pnl'],
                'win_rate': report['executive_summary']['win_rate'],
                'risk_score': report['risk_score'],
                'risk_level': report['executive_summary']['risk_level']
            })
            
            print(f"✓ {trader_name}: Risk Score {report['risk_score']}/100\n")
            
        except Exception as e:
            print(f"✗ {trader_name}: Error - {e}\n")
    
    # Create summary report
    if results:
        summary_df = pd.DataFrame(results)
        summary_df = summary_df.sort_values('risk_score', ascending=False)
        
        print("\n" + "="*60)
        print("BATCH ANALYSIS SUMMARY")
        print("="*60)
        print(summary_df.to_string(index=False))
        
        # Save summary
        summary_df.to_csv('data/reports/batch_summary.csv', index=False)
        print(f"\n✅ Summary saved to data/reports/batch_summary.csv")
