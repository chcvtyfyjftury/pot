import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes, ConversationHandler, CallbackQueryHandler, MessageHandler, filters
)

from src.config import ADMIN_IDS
from src.database import queries as db
from src.middlewares.auth import allow_free_access

logger = logging.getLogger(__name__)

SUB_SELECT_METHOD, SUB_CASH_PROOF = range(700, 702)


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


async def handle_sub_method_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """دالة موحدة ومضمونة تستقبل ضغطات كافة طرق الدفع (USDT والكاش) وتوجههم لمرحلة الإثبات"""
    query = update.callback_query
    await query.answer()

    method_type = query.data.replace("sub_method_", "")
    plan = context.user_data.get("sub_plan", {})
    setting = db.get_payment_setting(method_type)
    
    if not setting or not setting.get("address"):
        await query.edit_message_text(
            f"❌ لم يتم إعداد بيانات الدفع لـ {method_type} بعد\nيرجى التواصل مع الإدارة.",
            parse_mode="Markdown",
            reply_markup=_back_sub(),
        )
        return ConversationHandler.END

    context.user_data["sub_method"] = method_type
    context.user_data["sub_setting"] = dict(setting)
    instr = setting.get("instructions") or ""
    display_name = setting.get("display_name", method_type.replace("_", " ").title())
    
    text = (
        f"💳 *الدفع عبر {display_name}*\n\n"
        f"📦 الباقة: *{plan.get('name','')}*\n"
        f"💰 السعر: `{plan.get('price',0)}$`\n\n"
        f"📌 *تفاصيل الحساب / العنوان أو الرقم:*\n`{setting['address']}`\n\n"
        f"{instr}\n\n"
        f"📷 بعد إتمام التحويل، يرجى إرسال *صورة لقطة شاشة (Screenshot) كإثبات للعملية:*"
    )
    kb = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data="sub_menu")]])
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=kb)
    return SUB_CASH_PROOF


async def handle_sub_proof(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    uid = user.id
    
    if not update.message.photo:
        await update.message.reply_text("❌ عذراً، يرجى إرسال الإثبات كصورة حصراً.")
        return SUB_CASH_PROOF

    photo = update.message.photo[-1]
    plan = context.user_data.get("sub_plan", {})
    method = context.user_data.get("sub_method", "unknown")
    
    await update.message.reply_text(
        "✅ تم استقبال إثبات الدفع بنجاح.\n⏳ جاري مراجعته من قبل الإدارة لتفعيل باقتك في أقرب وقت ممكن."
    )
    
    username_clean = f"@{user.username}" if user.username else user.full_name
    admin_text = (
        f"🚨 *طلب اشتراك جديد بانتظار المراجعة* 🚨\n\n"
        f"👤 المستخدِم: {username_clean}\n"
        f"🆔 آيدي الحساب: `{uid}`\n"
        f"📦 الباقة المطلوبة: *{plan.get('name', 'غير معروف')}*\n"
        f"💰 السعر: `{plan.get('price', 0)}$`\n"
        f"💳 طريقة الدفع: *{method.upper()}*\n"
    )
    
    kb = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ قبول وتفعيل", callback_data=f"admin_sub_approve_{uid}_{plan.get('id', 0)}"),
            InlineKeyboardButton("❌ رفض الطلب", callback_data=f"admin_sub_reject_{uid}")
        ]
    ])
    
    for admin_id in ADMIN_IDS:
        try:
            await context.bot.send_photo(
                chat_id=admin_id,
                photo=photo.file_id,
                caption=admin_text,
                reply_markup=kb,
                parse_mode="Markdown"
            )
        except Exception as e:
            logger.error(f"Failed to send sub proof to admin {admin_id}: {e}")
            
    return ConversationHandler.END


# =====================================================================
# 📊 نظام معالجة أزرار الأدمن (خارج الـ ConversationHandler لضمان عملها)
# =====================================================================
async def admin_sub_buttons_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id

    if user_id not in ADMIN_IDS:
        await query.answer("❌ ليس لديك صلاحية للتحكم بالاشتراكات.", show_alert=True)
        return

    await query.answer()
    data = query.data

    if data.startswith("admin_sub_approve_"):
        # تفكيك البيانات: admin_sub_approve_{uid}_{plan_id}
        parts = data.split("_")
        target_uid = int(parts[3])
        plan_id = int(parts[4])
        
        plan = db.get_plan_by_id(plan_id)
        if plan:
            # تفعيل الاشتراك في قاعدة البيانات
            db.add_or_update_subscription(target_uid, plan) # تأكد أن هذا اسم دالة الحفظ لديك بالـ DB
            
            # إرسال إشعار للمستخدم المستهدف بنجاح التفعيل
            try:
                await context.bot.send_message(
                    chat_id=target_uid,
                    text=f"🎉 *تهانينا\! تم قبول طلب التحويل وتفعيل باقة {plan['name']} بنجاح\.*",
                    parse_mode="MarkdownV2"
                )
            except Exception:
                pass
                
            await query.edit_message_caption(
                caption=query.message.caption + f"\n\n✅ *تم قبول الطلب وتفعيل الباقة بواسطة المشرف\.*",
                reply_markup=None,
                parse_mode="Markdown"
            )

    elif data.startswith("admin_sub_reject_"):
        target_uid = int(data.split("_")[3])
        
        # إشعار المستخدم بالرفض
        try:
            await context.bot.send_message(
                chat_id=target_uid,
                text="❌ *عذراً، تم رفض طلب الاشتراك لعدم صحة بيانات التحويل، يرجى مراجعة الدعم الفني\.*",
                parse_mode="MarkdownV2"
            )
        except Exception:
            pass
            
        await query.edit_message_caption(
            caption=query.message.caption + f"\n\n❌ *تم رفض هذا الطلب وإلغاؤه بواسطة المشرف\.*",
            reply_markup=None,
            parse_mode="Markdown"
        )


def get_handlers():
    conv_handler = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(sub_menu, pattern="^sub_menu$")
        ],
        states={
            SUB_SELECT_METHOD: [
                CallbackQueryHandler(sub_select_plan, pattern="^sub_plan_"),
                CallbackQueryHandler(handle_sub_method_selection, pattern="^sub_method_") # يلتقط أي وسيلة دفع ديناميكياً
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
    
    # معالج أزرار الأدمن يوضع كمستمع عام منفصل ليعمل بشكل مستقل عن محادثات المستخدمين
    admin_buttons_handler = CallbackQueryHandler(admin_sub_buttons_handler, pattern="^admin_sub_(approve|reject)_")
    
    return [conv_handler, admin_buttons_handler]
