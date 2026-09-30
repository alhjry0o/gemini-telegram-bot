# -*- coding: utf-8 -*-
"""لوحة التحكم الإدارية /admin وجميع أزرارها"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from config.settings import DEVELOPER_ID, DEVELOPER_NAME
from core.admin_manager import AdminManager
from utils.logger import setup_logger

logger = setup_logger(__name__)

# =============================================================================
# حالات انتظار المطور
# =============================================================================
STATE_BLOCK = "wait_block"
STATE_UNBLOCK = "wait_unblock"
STATE_BROADCAST = "wait_broadcast"


def main_menu() -> InlineKeyboardMarkup:
    """لوحة التحكم الرئيسية."""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("👥 عدد المستخدمين", callback_data="admin_users_count")],
        [InlineKeyboardButton("⛔ قسم الحظر", callback_data="admin_ban_menu")],
        [InlineKeyboardButton("🎙 الإذاعة", callback_data="admin_broadcast")],
        [InlineKeyboardButton("👀 حالة البوت", callback_data="admin_bot_state")],
    ])


def ban_menu() -> InlineKeyboardMarkup:
    """قائمة قسم الحظر."""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⛔ حظر مستخدم", callback_data="admin_block_user")],
        [InlineKeyboardButton("❌ إلغاء حظر مستخدم", callback_data="admin_unblock_user")],
        [InlineKeyboardButton("🗒 قائمة المحظورين", callback_data="admin_blocked_list")],
        [InlineKeyboardButton("🔙 رجوع للقائمة الرئيسية", callback_data="admin_main")],
    ])


# =============================================================================
# أمر /admin
# =============================================================================
async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالج /admin — خاص بالمطور فقط."""
    if update.effective_user.id != DEVELOPER_ID:
        return

    # تصفير الحالة
    context.user_data.pop("admin_state", None)

    text = f"مرحباً يا {DEVELOPER_NAME} 👋\n\nهذه قائمة الأوامر ⬇️"
    await update.message.reply_text(
        text, parse_mode=ParseMode.MARKDOWN, reply_markup=main_menu()
    )


# =============================================================================
# معالج الأزرار
# =============================================================================
async def admin_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالج جميع أزرار لوحة التحكم."""
    query = update.callback_query
    await query.answer()

    # أمان
    if query.from_user.id != DEVELOPER_ID:
        return

    data = query.data

    # =========================================================================
    # 🤝 التحقق من الاشتراك
    # =========================================================================
    if data == "check_sub":
        from handlers.subscription_handler import check_subscription
        if await check_subscription(query.from_user.id, context):
            await query.edit_message_text(
                "✅ *تم التحقق من اشتراكك بنجاح!*\n\nأرسل /start للبدء.",
                parse_mode=ParseMode.MARKDOWN,
            )
        else:
            await query.answer("⚠️ لا تزال غير مشترك في القناة.", show_alert=True)
        return

    # =========================================================================
    # 👥 عدد المستخدمين
    # =========================================================================
    if data == "admin_users_count":
        count = AdminManager.get_users_count()
        await query.edit_message_text(
            f"👥 *عدد المستخدمين:*\n\n*{count}* مستخدم",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 رجوع للقائمة الرئيسية", callback_data="admin_main")]
            ]),
        )
        return

    # =========================================================================
    # ⛔ قسم الحظر
    # =========================================================================
    if data == "admin_ban_menu":
        context.user_data.pop("admin_state", None)
        await query.edit_message_text(
            "⛔ *إليك قسم الحظر:*",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=ban_menu(),
        )
        return

    if data == "admin_block_user":
        context.user_data["admin_state"] = STATE_BLOCK
        await query.edit_message_text(
            "✏️ *أرسل ID المستخدم المراد حظره:*",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("❌ إلغاء الأمر", callback_data="admin_ban_menu")]
            ]),
        )
        return

    if data == "admin_unblock_user":
        context.user_data["admin_state"] = STATE_UNBLOCK
        await query.edit_message_text(
            "✏️ *أرسل ID المستخدم المراد إلغاء حظره:*",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("❌ إلغاء الأمر", callback_data="admin_ban_menu")]
            ]),
        )
        return

    if data == "admin_blocked_list":
        blocked = AdminManager.get_blocked_list()
        if blocked:
            text = "🗒 *قائمة المحظورين:*\n\n" + "\n".join(f"• `{uid}`" for uid in blocked)
        else:
            text = "🗒 *قائمة المحظورين فارغة.*"
        await query.edit_message_text(
            text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 رجوع لقسم الحظر", callback_data="admin_ban_menu")]
            ]),
        )
        return

    # =========================================================================
    # 🎙 الإذاعة
    # =========================================================================
    if data == "admin_broadcast":
        context.user_data["admin_state"] = STATE_BROADCAST
        await query.edit_message_text(
            "🎙 *أرسل محتوى الإذاعة الذي تريد إرساله لجميع المستخدمين:*",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("❌ إلغاء الإذاعة", callback_data="admin_main")]
            ]),
        )
        return

    # =========================================================================
    # 👀 حالة البوت
    # =========================================================================
    if data == "admin_bot_state":
        await show_bot_state(query)
        return

    if data == "admin_lock_bot":
        await query.edit_message_text(
            "🔒 *هل أنت متأكد من قفل البوت؟*\n\n"
            "عند القفل، لن يتمكن أي مستخدم (ما عدا المطور) من استخدام البوت.",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("✅ تأكيد", callback_data="admin_confirm_lock"),
                    InlineKeyboardButton("❌ إلغاء", callback_data="admin_bot_state"),
                ]
            ]),
        )
        return

    if data == "admin_confirm_lock":
        AdminManager.set_bot_state("closed")
        await query.edit_message_text(
            "🔒 *تم قفل البوت بنجاح.*",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 رجوع", callback_data="admin_bot_state")]
            ]),
        )
        return

    if data == "admin_unlock_bot":
        await query.edit_message_text(
            "🔓 *هل أنت متأكد من فتح البوت؟*",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("✅ تأكيد", callback_data="admin_confirm_unlock"),
                    InlineKeyboardButton("❌ إلغاء", callback_data="admin_bot_state"),
                ]
            ]),
        )
        return

    if data == "admin_confirm_unlock":
        AdminManager.set_bot_state("open")
        await query.edit_message_text(
            "🔓 *تم فتح البوت بنجاح.*",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 رجوع", callback_data="admin_bot_state")]
            ]),
        )
        return

    # =========================================================================
    # 🔙 رجوع للقائمة الرئيسية
    # =========================================================================
    if data == "admin_main":
        context.user_data.pop("admin_state", None)
        text = f"مرحباً يا {DEVELOPER_NAME} 👋\n\nهذه قائمة الأوامر ⬇️"
        await query.edit_message_text(
            text, parse_mode=ParseMode.MARKDOWN, reply_markup=main_menu()
        )
        return


# =============================================================================
# عرض حالة البوت
# =============================================================================
async def show_bot_state(query) -> None:
    """عرض حالة البوت الحالية."""
    state = AdminManager.get_bot_state()
    state_text = "🟢 مفتوح" if state == "open" else "🔴 مقفل"

    if state == "open":
        keyboard = [
            [InlineKeyboardButton("🔒 قفل البوت", callback_data="admin_lock_bot")],
            [InlineKeyboardButton("🔙 رجوع", callback_data="admin_main")],
        ]
    else:
        keyboard = [
            [InlineKeyboardButton("🔓 فتح البوت", callback_data="admin_unlock_bot")],
            [InlineKeyboardButton("🔙 رجوع", callback_data="admin_main")],
        ]

    await query.edit_message_text(
        f"👀 *حالة البوت:*\n\n{state_text}",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


# =============================================================================
# معالجة رسائل المطور في حالات الانتظار
# =============================================================================
async def handle_admin_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """
    معالجة رسائل المطور أثناء حالات الانتظار (حظر/إذاعة).
    
    Returns:
        True إذا تمت المعالجة، False إذا لا توجد حالة انتظار.
    """
    if update.effective_user.id != DEVELOPER_ID:
        return False

    state = context.user_data.get("admin_state")
    if not state:
        return False

    # =========================================================================
    # ⛔ حظر مستخدم
    # =========================================================================
    if state == STATE_BLOCK:
        text = (update.message.text or "").strip()
        if not text.isdigit():
            await update.message.reply_text("⚠️ الرجاء إرسال ID صحيح (أرقام فقط).")
            return True

        target_id = int(text)
        if target_id == DEVELOPER_ID:
            await update.message.reply_text("⚠️ لا يمكنك حظر نفسك!")
            return True

        if AdminManager.block_user(target_id):
            msg = f"✅ *تم حظر المستخدم بنجاح.*\n\n• الأيدي: `{target_id}`"
        else:
            msg = f"⚠️ المستخدم `{target_id}` محظور مسبقًا."

        await update.message.reply_text(
            msg,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 رجوع لقسم الحظر", callback_data="admin_ban_menu")]
            ]),
        )
        context.user_data.pop("admin_state", None)
        return True

    # =========================================================================
    # ❌ إلغاء حظر
    # =========================================================================
    if state == STATE_UNBLOCK:
        text = (update.message.text or "").strip()
        if not text.isdigit():
            await update.message.reply_text("⚠️ الرجاء إرسال ID صحيح (أرقام فقط).")
            return True

        target_id = int(text)
        if AdminManager.unblock_user(target_id):
            msg = f"✅ *تم إلغاء الحظر عن المستخدم بنجاح.*\n\n• الأيدي: `{target_id}`"
        else:
            msg = f"⚠️ المستخدم `{target_id}` غير محظور أساسًا."

        await update.message.reply_text(
            msg,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 رجوع لقسم الحظر", callback_data="admin_ban_menu")]
            ]),
        )
        context.user_data.pop("admin_state", None)
        return True

    # =========================================================================
    # 🎙 الإذاعة
    # =========================================================================
    if state == STATE_BROADCAST:
        context.user_data.pop("admin_state", None)
        await broadcast_to_all(update, context)
        return True

    return False


# =============================================================================
# الإذاعة
# =============================================================================
async def broadcast_to_all(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """إرسال رسالة الإذاعة إلى جميع المستخدمين."""
    users = AdminManager.get_all_users()
    if not users:
        await update.message.reply_text("⚠️ لا يوجد مستخدمون لإرسال الإذاعة إليهم.")
        return

    status_msg = await update.message.reply_text(
        f"⏳ جاري إرسال الإذاعة إلى {len(users)} مستخدم..."
    )

    success = 0
    failed = 0

    for uid in users:
        try:
            await context.bot.copy_message(
                chat_id=uid,
                from_chat_id=update.message.chat_id,
                message_id=update.message.message_id,
            )
            success += 1
        except Exception as e:
            failed += 1
            logger.debug(f"فشل الإرسال إلى {uid}: {e}")

    try:
        await status_msg.edit_text(
            f"✅ *تمت الإذاعة بنجاح!*\n\n"
            f"• نجح الإرسال: *{success}*\n"
            f"• فشل الإرسال: *{failed}*",
            parse_mode=ParseMode.MARKDOWN,
        )
    except Exception:
        await update.message.reply_text(
            f"✅ تمت الإذاعة.\nنجح: {success} | فشل: {failed}"
        )
