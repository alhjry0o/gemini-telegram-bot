# -*- coding: utf-8 -*-
"""إعدادات المشروع المركزية"""

import os
from dotenv import load_dotenv

load_dotenv()

# =============================================================================
# المفاتيح الأساسية
# =============================================================================
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
DEVELOPER_ID = int(os.getenv("DEVELOPER_ID", "0"))
DEVELOPER_NAME = os.getenv("DEVELOPER_NAME", "عبدالله")
DEVELOPER_TELEGRAM_URL = os.getenv("DEVELOPER_TELEGRAM_URL", "")
CHANNEL_TELEGRAM_URL = os.getenv("CHANNEL_TELEGRAM_URL", "")
CHANNEL_ID = os.getenv("CHANNEL_ID", "")  # معرف القناة للتحقق من الاشتراك

# =============================================================================
# إعدادات Gemini
# =============================================================================
GEMINI_MODEL = "gemini-1.5-pro"
MAX_TEXT_LENGTH = 4000
MAX_INLINE_SIZE_MB = 20

# =============================================================================
# مسارات الملفات
# =============================================================================
USERS_FILE = "users.txt"
BLOCKED_FILE = "blocked_users.txt"
BOT_STATE_FILE = "bot_state.txt"

# =============================================================================
# التحقق من المتغيرات الإلزامية
# =============================================================================
def validate_config():
    """التحقق من وجود جميع المتغيرات الإلزامية."""
    errors = []
    if not GEMINI_API_KEY:
        errors.append("❌ GEMINI_API_KEY غير موجود في .env")
    if not TELEGRAM_BOT_TOKEN:
        errors.append("❌ TELEGRAM_BOT_TOKEN غير موجود في .env")
    if DEVELOPER_ID == 0:
        errors.append("❌ DEVELOPER_ID غير موجود أو غير صحيح في .env")
    if errors:
        raise ValueError("\n".join(errors))
    return True
