# -*- coding: utf-8 -*-
"""دوال مساعدة عامة"""

import re
from telegram import Message
from telegram.constants import ParseMode
from telegram.error import BadRequest

from utils.logger import setup_logger

logger = setup_logger(__name__)


def escape_markdown(text: str) -> str:
    """تأمين النص من كسر Markdown."""
    if not text:
        return ""
    # حماية الرموز الخاصة في MarkdownV1
    for char in ["_", "*", "`", "["]:
        text = text.replace(char, f"\\{char}")
    return text


def format_user_link(user_id: int, full_name: str) -> str:
    """إنشاء رابط المستخدم بتنسيق tg://"""
    safe_name = escape_markdown(full_name or f"User {user_id}")
    return f"[{safe_name}](tg://user?id={user_id})"


async def send_long_text(message: Message, text: str, chunk_size: int = 4000) -> None:
    """
    إرسال نص طويل مقسم إلى أجزاء.
    يحاول Markdown أولاً، وإن فشل يرسل كنص عادي.
    """
    if not text:
        return

    for i in range(0, len(text), chunk_size):
        chunk = text[i:i + chunk_size]
        try:
            await message.reply_text(chunk, parse_mode=ParseMode.MARKDOWN)
        except BadRequest:
            # إعادة الإرسال بدون Markdown
            try:
                await message.reply_text(chunk)
            except Exception as e:
                logger.error(f"فشل إرسال جزء من النص: {e}")


def truncate(text: str, max_len: int = 200) -> str:
    """اقتطاع النص مع إضافة ..."""
    if len(text) <= max_len:
        return text
    return text[:max_len].rstrip() + "..."


def is_valid_telegram_id(text: str) -> bool:
    """التحقق من صحة معرف تيليجرام (أرقام فقط)."""
    return text.strip().lstrip("-").isdigit()
