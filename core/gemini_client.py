# -*- coding: utf-8 -*-
"""عميل Gemini وإدارة الجلسات لكل مستخدم"""

from typing import Dict
from google import genai
from google.genai import types

from config.settings import (
    GEMINI_API_KEY, GEMINI_MODEL, TEMPERATURE,
    MAX_OUTPUT_TOKENS,
)
from utils.logger import setup_logger

logger = setup_logger(__name__)

# عميل Gemini العام
gemini_client = genai.Client(api_key=GEMINI_API_KEY)

# قاموس جلسات المستخدمين: {user_id: chat_session}
user_sessions: Dict[int, object] = {}

# تعليمات النظام
SYSTEM_INSTRUCTION = (
    "أنت مساعد ذكي متخصص في التعليم والبرمجة باللغة العربية. "
    "قدم إجابات دقيقة ومنظمة ومبسطة. "
    "عند كتابة أكواد برمجية، استخدم دائماً علامات ``` مع تحديد اللغة. "
    "عند كتابة مشروع متعدد الملفات، استخدم الصيغة التالية لكل ملف:\n"
    "```language:filename.ext\n"
    "محتوى الملف\n"
    "```\n"
    "مثال: ```python:main.py ثم المحتوى ثم ```. "
    "هذا يساعد في تجهيز المشروع كملفات منفصلة في ZIP."
)


def get_or_create_session(user_id: int):
    """
    استرجاع جلسة المستخدم أو إنشاء جلسة جديدة.
    
    Args:
        user_id: معرف المستخدم
    
    Returns:
        جلسة محادثة Gemini
    """
    if user_id not in user_sessions:
        try:
            user_sessions[user_id] = gemini_client.chats.create(
                model=GEMINI_MODEL,
                config=types.GenerateContentConfig(
                    temperature=TEMPERATURE,
                    max_output_tokens=MAX_OUTPUT_TOKENS,
                    system_instruction=SYSTEM_INSTRUCTION,
                ),
            )
            logger.info(f"✅ تم إنشاء جلسة جديدة للمستخدم {user_id}")
        except Exception as e:
            logger.error(f"❌ فشل إنشاء الجلسة للمستخدم {user_id}: {e}")
            raise
    return user_sessions[user_id]


def reset_session(user_id: int) -> bool:
    """إعادة تعيين جلسة المستخدم."""
    if user_id in user_sessions:
        del user_sessions[user_id]
        logger.info(f"🔄 تم إعادة تعيين جلسة المستخدم {user_id}")
        return True
    return False


def clear_all_sessions() -> int:
    """مسح جميع الجلسات. يعيد عدد الجلسات المحذوفة."""
    count = len(user_sessions)
    user_sessions.clear()
    logger.info(f"🗑️ تم مسح {count} جلسة")
    return count
