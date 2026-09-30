# -*- coding: utf-8 -*-
"""معالج الرسائل الرئيسي - يتضمن فحص الحظر والقفل"""

from telegram import Update
from telegram.constants import ParseMode, ChatAction
from telegram.ext import ContextTypes

from config.settings import DEVELOPER_ID, DEVELOPER_TELEGRAM_URL
from core.admin_manager import AdminManager
from handlers.admin_handler import handle_admin_message
from handlers.subscription_handler import require_subscription


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """المعالج الرئيسي لجميع رسائل المستخدمين."""

    user_id = update.effective_user.id
    message = update.message

    # =====================================================================
    # 0. إذا كان المطور في حالة انتظار (حظر/إذاعة) → عالجها أولاً
    # =====================================================================
    if await handle_admin_message(update, context):
        return

    # =====================================================================
    # 1. التحقق من الحظر
    # =====================================================================
    if AdminManager.is_blocked(user_id):
        await message.reply_text(
            "⛔ *أنت محظور من استخدام هذا البوت.*\n\n"
            "للاستفسار، تواصل مع المطور.",
            parse_mode=ParseMode.MARKDOWN,
        )
        return

    # =====================================================================
    # 2. التحقق من قفل البوت (المطور معفي)
    # =====================================================================
    if not AdminManager.is_bot_open() and user_id != DEVELOPER_ID:
        from telegram import InlineKeyboardButton, InlineKeyboardMarkup
        keyboard = [
            [InlineKeyboardButton("👨‍💻 تواصل مع المطور", url=DEVELOPER_TELEGRAM_URL)]
        ]
        await message.reply_text(
            "🔒 *البوت مقفل مؤقتاً.*\n\n"
            "يرجى المحاولة لاحقاً.",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        return

    # =====================================================================
    # 3. التحقق من الاشتراك الإجباري
    # =====================================================================
    if not await require_subscription(update, context):
        return

    # =====================================================================
    # 4. حفظ المستخدم إذا كان جديدًا (بدون /start)
    # =====================================================================
    is_new = AdminManager.save_user(user_id)
    if is_new:
        from services.notification_service import notify_developer_new_user
        await notify_developer_new_user(context.bot, update.effective_user)

    # =====================================================================
    # 5. متابعة المعالجة الطبيعية مع Gemini
    # =====================================================================
    await message.chat.send_action(action=ChatAction.TYPING)

    # ... بقية الكود الأصلي لمعالجة الرسائل مع Gemini ...
    # (نص + صور + مستندات + فيديو + صوت → إرسال لـ Gemini → توجيه الرد)
