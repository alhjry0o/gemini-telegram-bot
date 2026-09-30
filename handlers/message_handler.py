# -*- coding: utf-8 -*-
"""معالج الرسائل الرئيسي — قلب البوت"""

import asyncio
from datetime import datetime

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode, ChatAction
from telegram.ext import ContextTypes

from config.settings import (
    DEVELOPER_ID, DEVELOPER_TELEGRAM_URL,
    MAX_TEXT_LENGTH,
)
from core.admin_manager import AdminManager
from core.code_extractor import (
    extract_code_blocks, should_create_zip, create_zip_from_blocks,
)
from core.file_handler import process_media_message
from core.gemini_client import get_or_create_session
from handlers.admin_handler import handle_admin_message
from handlers.subscription_handler import require_subscription
from services.notification_service import notify_developer_new_user
from utils.helpers import send_long_text, truncate
from utils.logger import setup_logger

logger = setup_logger(__name__)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """المعالج الرئيسي لجميع رسائل المستخدمين."""
    user_id = update.effective_user.id
    message = update.message

    # =========================================================================
    # 0. حالات انتظار المطور
    # =========================================================================
    if await handle_admin_message(update, context):
        return

    # =========================================================================
    # 1. فحص الحظر
    # =========================================================================
    if AdminManager.is_blocked(user_id):
        await message.reply_text(
            "⛔ *أنت محظور من استخدام هذا البوت.*\n\n"
            "للاستفسار، تواصل مع المطور.",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("👨‍💻 تواصل مع المطور", url=DEVELOPER_TELEGRAM_URL)]
            ]),
        )
        return

    # =========================================================================
    # 2. فحص قفل البوت (المطور معفي)
    # =========================================================================
    if not AdminManager.is_bot_open() and user_id != DEVELOPER_ID:
        await message.reply_text(
            "🔒 *البوت مقفل مؤقتاً.*\n\nيرجى المحاولة لاحقاً.",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("👨‍💻 تواصل مع المطور", url=DEVELOPER_TELEGRAM_URL)]
            ]),
        )
        return

    # =========================================================================
    # 3. التحقق من الاشتراك الإجباري
    # =========================================================================
    if not await require_subscription(update, context):
        return

    # =========================================================================
    # 4. تسجيل المستخدم (إذا لم يستخدم /start)
    # =========================================================================
    if AdminManager.save_user(user_id):
        await notify_developer_new_user(context.bot, update.effective_user)

    # =========================================================================
    # 5. إظهار مؤشر الكتابة
    # =========================================================================
    try:
        await message.chat.send_action(action=ChatAction.TYPING)
    except Exception:
        pass

    # =========================================================================
    # 6. تجهيز المحتوى
    # =========================================================================
    try:
        parts = await process_media_message(update, context)
        if not parts:
            await message.reply_text("⚠️ عذراً، لم أتعرف على نوع المحتوى المرسل.")
            return

        # =====================================================================
        # 7. إرسال إلى Gemini
        # =====================================================================
        session = get_or_create_session(user_id)

        # نستخدم to_thread لأن SDK متزامن
        response = await asyncio.to_thread(session.send_message, parts)
        response_text = (response.text or "").strip()

        if not response_text:
            await message.reply_text("⚠️ لم أتمكن من توليد رد. حاول مرة أخرى.")
            return

        # =====================================================================
        # 8. توجيه الرد (Hybrid Routing)
        # =====================================================================
        code_blocks = extract_code_blocks(response_text)

        # السيناريو 1: إنشاء ZIP
        if should_create_zip(response_text, code_blocks):
            zip_buffer = create_zip_from_blocks(code_blocks)
            if zip_buffer:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                try:
                    await message.reply_document(
                        document=zip_buffer,
                        filename=f"project_{timestamp}.zip",
                        caption="📦 *تم تجهيز مشروعك بنجاح في ملف ZIP مرفق.*",
                        parse_mode=ParseMode.MARKDOWN,
                    )
                    # ملخص قصير
                    summary = truncate(response_text, 1500)
                    await message.reply_text(
                        f"📝 *ملخص المشروع:*\n\n{summary}",
                        parse_mode=ParseMode.MARKDOWN,
                    )
                except Exception as e:
                    logger.error(f"فشل إرسال ZIP: {e}")
                    await send_long_text(message, response_text)
                return

        # السيناريو 2: نص قصير
        if len(response_text) < MAX_TEXT_LENGTH:
            try:
                await message.reply_text(response_text, parse_mode=ParseMode.MARKDOWN)
            except Exception:
                await message.reply_text(response_text)
            return

        # السيناريو 3: نص طويل بدون ZIP
        await send_long_text(message, response_text)

    except Exception as e:
        logger.error(f"❌ خطأ في معالجة الرسالة: {e}", exc_info=True)
        try:
            await message.reply_text(
                "❌ عذراً، حدث خطأ أثناء معالجة طلبك. حاول مرة أخرى لاحقاً."
            )
        except Exception:
            pass
