# -*- coding: utf-8 -*-
"""معالج أمر /start"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from config.settings import CHANNEL_TELEGRAM_URL, DEVELOPER_TELEGRAM_URL
from core.admin_manager import AdminManager
from handlers.subscription_handler import require_subscription
from services.notification_service import notify_developer_new_user


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """رسالة الترحيب مع الأزرار."""
    user = update.effective_user

    # 1. التحقق من الاشتراك
    if not await require_subscription(update, context):
        return

    # 2. تسجيل المستخدم وإشعار المطور إذا كان جديدًا
    is_new = AdminManager.save_user(user.id)
    if is_new:
        await notify_developer_new_user(context.bot, user)

    # 3. نص الترحيب
    welcome_text = (
        "🌟 *مرحباً بك في المساعد الذكي!*\n\n"
        "أنا مساعد متخصص في *التعليم والبرمجة* باللغة العربية، "
        "مدعوم بتقنية Gemini 1.5 Pro من Google.\n\n"
        "📌 *ماذا يمكنني أن أفعل؟*\n"
        "• الإجابة عن أسئلتك التعليمية والبرمجية\n"
        "• تحليل الصور والمستندات (PDF, صور, فيديو, صوت)\n"
        "• كتابة وتوليد الأكواد بلغات متعددة\n"
        "• تجهيز مشاريع كاملة في ملف ZIP عند الطلب\n\n"
        "💡 *فقط أرسل سؤالك أو الملف الذي تريد تحليله وسأبدأ فوراً!*"
    )

    # 4. الأزرار
    keyboard = [
        [InlineKeyboardButton("📢 قناة البوت الرسمية", url=CHANNEL_TELEGRAM_URL)],
        [InlineKeyboardButton("👨‍💻 حساب مطور البوت", url=DEVELOPER_TELEGRAM_URL)],
    ]

    await update.message.reply_text(
        welcome_text,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup(keyboard),
    )
