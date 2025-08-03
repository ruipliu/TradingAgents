import os
import sys
import asyncio
from datetime import datetime
from typing import Tuple, Dict, Any
from pathlib import Path

# Add the parent directory to the path to import tradingagents
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG
from server.config import get_trading_config, DEFAULT_ANALYSTS


class TradingService:
    """Service wrapper for trading agents analysis."""
    
    def __init__(self):
        """Initialize the trading service."""
        self.config = self._create_config()
        self.graph = None
        
    def _create_config(self) -> Dict[str, Any]:
        """Create configuration for trading agents."""
        config = DEFAULT_CONFIG.copy()
        trading_config = get_trading_config()
        config.update(trading_config)
        return config
    
    def _initialize_graph(self):
        """Initialize the trading graph if not already done."""
        if self.graph is None:
            self.graph = TradingAgentsGraph(
                selected_analysts=DEFAULT_ANALYSTS,
                debug=False,  # Disable debug for server
                config=self.config
            )
    
    async def analyze_stock(self, symbol: str, trade_date: str = None) -> Tuple[str, Dict[str, Any]]:
        """
        Analyze a stock symbol and return trading decision.
        
        Args:
            symbol: Stock ticker symbol (e.g., 'AAPL')
            trade_date: Date for analysis (defaults to today)
            
        Returns:
            Tuple of (trading_decision, full_analysis_state)
        """
        if trade_date is None:
            trade_date = datetime.now().strftime("%Y-%m-%d")
        
        # Initialize graph if needed
        self._initialize_graph()
        
        # Run analysis in executor to avoid blocking
        loop = asyncio.get_event_loop()
        final_state, decision = await loop.run_in_executor(
            None, 
            self.graph.propagate, 
            symbol.upper(), 
            trade_date
        )
        
        return decision, final_state
    
    def format_decision_for_telegram(self, decision: str, symbol: str, trade_date: str) -> str:
        """
        Format the trading decision for Telegram message.
        
        Args:
            decision: Raw trading decision from agents
            symbol: Stock symbol
            trade_date: Analysis date
            
        Returns:
            Formatted message for Telegram
        """
        header = f"📊 *Trading Analysis for {symbol}*\n"
        header += f"📅 Date: {trade_date}\n"
        header += f"🤖 Analyzed by: All Agents (Market, Social, News, Fundamentals)\n\n"
        
        # Format the decision
        decision_section = f"💡 *Trading Decision:*\n{decision}\n\n"
        
        footer = "⚠️ *Disclaimer:* This is AI-generated analysis for educational purposes only. Not financial advice."
        
        message = header + decision_section + footer
        
        # Ensure message doesn't exceed Telegram limits
        if len(message) > 4000:  # Leave some buffer
            # Truncate decision if too long
            max_decision_length = 4000 - len(header) - len(footer) - 50
            truncated_decision = decision[:max_decision_length] + "..."
            decision_section = f"💡 *Trading Decision:*\n{truncated_decision}\n\n"
            message = header + decision_section + footer
        
        return message
    
    def get_results_path(self, symbol: str, trade_date: str) -> Path:
        """Get the path where results are stored."""
        return Path(self.config["results_dir"]) / symbol / trade_date
    
    def validate_symbol(self, symbol: str) -> bool:
        """
        Basic validation for stock symbol.
        
        Args:
            symbol: Stock ticker symbol
            
        Returns:
            True if symbol appears valid
        """
        if not symbol:
            return False
        
        # Basic checks
        symbol = symbol.upper().strip()
        if len(symbol) < 1 or len(symbol) > 10:
            return False
        
        # Should contain only letters and possibly dots/dashes
        if not all(c.isalpha() or c in '.-' for c in symbol):
            return False
        
        return True


# Global service instance
trading_service = TradingService()
