# -*- coding: utf-8 -*-
"""معالج الأوامر الإدارية /admin وجميع الأزرار التفاعلية"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from config.settings import DEVELOPER_ID, DEVELOPER_NAME, DEVELOPER_TELEGRAM_URL
from core.admin_manager import AdminManager

# =============================================================================
# حالات انتظار إدخال المطور
# =============================================================================
WAITING_FOR_BLOCK_ID = "waiting_block_id"
WAITING_FOR_UNBLOCK_ID = "waiting_unblock_id"
WAITING_FOR_BROADCAST = "waiting_broadcast"


# =============================================================================
# القائمة الرئيسية
# =============================================================================
def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    """بناء لوحة التحكم الرئيسية."""
    keyboard = [
        [InlineKeyboardButton("👥 عدد المستخدمين", callback_data="admin_users_count")],
        [InlineKeyboardButton("⛔ قسم الحظر", callback_data="admin_ban_menu")],
        [InlineKeyboardButton("🎙 الإذاعة", callback_data="admin_broadcast")],
        [InlineKeyboardButton("👀 حالة البوت", callback_data="admin_bot_state")],
    ]
    return InlineKeyboardMarkup(keyboard)


async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالج أمر /admin - خاص بالمطور فقط."""
    user_id = update.effective_user.id

    # تجاهل الأمر تمامًا إذا لم يكن المرسل هو المطور
    if user_id != DEVELOPER_ID:
        return

    # إعادة تعيين الحالة
    context.user_data.pop("admin_state", None)
    context.user_data.pop("broadcast_message", None)

    text = (
        f"مرحباً يا {DEVELOPER_NAME} 👋\n\n"
        f"هذه قائمة الأوامر ⬇️"
    )

    await update.message.reply_text(
        text,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=get_main_menu_keyboard(),
    )


# =============================================================================
# معالج الأزرار الرئيسية
# =============================================================================
async def admin_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """معالج جميع أزرار لوحة التحكم."""
    query = update.callback_query
    await query.answer()

    # التحقق الأمني: فقط المطور
    if query.from_user.id != DEVELOPER_ID:
        return

    data = query.data

    # =====================================================================
    # عدد المستخدمين
    # =====================================================================
    if data == "admin_users_count":
        count = AdminManager.get_users_count()
        keyboard = [
            [InlineKeyboardButton("🔙 رجوع للقائمة الرئيسية", callback_data="admin_main")]
        ]
        await query.edit_message_text(
            f"👥 *عدد المستخدمين:*\n\n*{count}* مستخدم",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        return

    # =====================================================================
    # قسم الحظر
    # =====================================================================
    if data == "admin_ban_menu":
        await show_ban_menu(query)
        return

    if data == "admin_block_user":
        context.user_data["admin_state"] = WAITING_FOR_BLOCK_ID
        keyboard = [
            [InlineKeyboardButton("❌ إلغاء الأمر", callback_data="admin_ban_menu")]
        ]
        await query.edit_message_text(
            "✏️ *أرسل ID المستخدم المراد حظره:*",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        return

    if data == "admin_unblock_user":
        context.user_data["admin_state"] = WAITING_FOR_UNBLOCK_ID
        keyboard = [
            [InlineKeyboardButton("❌ إلغاء الأمر", callback_data="admin_ban_menu")]
        ]
        await query.edit_message_text(
            "✏️ *أرسل ID المستخدم المراد إلغاء حظره:*",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        return

    if data == "admin_blocked_list":
        blocked = AdminManager.get_blocked_list()
        if blocked:
            text = "🗒 *قائمة المحظورين:*\n\n" + "\n".join(f"• `{uid}`" for uid in blocked)
        else:
            text = "🗒 *قائمة المحظورين فارغة.*"

        keyboard = [
            [InlineKeyboardButton("🔙 رجوع لقسم الحظر", callback_data="admin_ban_menu")]
        ]
        await query.edit_message_text(
            text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        return

    # =====================================================================
    # الإذاعة
    # =====================================================================
    if data == "admin_broadcast":
        context.user_data["admin_state"] = WAITING_FOR_BROADCAST
        keyboard = [
            [InlineKeyboardButton("❌ إلغاء الإذاعة", callback_data="admin_main")]
        ]
        await query.edit_message_text(
            "🎙 *أرسل محتوى الإذاعة الذي تريد إرساله لجميع المستخدمين:*",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        return

    # =====================================================================
    # حالة البوت
    # =====================================================================
    if data == "admin_bot_state":
        await show_bot_state(query)
        return

    if data == "admin_lock_bot":
        keyboard = [
            [
                InlineKeyboardButton("✅ تأكيد", callback_data="admin_confirm_lock"),
                InlineKeyboardButton("❌ إلغاء", callback_data="admin_bot_state"),
            ]
        ]
        await query.edit_message_text(
            "🔒 *هل أنت متأكد من قفل البوت؟*\n\n"
            "عند القفل، لن يتمكن أي مستخدم (ما عدا المطور) من استخدام البوت.",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        return

    if data == "admin_confirm_lock":
        AdminManager.set_bot_state("closed")
        keyboard = [
            [InlineKeyboardButton("🔙 رجوع", callback_data="admin_bot_state")]
        ]
        await query.edit_message_text(
            "🔒 *تم قفل البوت بنجاح.*",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        return

    if data == "admin_unlock_bot":
        keyboard = [
            [
                InlineKeyboardButton("✅ تأكيد", callback_data="admin_confirm_unlock"),
                InlineKeyboardButton("❌ إلغاء", callback_data="admin_bot_state"),
            ]
        ]
        await query.edit_message_text(
            "🔓 *هل أنت متأكد من فتح البوت؟*",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        return

    if data == "admin_confirm_unlock":
        AdminManager.set_bot_state("open")
        keyboard = [
            [InlineKeyboardButton("🔙 رجوع", callback_data="admin_bot_state")]
        ]
        await query.edit_message_text(
            "🔓 *تم فتح البوت بنجاح.*",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        return

    # =====================================================================
    # رجوع للقائمة الرئيسية
    # =====================================================================
    if data == "admin_main":
        context.user_data.pop("admin_state", None)
        context.user_data.pop("broadcast_message", None)
        text = f"مرحباً يا {DEVELOPER_NAME} 👋\n\nهذه قائمة الأوامر ⬇️"
        await query.edit_message_text(
            text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=get_main_menu_keyboard(),
        )
        return

    # =====================================================================
    # التحقق من الاشتراك (من subscription_handler)
    # =====================================================================
    if data == "check_sub":
        from handlers.subscription_handler import check_subscription
        if await check_subscription(query.from_user.id, context):
            await query.edit_message_text("✅ *تم التحقق من اشتراكك بنجاح!*\n\nأرسل /start للبدء.")
        else:
            await query.answer("⚠️ لا تزال غير مشترك في القناة.", show_alert=True)
        return


# =============================================================================
# دوال مساعدة للعرض
# =============================================================================
async def show_ban_menu(query) -> None:
    """عرض قائمة قسم الحظر."""
    keyboard = [
        [InlineKeyboardButton("⛔ حظر مستخدم", callback_data="admin_block_user")],
        [InlineKeyboardButton("❌ إلغاء حظر مستخدم", callback_data="admin_unblock_user")],
        [InlineKeyboardButton("🗒 قائمة المحظورين", callback_data="admin_blocked_list")],
        [InlineKeyboardButton("🔙 رجوع للقائمة الرئيسية", callback_data="admin_main")],
    ]
    await query.edit_message_text(
        "⛔ *إليك قسم الحظر:*",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


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
# معالج رسائل المطور (للحظر/الإذاعة)
# =============================================================================
async def handle_admin_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """
    معالجة رسائل المطور في حالات الانتظار.
    يعيد True إذا تمت المعالجة، False إذا لم تكن هناك حالة انتظار.
    """
    user_id = update.effective_user.id
    if user_id != DEVELOPER_ID:
        return False

    state = context.user_data.get("admin_state")
    if not state:
        return False

    text = update.message.text.strip() if update.message.text else ""

    # =====================================================================
    # انتظار ID الحظر
    # =====================================================================
    if state == WAITING_FOR_BLOCK_ID:
        if not text.isdigit():
            await update.message.reply_text("⚠️ الرجاء إرسال ID صحيح (أرقام فقط).")
            return True

        target_id = int(text)
        if target_id == DEVELOPER_ID:
            await update.message.reply_text("⚠️ لا يمكنك حظر نفسك!")
            return True

        if AdminManager.block_user(target_id):
            keyboard = [
                [InlineKeyboardButton("🔙 رجوع لقسم الحظر", callback_data="admin_ban_menu")]
            ]
            await update.message.reply_text(
                f"✅ *تم حظر المستخدم بنجاح.*\n\n• الأيدي: `{target_id}`",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(keyboard),
            )
        else:
            await update.message.reply_text(f"⚠️ المستخدم `{target_id}` محظور مسبقًا.")

        context.user_data.pop("admin_state", None)
        return True

    # =====================================================================
    # انتظار ID إلغاء الحظر
    # =====================================================================
    if state == WAITING_FOR_UNBLOCK_ID:
        if not text.isdigit():
            await update.message.reply_text("⚠️ الرجاء إرسال ID صحيح (أرقام فقط).")
            return True

        target_id = int(text)
        if AdminManager.unblock_user(target_id):
            keyboard = [
                [InlineKeyboardButton("🔙 رجوع لقسم الحظر", callback_data="admin_ban_menu")]
            ]
            await update.message.reply_text(
                f"✅ *تم إلغاء الحظر عن المستخدم بنجاح.*\n\n• الأيدي: `{target_id}`",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=InlineKeyboardMarkup(keyboard),
            )
        else:
            await update.message.reply_text(f"⚠️ المستخدم `{target_id}` غير محظور أساسًا.")

        context.user_data.pop("admin_state", None)
        return True

    # =====================================================================
    # انتظار محتوى الإذاعة
    # =====================================================================
    if state == WAITING_FOR_BROADCAST:
        context.user_data.pop("admin_state", None)
        await broadcast_to_all(update, context)
        return True

    return False


# =============================================================================
# دالة الإذاعة
# =============================================================================
async def broadcast_to_all(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """إرسال رسالة الإذاعة لجميع المستخدمين."""
    users = AdminManager.get_all_users()
    if not users:
        await update.message.reply_text("⚠️ لا يوجد مستخدمون لإرسال الإذاعة إليهم.")
        return

    success = 0
    failed = 0

    await update.message.reply_text(f"⏳ جاري إرسال الإذاعة إلى {len(users)} مستخدم...")

    for uid in users:
        try:
            await context.bot.copy_message(
                chat_id=uid,
                from_chat_id=update.message.chat_id,
                message_id=update.message.message_id,
            )
            success += 1
        except Exception:
            failed += 1

    await update.message.reply_text(
        f"✅ *تمت الإذاعة بنجاح!*\n\n"
        f"• نجح الإرسال: *{success}*\n"
        f"• فشل الإرسال: *{failed}*",
        parse_mode=ParseMode.MARKDOWN,
      )
