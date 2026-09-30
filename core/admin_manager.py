# -*- coding: utf-8 -*-
"""مدير العمليات الإدارية: الحظر، القفل، الإحصائيات"""

import os
from datetime import datetime
from typing import List, Optional

from config.settings import USERS_FILE, BLOCKED_FILE, BOT_STATE_FILE


class AdminManager:
    """إدارة العمليات الإدارية للبوت."""

    # =========================================================================
    # إدارة المستخدمين
    # =========================================================================
    @staticmethod
    def load_users() -> set:
        """قراءة جميع معرفات المستخدمين."""
        if not os.path.exists(USERS_FILE):
            return set()
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            return {line.strip() for line in f if line.strip().isdigit()}

    @staticmethod
    def save_user(user_id: int) -> bool:
        """حفظ معرف المستخدم. يعيد True إذا كان جديدًا."""
        existing = AdminManager.load_users()
        if str(user_id) in existing:
            return False
        with open(USERS_FILE, "a", encoding="utf-8") as f:
            f.write(f"{user_id}\n")
        return True

    @staticmethod
    def get_users_count() -> int:
        """إرجاع العدد الإجمالي للمستخدمين."""
        return len(AdminManager.load_users())

    @staticmethod
    def get_all_users() -> List[int]:
        """إرجاع قائمة بجميع معرفات المستخدمين."""
        return [int(uid) for uid in AdminManager.load_users()]

    # =========================================================================
    # إدارة الحظر
    # =========================================================================
    @staticmethod
    def load_blocked() -> set:
        """قراءة قائمة المحظورين."""
        if not os.path.exists(BLOCKED_FILE):
            return set()
        with open(BLOCKED_FILE, "r", encoding="utf-8") as f:
            return {line.strip() for line in f if line.strip().isdigit()}

    @staticmethod
    def block_user(user_id: int) -> bool:
        """حظر مستخدم. يعيد False إذا كان محظورًا مسبقًا."""
        blocked = AdminManager.load_blocked()
        if str(user_id) in blocked:
            return False
        with open(BLOCKED_FILE, "a", encoding="utf-8") as f:
            f.write(f"{user_id}\n")
        return True

    @staticmethod
    def unblock_user(user_id: int) -> bool:
        """إلغاء حظر مستخدم. يعيد False إذا لم يكن محظورًا."""
        blocked = AdminManager.load_blocked()
        if str(user_id) not in blocked:
            return False
        blocked.discard(str(user_id))
        with open(BLOCKED_FILE, "w", encoding="utf-8") as f:
            f.write("\n".join(sorted(blocked)) + ("\n" if blocked else ""))
        return True

    @staticmethod
    def is_blocked(user_id: int) -> bool:
        """التحقق مما إذا كان المستخدم محظورًا."""
        return str(user_id) in AdminManager.load_blocked()

    @staticmethod
    def get_blocked_list() -> List[int]:
        """إرجاع قائمة المحظورين."""
        return [int(uid) for uid in AdminManager.load_blocked()]

    # =========================================================================
    # إدارة حالة البوت (مفتوح/مقفل)
    # =========================================================================
    @staticmethod
    def get_bot_state() -> str:
        """قراءة حالة البوت. 'open' أو 'closed'."""
        if not os.path.exists(BOT_STATE_FILE):
            return "open"
        with open(BOT_STATE_FILE, "r", encoding="utf-8") as f:
            return f.read().strip() or "open"

    @staticmethod
    def set_bot_state(state: str) -> None:
        """تعيين حالة البوت."""
        with open(BOT_STATE_FILE, "w", encoding="utf-8") as f:
            f.write(state)

    @staticmethod
    def is_bot_open() -> bool:
        """التحقق مما إذا كان البوت مفتوحًا."""
        return AdminManager.get_bot_state() == "open"
