import re
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes, CallbackQueryHandler, MessageHandler, filters
)

from src.database import queries as db
from src.middlewares.auth import require_access
from src.services.singular import send_singular

logger = logging.getLogger(__name__)


def _back_kb(data: str = "singular_menu") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data=data)]])


def _events_kb(game_id: int, include_back: bool = True) -> InlineKeyboardMarkup:
    events = db.get_singular_events(game_id)
    kb = []
    for ev in events:
        kb.append([InlineKeyboardButton(f"🌟 {ev['display_name']}", callback_data=f"sg_send_{ev['id']}")])
    kb.append([InlineKeyboardButton("✨ حدث مخصص", callback_data="sg_custom_event")])
    kb.append([InlineKeyboardButton("🔢 لفل مخصص", callback_data="sg_custom_level")])
    if include_back:
        kb.append([InlineKeyboardButton("🔙 رجوع", callback_data="singular_menu")])
    return InlineKeyboardMarkup(kb)


def _result_text(status: int, resp: str) -> str:
    if status == 200:
        return "✅ *تم الإرسال بنجاح!*"
    return f"❌ *فشل الإرسال*\nالكود: `{status}`\n`{resp[:200]}`"


@require_access
async def singular_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data.pop("sg_state", None)
    games = db.get_all_games_singular()
    if not games:
        await query.edit_message_text(
            "❌ *لا توجد ألعاب Singular*",
            parse_mode="Markdown",
            reply_markup=_back_kb("main_menu"),
        )
        return
    kb = [
        [InlineKeyboardButton(f"{g['emoji']} {g['display_name']}", callback_data=f"sgame_{g['id']}")]
        for g in games
    ]
    kb.append([InlineKeyboardButton("🔙 رجوع", callback_data="main_menu")])
    await query.edit_message_text(
        "🌟 *اختر اللعبة - Singular*",
        reply_markup=InlineKeyboardMarkup(kb),
        parse_mode="Markdown",
    )


async def singular_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    gid = int(query.data.replace("sgame_", ""))
    game = db.get_game_singular_by_id(gid)
    if not game:
        await query.edit_message_text("❌ خطأ: اللعبة غير موجودة", parse_mode="Markdown")
        return

    context.user_data["sg_game_id"] = gid
    context.user_data["sg_game_name"] = game["display_name"]
    context.user_data["sg_game"] = dict(game)

    platform = db.get_user_platform(query.from_user.id)
    if platform == "ios":
        context.user_data["sg_state"] = "idfa"
        await query.edit_message_text(
            f"{game['emoji']} *{game['display_name']}*\n\n🍎 *iOS - Singular*\n📱 *أدخل IDFA:*\nمثال: `12345678-1234-1234-1234-123456789012`",
            parse_mode="Markdown",
        )
    else:
        context.user_data["sg_state"] = "aifa"
        await query.edit_message_text(
            f"{game['emoji']} *{game['display_name']}*\n\n🤖 *Android - Singular*\n📱 *أدخل AIFA (GAID):*\nمثال: `8de8604d-1318-4fd0-907c-402ea9de2529`",
            parse_mode="Markdown",
        )


async def singular_text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """يوجه رسائل النص حسب حالة المستخدم (aifa / idfa / idfv / uid / custom_event / custom_level)."""
    state = context.user_data.get("sg_state")
    if not state:
        return
    text = update.message.text.strip()
    game = context.user_data.get("sg_game", {})
    game_id = context.user_data.get("sg_game_id")
    game_name = context.user_data.get("sg_game_name", "")
    uid = update.effective_user.id
    platform = db.get_user_platform(uid)
    proxy_row = db.get_proxy_for_user(uid)
    proxy = dict(proxy_row) if proxy_row else None

    if state == "aifa":
        context.user_data["sg_aifa"] = text
        context.user_data["sg_state"] = "uid"
        await update.message.reply_text(
            "🆔 *أدخل Custom User ID:*\nمثال: `your_user_id_123`",
            parse_mode="Markdown",
        )

    elif state == "idfa":
        context.user_data["sg_idfa"] = text
        context.user_data["sg_state"] = "idfv"
        await update.message.reply_text(
            "🍎 *أدخل IDFV:*\nمثال: `12345678-1234-1234-1234-123456789012`",
            parse_mode="Markdown",
        )

    elif state == "idfv":
        context.user_data["sg_idfv"] = text
        context.user_data["sg_state"] = "uid_ios"
        await update.message.reply_text(
            "🆔 *أدخل Custom User ID:*\nمثال: `your_user_id_123`",
            parse_mode="Markdown",
        )

    elif state == "uid":
        context.user_data["sg_uid"] = text
        context.user_data.pop("sg_state", None)
        events = db.get_singular_events(game_id)
        if not events:
            await update.message.reply_text(
                f"❌ *لا توجد أحداث لهذه اللعبة*\n🌟 {game_name}",
                parse_mode="Markdown",
                reply_markup=_back_kb("singular_menu"),
            )
            return
        await update.message.reply_text(
            f"🎯 *اختر الحدث*\n🌟 {game_name}",
            reply_markup=_events_kb(game_id),
            parse_mode="Markdown",
        )

    elif state == "uid_ios":
        context.user_data["sg_uid"] = text
        context.user_data.pop("sg_state", None)
        events = db.get_singular_events(game_id)
        if not events:
            await update.message.reply_text(
                f"❌ *لا توجد أحداث لهذه اللعبة*\n🌟 {game_name}",
                parse_mode="Markdown",
                reply_markup=_back_kb("singular_menu"),
            )
            return
        await update.message.reply_text(
            f"🎯 *اختر الحدث*\n🌟 {game_name}",
            reply_markup=_events_kb(game_id),
            parse_mode="Markdown",
        )

    elif state == "custom_event":
        if not text:
            await update.message.reply_text("❌ الرجاء إدخال اسم صحيح")
            return
        context.user_data.pop("sg_state", None)
        await update.message.reply_text("📤 *جاري الإرسال فوراً...*", parse_mode="Markdown")
        status, resp = send_singular(
            event_name=text,
            aifa=context.user_data.get("sg_aifa", ""),
            uid=context.user_data.get("sg_uid", ""),
            package=game.get("package", ""),
            app_key=game.get("app_key", ""),
            level=None,
            proxy=proxy,
            platform=platform,
            idfa=context.user_data.get("sg_idfa"),
            idfv=context.user_data.get("sg_idfv"),
            singular_uid=context.user_data.get("sg_uid"),
        )
        db.increment_requests(uid)
        kb = [
            [InlineKeyboardButton("🎯 حدث آخر", callback_data=f"sgame_{game_id}")],
            [InlineKeyboardButton("🔙 رجوع", callback_data="singular_menu")],
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
                    [InlineKeyboardButton("🔙 إلغاء", callback_data=f"sgame_{game_id}")]
                ]),
            )
            return
        context.user_data.pop("sg_state", None)
        pkg = game.get("package", "")
        app_key = game.get("app_key", "")
        aifa = context.user_data.get("sg_aifa", "")
        sg_uid = context.user_data.get("sg_uid", "")

        if not pkg or not app_key:
            await update.message.reply_text(
                "❌ خطأ: بيانات اللعبة غير موجودة، الرجاء إعادة اختيار اللعبة",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔙 إلغاء", callback_data=f"sgame_{game_id}")]
                ]),
            )
            return

        events = db.get_singular_events(game_id) if game_id else []
        if events:
            base_event = events[0]["event_name"]
            if base_event.endswith("_"):
                event_name = base_event + digits
                level_param = None
            elif re.search(r'\d+$', base_event):
                event_name = re.sub(r'\d+$', digits, base_event)
                level_param = None
            elif re.search(r'\d+', base_event):
                event_name = re.sub(r'\d+', digits, base_event)
                level_param = None
            else:
                event_name = base_event
                level_param = digits
        else:
            event_name = f"level_{digits}"
            level_param = None

        await update.message.reply_text("📤 *جاري الإرسال فوراً...*", parse_mode="Markdown")
        status, resp = send_singular(
            event_name=event_name,
            aifa=aifa,
            uid=sg_uid,
            package=pkg,
            app_key=app_key,
            level=level_param,
            proxy=proxy,
            platform=platform,
            idfa=context.user_data.get("sg_idfa"),
            idfv=context.user_data.get("sg_idfv"),
            singular_uid=sg_uid,
        )
        db.increment_requests(uid)
        kb = [
            [InlineKeyboardButton("🎯 حدث آخر", callback_data=f"sgame_{game_id}")],
            [InlineKeyboardButton("🔙 رجوع", callback_data="singular_menu")],
        ]
        await update.message.reply_text(
            f"{_result_text(status, resp)}\n🔢 *رقم اللفل:* {digits}\n🎮 *اللعبة:* {game_name}",
            reply_markup=InlineKeyboardMarkup(kb),
            parse_mode="Markdown",
        )


@require_access
async def singular_send(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    event_id = int(query.data.replace("sg_send_", ""))

    game_id = context.user_data.get("sg_game_id")
    if not game_id:
        await query.edit_message_text(
            "❌ *انتهت الجلسة. ابدأ من جديد.*",
            parse_mode="Markdown",
            reply_markup=_back_kb("singular_menu"),
        )
        return

    events = db.get_singular_events(game_id)
    event = next((e for e in events if e["id"] == event_id), None)
    if not event:
        await query.edit_message_text("❌ خطأ: الحدث غير موجود", parse_mode="Markdown")
        return

    game = context.user_data.get("sg_game", {})
    uid = update.effective_user.id
    platform = db.get_user_platform(uid)
    proxy_row = db.get_proxy_for_user(uid)

    await query.edit_message_text("🔄 *جاري الإرسال...*", parse_mode="Markdown")

    status, resp = send_singular(
        event_name=event["event_name"],
        aifa=context.user_data.get("sg_aifa", ""),
        uid=context.user_data.get("sg_uid", ""),
        package=game.get("package", ""),
        app_key=game.get("app_key", ""),
        level=event.get("level_value"),
        proxy=dict(proxy_row) if proxy_row else None,
        platform=platform,
        idfa=context.user_data.get("sg_idfa"),
        idfv=context.user_data.get("sg_idfv"),
        singular_uid=context.user_data.get("sg_uid"),
    )

    db.increment_requests(uid)

    kb = [
        [InlineKeyboardButton("🎯 حدث آخر", callback_data=f"sgame_{game.get('id')}")],
        [InlineKeyboardButton("🔙 رجوع", callback_data="singular_menu")],
    ]
    await query.message.reply_text(
        f"{_result_text(status, resp)}\n📝 *الحدث:* {event['display_name']}\n🎮 *اللعبة:* {game.get('display_name', '')}",
        reply_markup=InlineKeyboardMarkup(kb),
        parse_mode="Markdown",
    )


@require_access
async def singular_custom_event(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data["sg_state"] = "custom_event"
    await query.edit_message_text(
        "✨ *حدث مخصص*\n\n📝 *أدخل اسم الحدث:*\nمثال: `level_50` أو `Complete_Level`",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 إلغاء", callback_data=f"sgame_{context.user_data.get('sg_game_id', '')}")]
        ]),
    )


@require_access
async def singular_custom_level(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data["sg_state"] = "custom_level"
    await query.edit_message_text(
        "✨ *لفل مخصص*\n\nأدخل رقم اللفل المطلوب (مثال: 45 أو 46) وسيُرسل الحدث فوراً:",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 إلغاء", callback_data=f"sgame_{context.user_data.get('sg_game_id', '')}")]
        ]),
    )


def get_handlers():
    return [
        CallbackQueryHandler(singular_menu, pattern="^singular_menu$"),
        CallbackQueryHandler(singular_game, pattern=r"^sgame_\d+$"),
        CallbackQueryHandler(singular_send, pattern=r"^sg_send_\d+$"),
        CallbackQueryHandler(singular_custom_event, pattern="^sg_custom_event$"),
        CallbackQueryHandler(singular_custom_level, pattern="^sg_custom_level$"),
        MessageHandler(filters.TEXT & ~filters.COMMAND, singular_text_handler, block=False),
    ]
