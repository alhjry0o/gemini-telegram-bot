# -*- coding: utf-8 -*-
"""
إعدادات المشروع المركزية
يتم تحميل جميع المتغيرات من ملف .env والتحقق منها
"""

import os
from dotenv import load_dotenv

# تحميل ملف .env
load_dotenv()

# =============================================================================
# 🔑 المفاتيح الأساسية (املأها في .env)
# =============================================================================
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# =============================================================================
# 👨‍💻 بيانات المطور
# =============================================================================
DEVELOPER_ID = int(os.getenv("DEVELOPER_ID", "0"))
DEVELOPER_NAME = os.getenv("DEVELOPER_NAME", "عبدالله")
DEVELOPER_TELEGRAM_URL = os.getenv("DEVELOPER_TELEGRAM_URL", "https://t.me/")

# =============================================================================
# 📢 بيانات القناة
# =============================================================================
CHANNEL_TELEGRAM_URL = os.getenv("CHANNEL_TELEGRAM_URL", "https://t.me/")
# معرف القناة للتحقق من الاشتراك (مثال: @my_channel أو -1001234567890)
CHANNEL_ID = os.getenv("CHANNEL_ID", "")

# =============================================================================
# 🤖 إعدادات Gemini
# =============================================================================
GEMINI_MODEL = "gemini-1.5-pro"
MAX_TEXT_LENGTH = 4000           # الحد الأقصى لطول الرد النصي
MAX_INLINE_SIZE_MB = 20          # الحد الأقصى للملفات الصغيرة (MB)
ZIP_MIN_CODE_BLOCKS = 2          # أقل عدد كتل أكواد لإنشاء ZIP
TEMPERATURE = 0.7
MAX_OUTPUT_TOKENS = 8192

# =============================================================================
# 📂 مسارات الملفات
# =============================================================================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

USERS_FILE = os.path.join(BASE_DIR, "data", "users.txt")
BLOCKED_FILE = os.path.join(BASE_DIR, "data", "blocked_users.txt")
BOT_STATE_FILE = os.path.join(BASE_DIR, "data", "bot_state.txt")
LOGS_DIR = os.path.join(BASE_DIR, "logs")
UPLOADS_DIR = os.path.join(BASE_DIR, "data", "uploads")
PROJECTS_DIR = os.path.join(BASE_DIR, "data", "projects")

# إنشاء المجلدات إن لم تكن موجودة
for directory in [os.path.dirname(USERS_FILE), LOGS_DIR, UPLOADS_DIR, PROJECTS_DIR]:
    os.makedirs(directory, exist_ok=True)

# =============================================================================
# 🛡️ التحقق من المتغيرات الإلزامية
# =============================================================================
def validate_config() -> bool:
    """
    التحقق من وجود جميع المتغيرات الإلزامية.
    يرفع استثناء إذا كانت هناك متغيرات ناقصة.
    """
    errors = []

    if not GEMINI_API_KEY:
        errors.append("❌ GEMINI_API_KEY غير موجود في ملف .env")
    if not TELEGRAM_BOT_TOKEN:
        errors.append("❌ TELEGRAM_BOT_TOKEN غير موجود في ملف .env")
    if DEVELOPER_ID == 0:
        errors.append("❌ DEVELOPER_ID غير موجود أو غير صحيح في ملف .env")
    if not DEVELOPER_TELEGRAM_URL or DEVELOPER_TELEGRAM_URL == "https://t.me/":
        errors.append("⚠️ تحذير: DEVELOPER_TELEGRAM_URL لم يتم ضبطه بشكل صحيح")
    if not CHANNEL_TELEGRAM_URL or CHANNEL_TELEGRAM_URL == "https://t.me/":
        errors.append("⚠️ تحذير: CHANNEL_TELEGRAM_URL لم يتم ضبطه بشكل صحيح")

    # فصل الأخطاء الحرجة عن التحذيرات
    critical_errors = [e for e in errors if e.startswith("❌")]
    warnings = [e for e in errors if e.startswith("⚠️")]

    if warnings:
        import logging
        logger = logging.getLogger(__name__)
        for w in warnings:
            logger.warning(w)

    if critical_errors:
        raise ValueError("\n".join(critical_errors))

    return True
