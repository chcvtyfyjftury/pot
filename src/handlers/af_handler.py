import re
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes, CallbackQueryHandler, MessageHandler, filters
)

from src.database import queries as db
from src.middlewares.auth import require_access
from src.services.appsflyer import send_af

logger = logging.getLogger(__name__)


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


def _result_text(status: int, resp: str) -> str:
    if status == 200:
        return "✅ *تم الإرسال بنجاح!*"
    return f"❌ *فشل الإرسال*\nالكود: `{status}`\n`{resp[:200]}`"


@require_access
async def af_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data.pop("af_state", None)
    games = db.get_all_games_af()
    if not games:
        await query.edit_message_text(
            "❌ *لا توجد ألعاب AppsFlyer*",
            parse_mode="Markdown",
            reply_markup=_back_kb("main_menu"),
        )
        return
    kb = [
        [InlineKeyboardButton(f"{g['emoji']} {g['display_name']}", callback_data=f"afgame_{g['id']}")]
        for g in games
    ]
    kb.append([InlineKeyboardButton("🔙 رجوع", callback_data="main_menu")])
    await query.edit_message_text(
        "📱 *اختر اللعبة - AppsFlyer*",
        reply_markup=InlineKeyboardMarkup(kb),
        parse_mode="Markdown",
    )


async def af_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    gid = int(query.data.replace("afgame_", ""))
    game = db.get_game_af_by_id(gid)
    if not game:
        await query.edit_message_text("❌ خطأ: اللعبة غير موجودة", parse_mode="Markdown")
        return

    context.user_data["af_game_id"] = gid
    context.user_data["af_game_name"] = game["display_name"]
    context.user_data["af_game"] = dict(game)

    platform = db.get_user_platform(query.from_user.id)
    if platform == "ios":
        context.user_data["af_state"] = "idfa"
        await query.edit_message_text(
            f"{game['emoji']} *{game['display_name']}*\n\n🍎 *iOS - AppsFlyer*\n📱 *أدخل IDFA:*\nمثال: `12345678-1234-1234-1234-123456789012`",
            parse_mode="Markdown",
        )
    else:
        context.user_data["af_state"] = "gaid"
        await query.edit_message_text(
            f"{game['emoji']} *{game['display_name']}*\n\n🤖 *Android - AppsFlyer*\n📱 *أدخل GAID:*\nمثال: `8de8604d-1318-4fd0-907c-402ea9de2529`",
            parse_mode="Markdown",
        )


async def af_text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """يوجه رسائل النص حسب حالة المستخدم (gaid / idfa / idfv / uid / custom_event / custom_level)."""
    state = context.user_data.get("af_state")
    if not state:
        return
    text = update.message.text.strip()
    game = context.user_data.get("af_game", {})
    game_id = context.user_data.get("af_game_id")
    game_name = context.user_data.get("af_game_name", "")
    uid = update.effective_user.id
    platform = db.get_user_platform(uid)
    proxy_row = db.get_proxy_for_user(uid)
    proxy = dict(proxy_row) if proxy_row else None

    if state == "gaid":
        context.user_data["af_gaid"] = text
        context.user_data["af_state"] = "uid"
        await update.message.reply_text(
            "📱 *أدخل AF UID (AppsFlyer ID):*\nمثال: `1777884483`",
            parse_mode="Markdown",
        )

    elif state == "idfa":
        context.user_data["af_idfa"] = text
        context.user_data["af_state"] = "idfv"
        await update.message.reply_text(
            "🍎 *أدخل IDFV:*\nمثال: `12345678-1234-1234-1234-123456789012`",
            parse_mode="Markdown",
        )

    elif state == "idfv":
        context.user_data["af_idfv"] = text
        context.user_data["af_state"] = "uid_ios"
        await update.message.reply_text(
            "📱 *أدخل AF UID (AppsFlyer ID):*\nمثال: `1777884483`",
            parse_mode="Markdown",
        )

    elif state == "uid":
        context.user_data["af_uid"] = text
        context.user_data.pop("af_state", None)
        events = db.get_af_events(game_id)
        if not events:
            await update.message.reply_text(
                f"❌ *لا توجد أحداث لهذه اللعبة*\n📱 {game_name}",
                parse_mode="Markdown",
                reply_markup=_back_kb("af_menu"),
            )
            return
        await update.message.reply_text(
            f"🎯 *اختر الحدث*\n📱 {game_name}",
            reply_markup=_events_kb(game_id),
            parse_mode="Markdown",
        )

    elif state == "uid_ios":
        context.user_data["af_uid"] = text
        context.user_data.pop("af_state", None)
        events = db.get_af_events(game_id)
        if not events:
            await update.message.reply_text(
                f"❌ *لا توجد أحداث لهذه اللعبة*\n📱 {game_name}",
                parse_mode="Markdown",
                reply_markup=_back_kb("af_menu"),
            )
            return
        await update.message.reply_text(
            f"🎯 *اختر الحدث*\n📱 {game_name}",
            reply_markup=_events_kb(game_id),
            parse_mode="Markdown",
        )

    elif state == "custom_event":
        if not text:
            await update.message.reply_text("❌ الرجاء إدخال اسم صحيح")
            return
        context.user_data.pop("af_state", None)
        await update.message.reply_text("📤 *جاري الإرسال فوراً...*", parse_mode="Markdown")
        status, resp = send_af(
            pkg=game.get("package", ""),
            dev_key=game.get("dev_key", ""),
            gaid=context.user_data.get("af_gaid", ""),
            af_uid=context.user_data.get("af_uid", ""),
            event_name=text,
            revenue=None,
            proxy=proxy,
            platform=platform,
            idfa=context.user_data.get("af_idfa"),
            idfv=context.user_data.get("af_idfv"),
            level=None,
        )
        db.increment_requests(uid)
        kb = [
            [InlineKeyboardButton("🎯 حدث آخر", callback_data=f"afgame_{game_id}")],
            [InlineKeyboardButton("🔙 رجوع", callback_data="af_menu")],
        ]
        await update.message.reply_text(
            f"{_result_text(status, resp)}\n📝 *الحدث:* `{text}`\n🎮 *اللعبة:* {game_name}",
            reply_markup=InlineKeyboardMarkup(kb),
            parse_mode="Markdown",
        )

    elif state == "custom_level":
        digits = ''.join(filter(str.isdigit, text))
        if not digits:
            await update.message.reply_text(
                "❌ الرجاء إدخال رقم صحيح للفل (مثال: 45)",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔙 إلغاء", callback_data=f"afgame_{game_id}")]
                ]),
            )
            return
        context.user_data.pop("af_state", None)
        pkg = game.get("package", "")
        dev_key = game.get("dev_key", "")
        if not pkg or not dev_key:
            await update.message.reply_text(
                "❌ خطأ: بيانات اللعبة غير موجودة، الرجاء إعادة اختيار اللعبة",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔙 إلغاء", callback_data=f"afgame_{game_id}")]
                ]),
            )
            return

        events = db.get_af_events(game_id) if game_id else []
        if events:
            base_event = events[0]["event_name"]
            if re.search(r'\d+', base_event):
                event_name = re.sub(r'\d+', digits, base_event)
            else:
                event_name = f"af_level_{digits}_achieved"
        else:
            event_name = f"af_level_{digits}_achieved"

        await update.message.reply_text("📤 *جاري الإرسال فوراً...*", parse_mode="Markdown")
        status, resp = send_af(
            pkg=pkg,
            dev_key=dev_key,
            gaid=context.user_data.get("af_gaid", ""),
            af_uid=context.user_data.get("af_uid", ""),
            event_name=event_name,
            revenue=None,
            proxy=proxy,
            platform=platform,
            idfa=context.user_data.get("af_idfa"),
            idfv=context.user_data.get("af_idfv"),
            level=int(digits) if digits.isdigit() else None,
        )
        db.increment_requests(uid)
        kb = [
            [InlineKeyboardButton("🎯 حدث آخر", callback_data=f"afgame_{game_id}")],
            [InlineKeyboardButton("🔙 رجوع", callback_data="af_menu")],
        ]
        await update.message.reply_text(
            f"{_result_text(status, resp)}\n🔢 *رقم اللفل:* {digits}\n🎮 *اللعبة:* {game_name}",
            reply_markup=InlineKeyboardMarkup(kb),
            parse_mode="Markdown",
        )


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

    kb = [
        [InlineKeyboardButton("🎯 حدث آخر", callback_data=f"afgame_{game.get('id')}")],
        [InlineKeyboardButton("🔙 رجوع", callback_data="af_menu")],
    ]
    await query.message.reply_text(
        f"{_result_text(status, resp)}\n📝 *الحدث:* {event['display_name']}\n🎮 *اللعبة:* {game.get('display_name', '')}",
        reply_markup=InlineKeyboardMarkup(kb),
        parse_mode="Markdown",
    )


@require_access
async def af_custom_event(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data["af_state"] = "custom_event"
    await query.edit_message_text(
        "✨ *حدث مخصص*\n\n📝 *أدخل اسم الحدث:*\nمثال: `af_level_50` أو `Complete_Level`",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 إلغاء", callback_data=f"afgame_{context.user_data.get('af_game_id', '')}")]
        ]),
    )


@require_access
async def af_custom_level(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data["af_state"] = "custom_level"
    await query.edit_message_text(
        "✨ *لفل مخصص*\n\nأدخل رقم اللفل المطلوب (مثال: 45 أو 46) وسيُرسل الحدث فوراً:",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 إلغاء", callback_data=f"afgame_{context.user_data.get('af_game_id', '')}")]
        ]),
    )


def get_handlers():
    return [
        CallbackQueryHandler(af_menu, pattern="^af_menu$"),
        CallbackQueryHandler(af_game, pattern=r"^afgame_\d+$"),
        CallbackQueryHandler(af_send, pattern=r"^af_send_\d+$"),
        CallbackQueryHandler(af_custom_event, pattern="^af_custom_event$"),
        CallbackQueryHandler(af_custom_level, pattern="^af_custom_level$"),
        MessageHandler(filters.TEXT & ~filters.COMMAND, af_text_handler, block=False),
    ]
