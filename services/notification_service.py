# -*- coding: utf-8 -*-
"""خدمة إشعارات المطور"""

from telegram import Bot, User
from telegram.constants import ParseMode

from config.settings import DEVELOPER_ID
from core.admin_manager import AdminManager
from utils.logger import setup_logger

logger = setup_logger(__name__)


async def notify_developer_new_user(bot: Bot, user: User) -> None:
    """
    إرسال إشعار للمطور عند انضمام مستخدم جديد.
    
    Args:
        bot: كائن البوت
        user: بيانات المستخدم الجديد
    """
    try:
        # رابط المستخدم بتنسيق tg://
        user_link = f"[{user.full_name}](tg://user?id={user.id})"
        total_users = AdminManager.get_users_count()

        message = (
            f"📊 *مستخدم جديد انضم للبوت!*\n\n"
            f"• الاسم: {user_link}\n"
            f"• الأيدي: `{user.id}`\n"
            f"• إجمالي مستخدمي البوت الحالي: *{total_users}*"
        )

        await bot.send_message(
            chat_id=DEVELOPER_ID,
            text=message,
            parse_mode=ParseMode.MARKDOWN,
        )
        logger.info(f"✅ تم إشعار المطور بالمستخدم الجديد: {user.id}")
    except Exception as e:
        logger.error(f"❌ فشل إرسال الإشعار للمطور: {e}")


async def notify_developer_error(bot: Bot, error: Exception, context: str = "") -> None:
    """
    إرسال إشعار للمطور عند حدوث خطأ حرج.
    
    Args:
        bot: كائن البوت
        error: الاستثناء
        context: سياق الخطأ
    """
    try:
        message = (
            f"⚠️ *خطأ في البوت*\n\n"
            f"• السياق: `{context}`\n"
            f"• الخطأ: `{type(error).__name__}`\n"
            f"• التفاصيل: `{str(error)[:500]}`"
        )
        await bot.send_message(
            chat_id=DEVELOPER_ID,
            text=message,
            parse_mode=ParseMode.MARKDOWN,
        )
    except Exception as e:
        logger.error(f"فشل إرسال إشعار الخطأ: {e}")
