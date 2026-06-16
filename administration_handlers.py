from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackQueryHandler, MessageHandler, filters, ConversationHandler, ContextTypes
from handlers import (
    get_user_by_chat_id,
    get_empire_by_user,
    get_total_resources,
    get_upkeep_units_in_garrison,
    get_resource_count,
    place_units_to_garrison,

)
from states_for_dialogs import (
    WAITING_COUNT_UNITS_PLACE_GARRISON,
    CONFIRMATION_FOR_UNITS_PLACE_GARRISON
)
from validations import (
    validate_positive_number
)
from utils_messages import delete_last_message



async def empire_administration_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.callback_query.answer()


    context.user_data.clear()


    chat_id = update.callback_query.from_user.id
    user = get_user_by_chat_id(chat_id)


    message = (
        f"🏛️ <b>Администрирование империи.</b>\n\n"
        f"<b>Здесь вы можете усилить защиту империи, на время входящих атак, разместив в гарнизоне определённое количество юнитов армии.</b>\n\n"
    )


    keyboard = [
        [InlineKeyboardButton("Гарнизон", callback_data="empire_administration_garrison_handler")],
        [InlineKeyboardButton("Назад", callback_data="manage_empire_handler")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)


    await update.callback_query.edit_message_text(
        text=message,
        parse_mode="HTML",
        reply_markup=reply_markup
    )

    return ConversationHandler.END



async def empire_administration_garrison_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.callback_query.answer()


    context.user_data.clear()


    chat_id = update.callback_query.from_user.id
    user = get_user_by_chat_id(chat_id)
    empire = get_empire_by_user(user)

    resources = get_total_resources(empire)


    message = (
        f"Введите количество юнитов армии, размещаемых вами в гарнизоне:\n\n"
        f"Всего юнитов армии в империи: {resources['units_army']}\n\n"
        f"Расход золота на одного юнита армии в усилении: {get_upkeep_units_in_garrison()} ед. / минуту.\n\n"
    )


    keyboard = [
        [InlineKeyboardButton("Отмена", callback_data="cancel_units_place_garrison_handler")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)


    message_send = await update.callback_query.edit_message_text(
        text=message,
        parse_mode="HTML",
        reply_markup=reply_markup
    )

    context.user_data['chat_id'] = chat_id
    context.user_data['last_message'] = message_send.message_id

    return WAITING_COUNT_UNITS_PLACE_GARRISON



async def process_count_units_for_place_garrison(update, context):
    if 'last_message' in context.user_data and 'chat_id' in context.user_data:
        try:
            await context.bot.delete_message(context.user_data.get('chat_id'), context.user_data.get('last_message'))
        except:
            context.user_data.clear()
            return ConversationHandler.END

    chat_id = context.user_data.get('chat_id')
    user = get_user_by_chat_id(chat_id)
    empire = get_empire_by_user(user)


    count_units_army = update.message.text.strip()


    if not validate_positive_number(count_units_army):

        keyboard = [
            [InlineKeyboardButton("Отмена", callback_data="cancel_units_place_garrison_handler")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        message_send = await update.message.reply_text(
            text="Вы ввели неверное значение для количества юнитов армии. Введите корректное значение размещаемых юнитов армии в гарнизоне:",
            reply_markup=reply_markup
        )

        context.user_data['chat_id'] = chat_id
        context.user_data['last_message'] = message_send.message_id

        return WAITING_COUNT_UNITS_PLACE_GARRISON


    count_units_army = int(count_units_army)


    current_count_units_army = get_resource_count(empire, "units_army")
    if current_count_units_army < count_units_army:

        keyboard = [
            [InlineKeyboardButton("Отмена", callback_data="cancel_units_place_garrison_handler")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        message_send = await update.message.reply_text(
            text="У вас не хватает юнитов армии. Введите другое значение:",
            reply_markup=reply_markup
        )

        context.user_data['chat_id'] = chat_id
        context.user_data['last_message'] = message_send.message_id

        return WAITING_COUNT_UNITS_PLACE_GARRISON


    keyboard = [
        [InlineKeyboardButton("✅ Подтвердить", callback_data="confirm_for_units_place_garrison_handler")],
        [InlineKeyboardButton("❌ Отменить", callback_data="cancel_units_place_garrison_handler")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    message_text = (
        f"Вы собираетесь усилить гарнизон юнитами армии, в количестве: {count_units_army}.\n\n"
        f"Расход золота на гарнизон: {count_units_army * get_upkeep_units_in_garrison():.2f} ед. / минуту."
        "\n\nПодтвердите или отмените:"
    )

    message_send = await update.message.reply_text(
        text=message_text,
        reply_markup=reply_markup
    )

    context.user_data['last_message'] = message_send.message_id
    context.user_data['count_units_army'] = count_units_army

    return CONFIRMATION_FOR_UNITS_PLACE_GARRISON



async def confirm_for_units_place_garrison_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.callback_query.from_user.id
    count_units_army = context.user_data.get("count_units_army")

    user = get_user_by_chat_id(chat_id)
    empire = get_empire_by_user(user)

    if not user:
        await update.callback_query.edit_message_text("Ошибка: Пользователь не найден.")
        return ConversationHandler.END


    result, msg = place_units_to_garrison(empire, count_units_army)

    keyboard = [
        [InlineKeyboardButton("Вернуться в меню", callback_data="empire_administration_handler")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if result is not None:
        await update.callback_query.edit_message_text(
            text=msg,
            reply_markup=reply_markup
        )
    else:
        await update.callback_query.edit_message_text(
            text=msg,
            reply_markup=reply_markup
        )

    return ConversationHandler.END



async def cancel_units_place_garrison_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    chat_id = update.callback_query.from_user.id
    await delete_last_message(context, chat_id)


    message = await update.callback_query.message.reply_text(
        text="Вы отменили усиление гарнизона."
    )
    context.user_data["last_message"] = message.message_id
    return ConversationHandler.END


conversation_handler_units_place_garrison = ConversationHandler(
        entry_points=[CallbackQueryHandler(empire_administration_garrison_handler, pattern="empire_administration_garrison_handler")],
        states={
            WAITING_COUNT_UNITS_PLACE_GARRISON: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND, process_count_units_for_place_garrison
                ),
                CallbackQueryHandler(cancel_units_place_garrison_handler, pattern="cancel_units_place_garrison_handler")
            ],
            CONFIRMATION_FOR_UNITS_PLACE_GARRISON: [
                CallbackQueryHandler(confirm_for_units_place_garrison_handler, pattern="confirm_for_units_place_garrison_handler"),
                CallbackQueryHandler(cancel_units_place_garrison_handler, pattern="cancel_units_place_garrison_handler")
            ],
        },
        fallbacks=[
            CallbackQueryHandler(cancel_units_place_garrison_handler, pattern="cancel_units_place_garrison_handler")
        ]
    )
