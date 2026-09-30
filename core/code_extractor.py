# -*- coding: utf-8 -*-
"""استخراج الأكواد من ردود Gemini وإنشاء ملفات ZIP"""

import io
import re
import zipfile
from typing import List, Dict, Optional

from config.settings import ZIP_MIN_CODE_BLOCKS
from utils.logger import setup_logger

logger = setup_logger(__name__)

# خريطة امتدادات اللغات
LANG_EXT = {
    "python": "py", "py": "py",
    "javascript": "js", "js": "js",
    "typescript": "ts", "ts": "ts",
    "html": "html", "htm": "html",
    "css": "css", "scss": "scss",
    "php": "php", "dart": "dart",
    "json": "json", "xml": "xml",
    "yaml": "yaml", "yml": "yml",
    "sql": "sql", "bash": "sh",
    "shell": "sh", "sh": "sh",
    "java": "java", "kotlin": "kt",
    "swift": "swift", "go": "go",
    "rust": "rs", "c": "c",
    "cpp": "cpp", "csharp": "cs",
    "markdown": "md", "md": "md",
}


def extract_code_blocks(text: str) -> List[Dict[str, str]]:
    """
    استخراج كتل الأكواد من النص.
    
    يدعم الصيغ التالية:
        ```python:filename.py
        ```python
        ```
    
    Returns:
        قائمة من dict تحتوي على 'filename' و 'content'
    """
    blocks = []
    # نمط يلتقط: ```lang أو ```lang:filename
    pattern = r"```(\w+)?(?::([^\n\r]+))?\r?\n(.*?)```"
    matches = re.findall(pattern, text, re.DOTALL)

    for i, (lang, filename, code) in enumerate(matches):
        # تحديد اسم الملف
        if filename and filename.strip():
            name = filename.strip()
        else:
            lang_lower = (lang or "").lower()
            ext = LANG_EXT.get(lang_lower, "txt")
            name = f"file_{i + 1}.{ext}"

        # تنظيف اسم الملف من المسارات الخطرة
        name = name.replace("..", "").lstrip("/\\")
        if not name:
            name = f"file_{i + 1}.txt"

        blocks.append({"filename": name, "content": code.strip()})

    logger.info(f"📦 تم استخراج {len(blocks)} كتلة كود")
    return blocks


def should_create_zip(response_text: str, code_blocks: List[Dict]) -> bool:
    """
    تحديد ما إذا كان يجب إنشاء ZIP.
    
    الشروط:
        - عدد كتل الأكواد >= ZIP_MIN_CODE_BLOCKS
        - أو الرد أطول من 4000 حرف ويحتوي على 1+ كتلة
    """
    if len(code_blocks) >= ZIP_MIN_CODE_BLOCKS:
        return True
    if len(response_text) > 4000 and len(code_blocks) >= 1:
        return True
    return False


def create_zip_from_blocks(code_blocks: List[Dict]) -> Optional[io.BytesIO]:
    """
    إنشاء ملف ZIP من كتل الأكواد.
    
    Returns:
        BytesIO buffer جاهز للإرسال، أو None عند الفشل
    """
    if not code_blocks:
        return None

    try:
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            used_names = set()
            for block in code_blocks:
                name = block["filename"]
                # منع التكرار
                if name in used_names:
                    base, ext = name.rsplit(".", 1) if "." in name else (name, "")
                    counter = 2
                    while f"{base}_{counter}.{ext}" in used_names:
                        counter += 1
                    name = f"{base}_{counter}.{ext}" if ext else f"{base}_{counter}"
                used_names.add(name)
                zf.writestr(name, block["content"])

            # إضافة ملف README تلقائي
            readme = (
                "# مشروع مُنشأ بواسطة بوت الذكاء الاصطناعي\n\n"
                f"عدد الملفات: {len(code_blocks)}\n\n"
                "الملفات المضمنة:\n"
                + "\n".join(f"- {b['filename']}" for b in code_blocks)
            )
            zf.writestr("README.md", readme)

        zip_buffer.seek(0)
        logger.info(f"✅ تم إنشاء ZIP بـ {len(code_blocks)} ملف")
        return zip_buffer

    except Exception as e:
        logger.error(f"❌ فشل إنشاء ZIP: {e}")
        return None
