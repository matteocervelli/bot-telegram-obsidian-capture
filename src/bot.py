"""Telegram bot entry point."""

import structlog
from telegram import Update
from telegram.ext import Application, MessageHandler, filters

from src.config import settings
from src.handlers import handle_document, handle_photo, handle_text, handle_voice

structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.dev.ConsoleRenderer(),
    ]
)
log = structlog.get_logger()


def user_filter() -> filters.BaseFilter:
    """Filter to only accept messages from whitelisted user."""
    return filters.User(user_id=settings.telegram_user_id)


def main() -> None:
    """Start the bot."""
    log.info("starting_bot", user_id=settings.telegram_user_id)

    app = Application.builder().token(settings.telegram_token).build()

    # Register handlers with user whitelist filter
    allowed = user_filter()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND & allowed, handle_text))
    app.add_handler(MessageHandler(filters.VOICE & allowed, handle_voice))
    app.add_handler(MessageHandler(filters.PHOTO & allowed, handle_photo))
    app.add_handler(MessageHandler(filters.Document.ALL & allowed, handle_document))

    log.info("bot_ready")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
