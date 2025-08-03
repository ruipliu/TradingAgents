import os
from typing import Dict, Any

# Server configuration
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "")  # For production webhook setup
PORT = int(os.getenv("PORT", 8000))
HOST = os.getenv("HOST", "0.0.0.0")

# Google API configuration
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Trading agent configuration
def get_trading_config() -> Dict[str, Any]:
    """Get configuration for trading agents with Google Gemini models."""
    return {
        "llm_provider": "google",
        "backend_url": "https://generativelanguage.googleapis.com/v1",
        "deep_think_llm": "gemini-2.5-pro",  # Pro model for reasoning
        "quick_think_llm": "gemini-2.5-flash",  # Flash model for quick tasks
        "max_debate_rounds": 1,
        "max_risk_discuss_rounds": 1,
        "online_tools": True,
        "results_dir": "./results",  # Same as CLI
    }

# Default analysts to use (all available)
DEFAULT_ANALYSTS = ["market", "social", "news", "fundamentals"]

# Validation
def validate_config():
    """Validate required environment variables."""
    if not TELEGRAM_BOT_TOKEN:
        raise ValueError("TELEGRAM_BOT_TOKEN environment variable is required")
    if not GOOGLE_API_KEY:
        raise ValueError("GOOGLE_API_KEY environment variable is required")

# Bot settings
MAX_MESSAGE_LENGTH = 4096  # Telegram message limit
ANALYSIS_TIMEOUT = 300  # 5 minutes timeout for analysis
