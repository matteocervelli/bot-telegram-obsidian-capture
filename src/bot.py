"""Telegram bot entry point."""

import structlog
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters

from src.config import settings
from src.handlers import handle_document, handle_photo, handle_text, handle_voice
from src.handlers.commands import (
    handle_daily,
    handle_done,
    handle_task,
    handle_task_list,
    handle_undo,
)
from src.handlers.video import handle_video, handle_video_note

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

    # Command handlers
    app.add_handler(CommandHandler("undo", handle_undo, filters=allowed))
    app.add_handler(CommandHandler("daily", handle_daily, filters=allowed))
    app.add_handler(CommandHandler("task", handle_task, filters=allowed))
    app.add_handler(CommandHandler("task_list", handle_task_list, filters=allowed))
    app.add_handler(CommandHandler("done", handle_done, filters=allowed))

    # Message handlers
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND & allowed, handle_text))
    app.add_handler(MessageHandler(filters.VOICE & allowed, handle_voice))
    app.add_handler(MessageHandler(filters.PHOTO & allowed, handle_photo))
    app.add_handler(MessageHandler(filters.VIDEO & allowed, handle_video))
    app.add_handler(MessageHandler(filters.VIDEO_NOTE & allowed, handle_video_note))
    app.add_handler(MessageHandler(filters.Document.ALL & allowed, handle_document))

    log.info("bot_ready")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
