# -*- coding: utf-8 -*-
"""نقطة انطلاق البوت — Main Entry Point"""

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)

from config.settings import TELEGRAM_BOT_TOKEN, validate_config
from handlers.start_handler import start_command
from handlers.stats_handler import stats_command
from handlers.admin_handler import admin_command, admin_callback
from handlers.message_handler import handle_message
from utils.logger import setup_logger

logger = setup_logger("bot")


async def error_handler(update: object, context) -> None:
    """معالج الأخطاء العام."""
    logger.error(f"❌ استثناء: {context.error}", exc_info=context.error)


def main() -> None:
    """الدالة الرئيسية لتشغيل البوت."""
    logger.info("🚀 جاري تشغيل البوت...")

    # التحقق من الإعدادات
    validate_config()

    # بناء التطبيق
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # =========================================================================
    # معالجات الأوامر
    # =========================================================================
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("stats", stats_command))
    application.add_handler(CommandHandler("admin", admin_command))

    # =========================================================================
    # معالج الأزرار
    # =========================================================================
    application.add_handler(CallbackQueryHandler(admin_callback))

    # =========================================================================
    # معالج الرسائل العامة (نص + وسائط)
    # =========================================================================
    application.add_handler(
        MessageHandler(
            filters.TEXT
            | filters.PHOTO
            | filters.Document.ALL
            | filters.VIDEO
            | filters.VOICE
            | filters.AUDIO,
            handle_message,
        )
    )

    # =========================================================================
    # معالج الأخطاء
    # =========================================================================
    application.add_error_handler(error_handler)

    logger.info("✅ البوت جاهز للعمل!")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
