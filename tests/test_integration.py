"""
Integration Test for Trading Analysis System
Tests all components to ensure they work together correctly
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.data_processor import TradingDataProcessor
from src.metrics_calculator import TradingMetricsCalculator
from src.pattern_detector import TradingPatternDetector

def create_sample_data():
    """Create sample trading data for testing"""
    
    base_date = datetime(2025, 9, 1, 9, 15)
    trades = []
    
    # Create 50 sample trades
    for i in range(50):
        trade_date = base_date + timedelta(days=i//5, hours=i%5, minutes=i*3)
        
        # Alternate between BUY and SELL
        transaction_type = 'BUY' if i % 2 == 0 else 'SELL'
        
        # Random symbols
        symbols = ['NIFTY 25200 CALL', 'NIFTY 25200 PUT', 'BANKNIFTY 54300 CALL']
        symbol = symbols[i % 3]
        
        # Random price and quantity
        price = 40 + (i % 20) + np.random.uniform(-5, 5)
        quantity = 75 + (i % 25)
        
        trades.append({
            'trade_date': trade_date,
            'symbol': symbol,
            'transaction_type': transaction_type,
            'quantity': quantity,
            'price': price
        })
    
    return pd.DataFrame(trades)

def test_data_processor():
    """Test data processor module"""
    print("Testing Data Processor...")
    
    config = {
        'data': {
            'required_columns': ['trade_date', 'symbol', 'transaction_type', 'quantity', 'price']
        }
    }
    
    processor = TradingDataProcessor(config)
    df = create_sample_data()
    
    # Test validation
    is_valid, missing_cols = processor.validate_data(df)
    assert is_valid, f"Validation failed: {missing_cols}"
    print("  ✓ Data validation passed")
    
    # Test cleaning
    df_clean = processor.clean_data(df)
    assert 'trade_hour' in df_clean.columns
    assert 'trade_day_of_week' in df_clean.columns
    assert 'trade_value' in df_clean.columns
    print("  ✓ Data cleaning passed")
    
    # Test pairing
    df_paired = processor.pair_trades(df_clean)
    assert 'pnl' in df_paired.columns
    assert 'holding_period_minutes' in df_paired.columns
    print("  ✓ Trade pairing passed")
    
    return df_paired

def test_metrics_calculator(df):
    """Test metrics calculator module"""
    print("\nTesting Metrics Calculator...")
    
    config = {
        'metrics': {
            'risk_free_rate': 0.065,
            'trading_days_per_year': 252
        }
    }
    
    calculator = TradingMetricsCalculator(config)
    metrics = calculator.calculate_all_metrics(df)
    
    # Check essential metrics
    assert 'total_trades' in metrics
    assert 'total_pnl' in metrics
    assert 'win_rate' in metrics
    assert 'sharpe_ratio' in metrics
    assert 'max_drawdown' in metrics
    print("  ✓ All metrics calculated")
    
    # Print some metrics
    print(f"  → Total Trades: {metrics['total_trades']}")
    print(f"  → Total P&L: ₹{metrics['total_pnl']:.2f}")
    print(f"  → Win Rate: {metrics['win_rate']:.2f}%")
    print(f"  → Sharpe Ratio: {metrics['sharpe_ratio']:.2f}")
    
    return metrics

def test_pattern_detector(df):
    """Test pattern detector module"""
    print("\nTesting Pattern Detector...")
    
    config = {
        'analysis': {
            'min_trades_for_pattern': 5
        }
    }
    
    detector = TradingPatternDetector(config)
    patterns = detector.detect_all_patterns(df)
    
    # Check essential patterns
    assert 'overtrading' in patterns
    assert 'revenge_trading' in patterns
    assert 'scalping' in patterns
    assert 'hedging' in patterns
    print("  ✓ All patterns detected")
    
    # Print some patterns
    print(f"  → Overtrading: {patterns['overtrading']['detected']}")
    print(f"  → Revenge Trading: {patterns['revenge_trading']['detected']}")
    print(f"  → Scalping: {patterns['scalping']['detected']}")
    
    return patterns

def test_report_structure(metrics, patterns):
    """Test report generation structure"""
    print("\nTesting Report Structure...")
    
    from src.report_generator import ReportGenerator
    
    config = {
        'report': {
            'output_format': ['html', 'json'],
            'include_charts': True,
            'chart_style': 'seaborn'
        }
    }
    
    generator = ReportGenerator(config)
    
    # Mock analysis for testing
    analysis = {
        'trader_profile': 'Test trader profile',
        'risk_assessment': 'Test risk assessment',
        'behavioral_insights': 'Test behavioral insights',
        'recommendations': '- Test recommendation 1\n- Test recommendation 2',
        'performance_summary': 'Test performance summary'
    }
    
    report = generator.generate_report(metrics, patterns, analysis, 'Test Trader')
    
    # Check report structure
    assert 'metadata' in report
    assert 'executive_summary' in report
    assert 'detailed_metrics' in report
    assert 'detected_patterns' in report
    assert 'ai_analysis' in report
    assert 'risk_score' in report
    print("  ✓ Report structure valid")
    
    print(f"  → Risk Score: {report['risk_score']}/100")
    print(f"  → Risk Level: {report['executive_summary']['risk_level']}")
    
    return report

def main():
    """Run all tests"""
    print("="*60)
    print("TRADING ANALYSIS SYSTEM - INTEGRATION TEST")
    print("="*60)
    
    try:
        # Test 1: Data Processor
        df = test_data_processor()
        
        # Test 2: Metrics Calculator
        metrics = test_metrics_calculator(df)
        
        # Test 3: Pattern Detector
        patterns = test_pattern_detector(df)
        
        # Test 4: Report Structure
        report = test_report_structure(metrics, patterns)
        
        print("\n" + "="*60)
        print("✅ ALL TESTS PASSED SUCCESSFULLY!")
        print("="*60)
        print("\nThe trading analysis system is ready to use.")
        print("You can now run: python main.py <your_data_file.csv>")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
