import re
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes, ConversationHandler, CallbackQueryHandler, MessageHandler, filters
)

from src.database import queries as db
from src.middlewares.auth import require_access
from src.services.appsflyer import send_af

logger = logging.getLogger(__name__)

AF_GAID, AF_IDFA, AF_IDFV, AF_UID, AF_UID_IOS, AF_CUSTOM_LEVEL = range(100, 106)


def _result_text(status: int, resp: str) -> str:
    if status == 200:
        return "✅ *تم الإرسال بنجاح!*"
    return f"❌ *فشل الإرسال*\nالكود: `{status}`\n`{resp[:200]}`"


def _back_kb(data: str = "af_menu") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data=data)]])


def _events_kb(game_id: int, include_back: bool = True) -> InlineKeyboardMarkup:
    events = db.get_af_events(game_id)
    kb = []
    for ev in events:
        kb.append([InlineKeyboardButton(f"📊 {ev['display_name']}", callback_data=f"af_send_{ev['id']}")])
    kb.append([InlineKeyboardButton("✨ حدث مخصص", callback_data="af_custom_event")])
    kb.append([InlineKeyboardButton("🔢 لفل مخصص", callback_data="af_custom_level")])
    if include_back:
        kb.append([InlineKeyboardButton("🔙 رجوع", callback_data="af_menu")])
    return InlineKeyboardMarkup(kb)


@require_access
async def af_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    games = db.get_all_games_af()
    if not games:
        await query.edit_message_text(
            "❌ *لا توجد ألعاب AppsFlyer*",
            parse_mode="Markdown",
            reply_markup=_back_kb("main_menu"),
        )
        return ConversationHandler.END

    kb = [
        [InlineKeyboardButton(f"{g['emoji']} {g['display_name']}", callback_data=f"af_game_{g['id']}")]
        for g in games
    ]
    kb.append([InlineKeyboardButton("🔙 رجوع", callback_data="main_menu")])
    await query.edit_message_text(
        "📱 *اختر اللعبة - AppsFlyer*",
        reply_markup=InlineKeyboardMarkup(kb),
        parse_mode="Markdown",
    )
    return ConversationHandler.END


@require_access
async def af_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    game_id = int(query.data.replace("af_game_", ""))
    game = db.get_game_af_by_id(game_id)
    if not game:
        await query.edit_message_text("❌ خطأ: اللعبة غير موجودة", parse_mode="Markdown")
        return ConversationHandler.END

    context.user_data["af_game_id"] = game_id
    context.user_data["af_game"] = dict(game)
    uid = update.effective_user.id
    platform = db.get_user_platform(uid)

    if platform == "ios":
        await query.edit_message_text(
            f"🍎 *iOS - AppsFlyer*\n🎮 {game['display_name']}\n\n📱 *أدخل IDFA:*\nمثال: `12345678-1234-1234-1234-123456789012`",
            parse_mode="Markdown",
        )
        return AF_IDFA
    else:
        await query.edit_message_text(
            f"🤖 *Android - AppsFlyer*\n🎮 {game['display_name']}\n\n📱 *أدخل GAID:*\nمثال: `8de8604d-1318-4fd0-907c-402ea9de2529`",
            parse_mode="Markdown",
        )
        return AF_GAID


async def af_gaid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    gaid = update.message.text.strip()
    context.user_data["af_gaid"] = gaid
    await update.message.reply_text(
        "📱 *أدخل AF UID (AppsFlyer ID):*\nمثال: `1777884483`",
        parse_mode="Markdown",
    )
    return AF_UID


async def af_idfa(update: Update, context: ContextTypes.DEFAULT_TYPE):
    idfa = update.message.text.strip()
    context.user_data["af_idfa"] = idfa
    await update.message.reply_text(
        "🍎 *أدخل IDFV:*\nمثال: `12345678-1234-1234-1234-123456789012`",
        parse_mode="Markdown",
    )
    return AF_IDFV


async def af_idfv(update: Update, context: ContextTypes.DEFAULT_TYPE):
    idfv = update.message.text.strip()
    context.user_data["af_idfv"] = idfv
    await update.message.reply_text(
        "📱 *أدخل AF UID (AppsFlyer ID):*\nمثال: `1777884483`",
        parse_mode="Markdown",
    )
    return AF_UID_IOS


async def af_uid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["af_uid"] = update.message.text.strip()
    return await _show_af_events(update, context)


async def af_uid_ios(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["af_uid"] = update.message.text.strip()
    return await _show_af_events(update, context)


async def _show_af_events(update: Update, context: ContextTypes.DEFAULT_TYPE):
    game_id = context.user_data.get("af_game_id")
    game = context.user_data.get("af_game", {})
    events = db.get_af_events(game_id)
    if not events:
        await update.message.reply_text(
            "❌ *لا توجد أحداث لهذه اللعبة*",
            parse_mode="Markdown",
            reply_markup=_back_kb("af_menu"),
        )
        return ConversationHandler.END

    await update.message.reply_text(
        f"🎯 *اختر الحدث*\n🎮 {game.get('display_name', '')}",
        reply_markup=_events_kb(game_id),
        parse_mode="Markdown",
    )
    return ConversationHandler.END


@require_access
async def af_send(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    event_id = int(query.data.replace("af_send_", ""))

    game_id = context.user_data.get("af_game_id")
    if not game_id:
        await query.edit_message_text(
            "❌ *انتهت الجلسة. ابدأ من جديد.*",
            parse_mode="Markdown",
            reply_markup=_back_kb("af_menu"),
        )
        return

    events = db.get_af_events(game_id)
    event = next((e for e in events if e["id"] == event_id), None)
    if not event:
        await query.edit_message_text("❌ خطأ: الحدث غير موجود", parse_mode="Markdown")
        return

    game = context.user_data.get("af_game", {})
    uid = update.effective_user.id
    platform = db.get_user_platform(uid)
    proxy_row = db.get_proxy_for_user(uid)

    await query.edit_message_text("🔄 *جاري الإرسال...*", parse_mode="Markdown")

    status, resp = send_af(
        pkg=game.get("package", ""),
        dev_key=game.get("dev_key", ""),
        gaid=context.user_data.get("af_gaid", ""),
        af_uid=context.user_data.get("af_uid", ""),
        event_name=event["event_name"],
        revenue=event.get("revenue"),
        proxy=dict(proxy_row) if proxy_row else None,
        platform=platform,
        idfa=context.user_data.get("af_idfa"),
        idfv=context.user_data.get("af_idfv"),
        level=event.get("level_value"),
    )

    db.increment_requests(uid)

    result_text = _result_text(status, resp)
    kb = [
        [InlineKeyboardButton("🎯 حدث آخر", callback_data=f"af_game_{game.get('id')}")],
        [InlineKeyboardButton("🔙 قائمة الألعاب", callback_data="af_menu")],
        [InlineKeyboardButton("🏠 القائمة الرئيسية", callback_data="main_menu")],
    ]
    await query.edit_message_text(
        f"{result_text}\n\n📝 *الحدث:* {event['display_name']}\n🎮 *اللعبة:* {game.get('display_name', '')}",
        reply_markup=InlineKeyboardMarkup(kb),
        parse_mode="Markdown",
    )


@require_access
async def af_custom_event(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data["af_custom_state"] = "event_name"
    await query.edit_message_text(
        "✨ *حدث مخصص*\n\n📝 *أدخل اسم الحدث:*\nمثال: `af_level_50` أو `Complete_Level`",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 إلغاء", callback_data=f"af_game_{context.user_data.get('af_game_id', '')}")]
        ]),
    )
    return AF_CUSTOM_LEVEL


@require_access
async def af_custom_level(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data["af_custom_state"] = "level"
    await query.edit_message_text(
        "✨ *لفل مخصص*\n\n"
        "أدخل رقم اللفل المطلوب (مثال: 45 أو 46) وسيُرسل الحدث فوراً:",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 إلغاء", callback_data=f"af_game_{context.user_data.get('af_game_id', '')}")]
        ]),
    )
    return AF_CUSTOM_LEVEL


async def af_custom_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    state = context.user_data.get("af_custom_state")
    text = update.message.text.strip()
    game_id = context.user_data.get("af_game_id")
    game = context.user_data.get("af_game", {})
    cancel_kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 إلغاء", callback_data=f"af_game_{game_id}")]
    ])

    if state == "event_name":
        if not text:
            await update.message.reply_text("❌ الرجاء إدخال اسم صحيح", reply_markup=cancel_kb)
            return AF_CUSTOM_LEVEL
        context.user_data.pop("af_custom_state", None)

        uid = update.effective_user.id
        platform = db.get_user_platform(uid)
        proxy_row = db.get_proxy_for_user(uid)

        await update.message.reply_text("📤 *جاري الإرسال فوراً...*", parse_mode="Markdown")
        status, resp = send_af(
            pkg=game.get("package", ""),
            dev_key=game.get("dev_key", ""),
            gaid=context.user_data.get("af_gaid", ""),
            af_uid=context.user_data.get("af_uid", ""),
            event_name=text,
            revenue=None,
            proxy=dict(proxy_row) if proxy_row else None,
            platform=platform,
            idfa=context.user_data.get("af_idfa"),
            idfv=context.user_data.get("af_idfv"),
            level=None,
        )
        db.increment_requests(uid)
        result_text = _result_text(status, resp)
        kb = [
            [InlineKeyboardButton("🎯 حدث آخر", callback_data=f"af_game_{game_id}")],
            [InlineKeyboardButton("🔙 قائمة الألعاب", callback_data="af_menu")],
            [InlineKeyboardButton("🏠 القائمة الرئيسية", callback_data="main_menu")],
        ]
        await update.message.reply_text(
            f"{result_text}\n\n📝 *الحدث:* `{text}`\n🎮 *اللعبة:* {game.get('display_name', '')}",
            reply_markup=InlineKeyboardMarkup(kb),
            parse_mode="Markdown",
        )
        return ConversationHandler.END

    elif state == "level":
        digits = ''.join(filter(str.isdigit, text))
        if not digits:
            await update.message.reply_text(
                "❌ الرجاء إدخال رقم صحيح للفل (مثال: 45)",
                reply_markup=cancel_kb,
            )
            return AF_CUSTOM_LEVEL

        context.user_data.pop("af_custom_state", None)
        pkg = game.get("package", "")
        dev_key = game.get("dev_key", "")
        if not pkg or not dev_key:
            await update.message.reply_text("❌ خطأ: بيانات اللعبة غير موجودة، الرجاء إعادة اختيار اللعبة", reply_markup=cancel_kb)
            return ConversationHandler.END

        # بناء اسم الحدث من أول حدث مخزّن للعبة مع استبدال الرقم
        events = db.get_af_events(game_id) if game_id else []
        if events:
            base_event = events[0]["event_name"]
            if re.search(r'\d+', base_event):
                event_name = re.sub(r'\d+', digits, base_event)
            else:
                event_name = f"af_level_{digits}_achieved"
        else:
            event_name = f"af_level_{digits}_achieved"

        uid = update.effective_user.id
        platform = db.get_user_platform(uid)
        proxy_row = db.get_proxy_for_user(uid)

        await update.message.reply_text("📤 *جاري الإرسال فوراً...*", parse_mode="Markdown")
        status, resp = send_af(
            pkg=pkg,
            dev_key=dev_key,
            gaid=context.user_data.get("af_gaid", ""),
            af_uid=context.user_data.get("af_uid", ""),
            event_name=event_name,
            revenue=None,
            proxy=dict(proxy_row) if proxy_row else None,
            platform=platform,
            idfa=context.user_data.get("af_idfa"),
            idfv=context.user_data.get("af_idfv"),
            level=int(digits) if digits.isdigit() else None,
        )
        db.increment_requests(uid)
        result_text = _result_text(status, resp)
        kb = [
            [InlineKeyboardButton("🎯 حدث آخر", callback_data=f"af_game_{game_id}")],
            [InlineKeyboardButton("🔙 قائمة الألعاب", callback_data="af_menu")],
            [InlineKeyboardButton("🏠 القائمة الرئيسية", callback_data="main_menu")],
        ]
        await update.message.reply_text(
            f"{result_text}\n\n📝 *الحدث:* `{event_name}`\n🔢 *رقم اللفل:* {digits}\n🎮 *اللعبة:* {game.get('display_name', '')}",
            reply_markup=InlineKeyboardMarkup(kb),
            parse_mode="Markdown",
        )
        return ConversationHandler.END

    return ConversationHandler.END


def get_handlers():
    conv = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(af_menu, pattern="^af_menu$"),
            CallbackQueryHandler(af_game, pattern=r"^af_game_\d+$"),
        ],
        states={
            AF_GAID:        [MessageHandler(filters.TEXT & ~filters.COMMAND, af_gaid)],
            AF_IDFA:        [MessageHandler(filters.TEXT & ~filters.COMMAND, af_idfa)],
            AF_IDFV:        [MessageHandler(filters.TEXT & ~filters.COMMAND, af_idfv)],
            AF_UID:         [MessageHandler(filters.TEXT & ~filters.COMMAND, af_uid)],
            AF_UID_IOS:     [MessageHandler(filters.TEXT & ~filters.COMMAND, af_uid_ios)],
            AF_CUSTOM_LEVEL:[MessageHandler(filters.TEXT & ~filters.COMMAND, af_custom_input)],
        },
        fallbacks=[CallbackQueryHandler(af_menu, pattern="^af_menu$")],
        allow_reentry=True,
    )
    return [
        conv,
        CallbackQueryHandler(af_send, pattern=r"^af_send_\d+$"),
        CallbackQueryHandler(af_custom_event, pattern="^af_custom_event$"),
        CallbackQueryHandler(af_custom_level, pattern="^af_custom_level$"),
    ]
