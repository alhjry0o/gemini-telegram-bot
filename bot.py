# -*- coding: utf-8 -*-
"""نقطة انطلاق البوت"""

import logging

from telegram import Update
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    CallbackQueryHandler, filters,
)

from config.settings import TELEGRAM_BOT_TOKEN, validate_config
from handlers.start_handler import start_command
from handlers.stats_handler import stats_command
from handlers.message_handler import handle_message
from handlers.admin_handler import admin_command, admin_callback


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


async def error_handler(update: object, context) -> None:
    logger.error(f"استثناء: {context.error}", exc_info=True)


def main() -> None:
    validate_config()
    logger.info("🚀 جاري تشغيل البوت...")

    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # =====================================================================
    # أوامر المستخدمين
    # =====================================================================
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("stats", stats_command))

    # =====================================================================
    # أوامر المطور
    # =====================================================================
    application.add_handler(CommandHandler("admin", admin_command))

    # =====================================================================
    # معالج أزرار لوحة التحكم
    # =====================================================================
    application.add_handler(CallbackQueryHandler(admin_callback))

    # =====================================================================
    # معالج الرسائل العامة
    # =====================================================================
    application.add_handler(
        MessageHandler(
            filters.TEXT | filters.PHOTO | filters.Document.ALL
            | filters.VIDEO | filters.VOICE | filters.AUDIO,
            handle_message,
        )
    )

    application.add_error_handler(error_handler)
    logger.info("✅ البوت جاهز!")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
