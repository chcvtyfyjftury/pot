import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes, CallbackQueryHandler, MessageHandler, filters
)

from src.database import queries as db
from src.middlewares.auth import require_access
from src.services.adjust import send_adj

logger = logging.getLogger(__name__)


def _back_kb(data: str = "adj_menu") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data=data)]])


def _events_kb(game_id: int, include_back: bool = True) -> InlineKeyboardMarkup:
    events = db.get_adj_events(game_id)
    kb = []
    for ev in events:
        display = ev["display_name"] if ev["display_name"] else ev["event_name"]
        kb.append([InlineKeyboardButton(f"📊 {display}", callback_data=f"adj_send_{ev['id']}")])
    kb.append([InlineKeyboardButton("✨ حدث مخصص", callback_data="adj_custom")])
    if include_back:
        kb.append([InlineKeyboardButton("🔙 رجوع", callback_data="adj_menu")])
    return InlineKeyboardMarkup(kb)


@require_access
async def adj_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data.pop("adj_state", None)
    kb = [
        [InlineKeyboardButton("🎮 عرض الألعاب", callback_data="adj_show_games")],
        [InlineKeyboardButton("🔍 بحث", callback_data="adj_search_game")],
        [InlineKeyboardButton("🔙 رجوع", callback_data="main_menu")],
    ]
    await query.edit_message_text("📊 *Adjust*", reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")


async def adj_show_games(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    games = db.get_all_games_adj()
    kb = [[InlineKeyboardButton(f"{g['emoji']} {g['display_name']}", callback_data=f"adjgame_{g['id']}")] for g in games]
    kb.append([InlineKeyboardButton("🔙 رجوع", callback_data="adj_menu")])
    await query.edit_message_text("🎮 *اختر اللعبة*", reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")


async def adj_search_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data["adj_state"] = "search"
    await query.edit_message_text("🔍 *أدخل اسم اللعبة*", parse_mode="Markdown")


async def adj_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    gid = int(query.data.replace("adjgame_", ""))
    game = db.get_game_adj_by_id(gid)
    if not game:
        await query.edit_message_text("❌ خطأ: اللعبة غير موجودة", parse_mode="Markdown")
        return

    context.user_data.update({
        "adj_game_id": game["id"],
        "adj_game_name": game["display_name"],
        "adj_app_token": game["app_token"],
        "adj_game": dict(game),
        "adj_state": "adid",
    })

    platform = db.get_user_platform(query.from_user.id)
    if platform == "ios":
        await query.edit_message_text(
            f"{game['emoji']} *{game['display_name']}*\n\n🍎 *iOS*\n📱 *أدخل IDFA:*\nمثال: `12345678-1234-1234-1234-123456789012`\n\n⚠️ *مطلوب لـ Adjust (سيتم استخدامه كـ GPS ADID)*",
            parse_mode="Markdown",
        )
    else:
        await query.edit_message_text(
            f"{game['emoji']} *{game['display_name']}*\n\n🤖 *Android*\n📱 *أدخل GPS ADID:*\nمثال: `8de8604d-1318-4fd0-907c-402ea9de2529`\n\n⚠️ *مطلوب لـ Android*",
            parse_mode="Markdown",
        )


async def adj_text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """يوجه رسائل النص حسب حالة المستخدم (search / adid / custom_level)."""
    state = context.user_data.get("adj_state")
    text = update.message.text.strip()

    if state == "search":
        games = db.search_adj_games(text)
        if not games:
            await update.message.reply_text("❌ *لا يوجد*", parse_mode="Markdown")
            return
        kb = [[InlineKeyboardButton(f"{g['emoji']} {g['display_name']}", callback_data=f"adjgame_{g['id']}")] for g in games]
        kb.append([InlineKeyboardButton("🔙 رجوع", callback_data="adj_menu")])
        await update.message.reply_text("✅ *نتائج البحث*", reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")

    elif state == "adid":
        context.user_data["adj_gps"] = text
        context.user_data.pop("adj_state", None)
        game_id = context.user_data.get("adj_game_id")
        events = db.get_adj_events(game_id)
        if not events:
            kb = [[InlineKeyboardButton("🔙 رجوع", callback_data="adj_menu")]]
            await update.message.reply_text(
                f"❌ *لا توجد أحداث لهذه اللعبة*\n\n📊 *{context.user_data.get('adj_game_name', '')}*",
                reply_markup=InlineKeyboardMarkup(kb),
                parse_mode="Markdown",
            )
            return
        await update.message.reply_text(
            f"🎯 *اختر الحدث*\n📊 {context.user_data.get('adj_game_name', '')}",
            reply_markup=_events_kb(game_id),
            parse_mode="Markdown",
        )

    elif state == "custom_level":
        digits = ''.join(filter(str.isdigit, text))
        if not digits:
            await update.message.reply_text(
                "❌ الرجاء إدخال رقم صحيح للفل (مثال: 45)",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔙 إلغاء", callback_data=f"adj_resend_{context.user_data.get('adj_game_id', '')}")]
                ]),
            )
            return
        context.user_data.pop("adj_state", None)
        event_token = digits
        app_token = context.user_data.get("adj_app_token", "")
        gps = context.user_data.get("adj_gps", "")
        uid = update.effective_user.id
        platform = db.get_user_platform(uid)
        proxy_row = db.get_proxy_for_user(uid)
        await update.message.reply_text("📤 *جاري الإرسال فوراً...*", parse_mode="Markdown")
        status, resp = send_adj(
            app_token=app_token,
            event_token=event_token,
            gps_adid=gps,
            proxy=dict(proxy_row) if proxy_row else None,
            platform=platform,
            idfa=gps,
        )
        db.increment_requests(uid)
        if status == 200:
            result = "✅ *تم الإرسال بنجاح!*"
        else:
            result = f"❌ *فشل الإرسال* (HTTP {status})"
        kb = [
            [InlineKeyboardButton("🎯 حدث اخر", callback_data=f"adj_resend_{context.user_data.get('adj_game_id')}")],
            [InlineKeyboardButton("🔙 رجوع", callback_data="adj_menu")],
        ]
        await update.message.reply_text(
            f"{result}\n🔢 *رقم اللفل:* {digits}\n🎮 *اللعبة:* {context.user_data.get('adj_game_name', '')}",
            reply_markup=InlineKeyboardMarkup(kb),
            parse_mode="Markdown",
        )


@require_access
async def adj_send(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    event_id_str = query.data.replace("adj_send_", "")
    try:
        event_id = int(event_id_str)
    except ValueError:
        await query.edit_message_text("❌ خطأ في معرف الحدث", parse_mode="Markdown")
        return

    event = db.get_adj_event_by_id(event_id)
    if not event:
        await query.edit_message_text("❌ حدث غير موجود", parse_mode="Markdown")
        return

    event_token = event["event_token"]
    display_name = event["display_name"] if event["display_name"] else event_token

    app_token = context.user_data.get("adj_app_token", "")
    gps = context.user_data.get("adj_gps", "")
    uid = query.from_user.id
    platform = db.get_user_platform(uid)
    proxy_row = db.get_proxy_for_user(uid)

    await query.edit_message_text("📤 *جاري الإرسال...*", parse_mode="Markdown")

    status, resp = send_adj(
        app_token=app_token,
        event_token=event_token,
        gps_adid=gps,
        proxy=dict(proxy_row) if proxy_row else None,
        platform=platform,
        idfa=context.user_data.get("adj_gps"),
        level=event.get("level_value"),
    )

    db.increment_requests(uid)

    if status == 200:
        result = "✅ *تم الإرسال بنجاح!*"
    else:
        result = f"❌ *فشل الإرسال* (HTTP {status})"

    kb = [
        [InlineKeyboardButton("🎯 حدث اخر", callback_data=f"adj_resend_{context.user_data.get('adj_game_id')}")],
        [InlineKeyboardButton("🔙 رجوع", callback_data="adj_menu")],
    ]
    await query.message.reply_text(
        f"{result}\n📝 *الحدث:* {display_name}\n🎮 *اللعبة:* {context.user_data.get('adj_game_name', '')}",
        reply_markup=InlineKeyboardMarkup(kb),
        parse_mode="Markdown",
    )


@require_access
async def adj_resend(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if not query.data or not query.data.startswith("adj_resend_"):
        await query.edit_message_text("❌ خطأ في البيانات", parse_mode="Markdown")
        return

    try:
        game_id = int(query.data.replace("adj_resend_", ""))
    except ValueError:
        await query.edit_message_text("❌ خطأ في معرف اللعبة", parse_mode="Markdown")
        return

    game = db.get_game_adj_by_id(game_id)
    if not game:
        await query.edit_message_text("❌ اللعبة غير موجودة", parse_mode="Markdown")
        return

    context.user_data["adj_game_id"] = game_id
    context.user_data["adj_game_name"] = game["display_name"]
    context.user_data["adj_app_token"] = game["app_token"]
    context.user_data["adj_game"] = dict(game)

    events = db.get_adj_events(game_id)
    if not events:
        kb = [[InlineKeyboardButton("🔙 رجوع", callback_data="adj_menu")]]
        await query.edit_message_text(
            f"❌ *لا توجد أحداث لهذه اللعبة*\n📊 {game['display_name']}",
            reply_markup=InlineKeyboardMarkup(kb),
            parse_mode="Markdown",
        )
        return

    await query.edit_message_text(
        f"🎯 *اختر الحدث*\n📊 {context.user_data['adj_game_name']}",
        reply_markup=_events_kb(game_id),
        parse_mode="Markdown",
    )


@require_access
async def adj_custom(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data["adj_state"] = "custom_level"
    await query.edit_message_text(
        "✨ *لفل مخصص*\n\nأدخل رقم اللفل المطلوب (مثال: 45 أو 46) وسيُرسل الحدث فوراً:",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 إلغاء", callback_data=f"adj_resend_{context.user_data.get('adj_game_id', '')}")]
        ]),
    )


def get_handlers():
    return [
        CallbackQueryHandler(adj_menu, pattern="^adj_menu$"),
        CallbackQueryHandler(adj_show_games, pattern="^adj_show_games$"),
        CallbackQueryHandler(adj_search_game, pattern="^adj_search_game$"),
        CallbackQueryHandler(adj_game, pattern=r"^adjgame_\d+$"),
        CallbackQueryHandler(adj_send, pattern=r"^adj_send_"),
        CallbackQueryHandler(adj_resend, pattern=r"^adj_resend_\d+$"),
        CallbackQueryHandler(adj_custom, pattern="^adj_custom$"),
        MessageHandler(filters.TEXT & ~filters.COMMAND, adj_text_handler, block=False),
    ]
