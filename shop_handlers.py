from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from handlers import (
    get_user_by_chat_id,
    get_today_lootbox,
    get_today_lootlucky,
    can_claim_lootbox,
    format_lootbox_content,
    get_empire_by_user,
    add_loot_to_empire_from_box,
    pick_random_lucky_item,
    add_lootlucky_to_empire_from_box,
    get_active_buster_ids,
    get_all_busters,
    get_buster_by_id,
    deduct_balance,
    apply_buster_to_empire
)
from locales.locales_names import buster_name, buster_description


async def market_ingame_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    chat_id = query.from_user.id
    user = get_user_by_chat_id(chat_id)

    if not user:
        await query.edit_message_text(
            text="Пользователь не найден."
        )
        return

    message = (
        f"Это магазин внутриигровых покупок."
    )

    keyboard = [
        [InlineKeyboardButton("Ежедневные бесплатные ресурсы", callback_data="daily_free_resources")],
        [InlineKeyboardButton("Бустеры, бонусы", callback_data="bonuses_busters_menu")],
        [InlineKeyboardButton("Назад", callback_data="manage_empire_handler")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)


    await update.callback_query.edit_message_text(
        text=message,
        reply_markup=reply_markup,
        parse_mode="HTML"
    )


async def daily_free_resources(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    chat_id = query.from_user.id
    user = get_user_by_chat_id(chat_id)
    empire = get_empire_by_user(user)

    if not user:
        await query.edit_message_text(
            text="Пользователь не найден."
        )
        return

    if not empire:
        await query.edit_message_text(
            text="Империя не найдена."
        )
        return

    if not can_claim_lootbox(empire):
        keyboard = [
            [InlineKeyboardButton("Назад", callback_data="market_ingame_handler")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            text="Вы уже получали лутбоксы сегодня.",
            reply_markup=reply_markup,
            parse_mode="HTML"
        )
        return

    lootbox = get_today_lootbox()
    lootlucky = get_today_lootlucky()

    if not lootbox or not lootlucky:
        await query.edit_message_text(
            text="Лутбоксы на сегодня ещё не сгенерированы."
        )
        return

    message = (
        f"{format_lootbox_content(lootbox, '🎁 <b>Стандартный набор:</b>')}\n\n"
        f"{format_lootbox_content(lootlucky, '🎡 <b>Сегодняшнее меню удачи:</b>')}\n\n"
        f"<i>Из меню удачи можно получить только одну награду.</i>"
    )

    keyboard = [
        [InlineKeyboardButton("📦 Стандартный набор", callback_data=f"get_standard_set")],
        [InlineKeyboardButton("🎲 Мне повезёт", callback_data="get_lucky_item")],
        [InlineKeyboardButton("Назад", callback_data="market_ingame_handler")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        text=message,
        reply_markup=reply_markup,
        parse_mode="HTML"
    )


async def handle_get_standard_set(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    chat_id = query.from_user.id
    user = get_user_by_chat_id(chat_id)
    empire = get_empire_by_user(user)

    if not user:
        await query.edit_message_text(
            text="Пользователь не найден."
        )
        return

    if not empire:
        await query.edit_message_text(
            text="Империя не найдена."
        )
        return

    if not can_claim_lootbox(empire):
        keyboard = [
            [InlineKeyboardButton("Назад", callback_data="market_ingame_handler")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            text="Вы уже получали лутбоксы сегодня.",
            reply_markup=reply_markup,
            parse_mode="HTML"
        )
        return

    lootbox = get_today_lootbox()

    if not lootbox:
        await query.edit_message_text(
            text="Лутбоксы на сегодня ещё не сгенерированы."
        )
        return

    empire.has_lootbox = lootbox
    empire.save()

    add_loot_to_empire_from_box(empire, lootbox)

    keyboard = [
            [InlineKeyboardButton("Назад", callback_data="market_ingame_handler")]
        ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        text=f"Вы получили: \n{format_lootbox_content(lootbox, '🎁 <b>Стандартный набор:</b>')}\n\n",
        reply_markup=reply_markup,
        parse_mode="HTML"
    )


async def handle_get_lucky_item(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    chat_id = query.from_user.id
    user = get_user_by_chat_id(chat_id)
    empire = get_empire_by_user(user)

    if not user:
        await query.edit_message_text(
            text="Пользователь не найден."
        )
        return

    if not empire:
        await query.edit_message_text(
            text="Империя не найдена."
        )
        return

    if not can_claim_lootbox(empire):
        keyboard = [
            [InlineKeyboardButton("Назад", callback_data="market_ingame_handler")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            text="Вы уже получали лутбоксы сегодня.",
            reply_markup=reply_markup,
            parse_mode="HTML"
        )
        return

    lootlucky = get_today_lootlucky()

    if not lootlucky:
        await query.edit_message_text(
            text="Лутбоксы на сегодня ещё не сгенерированы."
        )
        return

    empire.has_lootbox_lucky = lootlucky
    empire.save()
    result = pick_random_lucky_item()

    if not result:
        await query.edit_message_text(
            text="❌ Награды сегодня отсутствуют."
        )
        return

    reward_type, reward_value = result

    if reward_type == "item":
        add_lootlucky_to_empire_from_box(empire, item=reward_value)
    else:
        add_lootlucky_to_empire_from_box(empire, resource_name=reward_type, amount=reward_value)

    keyboard = [
            [InlineKeyboardButton("Назад", callback_data="market_ingame_handler")]
        ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        text=f"Вы получаете: {result}",
        reply_markup=reply_markup,
        parse_mode="HTML"
    )


async def bonuses_busters_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    chat_id = query.from_user.id
    user = get_user_by_chat_id(chat_id)
    empire = get_empire_by_user(user)

    if not user:
        await query.edit_message_text(
            text="Пользователь не найден."
        )
        return

    if not empire:
        await query.edit_message_text(
            text="Империя не найдена."
        )
        return

    active_buster_ids = get_active_buster_ids(empire)
    busters = get_all_busters()
    message_lines = ["Магазин находится в разработке.\n\n", "<b>Доступные бустеры:</b>"]
    keyboard = []

    for b in busters:
        is_active = b.buster_id in active_buster_ids
        message_lines.append(
            f"🧪 <b>{buster_name[b.name]}</b>\n"
            f"💰 Цена: {b.cost} рублей.\n"
            f"📊 Эффект: {buster_description[b.description]}\n"
            f"⏳ Длительность: {b.base_action_time // 60} мин.\n"
            f"{'🟢 Активен' if is_active else ''}\n\n"
        )
        if not is_active:
            keyboard.append([
                InlineKeyboardButton(f"Купить бустер - {buster_name[b.name]}", callback_data=f"test_buy_buster:{b.buster_id}")
            ])

    keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="market_ingame_handler")])
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        text="\n".join(message_lines),
        reply_markup=reply_markup,
        parse_mode="HTML"
    )


async def handle_buy_buster(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    chat_id = query.from_user.id
    user = get_user_by_chat_id(chat_id)
    empire = get_empire_by_user(user)

    if not user:
        await query.edit_message_text(
            text="Пользователь не найден."
        )
        return

    if not empire:
        await query.edit_message_text(
            text="Империя не найдена."
        )
        return

    buster_id = int(query.data.split(":")[1])
    buster = get_buster_by_id(buster_id)

    if not buster:
        await query.edit_message_text("Бустер не найден.")
        return

    if user.balance < buster.cost:
        await query.edit_message_text("Недостаточно средств.")
        return


    try:
        deduct_balance(user, buster.cost)
        apply_buster_to_empire(empire, buster)

        message = (
            f"✅ Вы купили бустер <b>{buster_name[buster.name]}</b>!\n"
            f"🎯 Эффект: {buster_description[buster.description]}"
            f"⏳ Длительность: {buster.base_action_time // 60} мин."
        )

        keyboard = [
            [InlineKeyboardButton("🔙 Назад", callback_data="market_ingame_handler")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            text=message,
            reply_markup=reply_markup,
            parse_mode="HTML"
        )
    except Exception as e:
        await query.edit_message_text(f"Ошибка покупки: {e}")
