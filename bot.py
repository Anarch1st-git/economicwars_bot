from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ConversationHandler, ContextTypes, PreCheckoutQueryHandler
import asyncio
from db import initialize_db
from handlers import (
    get_user_by_chat_id,
    create_user,
    create_empire,
    get_empire_by_user,
    get_total_resources,
    get_completed_buildings_count,
    get_total_buildings_count,
    get_completed_research_count,
    get_total_technologies_count,
    get_empire_items_count,
    get_outgoing_attacks_count,
    get_incoming_attacks_count,
    get_science_research_speed,
    get_empire_defense_info,
    get_current_rating_layer,
    get_target_rating_layer,
    move_empire_to_new_layer,
    assign_quest_to_empire,
    get_empire_rank,
    render_energy_status,
    is_empire_name_taken,
    is_research_completed,
    get_current_season,
    get_active_event
)




from buildings_handlers import (
    empire_buildings_handler,
    empire_buildings_social_handler,
    empire_buildings_military_handler,
    empire_buildings_economics_handler,
    empire_building_menu_handler,
    empire_build_handler,

    upgrade_building_handler,
    hire_units_handler,
    cancel_build_handler
)
from market_handlers import (
    conversation_handler_market,
    empire_market_handler,
    empire_market_sell_item,
    confirm_item_sell,
    perform_item_sale
)
from missions_handlers import (
    conversation_handler_attack_empire,
    conversation_handler_espionage_empire,
    conversation_handler_exploration,
    conversation_handler_attack_location,
    empire_missions_handler,
    empire_missions_current_missions_handler,
    current_mission_details_handler,
    empire_missions_results_missions_handler,
    mission_result_handler,
    cancel_mission_handler
)
from technologies_handlers import (
    empire_technologies_handler,
    empire_research_general_handler,
    empire_research_extracting_handler,
    extracting_category_handler,
    building_research_handler,
    research_menu_handler,
    start_research_handler,
    start_research_handler,
    cancel_research_handler
)
from cluster_map_handlers import (
    cluster_map_handler,
    cluster_map_finder_locations,
    cluster_map_list_empiries,
    location_report_handler
)
from profile_handlers import (
    subscribe_menu_handler,

)
from shop_handlers import (
    market_ingame_handler,
    daily_free_resources,
    handle_get_standard_set,
    handle_get_lucky_item,
    bonuses_busters_menu,
    handle_buy_buster
)
from game_news_handler import (
    game_news_handler
)
from inventory_handler import (
    empire_inventory_handler,
    empire_inventory_items_handler
)
from effects_handler import (
    empire_effects_handler
)
from utils_messages import (
    delete_last_message
)
from configs import (
    BOT_TOKEN
)
from states_for_dialogs import (
    WAITING_FOR_NAME_EMPIRE,
    CONFIRMATION_NAME_EMPIRE
)
from emojis import (
    LEFT_ARROW,
    RIGHT_ARROW
)
from validations import is_valid_empire_name
from i18n import I18N

from datetime import datetime
from locales.locales_names import season_name, rating_name, events_effects_name

i18n = I18N("ru")


async def start_command_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data.clear()
    context.chat_data.clear()

    chat_id = update.message.chat.id
    user = get_user_by_chat_id(chat_id)

    empire = get_empire_by_user(user)

    if isinstance(user, dict) and user.get("error"):

        agreement_text = (
            f"📜 Прежде чем начать игру, ознакомьтесь с Пользовательским соглашением и Политикой конфиденциальности.\n\n"
            f"Контакты: https://agwcorp.ru\n\n"
            f"Чтобы продолжить использование бота, подтвердите, что вы согласны с его условиями.\n\n"
            f"👇 Выберите один из вариантов:"
        )



        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(i18n.t("buttons.user_agreement"), url="https://agwcorp.ru/agreement"),
                    InlineKeyboardButton(i18n.t("buttons.privacy_policy"), url="https://agwcorp.ru/policy"),
                ],
                [InlineKeyboardButton(i18n.t("buttons.confirm"), callback_data="confirm_agreement")],
            ]
        )
        await update.message.reply_text(agreement_text, reply_markup=keyboard)
    else:

        if not empire:
            await update.message.reply_text(
                text=i18n.t("messages.welcome_1"),
                reply_markup=InlineKeyboardMarkup(
                    inline_keyboard=[[InlineKeyboardButton(i18n.t("buttons.create_empire"), callback_data="create_empire")]]
                ),
            )
        else:
            await update.message.reply_text(
                text=i18n.t("messages.welcome_2", username=user.username, empire_name=empire.name, empire_rating_layer_name=rating_name[empire.rating_layer.name]),
                reply_markup=ReplyKeyboardMarkup(
                    keyboard=[
                        [KeyboardButton(i18n.t("buttons.keyboard_menu"))],
                        [KeyboardButton(i18n.t("buttons.keyboard_profile"))],
                        [KeyboardButton(i18n.t("buttons.keyboard_support"))]
                    ],
                    resize_keyboard=True,
                )
            )
    return ConversationHandler.END



async def confirm_agreement_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.callback_query.from_user.id
    username = update.callback_query.from_user.username or "username_tg"

    try:
        new_user, created = create_user(chat_id, username)
        if created:
            try:
                await update.callback_query.message.delete()
            except Exception as err:
                print(err)
            await update.callback_query.message.reply_text(
                text=i18n.t("messages.success_register"),
                reply_markup=InlineKeyboardMarkup(
                    inline_keyboard=[[InlineKeyboardButton(i18n.t("buttons.create_empire"), callback_data="create_empire_handler")]]
                ),
            )
        else:
            try:
                await update.callback_query.message.delete()
            except Exception as err:
                print(err)
            await update.callback_query.message.reply_text(
                text=i18n.t("messages.already_register"),
                reply_markup=InlineKeyboardMarkup(
                    inline_keyboard=[[InlineKeyboardButton(i18n.t("buttons.create_empire"), callback_data="create_empire_handler")]]
                ),
            )
    except Exception as e:
        print(e)
        await update.callback_query.message.reply_text(
            text=i18n.t("errors.err_register")
        )



async def create_empire_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.callback_query.message.delete()

    chat_id = update.callback_query.from_user.id

    message = i18n.t("messages.requirements_name_empire")

    message = await update.callback_query.message.reply_text(
        text=message,
        parse_mode="HTML"
    )
    context.user_data['chat_id'] = chat_id
    context.user_data['last_message'] = message.message_id
    return WAITING_FOR_NAME_EMPIRE



async def process_empire_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if 'last_message' in context.user_data and 'chat_id' in context.user_data:
        await context.bot.delete_message(context.user_data.get('chat_id'), context.user_data.get('last_message'))

    name = update.message.text.strip()

    if not is_valid_empire_name(name):
        message = await update.message.reply_text(
            text=i18n.t("incorrect_input.incr_name_empire"),
            parse_mode="HTML"
        )
        context.user_data['last_message'] = message.message_id
        return WAITING_FOR_NAME_EMPIRE

    if is_empire_name_taken(name):
        message = await update.message.reply_text(
            text=i18n.t("incorrect_input.name_empire_already_exists")
        )
        context.user_data['last_message'] = message.message_id
        return WAITING_FOR_NAME_EMPIRE

    context.user_data['empire_name'] = name

    keyboard = [
        [InlineKeyboardButton(i18n.t("buttons.confirm"), callback_data="confirm_create_empire_handler")],
        [InlineKeyboardButton(i18n.t("buttons.cancel"), callback_data="cancel_create_empire_handler")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    message = await update.message.reply_text(
        text=i18n.t("messages.confirm_name_empire", name=name),
        reply_markup=reply_markup,
        parse_mode="HTML"
    )
    context.user_data['last_message'] = message.message_id

    return CONFIRMATION_NAME_EMPIRE



async def confirm_create_empire_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.callback_query.from_user.id
    empire_name = context.user_data.get("empire_name")

    if not empire_name:
        await update.callback_query.edit_message_text(
            text=i18n.t("messages.none_empire_name")
        )
        return ConversationHandler.END

    user = get_user_by_chat_id(chat_id)

    if not user:
        await update.callback_query.edit_message_text(
            text=i18n.t("messages.none_user")
        )
        return ConversationHandler.END

    empire = create_empire(user, empire_name)

    if not empire:
        await update.callback_query.edit_message_text(
            text=i18n.t("errors.other_err_name_empire")
        )
        return WAITING_FOR_NAME_EMPIRE

    context.user_data.clear()

    loading_messages = [
        i18n.t("labels.lbl_creating_empire"),
        i18n.t("labels.lbl_connect_world"),
        i18n.t("labels.lbl_loading")
    ]

    message = None
    for msg in loading_messages:
        try:

            if message is None:
                message = await update.callback_query.edit_message_text(
                    text=msg
                )
            else:
                await message.edit_text(
                    text=msg
                )


            await asyncio.sleep(1)
        except Exception as e:

            break


    if message:
        try:
            await message.delete()
        except Exception as e:
            pass


    assign_quest_to_empire(empire, "build_lab_name_quest")


    await context.bot.send_message(
        chat_id=chat_id,
        text=i18n.t("messages.create_empire_success", empire_name=empire_name),
        parse_mode="HTML",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(i18n.t("buttons.keyboard_menu"))],
                [KeyboardButton(i18n.t("buttons.keyboard_profile"))],
                [KeyboardButton(i18n.t("buttons.keyboard_support"))]
            ],
            resize_keyboard=True,
        )
    )

    await asyncio.sleep(1)

    msg_start = (
        f"👋 <b>Добро пожаловать в <u>Экономические войны</u></b> — "
        f"экономическую стратегию в реальном времени прямо в Telegram!\n\n"
        f"Ты один из первых игроков в нашей <b>первой версии</b> игры, поэтому будь готов к небольшим "
        f"багам и недочётам — мы активно работаем над улучшением.\n\n"
        f"💡 <b>Поддержи развитие проекта</b> — https://boosty.to/mr_anarch1st/donate"
        f"📩 По всем техническим вопросам ты можешь связаться с разработчиком — "
        f'<a href="https://t.me/anarch1st_agw">@anarch1st_agw</a>\n\n'
        f"📢 Также, чтобы поддержать разработку, подпишись на мой канал — "
        f'<a href="https://t.me/anarchygameworld">t.me/anarchygameworld</a>\n\n'
        f"<b>Удачи в экономических сражениях!</b> 💼💰"
    )

    await context.bot.send_message(
        chat_id=chat_id,
        text=msg_start,
        parse_mode="HTML"
    )

    await asyncio.sleep(2)

    await context.bot.send_message(
        chat_id=chat_id,
        text=i18n.t("messages.storyline_task_first"),
        parse_mode="HTML"
    )

    return ConversationHandler.END



async def cancel_create_empire_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    chat_id = update.callback_query.from_user.id
    await delete_last_message(context, chat_id)


    message = await update.callback_query.message.reply_text(
        text=i18n.t("notifications.cancel_create_empire")
    )
    context.user_data["last_message"] = message.message_id
    return WAITING_FOR_NAME_EMPIRE



async def menu_game_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    keyboard = [
        [InlineKeyboardButton(i18n.t("buttons.menu_game_news"), callback_data="news_page:1")],
        [InlineKeyboardButton(i18n.t("buttons.menu_game_statistics"), callback_data="statistics_empire")],
        [InlineKeyboardButton(i18n.t("buttons.menu_game_manage_empire"), callback_data="manage_empire_handler")],
        [InlineKeyboardButton(i18n.t("buttons.menu_game_cluster"), callback_data="cluster_map_handler")],
        [InlineKeyboardButton(i18n.t("buttons.menu_game_market"), callback_data="market_ingame_handler")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        text=i18n.t("messages.menu_game"),
        reply_markup=reply_markup,
        parse_mode="HTML"
    )



async def menu_game_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.callback_query.answer()


    keyboard = [
        [InlineKeyboardButton(i18n.t("buttons.menu_game_news"), callback_data="news_page:1")],
        [InlineKeyboardButton(i18n.t("buttons.menu_game_statistics"), callback_data="statistics_empire")],
        [InlineKeyboardButton(i18n.t("buttons.menu_game_manage_empire"), callback_data="manage_empire_handler")],
        [InlineKeyboardButton(i18n.t("buttons.menu_game_cluster"), callback_data="cluster_map_handler")],
        [InlineKeyboardButton(i18n.t("buttons.menu_game_market"), callback_data="market_ingame_handler")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)


    await update.callback_query.edit_message_text(
        text=i18n.t("messages.menu_game"),
        reply_markup=reply_markup,
        parse_mode="HTML"
    )



async def statistics_empire_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    await update.callback_query.answer()


    chat_id = update.callback_query.from_user.id
    user = get_user_by_chat_id(chat_id)
    empire = get_empire_by_user(user)

    empire_position = get_empire_rank(empire)

    rating_layer = empire.rating_layer
    rating_points = empire.rating_points
    level = empire.level
    current_progress_scale = empire.current_progress_scale

    buildings_count = get_completed_buildings_count(empire)
    max_buildings = get_total_buildings_count()

    technologies_count = get_completed_research_count(empire)
    max_technologies = get_total_technologies_count()

    items_count = get_empire_items_count(empire)

    next_rating_points = "∞" if empire.ready_to_upgrade else (
        rating_layer.max_rating_points if rating_layer else "—"
    )

    rating_layer_name = rating_layer.name if rating_layer else i18n.t("labels.no_data")

    keyboard = []


    message_parts = [
        i18n.t("render.statistics.line_01", empire_position=empire_position),
        i18n.t("render.statistics.line_02"),
        i18n.t("render.statistics.line_03"),
        f"🎖️ <i>{rating_name[rating_layer_name]}</i>\n",
        i18n.t("render.statistics.line_05", rating_points=rating_points, next_rating_points=next_rating_points),
        i18n.t("render.statistics.line_06"),
        i18n.t("render.statistics.line_07", level=level),
        i18n.t("render.statistics.line_08", current_progress_scale=current_progress_scale, empire=empire),
        i18n.t("render.statistics.line_09"),
        i18n.t("render.statistics.line_10", buildings_count=buildings_count, max_buildings=max_buildings),
        i18n.t("render.statistics.line_11", technologies_count=technologies_count, max_technologies=max_technologies),
        i18n.t("render.statistics.line_12", items_count=items_count),
        i18n.t("render.statistics.line_13"),
    ]

    message = "".join(message_parts)

    if empire.ready_to_upgrade:
        keyboard.append([InlineKeyboardButton(i18n.t("buttons.level_up"), callback_data="process_upgrade_cluster")])

    keyboard.append([InlineKeyboardButton("Текущий сезон", callback_data="current_season")])

    if get_active_event():
        keyboard.append([InlineKeyboardButton("Текущее событие", callback_data="current_event")])

    keyboard.append([InlineKeyboardButton(i18n.t("buttons.table_rating_web"), url="https://agwcorp.ru/rating")])

    keyboard.append([ InlineKeyboardButton(i18n.t("buttons.back"), callback_data="menu_game_handler")])
    reply_markup = InlineKeyboardMarkup(keyboard)


    await update.callback_query.edit_message_text(
        text=message,
        reply_markup=reply_markup,
        parse_mode="HTML"
    )


async def process_upgrade_cluster(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.callback_query.answer()

    chat_id = update.callback_query.from_user.id
    user = get_user_by_chat_id(chat_id)
    empire = get_empire_by_user(user)

    current_layer = get_current_rating_layer(empire.rating_layer)
    target_layer = get_target_rating_layer(empire.rating_points)

    if current_layer == target_layer:
        await update.callback_query.edit_message_text(
            text=i18n.t("notifications.already_level"),
            parse_mode="HTML"
        )
        return


    move_empire_to_new_layer(empire, target_layer)
    empire.ready_to_upgrade = False
    empire.save()

    keyboard = [[ InlineKeyboardButton(i18n.t("buttons.back_to_menu"), callback_data="menu_game_handler")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.callback_query.edit_message_text(
        text=i18n.t("notifications.moved_to_new_cluster"),
        reply_markup=reply_markup,
        parse_mode="HTML"
    )


async def handle_current_season(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    now = datetime.now()
    season = get_current_season()

    if not season:
        await query.edit_message_text("⛔️ В данный момент сезон не активен.")
        return

    text = (
        f"📅 <b>{season_name[season.name]}</b>\n"
        f"🗓 {season.start_date.strftime('%d.%m.%Y')} — {season.end_date.strftime('%d.%m.%Y')}\n\n"
    )

    if season.theme_description:
        text += f"🎨 <i>{season.theme_description}</i>\n\n"

    if season.reward_description:
        text += f"🏆 <b>Награды за 1 место в таблице рейтинга:</b>\n\n{season.reward_description}\n"

    keyboard = [
        [InlineKeyboardButton("🔙 Назад", callback_data="statistics_empire")]
    ]

    await query.edit_message_text(
        text=text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="HTML"
    )


async def handle_current_event(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    now = datetime.now()
    active_event = get_active_event()

    if not active_event:
        await query.edit_message_text("⚠️ Сейчас нет активного события.")
        return

    template = active_event.template
    target_str = f"🎯 Цель: {template.target}" if template.target else ""
    value_sign = "+" if template.value >= 0 else ""
    effect_str = f"{value_sign}{template.value * 100:.0f}%"

    text = (
        f"🔥 <b>{template.name}</b>\n"
        f"📆 {active_event.start_time.strftime('%d.%m %H:%M')} — {active_event.end_time.strftime('%d.%m %H:%M')}\n"
        f"🌀 Эффект: <b>{events_effects_name[template.effect_type]}</b>\n"
        f"{target_str}\n"
        f"📊 Значение: <b>{effect_str}</b>\n"
    )

    keyboard = [
        [InlineKeyboardButton("🔙 Назад", callback_data="statistics_empire")]
    ]

    await query.edit_message_text(
        text=text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="HTML"
    )



async def manage_empire_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.callback_query.answer()


    chat_id = update.callback_query.from_user.id
    user = get_user_by_chat_id(chat_id)
    empire = get_empire_by_user(user)

    resources = get_total_resources(empire)

    science_speed = get_science_research_speed(empire)

    outgoing_attacks = get_outgoing_attacks_count(empire)
    incoming_attacks = get_incoming_attacks_count(empire)

    defense_bonus, gold_upkeep_per_hour = get_empire_defense_info(empire)


    message_parts = [
        i18n.t("render.manage_empire.line_01"),
        i18n.t("render.manage_empire.line_02", defense_bonus=defense_bonus, gold_upkeep_per_hour=gold_upkeep_per_hour),
        i18n.t("render.manage_empire.line_03", science_speed=science_speed),





        i18n.t("render.manage_empire.line_09", render_energy_status=render_energy_status(empire)),
        i18n.t("render.manage_empire.line_10"),
        i18n.t("render.manage_empire.line_11", units_army_value=resources['units_army']),
        i18n.t("render.manage_empire.line_12", units_spy_value=resources['units_spy']),
        i18n.t("render.manage_empire.line_13", units_counterspy_value=resources['units_counterspy']),
        i18n.t("render.manage_empire.line_14", units_exploration_value=resources['units_exploration']),
        i18n.t("render.manage_empire.line_15", outgoing_attacks=outgoing_attacks),
        i18n.t("render.manage_empire.line_16", incoming_attacks=incoming_attacks),
    ]
    message = "".join(message_parts)

    is_market_unlocked = is_research_completed(empire, "tech_market")

    market_button_text = (
        f"{i18n.t('buttons.market')}"
        if is_market_unlocked else
        f"{i18n.t('buttons.market')} 🔒"
    )


    keyboard = [

        [InlineKeyboardButton(i18n.t("buttons.buildings"), callback_data="empire_buildings_handler")],
        [InlineKeyboardButton(i18n.t("buttons.technologies"), callback_data="empire_technologies_handler")],
        [InlineKeyboardButton(i18n.t("buttons.missions"), callback_data="empire_missions_handler")],
        [InlineKeyboardButton(market_button_text, callback_data="empire_market_handler")],
        [InlineKeyboardButton("📦 Инвентарь", callback_data="empire_inventory_handler")],
        [InlineKeyboardButton("🌀 Эффекты империи", callback_data="empire_effects_handler")],
        [InlineKeyboardButton(i18n.t("buttons.back"), callback_data="menu_game_handler")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)


    await update.callback_query.edit_message_text(
        text=message,
        parse_mode="HTML",
        reply_markup=reply_markup
    )

    return ConversationHandler.END



async def profile_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    chat_id = update.message.chat.id
    user = get_user_by_chat_id(chat_id)

    username = user.username

    subscription_status = user.subscription_status
    subscription_end = user.subscription_end if subscription_status else None

    keyboard = []



    if subscription_status:
        subscription_message = i18n.t("labels.sub_status_active", subscription_end=subscription_end)
    else:
        keyboard.append([InlineKeyboardButton(i18n.t("buttons.profile_subscribe"), callback_data="subscribe_menu_handler")])
        subscription_message = i18n.t("labels.sub_status_nonactive")


    message_parts = [
        i18n.t("render.profile.line_01"),
        i18n.t("render.profile.line_02", username=username),

        i18n.t("render.profile.line_04", subscription_message=subscription_message),
        i18n.t("render.profile.line_05")
    ]
    message = "".join(message_parts)

    reply_markup = InlineKeyboardMarkup(keyboard)


    await update.message.reply_text(
        text=message,
        reply_markup=reply_markup,
        parse_mode="HTML"
    )



async def profile_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    chat_id = query.from_user.id
    user = get_user_by_chat_id(chat_id)

    username = user.username

    subscription_status = user.subscription_status
    subscription_end = user.subscription_end if subscription_status else None

    keyboard = []



    if subscription_status:
        subscription_message = i18n.t("labels.sub_status_active", subscription_end=subscription_end)
    else:
        keyboard.append([InlineKeyboardButton(i18n.t("buttons.profile_subscribe"), callback_data="subscribe_menu_handler")])
        subscription_message = i18n.t("labels.sub_status_nonactive")


    message_parts = [
        i18n.t("render.profile.line_01"),
        i18n.t("render.profile.line_02", username=username),

        i18n.t("render.profile.line_04", subscription_message=subscription_message),
        i18n.t("render.profile.line_05")
    ]
    message = "".join(message_parts)

    reply_markup = InlineKeyboardMarkup(keyboard)


    await update.callback_query.edit_message_text(
        text=message,
        reply_markup=reply_markup,
        parse_mode="HTML"
    )



async def support_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        text=i18n.t("render.support.line_01"),
        parse_mode="HTML"
    )


def main() -> None:
    application = Application.builder().token(BOT_TOKEN).build()

    conversation_handler_create_empire = ConversationHandler(
        entry_points=[CallbackQueryHandler(create_empire_handler, pattern="create_empire_handler")],
        states={
            WAITING_FOR_NAME_EMPIRE: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND, process_empire_name
                )
            ],
            CONFIRMATION_NAME_EMPIRE: [
                CallbackQueryHandler(confirm_create_empire_handler, pattern="confirm_create_empire_handler"),
                CallbackQueryHandler(cancel_create_empire_handler, pattern="cancel_create_empire_handler")
            ],
        },
        fallbacks=[
            CallbackQueryHandler(cancel_create_empire_handler, pattern="cancel_create_empire_handler")
        ],
    )


    application.add_handler(conversation_handler_create_empire)
    application.add_handler(conversation_handler_attack_empire)
    application.add_handler(conversation_handler_espionage_empire)
    application.add_handler(conversation_handler_exploration)
    application.add_handler(conversation_handler_attack_location)
    application.add_handler(conversation_handler_market)

    application.add_handler(CommandHandler("start", start_command_handler))
    application.add_handler(CallbackQueryHandler(confirm_agreement_handler, pattern="^confirm_agreement$"))
    application.add_handler(CallbackQueryHandler(create_empire_handler, pattern="^create_empire$"))
    application.add_handler(CallbackQueryHandler(game_news_handler, pattern=r'^news_page:\d+$'))
    application.add_handler(CallbackQueryHandler(statistics_empire_handler, pattern="^statistics_empire$"))
    application.add_handler(CallbackQueryHandler(process_upgrade_cluster, pattern="^process_upgrade_cluster$"))
    application.add_handler(CallbackQueryHandler(handle_current_season, pattern="^current_season$"))
    application.add_handler(CallbackQueryHandler(handle_current_event, pattern="^current_event$"))
    application.add_handler(CallbackQueryHandler(manage_empire_handler, pattern="^manage_empire_handler$"))

    application.add_handler(CallbackQueryHandler(cluster_map_handler, pattern="^cluster_map_handler$"))
    application.add_handler(CallbackQueryHandler(cluster_map_finder_locations, pattern="^cluster_map_finder_locations$"))
    application.add_handler(CallbackQueryHandler(location_report_handler, pattern=r"^location_report_[\w]+$"))
    application.add_handler(CallbackQueryHandler(cluster_map_list_empiries, pattern=r"^cluster_map_list_empiries$|^cluster_map_list_page_\d+$"))
    application.add_handler(CallbackQueryHandler(cluster_map_finder_locations,pattern=r"^cluster_map_finder_locations_page_\d+$"))

    application.add_handler(CallbackQueryHandler(menu_game_handler, pattern="^menu_game_handler$"))

    application.add_handler(CallbackQueryHandler(empire_buildings_handler, pattern="^empire_buildings_handler$"))
    application.add_handler(CallbackQueryHandler(empire_buildings_military_handler, pattern="^empire_buildings_military_handler$"))
    application.add_handler(CallbackQueryHandler(empire_buildings_economics_handler, pattern="^empire_buildings_economics_handler$"))
    application.add_handler(CallbackQueryHandler(empire_buildings_social_handler, pattern="^empire_buildings_social_handler$"))
    application.add_handler(CallbackQueryHandler(empire_build_handler, pattern=r"^build:"))
    application.add_handler(CallbackQueryHandler(cancel_build_handler, pattern=r"^cancel_build:"))
    application.add_handler(CallbackQueryHandler(upgrade_building_handler, pattern=r"^upgrade:"))
    application.add_handler(CallbackQueryHandler(hire_units_handler, pattern=r"^hire_units:.+:\d+$"))

    application.add_handler(CallbackQueryHandler(empire_technologies_handler, pattern="^empire_technologies_handler$"))
    application.add_handler(CallbackQueryHandler(empire_research_general_handler, pattern=r'^empire_research_general:\d+$'))
    application.add_handler(CallbackQueryHandler(empire_research_extracting_handler, pattern="^empire_research_extracting_handler$"))
    application.add_handler(CallbackQueryHandler(extracting_category_handler, pattern="^extracting_category:.+"))
    application.add_handler(CallbackQueryHandler(building_research_handler, pattern="^building_research:\\d+:extracting$"))
    application.add_handler(CallbackQueryHandler(research_menu_handler, pattern="^research_menu:\\d+:.+$"))
    application.add_handler(CallbackQueryHandler(start_research_handler, pattern="^start_research:\\d+:.+$"))
    application.add_handler(CallbackQueryHandler(cancel_research_handler, pattern=r"^cancel_research:\d+"))

    application.add_handler(CallbackQueryHandler(empire_missions_handler, pattern="empire_missions_handler"))
    application.add_handler(CallbackQueryHandler(empire_missions_current_missions_handler, pattern="empire_missions_current_missions_handler"))
    application.add_handler(CallbackQueryHandler(current_mission_details_handler, pattern=r"^current_mission_\d+$"))
    application.add_handler(CallbackQueryHandler(empire_missions_results_missions_handler, pattern="empire_missions_results_missions_handler"))
    application.add_handler(CallbackQueryHandler(mission_result_handler, pattern=r"^mission_result_\d+$"))
    application.add_handler(CallbackQueryHandler(cancel_mission_handler, pattern=r"^cancel_mission_\d+$"))

    application.add_handler(CallbackQueryHandler(empire_market_handler, pattern="empire_market_handler"))
    application.add_handler(CallbackQueryHandler(empire_market_sell_item, pattern="^empire_market_sell_item$"))
    application.add_handler(CallbackQueryHandler(confirm_item_sell, pattern=r"^sell_item_\d+$"))
    application.add_handler(CallbackQueryHandler(perform_item_sale, pattern="^confirm_item_sale$"))

    application.add_handler(CallbackQueryHandler(empire_inventory_handler, pattern="empire_inventory_handler"))
    application.add_handler(CallbackQueryHandler(empire_inventory_items_handler, pattern="^empire_inventory_items_handler_\\d+$"))

    application.add_handler(CallbackQueryHandler(empire_effects_handler, pattern="empire_effects_handler"))

    application.add_handler(CallbackQueryHandler(empire_building_menu_handler, pattern="empire_building_menu_handler"))

    application.add_handler(CallbackQueryHandler(profile_handler, pattern="^profile_handler"))
    application.add_handler(CallbackQueryHandler(subscribe_menu_handler, pattern="^subscribe_menu_handler"))


    application.add_handler(CallbackQueryHandler(market_ingame_handler, pattern="^market_ingame_handler"))
    application.add_handler(CallbackQueryHandler(daily_free_resources, pattern="^daily_free_resources"))
    application.add_handler(CallbackQueryHandler(handle_get_standard_set, pattern="^get_standard_set$"))
    application.add_handler(CallbackQueryHandler(handle_get_lucky_item, pattern="^get_lucky_item$"))
    application.add_handler(CallbackQueryHandler(bonuses_busters_menu, pattern="^bonuses_busters_menu"))





    application.add_handler(MessageHandler(filters.TEXT & filters.Regex(i18n.t("buttons.keyboard_menu")), menu_game_button))
    application.add_handler(MessageHandler(filters.TEXT & filters.Regex(i18n.t("buttons.keyboard_profile")), profile_button))
    application.add_handler(MessageHandler(filters.TEXT & filters.Regex(i18n.t("buttons.keyboard_support")), support_button))

    application.run_polling()

if __name__ == "__main__":
    main()
