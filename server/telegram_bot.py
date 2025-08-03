import logging
import asyncio
from datetime import datetime
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.constants import ParseMode

from server.config import TELEGRAM_BOT_TOKEN, ANALYSIS_TIMEOUT
from server.trading_service import trading_service

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


class TradingBot:
    """Telegram bot for trading analysis."""

    def __init__(self):
        """Initialize the bot."""
        self.application = None
        self.bot = None
        self.polling_task = None
        self._is_running = False
        
    async def initialize(self):
        """Initialize the bot application."""
        self.application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
        self.bot = self.application.bot
        
        # Add handlers
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        
        # Add error handler
        self.application.add_error_handler(self.error_handler)
        
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command."""
        welcome_message = (
            "🤖 *Welcome to TradingAgents Bot!*\n\n"
            "I can analyze stocks using AI agents and provide trading insights.\n\n"
            "*How to use:*\n"
            "• Send a stock symbol to analyze (e.g., `AAPL`, `TSLA`, `NVDA`)\n\n"
            "*Features:*\n"
            "• Market analysis\n"
            "• Social sentiment analysis\n"
            "• News analysis\n"
            "• Fundamentals analysis\n"
            "• AI-powered trading recommendations\n\n"
            "⚠️ *Disclaimer:* This is for educational purposes only. Not financial advice."
        )
        
        await update.message.reply_text(
            welcome_message,
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command."""
        help_message = (
            "📖 *TradingAgents Bot Help*\n\n"
            "*Commands:*\n"
            "• `/start` - Show welcome message\n"
            "• `/help` - Show this help\n\n"
            "*How to analyze stocks:*\n"
            "• Send a stock symbol as a message (e.g., `AAPL`, `TSLA`, `NVDA`)\n\n"
            "*Examples:*\n"
            "• `AAPL` - Analyze Apple Inc.\n"
            "• `TSLA` - Analyze Tesla Inc.\n"
            "• `NVDA` - Analyze NVIDIA Corp.\n"
            "• `MSFT` - Analyze Microsoft Corp.\n\n"
            "*Analysis includes:*\n"
            "• Technical indicators\n"
            "• Social media sentiment\n"
            "• Recent news impact\n"
            "• Financial fundamentals\n"
            "• AI trading recommendation\n\n"
            "⏱️ Analysis typically takes 1-3 minutes.\n"
            "⚠️ This is educational content, not financial advice."
        )
        
        await update.message.reply_text(
            help_message,
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle text messages (stock symbols)."""
        message_text = update.message.text.strip()

        # Use the message as the symbol directly (no slash processing)
        symbol = message_text

        # Validate symbol
        if not trading_service.validate_symbol(symbol):
            error_message = (
                "❌ *Invalid stock symbol*\n\n"
                "Please send a valid stock ticker symbol.\n"
                "*Examples:* `AAPL`, `TSLA`, `NVDA`, `MSFT`"
            )
            await update.message.reply_text(
                error_message,
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        # Send processing message
        processing_message = await update.message.reply_text(
            f"🔄 *Analyzing {symbol.upper()}...*\n\n"
            "This may take 1-3 minutes. Please wait...\n"
            "🤖 AI agents are working on your analysis.",
            parse_mode=ParseMode.MARKDOWN
        )
        
        try:
            # Perform analysis with timeout
            decision, full_state = await asyncio.wait_for(
                trading_service.analyze_stock(symbol),
                timeout=ANALYSIS_TIMEOUT
            )
            
            # Format response
            today = datetime.now().strftime("%Y-%m-%d")
            response = trading_service.format_decision_for_telegram(
                decision, symbol.upper(), today
            )
            
            # Edit the processing message with results
            await processing_message.edit_text(
                response,
                parse_mode=ParseMode.MARKDOWN
            )
            
            logger.info(f"Successfully analyzed {symbol} for user {update.effective_user.id}")
            
        except asyncio.TimeoutError:
            await processing_message.edit_text(
                f"⏰ *Analysis timeout for {symbol.upper()}*\n\n"
                "The analysis is taking longer than expected. Please try again later.",
                parse_mode=ParseMode.MARKDOWN
            )
            logger.warning(f"Analysis timeout for {symbol}")
            
        except Exception as e:
            await processing_message.edit_text(
                f"❌ *Error analyzing {symbol.upper()}*\n\n"
                "Something went wrong. Please try again later.\n"
                f"Error: {str(e)[:100]}...",
                parse_mode=ParseMode.MARKDOWN
            )
            logger.error(f"Error analyzing {symbol}: {str(e)}")
    
    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle errors."""
        logger.error(f"Update {update} caused error {context.error}")
        
        if update and update.message:
            await update.message.reply_text(
                "❌ *An error occurred*\n\n"
                "Please try again later or contact support.",
                parse_mode=ParseMode.MARKDOWN
            )
    
    async def start_polling(self):
        """Start the bot with polling."""
        if self._is_running:
            logger.warning("Bot is already running")
            return

        if not self.application:
            await self.initialize()

        logger.info("Starting bot with polling...")
        self._is_running = True

        try:
            # Initialize the application
            await self.application.initialize()

            # Start the application (background tasks)
            await self.application.start()

            # Start polling for updates
            await self.application.updater.start_polling()

            logger.info("Bot polling started successfully")

            # Keep running until stopped
            while self._is_running:
                await asyncio.sleep(1)

        except Exception as e:
            logger.error(f"Error in polling: {e}")
            self._is_running = False
            raise
        finally:
            logger.info("Polling loop ended")

    async def stop_polling(self):
        """Stop the bot polling."""
        if not self._is_running:
            logger.info("Bot is not running")
            return

        logger.info("Stopping bot polling...")
        self._is_running = False

        if self.application:
            try:
                # Stop the updater first
                if self.application.updater:
                    await self.application.updater.stop()
                    logger.info("Updater stopped successfully")

                # Stop the application
                await self.application.stop()
                logger.info("Application stopped successfully")

            except Exception as e:
                logger.error(f"Error stopping application: {e}")

        logger.info("Bot polling stopped")

    async def shutdown(self):
        """Shutdown the bot completely."""
        logger.info("Shutting down bot...")

        # Stop polling if running
        if self._is_running:
            await self.stop_polling()

        # Shutdown application
        if self.application:
            try:
                await self.application.shutdown()
                logger.info("Application shutdown successfully")
            except Exception as e:
                logger.error(f"Error during application shutdown: {e}")

        # Reset state
        self._is_running = False
        logger.info("Bot shutdown complete")

    async def start_webhook(self, webhook_url: str, port: int = 8000):
        """Start the bot with webhook."""
        await self.initialize()
        logger.info(f"Starting bot with webhook: {webhook_url}")
        await self.application.run_webhook(
            listen="0.0.0.0",
            port=port,
            webhook_url=webhook_url
        )


# Global bot instance
trading_bot = TradingBot()
