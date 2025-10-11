#!/usr/bin/env python3
"""
Trading Persona Analyzer - Main Application
Analyze trading patterns and generate comprehensive insights using local LLMs
"""

import yaml
import logging
import argparse
from pathlib import Path
import sys
import os
from src.data_processor import TradingDataProcessor
from src.metrics_calculator import TradingMetricsCalculator
from src.pattern_detector import TradingPatternDetector
from src.llm_analyzer import OllamaAnalyzer
from src.report_generator import ReportGenerator
from src.ema_calculator import EMACalculator

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TradingPersonaAnalyzer:
    """Main application class for trading analysis"""

    def __init__(self, config_path: str = "config.yaml"):
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)

        self.data_processor = TradingDataProcessor(self.config)
        self.metrics_calculator = TradingMetricsCalculator(self.config)
        self.pattern_detector = TradingPatternDetector(self.config)
        self.llm_analyzer = OllamaAnalyzer(self.config)
        self.report_generator = ReportGenerator(self.config)

        # Initialize EMA calculator
        try:
            self.ema_calculator = EMACalculator(self.config)
            self.ema_enabled = True
            logger.info("EMA calculator initialized successfully")
        except Exception as e:
            logger.warning(f"EMA calculator initialization failed: {str(e)}. EMA scores will be skipped.")
            self.ema_enabled = False

    def analyze(self, data_filepath: str, trader_name: str = "Trader",
                output_dir: str = "data/reports", include_ema: bool = True):
        """Run complete analysis pipeline"""

        logger.info(f"Starting analysis for {trader_name}")

        # Step 1: Load and process data
        logger.info("Loading data...")
        df = self.data_processor.load_data(data_filepath)

        # Validate data
        is_valid, missing_cols = self.data_processor.validate_data(df)
        if not is_valid:
            logger.error(f"Missing required columns: {missing_cols}")
            return None

        # Clean data
        logger.info("Cleaning data...")
        df = self.data_processor.clean_data(df)

        # Pair trades for P&L
        logger.info("Pairing trades...")
        raw_df = df.copy()  # Keep original for pattern detection
        df = self.data_processor.pair_trades(df, data_filepath)

        # Step 1.5: Add EMA scores (NEW FEATURE)
        ema_stats = None
        if include_ema and self.ema_enabled:
            try:
                logger.info("Calculating EMA allocation scores...")
                df = self.ema_calculator.add_ema_scores_to_trades(df)
                ema_stats = self.ema_calculator.get_ema_summary_stats(df)
                logger.info("EMA scores calculated successfully")
            except Exception as e:
                logger.error(f"Error calculating EMA scores: {str(e)}")
                logger.warning("Continuing analysis without EMA scores")

        # Step 2: Calculate metrics
        logger.info("Calculating metrics...")
        metrics = self.metrics_calculator.calculate_all_metrics(df)

        # Add EMA stats to metrics if available
        if ema_stats:
            metrics['ema_allocation'] = ema_stats

        # Step 3: Detect patterns (use raw data)
        logger.info("Detecting patterns...")
        patterns = self.pattern_detector.detect_all_patterns(df)

        # Step 4: LLM Analysis
        logger.info("Generating AI analysis...")
        analysis = self.llm_analyzer.generate_analysis(metrics, patterns)

        # Step 5: Generate report
        logger.info("Generating report...")
        report = self.report_generator.generate_report(
            metrics, patterns, analysis, trader_name
        )

        # Step 6: Export report
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # Export as JSON
        json_path = output_path / f"{trader_name}_report.json"
        self.report_generator.export_json(report, str(json_path))
        logger.info(f"JSON report saved to {json_path}")

        # Export as HTML
        html_path = output_path / f"{trader_name}_report.html"
        self.report_generator.export_html(report, str(html_path))
        logger.info(f"HTML report saved to {html_path}")

        # Export enriched CSV with EMA scores
        if include_ema and self.ema_enabled:
            csv_path = output_path / f"{trader_name}_trades_with_ema.csv"
            df.to_csv(csv_path, index=False)
            logger.info(f"Enriched trades CSV saved to {csv_path}")

        logger.info("Analysis complete!")

        return report


def main():
    parser = argparse.ArgumentParser(description='Trading Persona Analyzer')
    parser.add_argument('--config', default='config.yaml', help='Path to config file')
    parser.add_argument('--data-dir', default='data', help='Directory containing trade CSV files')
    parser.add_argument('--output-dir', default='data/reports', help='Output directory for reports')
    parser.add_argument('--no-ema', action='store_true', help='Skip EMA score calculation')
    parser.add_argument('--single', help='Run analysis for a single file (optional)')
    args = parser.parse_args()

    analyzer = TradingPersonaAnalyzer(args.config)

    # ------------------------------------------------------
    # CASE 1: Single-file mode (explicitly provided)
    # ------------------------------------------------------
    if args.single:
        data_file = args.single
        trader_name = Path(data_file).stem.replace('trade_', '')
        analyzer.analyze(
            data_filepath=data_file,
            trader_name=trader_name,
            output_dir=args.output_dir,
            include_ema=not args.no_ema
        )
        return

    # ------------------------------------------------------
    # CASE 2: Auto-run for all trade_*.csv files
    # ------------------------------------------------------
    data_path = Path(args.data_dir)
    trade_files = sorted(data_path.glob("trade_*.csv"))

    if not trade_files:
        logger.error(f"No trade_*.csv files found in {data_path}")
        sys.exit(1)

    logger.info(f"Found {len(trade_files)} trade files to process.")
    for file_path in trade_files:
        trader_name = file_path.stem.replace("trade_", "")
        logger.info(f"\n{'='*80}\nStarting analysis for {trader_name}\n{'='*80}")
        try:
            analyzer.analyze(
                data_filepath=str(file_path),
                trader_name=trader_name,
                output_dir=args.output_dir,
                include_ema=not args.no_ema
            )
        except Exception as e:
            logger.error(f"❌ Failed to analyze {trader_name}: {e}")
            continue

    logger.info("✅ All analyses completed.")



if __name__ == "__main__":
    main()
