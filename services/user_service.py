# -*- coding: utf-8 -*-
"""
خدمة إدارة المستخدمين
تُستخدم من قبل المعالجات المختلفة
"""

from typing import List, Optional
from core.admin_manager import AdminManager


class UserService:
    """خدمة موحدة لإدارة المستخدمين."""

    @staticmethod
    def register_user(user_id: int) -> bool:
        """
        تسجيل مستخدم جديد.
        
        Returns:
            True إذا كان جديدًا، False إذا كان موجودًا.
        """
        return AdminManager.save_user(user_id)

    @staticmethod
    def get_total_count() -> int:
        """العدد الإجمالي للمستخدمين."""
        return AdminManager.get_users_count()

    @staticmethod
    def get_all_ids() -> List[int]:
        """جميع معرفات المستخدمين."""
        return AdminManager.get_all_users()

    @staticmethod
    def is_registered(user_id: int) -> bool:
        """التحقق من تسجيل المستخدم."""
        return AdminManager.user_exists(user_id)

    @staticmethod
    def is_blocked(user_id: int) -> bool:
        """التحقق من حظر المستخدم."""
        return AdminManager.is_blocked(user_id)

    @staticmethod
    def block(user_id: int) -> bool:
        """حظر مستخدم."""
        return AdminManager.block_user(user_id)

    @staticmethod
    def unblock(user_id: int) -> bool:
        """إلغاء حظر مستخدم."""
        return AdminManager.unblock_user(user_id)

    @staticmethod
    def get_blocked_ids() -> List[int]:
        """معرفات المحظورين."""
        return AdminManager.get_blocked_list()

    @staticmethod
    def is_bot_open() -> bool:
        """حالة البوت."""
        return AdminManager.is_bot_open()
