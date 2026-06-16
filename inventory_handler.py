from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackQueryHandler, MessageHandler, filters, ConversationHandler, ContextTypes
from handlers import (
    get_user_by_chat_id,
    get_empire_by_user,
    get_total_resources,
    get_empire_items_count,
    get_empire_items_list
)
from locales.locales_names import items_name
from i18n import I18N


i18n = I18N("ru")



async def empire_inventory_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.callback_query.answer()


    chat_id = update.callback_query.from_user.id
    user = get_user_by_chat_id(chat_id)
    empire = get_empire_by_user(user)

    resources = get_total_resources(empire)
    items_count = get_empire_items_count(empire)

    message = (
        f"Инвентарь вашей империи:\n\n"
        f"Ресурсы:\n\n"
        f"Лес: {resources['wood']}\n"
        f"Золото: {resources['gold']}\n"
        f"Нефть: {resources['oil']}\n"
        f"Алмазы: {resources['diamond']}\n"
        f"Количество предметов: {items_count}"
    )


    keyboard = [
        [InlineKeyboardButton("Предметы", callback_data="empire_inventory_items_handler_0")],
        [InlineKeyboardButton(i18n.t("buttons.back"), callback_data="manage_empire_handler")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)


    await update.callback_query.edit_message_text(
        text=message,
        parse_mode="HTML",
        reply_markup=reply_markup
    )

async def empire_inventory_items_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.callback_query.answer()

    ITEMS_PER_PAGE = 5


    chat_id = update.callback_query.from_user.id
    user = get_user_by_chat_id(chat_id)
    empire = get_empire_by_user(user)


    callback_data = update.callback_query.data
    page = 0
    if callback_data.startswith("empire_inventory_items_handler_"):
        try:
            page = int(callback_data.split("_")[-1])
        except ValueError:
            page = 0

    items = get_empire_items_list(empire)
    total_items = len(items)
    total_pages = max((total_items - 1) // ITEMS_PER_PAGE + 1, 1)

    start = page * ITEMS_PER_PAGE
    end = start + ITEMS_PER_PAGE
    current_items = items[start:end]


    if not current_items:
        message = "Нет предметов в инвентаре."
    else:
        message = "🎒 <b>Предметы империи:</b>\n\n"
        for i, item in enumerate(current_items, start=1 + start):
            message += f"{i}. {items_name[item.name]} (Уровень {item.level}, {item.category}) - 💰 {item.value}\n"


    keyboard = []
    if page > 0:
        keyboard.append(InlineKeyboardButton("⬅️ Пред. страница", callback_data=f"empire_inventory_items_handler_{page - 1}"))
    if end < total_items:
        keyboard.append(InlineKeyboardButton("➡️ След. страница", callback_data=f"empire_inventory_items_handler_{page + 1}"))

    nav_buttons = [keyboard] if keyboard else []
    nav_buttons.append([InlineKeyboardButton("🔙 Назад", callback_data="empire_inventory_handler")])
    reply_markup = InlineKeyboardMarkup(nav_buttons)

    await update.callback_query.edit_message_text(
        text=message,
        parse_mode="HTML",
        reply_markup=reply_markup
    )
