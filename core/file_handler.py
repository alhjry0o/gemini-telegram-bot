# -*- coding: utf-8 -*-
"""
معالج الوسائط والملفات
يدير الرفع للـ File API والتحويل إلى Inline Data
"""

import os
import asyncio
from typing import Optional, Tuple

from google.genai import types
from telegram import Update
from telegram.ext import ContextTypes

from config.settings import MAX_INLINE_SIZE_MB, UPLOADS_DIR
from core.gemini_client import gemini_client
from utils.logger import setup_logger

logger = setup_logger(__name__)


def detect_file_type(mime_type: str) -> str:
    """تحديد نوع الملف من MIME type."""
    if not mime_type:
        return "unknown"
    if mime_type.startswith("image/"):
        return "image"
    if mime_type.startswith("video/"):
        return "video"
    if mime_type.startswith("audio/"):
        return "audio"
    if mime_type == "application/pdf":
        return "pdf"
    if mime_type in ("text/plain", "text/csv", "application/json"):
        return "text"
    return "document"


async def upload_to_file_api(file_path: str) -> Optional[object]:
    """
    رفع ملف إلى Gemini File API.
    الملفات تبقى 48 ساعة، الحالة تصبح ACTIVE بعد المعالجة.
    
    Args:
        file_path: مسار الملف المحلي
    
    Returns:
        كائن الملف المرفوع أو None عند الفشل
    """
    try:
        uploaded_file = await asyncio.to_thread(
            gemini_client.files.upload, file=file_path
        )

        # انتظار حتى تصبح الحالة ACTIVE
        max_attempts = 30
        attempts = 0
        while attempts < max_attempts:
            state = str(getattr(uploaded_file.state, "name", uploaded_file.state))
            if "PROCESSING" not in state:
                break
            await asyncio.sleep(2)
            uploaded_file = await asyncio.to_thread(
                gemini_client.files.get, name=uploaded_file.name
            )
            attempts += 1

        state = str(getattr(uploaded_file.state, "name", uploaded_file.state))
        if "FAILED" in state:
            logger.error(f"❌ فشل رفع الملف: {uploaded_file.name}")
            return None

        logger.info(f"✅ تم رفع الملف: {uploaded_file.uri}")
        return uploaded_file

    except Exception as e:
        logger.error(f"❌ خطأ في رفع الملف: {e}")
        return None


async def download_telegram_file(update: Update, context: ContextTypes.DEFAULT_TYPE,
                                  file_id: str, filename: str) -> Optional[str]:
    """
    تنزيل ملف من تيليجرام إلى القرص.
    
    Returns:
        مسار الملف أو None عند الفشل
    """
    try:
        file = await context.bot.get_file(file_id)
        file_path = os.path.join(UPLOADS_DIR, filename)
        await file.download_to_drive(file_path)
        return file_path
    except Exception as e:
        logger.error(f"❌ فشل تنزيل الملف: {e}")
        return None


async def process_media_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> list:
    """
    معالجة رسالة المستخدم واستخراج جميع الوسائط منها.
    
    Returns:
        قائمة من Parts (نص + وسائط) لإرسالها إلى Gemini
    """
    message = update.message
    parts = []

    # =========================================================================
    # 1. النص
    # =========================================================================
    if message.text:
        parts.append(message.text)
    elif message.caption:
        parts.append(message.caption)

    # =========================================================================
    # 2. الصور
    # =========================================================================
    if message.photo:
        photo = message.photo[-1]  # أعلى دقة
        try:
            file = await context.bot.get_file(photo.file_id)
            file_bytes = bytes(await file.download_as_bytearray())
            parts.append(
                types.Part.from_bytes(data=file_bytes, mime_type="image/jpeg")
            )
        except Exception as e:
            logger.error(f"فشل تحميل الصورة: {e}")

    # =========================================================================
    # 3. المستندات
    # =========================================================================
    if message.document:
        doc = message.document
        mime = doc.mime_type or "application/octet-stream"
        size_mb = (doc.file_size or 0) / (1024 * 1024)

        if size_mb > MAX_INLINE_SIZE_MB:
            # ملف كبير → File API
            filename = doc.file_name or f"doc_{doc.file_unique_id}"
            file_path = await download_telegram_file(
                update, context, doc.file_id, filename
            )
            if file_path:
                uploaded = await upload_to_file_api(file_path)
                if uploaded:
                    parts.append(
                        types.Part.from_uri(
                            file_uri=uploaded.uri, mime_type=uploaded.mime_type
                        )
                    )
                # تنظيف
                try:
                    os.remove(file_path)
                except OSError:
                    pass
        else:
            # ملف صغير → Inline
            try:
                file = await context.bot.get_file(doc.file_id)
                file_bytes = bytes(await file.download_as_bytearray())
                parts.append(types.Part.from_bytes(data=file_bytes, mime_type=mime))
            except Exception as e:
                logger.error(f"فشل تحميل المستند: {e}")

    # =========================================================================
    # 4. الفيديو
    # =========================================================================
    if message.video:
        video = message.video
        mime = video.mime_type or "video/mp4"
        size_mb = (video.file_size or 0) / (1024 * 1024)

        if size_mb > MAX_INLINE_SIZE_MB:
            filename = video.file_name or f"video_{video.file_unique_id}.mp4"
            file_path = await download_telegram_file(
                update, context, video.file_id, filename
            )
            if file_path:
                uploaded = await upload_to_file_api(file_path)
                if uploaded:
                    parts.append(
                        types.Part.from_uri(
                            file_uri=uploaded.uri, mime_type=uploaded.mime_type
                        )
                    )
                try:
                    os.remove(file_path)
                except OSError:
                    pass
        else:
            try:
                file = await context.bot.get_file(video.file_id)
                file_bytes = bytes(await file.download_as_bytearray())
                parts.append(types.Part.from_bytes(data=file_bytes, mime_type=mime))
            except Exception as e:
                logger.error(f"فشل تحميل الفيديو: {e}")

    # =========================================================================
    # 5. الصوت (Voice + Audio)
    # =========================================================================
    audio = message.voice or message.audio
    if audio:
        mime = audio.mime_type or "audio/ogg"
        try:
            file = await context.bot.get_file(audio.file_id)
            file_bytes = bytes(await file.download_as_bytearray())
            parts.append(types.Part.from_bytes(data=file_bytes, mime_type=mime))
        except Exception as e:
            logger.error(f"فشل تحميل الصوت: {e}")

    return parts
