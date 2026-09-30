# -*- coding: utf-8 -*-
"""معالج أمر /stats — خاص بالمطور"""

from datetime import datetime
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from config.settings import DEVELOPER_ID
from core.admin_manager import AdminManager


async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """إحصائيات البوت — للمطور فقط."""
    if update.effective_user.id != DEVELOPER_ID:
        return

    count = AdminManager.get_users_count()
    blocked = len(AdminManager.get_blocked_list())
    state = "🟢 مفتوح" if AdminManager.is_bot_open() else "🔴 مقفل"

    text = (
        f"📊 *إحصائيات البوت:*\n\n"
        f"👥 إجمالي المستخدمين: *{count}*\n"
        f"⛔ المحظورون: *{blocked}*\n"
        f"🔋 حالة البوت: {state}\n"
        f"📅 التاريخ: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    )

    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)
