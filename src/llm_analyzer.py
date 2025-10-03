"""
LLM Analyzer Module
Integrates with Ollama for AI-powered analysis
"""

import requests
import json
from typing import Dict, List
import logging

class OllamaAnalyzer:
    """LLM-based analysis using Ollama"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.base_url = config['ollama']['base_url']
        self.model = config['ollama']['model']
        self.logger = logging.getLogger(__name__)
    
    def generate_analysis(self, metrics: Dict, patterns: Dict) -> Dict:
        """Generate comprehensive analysis using LLM"""
        
        # Prepare context
        context = self._prepare_context(metrics, patterns)
        
        # Generate different sections
        analysis = {
            'trader_profile': self._analyze_trader_profile(context),
            'risk_assessment': self._analyze_risk(context),
            'behavioral_insights': self._analyze_behavior(context),
            'recommendations': self._generate_recommendations(context),
            'performance_summary': self._summarize_performance(context)
        }
        
        return analysis

    def _prepare_context(self, metrics: Dict, patterns: Dict) -> str:
        """Prepare context for LLM"""

        def safe_convert(o):
            # Handle numpy / pandas dtypes
            if hasattr(o, "item"):  # numpy scalar
                return o.item()
            return str(o)  # fallback to string

        context = f"""
    TRADING METRICS:
    - Total Trades: {int(metrics.get('total_trades', 0))}
    - Total P&L: ₹{float(metrics.get('total_pnl', 0)):,.2f}
    - Win Rate: {float(metrics.get('win_rate', 0)):.2f}%
    - Sharpe Ratio: {float(metrics.get('sharpe_ratio', 0)):.2f}
    - Max Drawdown: {float(metrics.get('max_drawdown_pct', 0)):.2f}%
    - Average Trade Value: ₹{float(metrics.get('avg_trade_value', 0)):,.2f}

    DETECTED PATTERNS:
    - Overtrading: {patterns.get('overtrading', {}).get('detected', False)}
    - Revenge Trading: {patterns.get('revenge_trading', {}).get('detected', False)}
    - Scalping: {patterns.get('scalping', {}).get('detected', False)}
    - Hedging: {patterns.get('hedging', {}).get('detected', False)}

    Additional Context:
    {json.dumps(metrics, indent=2, default=safe_convert)}
    {json.dumps(patterns, indent=2, default=safe_convert)}
    """
        return context
    
    def _call_ollama(self, prompt: str, system_prompt: str = "") -> str:
        """Call Ollama API"""
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "system": system_prompt,
                    "stream": False,
                    "options": {
                        "temperature": self.config['ollama']['temperature'],
                        "top_p": self.config['ollama']['top_p']
                    }
                },
                timeout=120
            )
            
            if response.status_code == 200:
                return response.json()['response']
            else:
                self.logger.error(f"Ollama API error: {response.text}")
                return "Error generating analysis"
                
        except Exception as e:
            self.logger.error(f"Error calling Ollama: {str(e)}")
            return "Error generating analysis - Ollama may not be running"
    
    def _analyze_trader_profile(self, context: str) -> str:
        """Analyze trader profile"""
        prompt = f"""
Based on the following trading data, provide a detailed trader profile classification.
Include:
1. Trader type (scalper, day trader, swing trader, etc.)
2. Risk appetite (conservative, moderate, aggressive)
3. Trading style characteristics

{context}

Provide a concise but comprehensive trader profile (200-300 words):
"""
        
        system_prompt = "You are an expert financial analyst specializing in trading behavior analysis."
        
        return self._call_ollama(prompt, system_prompt)
    
    def _analyze_risk(self, context: str) -> str:
        """Analyze risk profile"""
        prompt = f"""
Based on the following trading metrics, provide a risk assessment.

{context}

Analyze:
1. Overall risk level (LOW/MEDIUM/HIGH/VERY HIGH)
2. Key risk factors
3. Risk-adjusted performance
4. Potential vulnerabilities

Provide detailed risk analysis (200-300 words):
"""
        
        system_prompt = "You are a risk management expert analyzing trading portfolios."
        
        return self._call_ollama(prompt, system_prompt)
    
    def _analyze_behavior(self, context: str) -> str:
        """Analyze behavioral patterns"""
        prompt = f"""
Based on the detected patterns, provide behavioral insights.

{context}

Focus on:
1. Psychological tendencies
2. Emotional trading signs
3. Discipline issues
4. Positive behaviors

Provide behavioral analysis (200-300 words):
"""
        
        system_prompt = "You are a trading psychology expert analyzing trader behavior."
        
        return self._call_ollama(prompt, system_prompt)
    
    def _generate_recommendations(self, context: str) -> str:
        """Generate actionable recommendations"""
        prompt = f"""
Based on the trading analysis, provide specific, actionable recommendations.

{context}

Provide:
1. Immediate actions (next 1-2 weeks)
2. Short-term improvements (1-3 months)
3. Long-term strategy changes
4. Specific metrics to target

Format as bullet points with clear action items:
"""
        
        system_prompt = "You are a professional trading coach providing improvement strategies."
        
        return self._call_ollama(prompt, system_prompt)
    
    def _summarize_performance(self, context: str) -> str:
        """Summarize overall performance"""
        prompt = f"""
Provide an executive summary of the trading performance.

{context}

Include:
1. Overall verdict (Excellent/Good/Average/Poor/Critical)
2. Key strengths
3. Major weaknesses
4. Bottom-line assessment

Be direct and honest in assessment (150-200 words):
"""
        
        system_prompt = "You are a senior financial advisor providing performance reviews."
        
        return self._call_ollama(prompt, system_prompt)
