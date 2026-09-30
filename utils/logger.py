# -*- coding: utf-8 -*-
"""إعداد نظام التسجيل الموحد للبوت"""

import os
import logging
from logging.handlers import RotatingFileHandler

from config.settings import LOGS_DIR


def setup_logger(name: str = "bot", level: int = logging.INFO) -> logging.Logger:
    """
    إعداد وتكوين logger موحد.
    
    Args:
        name: اسم الـ logger
        level: مستوى التسجيل
    
    Returns:
        logging.Logger: كائن الـ logger الجاهز
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # تجنب الإضافة المكررة للمعالجات
    if logger.handlers:
        return logger

    # =========================================================================
    # المنسق (Formatter)
    # =========================================================================
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # =========================================================================
    # المعالج 1: الطرفية (Console)
    # =========================================================================
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # =========================================================================
    # المعالج 2: ملف السجل مع تدوير تلقائي
    # =========================================================================
    log_file = os.path.join(LOGS_DIR, "bot.log")
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=5 * 1024 * 1024,  # 5 MB
        backupCount=3,
        encoding="utf-8",
    )
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger
