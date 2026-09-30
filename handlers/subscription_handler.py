# -*- coding: utf-8 -*-
"""التحقق من الاشتراك الإجباري في القناة"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from config.settings import CHANNEL_ID, CHANNEL_TELEGRAM_URL, DEVELOPER_ID
from utils.logger import setup_logger

logger = setup_logger(__name__)


async def check_subscription(user_id: int, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """
    التحقق من اشتراك المستخدم في القناة.
    
    Returns:
        True إذا كان مشتركًا أو تعذّر التحقق، False إذا لم يكن مشتركًا.
    """
    # إذا لم يتم ضبط القناة، تخطى التحقق
    if not CHANNEL_ID:
        return True

    # المطور معفي
    if user_id == DEVELOPER_ID:
        return True

    try:
        member = await context.bot.get_chat_member(
            chat_id=CHANNEL_ID,
            user_id=user_id,
        )
        subscribed = {"member", "administrator", "creator", "restricted"}
        return member.status in subscribed
    except Exception as e:
        # في حال فشل التحقق (البوت غير مشرف أو قناة خاطئة) → نسمح بالمرور
        logger.warning(f"⚠️ فشل التحقق من الاشتراك للمستخدم {user_id}: {e}")
        return True


async def require_subscription(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """
    إرسال رسالة الاشتراك الإجباري إذا لزم.
    
    Returns:
        True إذا كان مشتركًا، False إذا تم إرسال رسالة الاشتراك.
    """
    user_id = update.effective_user.id
    if await check_subscription(user_id, context):
        return True

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

    try:
        if update.callback_query:
            await update.callback_query.message.reply_text(
                text, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup
            )
        elif update.message:
            await update.message.reply_text(
                text, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup
            )
    except Exception as e:
        logger.error(f"فشل إرسال رسالة الاشتراك: {e}")

    return False
