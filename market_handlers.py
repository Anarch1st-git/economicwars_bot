from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackQueryHandler, MessageHandler, filters, ConversationHandler, ContextTypes
from handlers import (
    get_user_by_chat_id,
    get_empire_by_user,
    get_total_resources,
    is_research_completed,
    perform_market_transaction,
    has_building_complete,
    get_empire_items_list
)
from states_for_dialogs import (
    CHOOSE_RESOURCE,
    ASK_QUANTITY
)
from models import (
    MarketRate,
    Resource,
    EmpireResource,
    Items,
    EmpireItems
)
from utils_messages import delete_last_message



async def empire_market_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.callback_query.answer()

    chat_id = update.callback_query.from_user.id
    user = get_user_by_chat_id(chat_id)
    empire = get_empire_by_user(user)

    if not is_research_completed(empire, "tech_market") and not has_building_complete(empire, "market"):
        message = (
            "🔒 <b>Рынок недоступен</b>\n\n"
            "Изучите науку <b>Торговля</b>, и постройте здание <b>Рынок</b>, чтобы получить доступ к торговле."
        )
        keyboard = [
            [InlineKeyboardButton("↩️ Назад", callback_data="manage_empire_handler")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.callback_query.edit_message_text(
            text=message,
            parse_mode="HTML",
            reply_markup=reply_markup
        )
        return ConversationHandler.END

    resources = get_total_resources(empire)
    market_rates = MarketRate.select()

    message = "\U0001F4CA <b>Рынок ресурсов</b>\n\n"
    message += f"У вас {resources['gold']} золота\n\n"
    for rate in market_rates:
        if rate.resource.name != "gold":
            message += (
                f"💰 <b>{rate.resource.name}</b>\n"
                f"🔼 Покупка: <i>{rate.buy_price}</i> золота за 1 единицу.\n"
                f"🔽 Продажа: <i>{rate.sell_price}</i> золота за 1 единицу.\n"
                f"📦 У вас: <i>{resources.get(rate.resource.name, 0)}</i>\n\n"
            )

    keyboard = [
        [InlineKeyboardButton("Купить ресурс", callback_data="empire_market_buy")],
        [InlineKeyboardButton("Продать ресурс", callback_data="empire_market_sell")],
        [InlineKeyboardButton("Продать предмет", callback_data="empire_market_sell_item")],
        [InlineKeyboardButton("Назад", callback_data="manage_empire_handler")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.callback_query.edit_message_text(
        text=message,
        parse_mode="HTML",
        reply_markup=reply_markup
    )

    return ConversationHandler.END



async def empire_market_buy(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработчик для покупки ресурса."""
    context.user_data["action"] = "buy"
    return await choose_resource_handler(update, context)



async def empire_market_sell(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обработчик для продажи ресурса."""
    context.user_data["action"] = "sell"
    return await choose_resource_handler(update, context)



async def empire_market_sell_item(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.callback_query.answer()

    chat_id = update.callback_query.from_user.id
    user = get_user_by_chat_id(chat_id)
    empire = get_empire_by_user(user)
    items = get_empire_items_list(empire)

    if not items:
        await update.callback_query.edit_message_text(
            "📦 У вас нет предметов для продажи.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("↩️ Назад", callback_data="empire_market_handler")]])
        )
        return ConversationHandler.END

    keyboard = []
    for item in items:
        button_text = f"{item.name} (ур. {item.level}) — 💰 {int(item.cost)}"
        keyboard.append([InlineKeyboardButton(button_text, callback_data=f"sell_item_{item.item_id}")])

    keyboard.append([InlineKeyboardButton("↩️ Назад", callback_data="empire_market_handler")])

    await update.callback_query.edit_message_text(
        "💼 <b>Ваши предметы:</b>\n\nВыберите предмет для продажи:",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return ConversationHandler.END



async def confirm_item_sell(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.callback_query.answer()

    item_id = int(update.callback_query.data.split("_")[-1])
    chat_id = update.callback_query.from_user.id
    user = get_user_by_chat_id(chat_id)
    empire = get_empire_by_user(user)

    try:
        item = Items.get_by_id(item_id)
    except Items.DoesNotExist:
        await update.callback_query.edit_message_text("❌ Предмет не найден.")
        return ConversationHandler.END

    context.user_data["sell_item_id"] = item_id

    message = (
        f"🎯 <b>{item.name}</b> (ур. {item.level})\n"
        f"💰 <b>Цена продажи:</b> {int(item.cost)} золота\n\n"
        "Вы уверены, что хотите продать этот предмет?"
    )
    keyboard = [
        [InlineKeyboardButton("✅ Продать", callback_data="confirm_item_sale")],
        [InlineKeyboardButton("↩️ Назад", callback_data="empire_market_sell_item")]
    ]

    await update.callback_query.edit_message_text(
        message,
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return ConversationHandler.END



async def perform_item_sale(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.callback_query.answer()

    item_id = context.user_data.get("sell_item_id")
    if not item_id:
        await update.callback_query.edit_message_text("❌ Ошибка при продаже.")
        return ConversationHandler.END

    chat_id = update.callback_query.from_user.id
    user = get_user_by_chat_id(chat_id)
    empire = get_empire_by_user(user)

    try:
        item = Items.get_by_id(item_id)
        empire_item = EmpireItems.get(EmpireItems.empire == empire, EmpireItems.item == item)
    except (Items.DoesNotExist, EmpireItems.DoesNotExist):
        await update.callback_query.edit_message_text("❌ Предмет не найден.")
        return ConversationHandler.END


    empire_item.delete_instance()


    resources = EmpireResource.get(EmpireResource.empire == empire)
    resources.gold += int(item.cost)
    resources.save()

    await update.callback_query.edit_message_text(
        f"✅ Вы продали <b>{item.name}</b> за <b>{int(item.cost)} золота</b>.",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("↩️ Назад", callback_data="empire_market_sell_item")]])
    )
    return ConversationHandler.END


async def choose_resource_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Выбор ресурса для покупки или продажи."""
    await update.callback_query.answer()

    chat_id = update.callback_query.from_user.id

    action = context.user_data["action"]
    market_rates = MarketRate.select()

    keyboard = [
        [InlineKeyboardButton(rate.resource.name, callback_data=str(rate.resource.resource_id))]
        for rate in market_rates if rate.resource.name != "gold"
    ]
    keyboard.append([InlineKeyboardButton("Отмена", callback_data="cancel_operation_market_handler")])

    reply_markup = InlineKeyboardMarkup(keyboard)

    message_send = await update.callback_query.edit_message_text(
        text=f"Выберите ресурс для {'покупки' if action == 'buy' else 'продажи'}:",
        reply_markup=reply_markup
    )

    context.user_data['chat_id'] = chat_id
    context.user_data['last_message'] = message_send.message_id

    return CHOOSE_RESOURCE



async def ask_quantity_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Запрос количества ресурса (универсальный для покупки и продажи)."""
    resource_id = int(update.callback_query.data)
    context.user_data["resource_id"] = resource_id
    resource = Resource.get(Resource.resource_id == resource_id)
    context.user_data["resource_name"] = resource.name

    chat_id = update.callback_query.from_user.id
    user = get_user_by_chat_id(chat_id)
    empire = get_empire_by_user(user)
    empire_resources = get_total_resources(empire)

    resource_amount = empire_resources.get(resource.name.lower(), 0)

    await update.callback_query.answer()

    keyboard = [[InlineKeyboardButton("Отмена", callback_data="cancel_operation_market_handler")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    action_text = "покупки" if context.user_data["action"] == "buy" else "продажи"

    message_send = await update.callback_query.edit_message_text(
        text=f"📦 У вас {resource_amount} {resource.name}.\n"
             f"Введите количество для {action_text}:",
        reply_markup=reply_markup
    )

    context.user_data['chat_id'] = chat_id
    context.user_data['last_message'] = message_send.message_id

    return ASK_QUANTITY



async def confirm_transaction_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if 'last_message' in context.user_data and 'chat_id' in context.user_data:
        try:
            await context.bot.delete_message(context.user_data.get('chat_id'), context.user_data.get('last_message'))
        except:
            context.user_data.clear()
            return ConversationHandler.END

    chat_id = update.message.chat_id
    user = get_user_by_chat_id(chat_id)
    empire = get_empire_by_user(user)

    try:
        quantity = int(update.message.text)
        if quantity <= 0:
            raise ValueError
    except ValueError:
        await update.message.reply_text(
            text="❌ Введите корректное число!",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Отмена", callback_data="cancel_operation_market_handler")]])
        )
        return ASK_QUANTITY

    action = context.user_data["action"]
    resource_id = context.user_data["resource_id"]

    success, message = perform_market_transaction(empire, action, resource_id, quantity)

    await update.message.reply_text(
        text=message,
        parse_mode="HTML"
    )

    return ConversationHandler.END



async def cancel_operation_market_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    chat_id = update.callback_query.from_user.id
    await delete_last_message(context, chat_id)


    message = await update.callback_query.message.reply_text(
        text="Вы отменили работу с рынком."
    )
    context.user_data["last_message"] = message.message_id
    return ConversationHandler.END


conversation_handler_market = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(empire_market_buy, pattern="^empire_market_buy$"),
            CallbackQueryHandler(empire_market_sell, pattern="^empire_market_sell$")
        ],
        states={
            CHOOSE_RESOURCE: [
                CallbackQueryHandler(ask_quantity_handler, pattern=r"^\d+$"),
                CallbackQueryHandler(cancel_operation_market_handler, pattern="^cancel_operation_market_handler$")
            ],
            ASK_QUANTITY: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, confirm_transaction_handler),
                CallbackQueryHandler(cancel_operation_market_handler, pattern="^cancel_operation_market_handler$")
            ]
        },
        fallbacks=[
            CallbackQueryHandler(cancel_operation_market_handler, pattern="^cancel_operation_market_handler$")
        ]
    )
