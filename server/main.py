#!/usr/bin/env python3
"""
TradingAgents Telegram Bot Server

A FastAPI server that runs a Telegram bot for stock analysis using TradingAgents.
"""

import os
import sys
import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import uvicorn

# Add parent directory to path for tradingagents import
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from server.config import validate_config, PORT, HOST, WEBHOOK_URL
from server.telegram_bot import trading_bot

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan."""
    polling_task = None

    try:
        # Startup
        logger.info("Starting TradingAgents Telegram Bot Server...")

        # Validate configuration
        try:
            validate_config()
            logger.info("Configuration validated successfully")
        except ValueError as e:
            logger.error(f"Configuration error: {e}")
            raise

        # Initialize bot
        await trading_bot.initialize()
        logger.info("Telegram bot initialized")

        # Start bot based on configuration
        if WEBHOOK_URL:
            # Production mode with webhook
            logger.info(f"Setting up webhook: {WEBHOOK_URL}")
            await trading_bot.bot.set_webhook(url=f"{WEBHOOK_URL}/webhook")
        else:
            # Development mode with polling
            logger.info("Starting bot polling in background...")
            polling_task = asyncio.create_task(trading_bot.start_polling())
            trading_bot.polling_task = polling_task

        yield

    finally:
        # Shutdown
        logger.info("Shutting down...")

        try:
            if WEBHOOK_URL:
                # Webhook mode cleanup
                if trading_bot.bot:
                    await trading_bot.bot.delete_webhook()
                    logger.info("Webhook deleted")
            else:
                # Polling mode cleanup
                if polling_task and not polling_task.done():
                    logger.info("Cancelling polling task...")
                    polling_task.cancel()
                    try:
                        await asyncio.wait_for(polling_task, timeout=5.0)
                    except (asyncio.CancelledError, asyncio.TimeoutError):
                        logger.info("Polling task cancelled")
                    except Exception as e:
                        logger.error(f"Error cancelling polling task: {e}")

            # Shutdown the bot application
            await trading_bot.shutdown()

        except Exception as e:
            logger.error(f"Error during shutdown: {e}")

        logger.info("Shutdown complete")


# Create FastAPI app
app = FastAPI(
    title="TradingAgents Telegram Bot",
    description="AI-powered stock analysis bot using TradingAgents framework",
    version="1.0.0",
    lifespan=lifespan
)


@app.post("/webhook")
async def webhook(request: Request):
    """Webhook endpoint for Telegram."""
    if not WEBHOOK_URL:
        raise HTTPException(status_code=404, detail="Webhook not configured")
    
    try:
        # Get update from Telegram
        update_data = await request.json()
        
        # Process update
        from telegram import Update
        update = Update.de_json(update_data, trading_bot.bot)
        
        # Handle update
        await trading_bot.application.process_update(update)
        
        return JSONResponse({"status": "ok"})
        
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

def main():
    """Main entry point."""
    logger.info("Starting TradingAgents Telegram Bot Server...")

    # Run the server
    uvicorn.run(
        "main:app",
        host=HOST,
        port=PORT,
        reload=False,
        log_level="info"
    )


if __name__ == "__main__":
    main()
