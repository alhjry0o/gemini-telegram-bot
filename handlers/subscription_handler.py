# -*- coding: utf-8 -*-
"""التحقق من الاشتراك الإجباري في القناة"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from config.settings import CHANNEL_ID, CHANNEL_TELEGRAM_URL, DEVELOPER_ID


async def check_subscription(user_id: int, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """
    التحقق مما إذا كان المستخدم مشتركًا في القناة.
    يعيد True إذا كان مشتركًا أو إذا لم يتم ضبط CHANNEL_ID.
    """
    if not CHANNEL_ID:
        return True  # تجاهل التحقق إذا لم يتم ضبط القناة

    # المطور معفي دائمًا
    if user_id == DEVELOPER_ID:
        return True

    try:
        member = await context.bot.get_chat_member(
            chat_id=CHANNEL_ID,
            user_id=user_id,
        )
        # الحالات التي تعني أن المستخدم مشترك
        subscribed_statuses = {"member", "administrator", "creator"}
        return member.status in subscribed_statuses
    except Exception:
        # في حال حدث خطأ (مثل عدم وجود البوت في القناة)، نسمح بالمرور
        return True


async def require_subscription(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """
    إرسال رسالة الاشتراك الإجباري إذا لم يكن المستخدم مشتركًا.
    يعيد True إذا كان مشتركًا، False إذا تم إرسال رسالة الاشتراك.
    """
    user_id = update.effective_user.id
    if await check_subscription(user_id, context):
        return True

    # بناء رسالة الاشتراك
    keyboard = [
        [InlineKeyboardButton("📢 اشترك في القناة", url=CHANNEL_TELEGRAM_URL)],
        [InlineKeyboardButton("✅ تحقق من الاشتراك", callback_data="check_sub")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    text = (
        "⚠️ *عذراً عزيزي،*\n\n"
        "لا يمكنك استخدام البوت إلا بعد الاشتراك في قناتنا الرسمية.\n\n"
        "📢 *اضغط على الزر أدناه للاشتراك، ثم اضغط على زر التحقق.*"
    )

    if update.callback_query:
        await update.callback_query.message.reply_text(
            text, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup
        )
    elif update.message:
        await update.message.reply_text(
            text, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup
        )

    return False
