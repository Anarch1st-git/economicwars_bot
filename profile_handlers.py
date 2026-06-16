from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from handlers import (
    get_user_by_chat_id
)


async def subscribe_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    print("subscribe_menu_handler")
    query = update.callback_query
    await query.answer()

    chat_id = query.from_user.id
    user = get_user_by_chat_id(chat_id)

    if not user:
        await query.edit_message_text(
            text="Пользователь не найден."
        )
        return

    if user.subscription_status:
        await update.message.reply_text(
            text="У вас уже есть Премиум."
        )

        return

    message = (
        f"Раздел находится в разработке.\n\n"
        f"Премиум оформляется на: 7 дней, 30 дней, 180 дней или 360 дней. Премиум даёт на весь период действия такие бонусы как:\n\n"
        f"Возможность изучать неограниченное количество технологий одновременно.\n"
        f"Возможность строить неограниченное количество зданий одновременно.\n"
        f"<b>+15%</b> к скорости добычи всех ресурсов.\n"
        f"<b>+15%</b> к скорости изучения всех технологий.\n"
        f"<b>+10%</b> к скорости всех миссий.\n"
        f"<b>+25%</b> к скорости добычи базовой энергии империей.\n"
        f"<b>-3%</b> к содержанию юнитов армии и разведки.\n"
        f"<b>-1.5%</b> к потреблению всеми зданиями энергии и <b>+5%</b> к добыче основной энергии.\n\n"

        f"Тарифы Премиум:\n\n"
        f"7 дней: 690 рублей.\n"
        f"30 дней: 1999 рублей.\n"
        f"180 дней: 7990 рублей.\n"
        f"360 дней: 12990 рублей.\n"
    )

    keyboard = [
        [InlineKeyboardButton("7 дней [690 рублей]", callback_data="buy_subscribe_7")],
        [InlineKeyboardButton("30 дней [1999 рублей]", callback_data="buy_subscribe_30")],
        [InlineKeyboardButton("180 дней [7990 рублей]", callback_data="buy_subscribe_180")],
        [InlineKeyboardButton("360 дней [12990 рублей]", callback_data="buy_subscribe_360")],
        [InlineKeyboardButton("Назад", callback_data="profile_handler")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)


    await update.callback_query.edit_message_text(
        text=message,
        reply_markup=reply_markup,
        parse_mode="HTML"
    )


































