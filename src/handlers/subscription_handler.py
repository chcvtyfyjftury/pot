import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes, ConversationHandler, CallbackQueryHandler, MessageHandler, filters
)

from src.config import ADMIN_IDS
from src.database import queries as db
from src.middlewares.auth import allow_free_access

logger = logging.getLogger(__name__)

SUB_SELECT_METHOD, SUB_USDT_TX, SUB_CASH_PROOF = range(700, 703)


def _back_main() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data="main_menu")]])


def _back_sub() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data="sub_menu")]])


@allow_free_access
async def sub_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    uid = update.effective_user.id
    db.upsert_user(uid, update.effective_user.username or "", update.effective_user.full_name or "")

    sub = db.get_active_subscription(uid)
    sub_text = ""
    if sub and uid not in ADMIN_IDS:
        used = sub.get("daily_used", 0)
        limit = sub.get("daily_limit", 0)
        remaining = limit - used
        sub_text = f"\n\n✅ *اشتراكك الحالي:* {sub.get('plan_name','')}\n📊 الاستخدام اليوم: `{used}/{limit}`\n📈 متبقي: `{remaining}` عملية"

    plans = db.get_active_plans()
    if not plans:
        await query.edit_message_text(
            "📦 *الاشتراك*\n\nلا توجد باقات متاحة حالياً.",
            parse_mode="Markdown",
            reply_markup=_back_main(),
        )
        return ConversationHandler.END

    kb = []
    for p in plans:
        label = f"{p['name']} — {p['price']}$ | {p['daily_limit']} عملية/يوم | {p['duration_days']} يوم"
        kb.append([InlineKeyboardButton(label, callback_data=f"sub_plan_{p['id']}")])
    kb.append([InlineKeyboardButton("🔙 رجوع", callback_data="main_menu")])

    text = f"📦 *اختر الباقة المناسبة:*{sub_text}"
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")
    return SUB_SELECT_METHOD


async def sub_select_plan(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    plan_id = int(query.data.replace("sub_plan_", ""))
    plan = db.get_plan_by_id(plan_id)
    if not plan:
        await query.edit_message_text("❌ الباقة غير موجودة", reply_markup=_back_sub())
        return ConversationHandler.END

    context.user_data["sub_plan"] = plan

    methods = db.get_active_payment_settings()
    if not methods:
        await query.edit_message_text(
            "❌ لا توجد طرق دفع متاحة حالياً\nيرجى التواصل مع الإدارة.",
            parse_mode="Markdown",
            reply_markup=_back_sub(),
        )
        return ConversationHandler.END

    kb = []
    for m in methods:
        kb.append([InlineKeyboardButton(m["display_name"], callback_data=f"sub_method_{m['method']}")])
    kb.append([InlineKeyboardButton("🔙 رجوع", callback_data="sub_menu")])

    text = (
        f"💳 *اختر طريقة الدفع*\n\n"
        f"📦 الباقة: *{plan['name']}*\n"
        f"💰 السعر: `{plan['price']}$`\n"
        f"📊 الحد اليومي: `{plan['daily_limit']}` عملية\n"
        f"⏳ المدة: `{plan['duration_days']}` يوم"
    )
    await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")
    return SUB_SELECT_METHOD


async def sub_method_usdt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    plan = context.user_data.get("sub_plan", {})
    setting = db.get_payment_setting("usdt")
    if not setting or not setting.get("address"):
        await query.edit_message_text(
            "❌ لم يتم إعداد عنوان USDT بعد\nيرجى التواصل مع الإدارة.",
            parse_mode="Markdown",
            reply_markup=_back_sub(),
        )
        return ConversationHandler.END

    context.user_data["sub_method"] = "usdt"
    context.user_data["sub_setting"] = dict(setting)
    instr = setting.get("instructions") or ""
    
    text = (
        f"💎 *الدفع عبر USDT (TRC20)*\n\n"
        f"📦 الباقة: *{plan.get('name','')}*\n"
        f"💰 المبلغ: `{plan.get('price',0)}$`\n\n"
        f"📬 *عنوان المحفظة:*\n`{setting['address']}`\n\n"
        f"{instr}\n\n"
        f"📷 بعد الإرسال، أرسل *صورة إثبات التحويل:*"
    )
    kb = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data="sub_menu")]])
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=kb)
    return SUB_CASH_PROOF


async def handle_sub_proof(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """دالة مؤقتة لاستقبال الصورة حتى لا ينكسر الكود"""
    query = update.message
    await query.reply_text("✅ تم استقبال إثبات الدفع، سيتم مراجعته من قبل الإدارة.")
    return ConversationHandler.END


def get_handlers():
    """هذه الدالة التي يبحث عنها ملف main.py لتشغيل نظام الاشتراكات"""
    conv_handler = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(sub_menu, pattern="^sub_menu$")
        ],
        states={
            SUB_SELECT_METHOD: [
                CallbackQueryHandler(sub_select_plan, pattern="^sub_plan_"),
                CallbackQueryHandler(sub_method_usdt, pattern="^sub_method_usdt")
            ],
            SUB_CASH_PROOF: [
                MessageHandler(filters.PHOTO, handle_sub_proof),
                CallbackQueryHandler(sub_menu, pattern="^sub_menu$")
            ]
        },
        fallbacks=[
            CallbackQueryHandler(sub_menu, pattern="^sub_menu$")
        ],
        per_message=False
    )
    return [conv_handler]
