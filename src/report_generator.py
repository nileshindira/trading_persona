"""
Report Generator Module
Generates comprehensive HTML and JSON reports
"""

import json
from typing import Dict, List
from datetime import datetime
from jinja2 import Template
import markdown

class ReportGenerator:
    """Generate comprehensive trading reports"""
    
    def __init__(self, config: Dict):
        self.config = config
    
    def generate_report(self, 
                       metrics: Dict, 
                       patterns: Dict, 
                       analysis: Dict,
                       trader_name: str = "Trader") -> Dict:
        """Generate complete report"""
        
        # Convert markdown fields into HTML once here
        analysis_html = {
            key: markdown.markdown(analysis.get(key, ''), extensions=["tables", "fenced_code", "nl2br"])
            for key in ['trader_profile', 'risk_assessment', 'behavioral_insights', 'performance_summary']
        }

        report = {
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'trader_name': trader_name,
                'analysis_period': metrics.get('date_range', 'N/A')
            },
            'executive_summary': self._create_executive_summary(metrics, analysis),
            'detailed_metrics': metrics,
            'detected_patterns': patterns,
            'ai_analysis': analysis_html,   # now HTML safe
            'recommendations': self._format_recommendations(analysis.get('recommendations', '')),
            'risk_score': self._calculate_risk_score(metrics, patterns)
        }

        return report

    def _create_executive_summary(self, metrics: Dict, analysis: Dict) -> Dict:
        """Create executive summary"""
        return {
            'total_trades': metrics.get('total_trades', 0),
            'net_pnl': metrics.get('total_pnl', 0),
            'win_rate': metrics.get('win_rate', 0),
            'sharpe_ratio': metrics.get('sharpe_ratio', 0),
            'risk_level': self._get_risk_level(metrics),
            'trading_style': self._determine_trading_style(metrics, {}),
            'overall_verdict': analysis.get('performance_summary', '')[:200]
        }

    def _get_risk_level(self, metrics: Dict) -> str:
        """Determine risk level"""
        sharpe = metrics.get('sharpe_ratio', 0)
        drawdown = abs(metrics.get('max_drawdown_pct', 0))

        if sharpe < 0 or drawdown > 30:
            return "VERY HIGH"
        elif sharpe < 0.5 or drawdown > 20:
            return "HIGH"
        elif sharpe < 1.0 or drawdown > 10:
            return "MEDIUM"
        else:
            return "LOW"

    def _determine_trading_style(self, metrics: Dict, patterns: Dict) -> str:
        """Determine trading style"""
        avg_trades_per_day = metrics.get('avg_trades_per_day', 0)

        if avg_trades_per_day > 10:
            return "High-Frequency Scalper"
        elif avg_trades_per_day > 5:
            return "Day Trader"
        elif avg_trades_per_day > 2:
            return "Active Trader"
        else:
            return "Position Trader"

    def _format_recommendations(self, recommendations_text: str) -> List[str]:
        """Format recommendations as list"""
        lines = recommendations_text.split('\n')
        recs = [line.strip() for line in lines if line.strip() and (line.strip().startswith('-') or line.strip().startswith('•') or line.strip().startswith('*'))]
        return recs[:10] if recs else ["Focus on risk management", "Reduce trading frequency", "Implement strict stop losses"]

    def _calculate_risk_score(self, metrics: Dict, patterns: Dict) -> int:
        """Calculate risk score 0-100"""
        score = 50  # Base score

        # Adjust based on metrics
        if metrics.get('sharpe_ratio', 0) < 0:
            score += 20
        if abs(metrics.get('max_drawdown_pct', 0)) > 20:
            score += 15
        if metrics.get('win_rate', 50) < 45:
            score += 10

        # Adjust based on patterns
        if patterns.get('overtrading', {}).get('detected', False):
            score += 10
        if patterns.get('revenge_trading', {}).get('detected', False):
            score += 10

        return min(100, max(0, score))

    def export_html(self, report: Dict, filepath: str):
        """Export report as HTML"""
        html_template = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Trading Analysis Report - {{ report.metadata.trader_name }}</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        .container { max-width: 1200px; margin: auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }
        h2 { color: #34495e; margin-top: 30px; }
        .metric { display: inline-block; margin: 10px 20px; padding: 15px; background: #ecf0f1; border-radius: 5px; }
        .metric-label { font-weight: bold; color: #7f8c8d; font-size: 14px; }
        .metric-value { font-size: 24px; color: #2c3e50; font-weight: bold; }
        .risk-very-high { color: #c0392b; }
        .risk-high { color: #e74c3c; }
        .risk-medium { color: #f39c12; }
        .risk-low { color: #27ae60; }
        .pattern-detected { color: #e74c3c; font-weight: bold; }
        .pattern-not-detected { color: #27ae60; }
        .recommendations { background: #ecf0f1; padding: 20px; border-radius: 5px; margin-top: 20px; }
        .recommendations li { margin: 10px 0; }
        .analysis-section { margin: 20px 0; padding: 15px; background: #f8f9fa; border-left: 4px solid #3498db; }
        .analysis-section p { margin: 8px 0; }
        .analysis-section ul { padding-left: 20px; margin: 10px 0; }
        .analysis-section li { margin: 5px 0; }
        .analysis-section strong { color: #2c3e50; }
        .footer { margin-top: 40px; padding-top: 20px; border-top: 1px solid #ddd; text-align: center; color: #7f8c8d; }
        .analysis-section table {width: 100%;border-collapse: collapse;margin: 15px 0;font-size: 14px;}
        .analysis-section table th,
        .analysis-section table td {border: 1px solid #ddd;padding: 8px;text-align: left;}
        .analysis-section table th {background: #f2f2f2;font-weight: bold;}
        .analysis-section ul {list-style: disc inside;margin: 10px 0 10px 20px;padding: 0;}
        .analysis-section li {margin: 6px 0;}
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 Trading Persona Analysis Report</h1>
        
        <div class="metadata">
            <p><strong>Trader:</strong> {{ report.metadata.trader_name }}</p>
            <p><strong>Analysis Period:</strong> {{ report.metadata.analysis_period }}</p>
            <p><strong>Generated:</strong> {{ report.metadata.generated_at }}</p>
        </div>
        
        <h2>🎯 Executive Summary</h2>
        <div class="metrics">
            <div class="metric">
                <div class="metric-label">Total Trades</div>
                <div class="metric-value">{{ report.executive_summary.total_trades }}</div>
            </div>
            <div class="metric">
                <div class="metric-label">Net P&L</div>
                <div class="metric-value">₹{{ "%.2f"|format(report.executive_summary.net_pnl) }}</div>
            </div>
            <div class="metric">
                <div class="metric-label">Win Rate</div>
                <div class="metric-value">{{ "%.1f"|format(report.executive_summary.win_rate) }}%</div>
            </div>
            <div class="metric">
                <div class="metric-label">Risk Level</div>
                <div class="metric-value risk-{{ report.executive_summary.risk_level|lower|replace(' ', '-') }}">
                    {{ report.executive_summary.risk_level }}
                </div>
            </div>
            <div class="metric">
                <div class="metric-label">Risk Score</div>
                <div class="metric-value">{{ report.risk_score }}/100</div>
            </div>
        </div>
        
        <h2>🤖 AI Analysis</h2>
        
        <div class="analysis-section">
            <h3>Trader Profile</h3>
            <div>{{ report.ai_analysis.trader_profile | safe }}</div>
        </div>
        
        <div class="analysis-section">
            <h3>Risk Assessment</h3>
            <div>{{ report.ai_analysis.risk_assessment | safe }}</div>
        </div>
        
        <div class="analysis-section">
            <h3>Behavioral Insights</h3>
            <div>{{ report.ai_analysis.behavioral_insights | safe }}</div>
        </div>
        
        <h2>🔍 Detected Patterns</h2>
        <ul>
            <li>Overtrading: <span class="pattern-{{ 'detected' if report.detected_patterns.overtrading.detected else 'not-detected' }}">
                {{ 'YES' if report.detected_patterns.overtrading.detected else 'NO' }}
            </span></li>
            <li>Revenge Trading: <span class="pattern-{{ 'detected' if report.detected_patterns.revenge_trading.detected else 'not-detected' }}">
                {{ 'YES' if report.detected_patterns.revenge_trading.detected else 'NO' }}
            </span></li>
            <li>Scalping: <span class="pattern-{{ 'detected' if report.detected_patterns.scalping.detected else 'not-detected' }}">
                {{ 'YES' if report.detected_patterns.scalping.detected else 'NO' }}
            </span></li>
        </ul>
        
        <h2>💡 Recommendations</h2>
        <div class="recommendations">
            <ul>
                {% for rec in report.recommendations %}
                <li>{{ rec }}</li>
                {% endfor %}
            </ul>
        </div>
        
        <h2>📈 Performance Summary</h2>
        <div>{{ report.ai_analysis.performance_summary | safe }}</div>
        
        <div class="footer">
            <p>This report was generated using AI-powered analysis. Not financial advice.</p>
            <p>Made with ❤️ by Trade Analysis Dhan</p>
        </div>
    </div>
</body>
</html>
        """
        
        template = Template(html_template)
        html_content = template.render(report=report)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)

    def export_json(self, report: Dict, filepath: str):
        """Export report as JSON"""

        def safe_convert(o):
            if hasattr(o, "item"):  # NumPy scalar
                return o.item()
            if isinstance(o, (set,)):
                return list(o)  # convert sets to lists if needed
            return str(o)  # fallback

        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2, default=safe_convert)
