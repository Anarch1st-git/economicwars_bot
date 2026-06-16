from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackQueryHandler, MessageHandler, filters, ConversationHandler, ContextTypes
from handlers import (
    get_user_by_chat_id,
    get_empire_by_user,
    get_current_missions_by_empire,
    get_empire_by_id,
    are_empires_in_same_cluster,
    get_resource_count,
    start_mission_attack,
    start_mission_espionage,
    start_mission_exploration,
    get_location_by_id,
    start_mission_attack_location,
    get_total_empires_from_cluster,
    get_mission_by_id,
    get_mission_speed_modifiers,
    render_progress_bar_emoji,
    get_units_exploration,
    has_completed_barracks,
    get_units_army,
    calculate_time_for_mission_attack,
    calculate_time_for_mission_espionage,
    calculate_time_for_mission_exploration,
    has_completed_spy_center,
    get_units_spy,
    has_completed_exp_corpus,
    cancel_mission_by_id,
    update_mission_progress
)
from models import (
    Mission,
    EmpireLocations,
    EmpireMission,
    EmpireMissionResult,
    EmpireStatus
)
from states_for_dialogs import (
    WAITING_ID_ATTACKING_EMPIRE,
    WAITING_COUNT_UNITS_ATTACKING_EMPIRE,
    CONFIRMATION_FOR_ATTACK_EMPIRE,
    WAITING_ID_ESPIONAGE_EMPIRE,
    WAITING_COUNT_UNITS_ESPIONAGE_EMPIRE,
    CONFIRMATION_FOR_ESPIONAGE_EMPIRE,
    WAITING_RADIUS_FOR_EXPLORATION,
    WAITING_COUNT_UNITS_EXPLORATION,
    CONFIRMATION_FOR_EXPLORATION_EMPIRE,
    WAITING_COUNT_UNITS_ATTACKING_LOCATION,
    CONFIRMATION_FOR_ATTACK_LOCATION
)
from validations import (
    validate_empire_id,
    validate_positive_number
)
from utils_messages import delete_last_message
from datetime import datetime
from i18n import I18N
from locales.locales_names import mission_type, locations_name


i18n = I18N("ru")



async def empire_missions_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.callback_query.answer()


    chat_id = update.callback_query.from_user.id
    user = get_user_by_chat_id(chat_id)


    message_parts = [
        i18n.t("render.missions.caption.line_01"),
        i18n.t("render.missions.caption.line_02"),
        i18n.t("render.missions.caption.line_03"),
        i18n.t("render.missions.caption.line_04"),
        i18n.t("render.missions.caption.line_05")
    ]
    message = "".join(message_parts)


    keyboard = [
        [InlineKeyboardButton(i18n.t("render.missions.buttons.current_missions"), callback_data="empire_missions_current_missions_handler")],
        [InlineKeyboardButton(i18n.t("render.missions.buttons.results_missions"), callback_data="empire_missions_results_missions_handler")],
        [InlineKeyboardButton(i18n.t("render.missions.buttons.mission_attack"), callback_data="empire_missions_attack_handler")],
        [InlineKeyboardButton(i18n.t("render.missions.buttons.mission_espionage"), callback_data="empire_missions_espionage_handler")],
        [InlineKeyboardButton(i18n.t("render.missions.buttons.mission_exploration"), callback_data="empire_missions_exploration_handler")],
        [InlineKeyboardButton(i18n.t("buttons.back"), callback_data="manage_empire_handler")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.callback_query.edit_message_text(
        text=message,
        reply_markup=reply_markup,
        parse_mode="HTML"
    )

    return ConversationHandler.END



async def empire_missions_current_missions_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.callback_query.answer()

    chat_id = update.callback_query.from_user.id
    user = get_user_by_chat_id(chat_id)
    empire = get_empire_by_user(user)

    current_missions = get_current_missions_by_empire(empire)

    keyboard = []

    for mission in current_missions:

        keyboard.append([
            InlineKeyboardButton(i18n.t("render.missions.buttons.mission_view_details", mission_type=mission_type[mission.mission_type.name]),
                                 callback_data=f"current_mission_{mission.mission_id}")
        ])

    message = i18n.t("render.missions.labels.current_missions") if keyboard else i18n.t("render.missions.labels.non_missions")

    keyboard.append([InlineKeyboardButton(i18n.t("buttons.back"), callback_data="empire_missions_handler")])
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.callback_query.edit_message_text(
        text=message,
        reply_markup=reply_markup,
        parse_mode="HTML"
    )


async def current_mission_details_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.callback_query.answer()

    query = update.callback_query
    mission_id = int(query.data.split("_")[-1])

    mission = get_mission_by_id(mission_id)
    if not mission:
        await query.edit_message_text(
            text=i18n.t("render.missions.labels.not_found_mission")
        )
        return

    if mission.location:
        target_text = mission.location.name
    elif mission.target:
        target_text = f"{mission.target.name}, ID: {mission.target.empire_id}"
    elif mission.mission_type.name == "exploration":
        target_text = i18n.t("render.missions.labels.exploration_territory")
    else:
        target_text = i18n.t("labels.unknown")

    now = datetime.now()
    time_passed = (now - mission.last_update).total_seconds()


    base_speed = 1.0
    modifiers = get_mission_speed_modifiers(mission.empire)
    actual_speed = base_speed * modifiers

    progress_gained = actual_speed * time_passed
    mission.progress += progress_gained
    mission.last_update = now

    progress_bar_emoji = render_progress_bar_emoji(mission.progress, mission.total_points)

    remaining = max(mission.total_points - mission.progress, 0)
    if actual_speed > 0:
        seconds_left = remaining / actual_speed
        h, m, s = int(seconds_left // 3600), int((seconds_left % 3600) // 60), int(seconds_left % 60)
        time_left_str = f"{h}{i18n.t('legend.h')} {m}{i18n.t('legend.m')} {s}{i18n.t('legend.s')}"
    else:
        time_left_str = i18n.t("legend.infinity")

    message_parts = [
        i18n.t("render.missions.current_mission_report.line_01", mission_type=mission_type[mission.mission_type.name]),
        i18n.t("render.missions.current_mission_report.line_02", target_text=locations_name[target_text]),
        i18n.t("render.missions.current_mission_report.line_03", units_sent=mission.units_sent),
        i18n.t("render.missions.current_mission_report.line_04", time_left_str=time_left_str)
    ]

    mission_text = "".join(message_parts)
    mission_text += f"{progress_bar_emoji}\n"


    keyboard = [[InlineKeyboardButton(i18n.t("buttons.back"), callback_data="empire_missions_current_missions_handler")]]


    if mission.status == "pending":
        keyboard.insert(0, [InlineKeyboardButton("❌ Отменить миссию", callback_data=f"cancel_mission_{mission.mission_id}")])

    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        text=mission_text,
        reply_markup=reply_markup,
        parse_mode="HTML"
    )


async def cancel_mission_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    mission_id = int(query.data.split("_")[-1])

    mission = get_mission_by_id(mission_id)
    if not mission:
        await query.edit_message_text(
            text=i18n.t("render.missions.labels.not_found_mission")
        )
        return

    chat_id = query.from_user.id
    user = get_user_by_chat_id(chat_id)
    empire = get_empire_by_user(user)

    update_mission_progress(mission)

    remaining_seconds = max(mission.total_points - mission.progress, 0) / get_mission_speed_modifiers(empire)

    if remaining_seconds < 300:
        await query.edit_message_text(
            text="Миссию нельзя отменить — осталось меньше 5 минут до завершения."
        )
        return

    result, message = cancel_mission_by_id(empire, mission)

    await query.edit_message_text(
        text=message,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton(i18n.t("buttons.back"), callback_data="empire_missions_current_missions_handler")]
        ])
    )



async def empire_missions_results_missions_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.callback_query.answer()

    chat_id = update.callback_query.from_user.id
    user = get_user_by_chat_id(chat_id)
    empire = get_empire_by_user(user)


    mission_results = (EmpireMissionResult
        .select()
        .where(EmpireMissionResult.empire == empire)
        .order_by(EmpireMissionResult.created_at.desc())
        .limit(10))

    keyboard = []

    for result in mission_results:

        keyboard.append([
            InlineKeyboardButton(f"📜 {result.mission_id} - {'✅' if result.success else '❌'}",
                                 callback_data=f"mission_result_{result.mission_result_id}")
        ])


    message = i18n.t("render.missions.labels.results_missions") if keyboard else i18n.t("render.missions.labels.not_found_completed_missions")

    keyboard.append([InlineKeyboardButton(i18n.t("buttons.back"), callback_data="empire_missions_handler")])
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.callback_query.edit_message_text(
        text=message,
        reply_markup=reply_markup,
        parse_mode="HTML"
    )


async def mission_result_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.callback_query.answer()
    query = update.callback_query
    mission_result_id = int(query.data.split("_")[-1])


    try:
        result = EmpireMissionResult.get_by_id(mission_result_id)
    except EmpireMissionResult.DoesNotExist:
        await query.edit_message_text("❌ Результат миссии не найден.")
        return


    mission_text = (
        f"<b>📜 Отчёт по миссии #{result.mission_id}</b>\n"
        f"{result.description}\n\n"
        f"<b>✅ Успешность:</b> {'Да' if result.success else 'Нет'}\n"
        f"<b>🚀 Отправлено юнитов:</b> {result.units_sent}\n"
        f"<b>🎯 Цель (юнитов):</b> {result.target_units}\n"
        f"<b>💀 Потери:</b> {result.units_lost}\n"
        f"<b>🎒 Вернулось:</b> {result.units_return}\n\n"
        f"<b>🪵 Древесина:</b> {result.loot_wood}\n"
        f"<b>🪙 Золото:</b> {result.loot_gold}\n"
        f"<b>🛢️ Нефть:</b> {result.loot_oil}\n"
        f"<b>💎 Алмазы:</b> {result.loot_diamond}\n"
    )


    if result.loot_items:
        loot_items_str = "\n".join(f"• {k}: {v}" for k, v in result.loot_items.items())
        mission_text += f"\n<b>🎁 Предметы:</b>\n{loot_items_str}\n"


    if result.intel_data:
        intel_str = "\n".join(f"• {k}: {v}" for k, v in result.intel_data.items())
        mission_text += f"\n<b>🕵️ Шпионаж:</b>\n{intel_str}\n"

    mission_text += f"\n<b>📅 Завершено:</b> {result.created_at.strftime('%Y-%m-%d %H:%M:%S')}"


    keyboard = [[
        InlineKeyboardButton("🔙 Назад", callback_data="empire_missions_results_missions_handler")
    ]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        text=mission_text,
        reply_markup=reply_markup,
        parse_mode="HTML"
    )



async def empire_missions_attack_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.callback_query.answer()

    PAGE_SIZE = 10

    chat_id = update.callback_query.from_user.id
    user = get_user_by_chat_id(chat_id)
    empire = get_empire_by_user(user)

    cancel_keyboard = InlineKeyboardMarkup(
        [[InlineKeyboardButton("❌ Отмена", callback_data="cancel_missions_attack_handler")]]
    )

    if not has_completed_barracks(empire):
        await update.callback_query.edit_message_text(
            text="🏗️ У вас нет построенной казармы. Постройте её, чтобы тренировать войска, атаковать локации и другие империи.",
            reply_markup=cancel_keyboard,
            parse_mode="HTML"
        )
        return ConversationHandler.END

    if get_units_army(empire) <= 0:
        await update.callback_query.edit_message_text(
            text="⚔️ У вас нет войск для атаки. Нанимайте армию в казармах перед отправкой миссии.",
            reply_markup=cancel_keyboard,
            parse_mode="HTML"
        )
        return ConversationHandler.END


    mission_type = Mission.get_or_none(Mission.name == "attack")
    if mission_type is None:
        raise ValueError(f"Тип миссии {mission_type} не найден в таблице Mission")


    existing_mission = EmpireMission.get_or_none(
        (EmpireMission.empire == empire) &
        (EmpireMission.mission_type == mission_type) &
        (EmpireMission.status == "pending")
    )
    if existing_mission:
        keyboard = [
            [InlineKeyboardButton(i18n.t("buttons.cancel"), callback_data="cancel_missions_attack_handler")]
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.callback_query.edit_message_text(
            text=i18n.t("render.missions.labels.warning_not_sub_missions_attack"),
            reply_markup=reply_markup,
            parse_mode="HTML"
        )
        return

    empires_from_cluster = get_total_empires_from_cluster(empire)
    total_empires = len(empires_from_cluster)

    total_pages = max((total_empires + PAGE_SIZE - 1) // PAGE_SIZE, 1)

    query_data = update.callback_query.data
    if query_data.startswith("attack_empire_page_"):
        page = int(query_data.rsplit('_', 1)[1])
    else:
        page = 0

    page = max(0, min(page, total_pages - 1))

    start_index = page * PAGE_SIZE
    end_index = start_index + PAGE_SIZE
    page_empires = empires_from_cluster[start_index:end_index]

    message_text = i18n.t("render.missions.labels.choise_empire_for_attack")

    keyboard = []
    for empire in page_empires:
        empire_id = empire.id
        empire_name = empire.name
        keyboard.append([InlineKeyboardButton(f"{empire_name}", callback_data=f"attack_empire_{empire_id}")])

    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton(i18n.t("buttons.back"), callback_data=f"attack_empire_page_{page - 1}"))
    if page < total_pages - 1:
        nav_buttons.append(InlineKeyboardButton(i18n.t("buttons.forward"), callback_data=f"attack_empire_page_{page + 1}"))

    if nav_buttons:
        keyboard.append(nav_buttons)

    keyboard.append([InlineKeyboardButton(i18n.t("buttons.cancel"), callback_data="cancel_missions_attack_handler")])

    reply_markup = InlineKeyboardMarkup(keyboard)

    message_send = await update.callback_query.edit_message_text(
        text=message_text,
        reply_markup=reply_markup,
        parse_mode="HTML"
    )

    context.user_data['chat_id'] = chat_id
    context.user_data['last_message'] = message_send.message_id

    return WAITING_ID_ATTACKING_EMPIRE



async def process_id_for_attack_empire(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.callback_query.answer()

    chat_id = update.callback_query.from_user.id
    user = get_user_by_chat_id(chat_id)
    empire = get_empire_by_user(user)

    query_data = update.callback_query.data
    empire_attacked_id = int(query_data.split("_")[-1])

    empire_attacked = get_empire_by_id(empire_attacked_id)

    if not empire_attacked:
        await update.callback_query.edit_message_text(
            text=i18n.t("render.missions.errors.empire_not_found")
        )
        return WAITING_ID_ATTACKING_EMPIRE

    if not are_empires_in_same_cluster(empire.id, empire_attacked_id):
        await update.callback_query.edit_message_text(
            text=i18n.t("render.missions.errors.not_possible_attack_other_claster")
        )
        return WAITING_ID_ATTACKING_EMPIRE

    if empire == empire_attacked:
        await update.callback_query.edit_message_text(
            text=i18n.t("render.missions.errors.not_self_attack")
        )
        return WAITING_ID_ATTACKING_EMPIRE

    context.user_data['empire_attacked_id'] = empire_attacked_id
    context.user_data['chat_id'] = chat_id

    keyboard = [
        [InlineKeyboardButton(i18n.t("buttons.cancel"), callback_data="cancel_missions_attack_handler")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    message_send = await update.callback_query.edit_message_text(
        text=i18n.t("render.missions.labels.enter_count_units_sent", empire_attacked=empire_attacked.name),
        reply_markup=reply_markup
    )

    context.user_data['last_message'] = message_send.message_id

    return WAITING_COUNT_UNITS_ATTACKING_EMPIRE



async def process_count_units_for_attack_empire(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if 'last_message' in context.user_data and 'chat_id' in context.user_data:
        await context.bot.delete_message(context.user_data.get('chat_id'), context.user_data.get('last_message'))

    chat_id = context.user_data.get('chat_id')
    user = get_user_by_chat_id(chat_id)
    empire = get_empire_by_user(user)


    empire_attacked_id = context.user_data.get('empire_attacked_id')


    count_units = update.message.text.strip()


    if not validate_positive_number(count_units):

        keyboard = [
            [InlineKeyboardButton(i18n.t("buttons.cancel"), callback_data="cancel_missions_attack_handler")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            text=i18n.t("render.missions.errors.not_valid_value_count_units"),
            reply_markup=reply_markup
        )
        return WAITING_COUNT_UNITS_ATTACKING_EMPIRE


    count_units = int(count_units)


    current_count_units = get_resource_count(empire, "units_army")
    if current_count_units < count_units:

        keyboard = [
            [InlineKeyboardButton(i18n.t("buttons.cancel"), callback_data="cancel_missions_attack_handler")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            text=i18n.t("render.missions.errors.not_enough_attack_units"),
            reply_markup=reply_markup
        )
        return WAITING_COUNT_UNITS_ATTACKING_EMPIRE


    keyboard = [
        [InlineKeyboardButton(i18n.t("buttons.confirm"), callback_data="confirm_for_attack_empire_handler")],
        [InlineKeyboardButton(i18n.t("buttons.cancel"), callback_data="cancel_missions_attack_handler")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)


    mission_duration_seconds = calculate_time_for_mission_attack(empire, count_units)


    mission_duration_minutes = mission_duration_seconds // 60
    mission_duration_remain_seconds = mission_duration_seconds % 60
    formatted_duration = f"{mission_duration_minutes} мин {mission_duration_remain_seconds:02} сек"

    message_parts = [
        i18n.t("render.missions.labels.confirm_attack_line_01", empire_attacked_id=empire_attacked_id),
        i18n.t("render.missions.labels.confirm_attack_line_02", count_units=count_units),
        f"\nОжидаемое время миссии: {formatted_duration}",
        i18n.t("render.missions.labels.confirm_attack_line_03")
    ]

    message_text = "".join(message_parts)

    message_send = await update.message.reply_text(
        text=message_text,
        reply_markup=reply_markup
    )
    context.user_data['last_message'] = message_send.message_id
    context.user_data['empire_attacked_id'] = empire_attacked_id
    context.user_data['count_units'] = count_units

    return CONFIRMATION_FOR_ATTACK_EMPIRE



async def confirm_for_attack_empire_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.callback_query.from_user.id
    empire_attacked_id = context.user_data.get("empire_attacked_id")
    count_units = context.user_data.get("count_units")

    user = get_user_by_chat_id(chat_id)
    empire = get_empire_by_user(user)

    if not user:
        await update.callback_query.edit_message_text(
            text=i18n.t("errors.none_user")
        )
        return ConversationHandler.END



    mission, msg = start_mission_attack(empire, empire_attacked_id, count_units)

    keyboard = [
        [InlineKeyboardButton(i18n.t("buttons.back_to_menu"), callback_data="empire_missions_handler")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)


    if mission is not None:
        await update.callback_query.edit_message_text(
            text=i18n.t("render.missions.labels.mission_start"),
            reply_markup=reply_markup
        )
    else:
        await update.callback_query.edit_message_text(
            text=msg,
            reply_markup=reply_markup
        )

    return ConversationHandler.END



async def cancel_missions_attack_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    chat_id = update.callback_query.from_user.id
    await delete_last_message(context, chat_id)


    message = await update.callback_query.message.reply_text(
        text=i18n.t("render.missions.labels.mission_attack_calcel")
    )
    context.user_data["last_message"] = message.message_id
    return ConversationHandler.END



async def empire_missions_espionage_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.callback_query.answer()


    chat_id = update.callback_query.from_user.id
    user = get_user_by_chat_id(chat_id)
    empire = get_empire_by_user(user)

    cancel_keyboard = InlineKeyboardMarkup(
        [[InlineKeyboardButton("❌ Отмена", callback_data="cancel_missions_attack_handler")]]
    )

    if not has_completed_spy_center(empire):
        await update.callback_query.edit_message_text(
            text="🏗️ У вас нет построенного разведывательного центра. Постройте сначала разведывательный центр, чтобы тренировать шпионов и выполнять миссии шпионажа в отношении других империй.",
            reply_markup=cancel_keyboard,
            parse_mode="HTML"
        )
        return ConversationHandler.END

    if get_units_spy(empire) <= 0:
        await update.callback_query.edit_message_text(
            text="⚔️ У вас нет шпионов для миссии шпионажа. Тренируйте шпионов в разведывательном центре перед отправкой миссии.",
            reply_markup=cancel_keyboard,
            parse_mode="HTML"
        )
        return ConversationHandler.END


    mission_type = Mission.get_or_none(Mission.name == "espionage")
    if mission_type is None:
        raise ValueError(f"Тип миссии {mission_type} не найден в таблице Mission")


    existing_mission = EmpireMission.get_or_none(
        (EmpireMission.empire == empire) &
        (EmpireMission.mission_type == mission_type) &
        (EmpireMission.status == "pending")
    )
    if existing_mission:
        keyboard = [
            [InlineKeyboardButton(i18n.t("buttons.cancel"), callback_data="cancel_missions_espionage_handler")]
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.callback_query.edit_message_text(
            text=i18n.t("render.missions.labels.warning_not_sub_missions_espionage"),
            reply_markup=reply_markup,
            parse_mode="HTML"
        )
        return

    message_parts = [
        i18n.t("render.missions.labels.mission_espionage_enter_id_01"),
        i18n.t("render.missions.labels.mission_espionage_enter_id_02")
    ]

    message_text = "".join(message_parts)


    keyboard = [
        [InlineKeyboardButton(i18n.t("buttons.cancel"), callback_data="cancel_missions_espionage_handler")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    message_send = await update.callback_query.edit_message_text(
        text=message_text,
        reply_markup=reply_markup,
        parse_mode="HTML"
    )

    context.user_data['chat_id'] = chat_id
    context.user_data['last_message'] = message_send.message_id

    return WAITING_ID_ESPIONAGE_EMPIRE



async def process_id_for_espionage_empire(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if 'last_message' in context.user_data and 'chat_id' in context.user_data:
        await context.bot.delete_message(context.user_data.get('chat_id'), context.user_data.get('last_message'))

    chat_id = context.user_data.get('chat_id')
    user = get_user_by_chat_id(chat_id)
    empire = get_empire_by_user(user)


    empire_espionage_id = update.message.text.strip()


    if not validate_empire_id(empire_espionage_id):

        keyboard = [
            [InlineKeyboardButton(i18n.t("buttons.cancel"), callback_data="cancel_missions_espionage_handler")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            text=i18n.t("render.missions.errors.not_valid_id_espionage"),
            reply_markup=reply_markup
        )
        return WAITING_ID_ESPIONAGE_EMPIRE


    empire_espionage = get_empire_by_id(empire_espionage_id)
    if empire_espionage is None:

        keyboard = [
            [InlineKeyboardButton(i18n.t("buttons.cancel"), callback_data="cancel_missions_espionage_handler")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            text=i18n.t("render.missions.errors.not_found_empire_by_id"),
            reply_markup=reply_markup
        )
        return WAITING_ID_ESPIONAGE_EMPIRE


    if not are_empires_in_same_cluster(empire.empire_id, empire_espionage_id):

        keyboard = [
            [InlineKeyboardButton(i18n.t("buttons.cancel"), callback_data="cancel_missions_espionage_handler")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            text=i18n.t("render.missions.errors.not_possible_espionage_other_cluster"),
            reply_markup=reply_markup
        )
        return WAITING_ID_ESPIONAGE_EMPIRE


    if empire == empire_espionage:

        keyboard = [
            [InlineKeyboardButton(i18n.t("buttons.cancel"), callback_data="cancel_missions_espionage_handler")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            text=i18n.t("render.missions.errors.not_self_espionage"),
            reply_markup=reply_markup
        )
        return WAITING_ID_ESPIONAGE_EMPIRE


    context.user_data['empire_espionage_id'] = empire_espionage_id
    context.user_data['chat_id'] = chat_id

    message_send = await update.message.reply_text(
        text=i18n.t("render.missions.labels.enter_count_espionage_units")
    )

    context.user_data['last_message'] = message_send.message_id

    return WAITING_COUNT_UNITS_ESPIONAGE_EMPIRE



async def process_count_units_for_espionage_empire(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if 'last_message' in context.user_data and 'chat_id' in context.user_data:
        await context.bot.delete_message(context.user_data.get('chat_id'), context.user_data.get('last_message'))

    chat_id = context.user_data.get('chat_id')
    user = get_user_by_chat_id(chat_id)
    empire = get_empire_by_user(user)


    empire_espionage_id = context.user_data.get('empire_espionage_id')


    count_units_spy = update.message.text.strip()


    if not validate_positive_number(count_units_spy):

        keyboard = [
            [InlineKeyboardButton(i18n.t("buttons.cancel"), callback_data="cancel_missions_espionage_handler")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            text=i18n.t("render.missions.errors.not_valid_espionage_units"),
            reply_markup=reply_markup
        )
        return WAITING_COUNT_UNITS_ESPIONAGE_EMPIRE


    count_units_spy = int(count_units_spy)


    current_count_units_spy = get_resource_count(empire, "units_spy")
    if current_count_units_spy < count_units_spy:

        keyboard = [
            [InlineKeyboardButton(i18n.t("buttons.cancel"), callback_data="cancel_missions_espionage_handler")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            text=i18n.t("render.missions.errors.not_enouth_espionage_units"),
            reply_markup=reply_markup
        )
        return WAITING_COUNT_UNITS_ESPIONAGE_EMPIRE


    keyboard = [
        [InlineKeyboardButton(i18n.t("buttons.confirm"), callback_data="confirm_for_espionage_empire_handler")],
        [InlineKeyboardButton(i18n.t("buttons.cancel"), callback_data="cancel_missions_espionage_handler")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)


    mission_duration_seconds = calculate_time_for_mission_espionage(empire, count_units_spy)


    mission_duration_minutes = mission_duration_seconds // 60
    mission_duration_remain_seconds = mission_duration_seconds % 60
    formatted_duration = f"{mission_duration_minutes} мин {mission_duration_remain_seconds:02} сек"

    message_parts = [
        i18n.t("render.missions.labels.confirm_espionage_line_01", empire_espionage_id=empire_espionage_id),
        i18n.t("render.missions.labels.confirm_espionage_line_02", count_units_spy=count_units_spy),
        f"\nОжидаемое время миссии: {formatted_duration}",
        i18n.t("render.missions.labels.confirm_espionage_line_03")
    ]

    message_text = "".join(message_parts)

    message_send = await update.message.reply_text(
        text=message_text,
        reply_markup=reply_markup
    )
    context.user_data['last_message'] = message_send.message_id
    context.user_data['empire_espionage_id'] = empire_espionage_id
    context.user_data['count_units_spy'] = count_units_spy

    return CONFIRMATION_FOR_ESPIONAGE_EMPIRE



async def confirm_for_espionage_empire_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.callback_query.from_user.id
    empire_espionage_id = context.user_data.get("empire_espionage_id")
    count_units_spy = context.user_data.get("count_units_spy")

    user = get_user_by_chat_id(chat_id)
    empire = get_empire_by_user(user)

    if not user:
        await update.callback_query.edit_message_text(
            text=i18n.t("errors.none_user")
        )
        return ConversationHandler.END



    mission, msg = start_mission_espionage(empire, empire_espionage_id, count_units_spy)

    keyboard = [
        [InlineKeyboardButton(i18n.t("buttons.back_to_menu"), callback_data="empire_missions_handler")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)


    if mission is not None:
        await update.callback_query.edit_message_text(
            text=i18n.t("render.missions.labels.mission_start"),
            reply_markup=reply_markup
        )
    else:
        await update.callback_query.edit_message_text(
            text=msg,
            reply_markup=reply_markup
        )

    return ConversationHandler.END



async def cancel_missions_espionage_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    chat_id = update.callback_query.from_user.id
    await delete_last_message(context, chat_id)


    message = await update.callback_query.message.reply_text(
        text=i18n.t("render.missions.labels.mission_espionage_cancel")
    )
    context.user_data["last_message"] = message.message_id
    return ConversationHandler.END



async def empire_missions_exploration_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.callback_query.answer()


    chat_id = update.callback_query.from_user.id
    user = get_user_by_chat_id(chat_id)
    empire = get_empire_by_user(user)

    cancel_keyboard = InlineKeyboardMarkup(
        [[InlineKeyboardButton("❌ Отмена", callback_data="cancel_missions_attack_handler")]]
    )

    if not has_completed_exp_corpus(empire):
        await update.callback_query.edit_message_text(
            text="🏗️ У вас нет построенного экспедиционного корпуса. Постройте сначала экспедиционный корпус, чтобы подготавливать исследователей и обнаруживать локации вокруг империи.",
            reply_markup=cancel_keyboard,
            parse_mode="HTML"
        )
        return ConversationHandler.END

    if get_units_exploration(empire) <= 0:
        await update.callback_query.edit_message_text(
            text="⚔️ У вас нет исследователей. Тренируйте исследователей в экспедиционном корпусе перед отправкой миссии.",
            reply_markup=cancel_keyboard,
            parse_mode="HTML"
        )
        return ConversationHandler.END


    mission_type = Mission.get_or_none(Mission.name == "exploration")
    if mission_type is None:
        raise ValueError(f"Тип миссии {mission_type} не найден в таблице Mission")


    existing_mission = EmpireMission.get_or_none(
        (EmpireMission.empire == empire) &
        (EmpireMission.mission_type == mission_type) &
        (EmpireMission.status == "pending")
    )
    if existing_mission:
        keyboard = [
            [InlineKeyboardButton(i18n.t("buttons.cancel"), callback_data="cancel_missions_exploration_handler")]
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.callback_query.edit_message_text(
            text=i18n.t("render.missions.labels.mission_exp_has_already"),
            reply_markup=reply_markup,
            parse_mode="HTML"
        )
        return



    radius_exploration = empire.level

    message_parts = [
        i18n.t("render.missions.labels.mission_exp_caption_line_01"),
        i18n.t("render.missions.labels.mission_exp_caption_line_02"),
        i18n.t("render.missions.labels.mission_exp_caption_line_03"),
        i18n.t("render.missions.labels.mission_exp_caption_line_04"),
        i18n.t("render.missions.labels.mission_exp_caption_line_05", radius_exploration=radius_exploration)
    ]

    message_text = "".join(message_parts)


    keyboard = [
        [InlineKeyboardButton(str(value), callback_data=f"missions_exploration_radius_{value}")]
        for value in range(1, radius_exploration + 1)
    ]


    keyboard.append(
        [InlineKeyboardButton(i18n.t("buttons.cancel"), callback_data="cancel_missions_exploration_handler")]
    )

    reply_markup = InlineKeyboardMarkup(keyboard)

    message_send = await update.callback_query.edit_message_text(
        text=message_text,
        reply_markup=reply_markup,
        parse_mode="HTML"
    )

    context.user_data['chat_id'] = chat_id
    context.user_data['last_message'] = message_send.message_id

    return WAITING_RADIUS_FOR_EXPLORATION



async def process_radius_for_exploration_handler(update, context):
    await update.callback_query.answer()


    query = update.callback_query
    radius = query.data.replace("missions_exploration_radius_", "")


    chat_id = query.from_user.id
    user = get_user_by_chat_id(chat_id)
    empire = get_empire_by_user(user)

    count_units_exp = get_units_exploration(empire)

    try:
        radius = int(radius)
    except ValueError:

        keyboard = [
            [InlineKeyboardButton(str(value), callback_data=f"missions_exploration_radius_{value}")]
            for value in range(1, radius + 1)
        ]


        keyboard.append(
            [InlineKeyboardButton(i18n.t("buttons.cancel"), callback_data="cancel_missions_exploration_handler")]
        )

        reply_markup = InlineKeyboardMarkup(keyboard)

        message_send = await query.edit_message_text(
            text=i18n.t("render.missions.errors.not_valid_exp_radius"),
            reply_markup=reply_markup,
            parse_mode="HTML"
        )

        context.user_data['chat_id'] = chat_id
        context.user_data['last_message'] = message_send.message_id

        return WAITING_RADIUS_FOR_EXPLORATION

    if radius == 0 or radius > empire.level:

        keyboard = [
            [InlineKeyboardButton(str(value), callback_data=f"missions_exploration_radius_{value}")]
            for value in range(1, radius + 1)
        ]


        keyboard.append(
            [InlineKeyboardButton(i18n.t("buttons.cancel"), callback_data="cancel_missions_exploration_handler")]
        )

        reply_markup = InlineKeyboardMarkup(keyboard)

        message_send = await query.edit_message_text(
            text=i18n.t("render.missions.errors.not_valid_exp_radius"),
            reply_markup=reply_markup,
            parse_mode="HTML"
        )

        context.user_data['chat_id'] = chat_id
        context.user_data['last_message'] = message_send.message_id

        return WAITING_RADIUS_FOR_EXPLORATION


    keyboard = [
        [InlineKeyboardButton(i18n.t("buttons.cancel"), callback_data="cancel_missions_exploration_handler")]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)


    message_send = await query.edit_message_text(
        text=i18n.t("render.missions.labels.mission_exp_enter_count_units", radius=radius, count_units_exp=count_units_exp),
        reply_markup=reply_markup,
        parse_mode="HTML"
    )

    context.user_data['chat_id'] = chat_id
    context.user_data['last_message'] = message_send.message_id
    context.user_data['radius'] = radius

    return WAITING_COUNT_UNITS_EXPLORATION



async def process_count_units_for_exploration_handler(update, context):
    if 'last_message' in context.user_data and 'chat_id' in context.user_data:
        await context.bot.delete_message(context.user_data.get('chat_id'), context.user_data.get('last_message'))

    chat_id = context.user_data.get('chat_id')
    user = get_user_by_chat_id(chat_id)
    empire = get_empire_by_user(user)


    radius = context.user_data.get('radius')


    count_units_exp = update.message.text.strip()


    if not validate_positive_number(count_units_exp):

        keyboard = [
            [InlineKeyboardButton(i18n.t("buttons.cancel"), callback_data="cancel_missions_exploration_handler")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        message_send = await update.message.reply_text(
            text=i18n.t("render.missions.errors.not_valid_exp_count_units"),
            reply_markup=reply_markup
        )

        context.user_data['chat_id'] = chat_id
        context.user_data['last_message'] = message_send.message_id
        context.user_data['radius'] = radius

        return WAITING_COUNT_UNITS_EXPLORATION


    count_units_exp = int(count_units_exp)


    current_count_units_exp = get_resource_count(empire, "units_exploration")
    if current_count_units_exp < count_units_exp:

        keyboard = [
            [InlineKeyboardButton(i18n.t("buttons.cancel"), callback_data="cancel_missions_exploration_handler")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        message_send = await update.message.reply_text(
            text=i18n.t("render.missions.errors.not_enough_exp_count_units"),
            reply_markup=reply_markup
        )

        context.user_data['chat_id'] = chat_id
        context.user_data['last_message'] = message_send.message_id
        context.user_data['radius'] = radius

        return WAITING_COUNT_UNITS_EXPLORATION


    keyboard = [
        [InlineKeyboardButton(i18n.t("buttons.confirm"), callback_data="confirm_for_exploration_empire_handler")],
        [InlineKeyboardButton(i18n.t("buttons.cancel"), callback_data="cancel_missions_exploration_handler")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)








    mission_duration_seconds = calculate_time_for_mission_exploration(empire, count_units_exp, radius)


    mission_duration_minutes = mission_duration_seconds // 60
    mission_duration_remain_seconds = mission_duration_seconds % 60
    formatted_duration = f"{mission_duration_minutes} мин {mission_duration_remain_seconds:02} сек"

    message_parts = [
        i18n.t("render.missions.labels.mission_exp_confirm_01"),
        i18n.t("render.missions.labels.mission_exp_confirm_02", count_units_exp=count_units_exp),
        f"\nОжидаемое время миссии: {formatted_duration}",
        i18n.t("render.missions.labels.mission_exp_confirm_03")
    ]

    message_text = "".join(message_parts)

    message_send = await update.message.reply_text(
        text=message_text,
        reply_markup=reply_markup
    )

    context.user_data['last_message'] = message_send.message_id
    context.user_data['radius'] = radius
    context.user_data['count_units_exp'] = count_units_exp

    return CONFIRMATION_FOR_EXPLORATION_EMPIRE



async def confirm_for_exploration_empire_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.callback_query.from_user.id
    radius = context.user_data.get("radius")
    count_units_exp = context.user_data.get("count_units_exp")

    user = get_user_by_chat_id(chat_id)
    empire = get_empire_by_user(user)

    if not user:
        await update.callback_query.edit_message_text(
            text=i18n.t("errors.none_user")
        )
        return ConversationHandler.END



    mission, msg = start_mission_exploration(empire, count_units_exp, radius)

    keyboard = [
        [InlineKeyboardButton(i18n.t("buttons.back_to_menu"), callback_data="empire_missions_handler")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)


    if mission is not None:
        await update.callback_query.edit_message_text(
            text=i18n.t("render.missions.labels.mission_start"),
            reply_markup=reply_markup
        )
    else:
        await update.callback_query.edit_message_text(
            text=msg,
            reply_markup=reply_markup
        )

    return ConversationHandler.END



async def cancel_missions_exploration_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    chat_id = update.callback_query.from_user.id
    await delete_last_message(context, chat_id)


    message = await update.callback_query.message.reply_text(
        text=i18n.t("render.missions.labels.mission_exp_cancel")
    )
    context.user_data["last_message"] = message.message_id
    return ConversationHandler.END



async def cluster_map_location_attack(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    chat_id = query.from_user.id
    user = get_user_by_chat_id(chat_id)
    empire = get_empire_by_user(user)

    count_units_army = get_units_army(empire)

    cancel_keyboard = InlineKeyboardMarkup(
        [[InlineKeyboardButton("❌ Отмена", callback_data="cancel_missions_attack_handler")]]
    )

    if not has_completed_barracks(empire):
        await update.callback_query.edit_message_text(
            text="🏗️ У вас нет построенной казармы. Постройте её, чтобы тренировать войска, атаковать локации и другие империи.",
            reply_markup=cancel_keyboard,
            parse_mode="HTML"
        )
        return ConversationHandler.END

    if get_units_army(empire) <= 0:
        await update.callback_query.edit_message_text(
            text="⚔️ У вас нет войск для атаки. Нанимайте армию в казармах перед отправкой миссии.",
            reply_markup=cancel_keyboard,
            parse_mode="HTML"
        )
        return ConversationHandler.END


    mission_type = Mission.get_or_none(Mission.name == "attack_location")
    if mission_type is None:
        raise ValueError(f"Тип миссии {mission_type} не найден в таблице Mission")


    existing_mission = EmpireMission.get_or_none(
        (EmpireMission.empire == empire) &
        (EmpireMission.mission_type == mission_type) &
        (EmpireMission.status == "pending")
    )
    if existing_mission:
        keyboard = [
            [InlineKeyboardButton(i18n.t("buttons.cancel"), callback_data="cancel_missions_attack_location_handler")]
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.callback_query.edit_message_text(
            text=i18n.t("render.missions.labels.mission_attack_loc_has_already"),
            reply_markup=reply_markup,
            parse_mode="HTML"
        )
        return


    location_id = query.data.split("_")[-1]


    target_location = get_location_by_id(empire, location_id)

    keyboard = [[InlineKeyboardButton(i18n.t("buttons.cancel"), callback_data="cancel_missions_attack_location_handler")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if target_location:
        message_send = await query.edit_message_text(
            text=i18n.t("render.missions.labels.mission_attack_loc_enter_count_units", target_location_name=target_location.name, count_units_army=count_units_army),
            reply_markup=reply_markup,
            parse_mode="HTML"
        )


        context.user_data['chat_id'] = chat_id
        context.user_data['last_message'] = message_send.message_id
        context.user_data['location_id'] = location_id
        context.user_data['target_location'] = {
            "ID": target_location.id,
            "name": target_location.name,
            "monsters": target_location.monsters
        }

        return WAITING_COUNT_UNITS_ATTACKING_LOCATION
    else:
        await query.edit_message_text(
            text=i18n.t("render.missions.errors.not_found_target_location"),
            reply_markup=reply_markup
        )



async def process_count_units_for_attack_location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if 'last_message' in context.user_data and 'chat_id' in context.user_data:
        await context.bot.delete_message(context.user_data.get('chat_id'), context.user_data.get('last_message'))

    chat_id = context.user_data.get('chat_id')
    user = get_user_by_chat_id(chat_id)
    empire = get_empire_by_user(user)


    target_location = context.user_data.get('target_location')


    location_id = context.user_data.get('location_id')


    count_units = update.message.text.strip()


    if not validate_positive_number(count_units):

        keyboard = [
            [InlineKeyboardButton(i18n.t("buttons.cancel"), callback_data="cancel_missions_attack_location_handler")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            text=i18n.t("render.missions.errors.not_valid_value_count_units"),
            reply_markup=reply_markup
        )
        return WAITING_COUNT_UNITS_ATTACKING_LOCATION


    count_units = int(count_units)


    current_count_units = get_resource_count(empire, "units_army")
    if current_count_units < count_units:

        keyboard = [
            [InlineKeyboardButton(i18n.t("buttons.cancel"), callback_data="cancel_missions_attack_location_handler")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            text=i18n.t("render.missions.errors.not_enough_attack_units"),
            reply_markup=reply_markup
        )
        return WAITING_COUNT_UNITS_ATTACKING_EMPIRE

    status = EmpireStatus.get_or_none(EmpireStatus.empire == empire)

    if not status:
        print("❌ Статус империи не найден!")
        return

    unit_capacity = status.units_army_capacity or 10
    total_capacity = count_units * unit_capacity


    keyboard = [
        [InlineKeyboardButton(i18n.t("buttons.confirm"), callback_data="confirm_for_attack_location_handler")],
        [InlineKeyboardButton(i18n.t("buttons.cancel"), callback_data="cancel_missions_attack_location_handler")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)


    mission_duration_seconds = calculate_time_for_mission_attack(empire, count_units)


    mission_duration_minutes = mission_duration_seconds // 60
    mission_duration_remain_seconds = mission_duration_seconds % 60
    formatted_duration = f"{mission_duration_minutes} мин {mission_duration_remain_seconds:02} сек"

    message_parts = [
        i18n.t("render.missions.labels.mission_attack_loc_confirm_01"),
        i18n.t("render.missions.labels.mission_attack_loc_confirm_02", count_units=count_units),
        i18n.t("render.missions.labels.mission_attack_loc_confirm_03", total_capacity=total_capacity),
        f"\nОжидаемое время миссии: {formatted_duration}",
        i18n.t("render.missions.labels.mission_attack_loc_confirm_04")
    ]

    message_text = "".join(message_parts)

    message_send = await update.message.reply_text(
        text=message_text,
        reply_markup=reply_markup
    )
    context.user_data['last_message'] = message_send.message_id
    context.user_data['location_id'] = location_id
    context.user_data['count_units'] = count_units
    context.user_data['target_location'] = target_location

    return CONFIRMATION_FOR_ATTACK_LOCATION



async def confirm_for_attack_location_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.callback_query.from_user.id
    location_id = context.user_data.get("location_id")
    print(location_id)
    count_units = context.user_data.get("count_units")
    target_location = context.user_data.get('target_location')

    user = get_user_by_chat_id(chat_id)
    empire = get_empire_by_user(user)

    if not user:
        await update.callback_query.edit_message_text(
            text=i18n.t("errors.none_user")
        )
        return ConversationHandler.END


    mission, msg = start_mission_attack_location(empire, location_id, count_units)

    keyboard = [
        [InlineKeyboardButton(i18n.t("buttons.back_list_locations"), callback_data="cluster_map_finder_locations")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)


    if mission is not None:
        await update.callback_query.edit_message_text(
            text=i18n.t("render.missions.labels.mission_attack_loc_start", target_location=target_location["name"], location_id=location_id),
            reply_markup=reply_markup
        )
    else:
        await update.callback_query.edit_message_text(
            text=msg,
            reply_markup=reply_markup
        )

    return ConversationHandler.END



async def cancel_missions_attack_location_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    chat_id = update.callback_query.from_user.id


    keyboard = [
        [InlineKeyboardButton(i18n.t("buttons.back_list_locations"), callback_data="cluster_map_finder_locations")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)


    await update.callback_query.edit_message_text(
        text=i18n.t("render.missions.labels.mission_attack_loc_cancel"),
        reply_markup=reply_markup
    )

    return ConversationHandler.END


conversation_handler_attack_empire = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(empire_missions_attack_handler, pattern="empire_missions_attack_handler"),
        CallbackQueryHandler(cancel_missions_attack_handler, pattern="cancel_missions_attack_handler")
    ],
    states={
        WAITING_ID_ATTACKING_EMPIRE: [
            CallbackQueryHandler(process_id_for_attack_empire, pattern=r"^attack_empire_\d+$"),
            CallbackQueryHandler(empire_missions_attack_handler, pattern=r"^attack_empire_page_\d+$"),
            CallbackQueryHandler(cancel_missions_attack_handler, pattern="cancel_missions_attack_handler")
        ],
        WAITING_COUNT_UNITS_ATTACKING_EMPIRE: [
            MessageHandler(
                filters.TEXT & ~filters.COMMAND, process_count_units_for_attack_empire
            ),
            CallbackQueryHandler(cancel_missions_attack_handler, pattern="cancel_missions_attack_handler")
        ],
        CONFIRMATION_FOR_ATTACK_EMPIRE: [
            CallbackQueryHandler(confirm_for_attack_empire_handler, pattern="confirm_for_attack_empire_handler"),
            CallbackQueryHandler(cancel_missions_attack_handler, pattern="cancel_missions_attack_handler")
        ],
    },
    fallbacks=[
        CallbackQueryHandler(cancel_missions_attack_handler, pattern="cancel_missions_attack_handler")
    ]
)


conversation_handler_espionage_empire = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(empire_missions_espionage_handler, pattern="empire_missions_espionage_handler"),
        CallbackQueryHandler(cancel_missions_espionage_handler, pattern="cancel_missions_espionage_handler")
    ],
    states={
        WAITING_ID_ESPIONAGE_EMPIRE: [
            MessageHandler(
                filters.TEXT & ~filters.COMMAND, process_id_for_espionage_empire
            ),
            CallbackQueryHandler(cancel_missions_espionage_handler, pattern="cancel_missions_espionage_handler")
        ],
        WAITING_COUNT_UNITS_ESPIONAGE_EMPIRE: [
            MessageHandler(
                filters.TEXT & ~filters.COMMAND, process_count_units_for_espionage_empire
            ),
            CallbackQueryHandler(cancel_missions_espionage_handler, pattern="cancel_missions_espionage_handler")
        ],
        CONFIRMATION_FOR_ESPIONAGE_EMPIRE: [
            CallbackQueryHandler(confirm_for_espionage_empire_handler, pattern="confirm_for_espionage_empire_handler"),
            CallbackQueryHandler(cancel_missions_espionage_handler, pattern="cancel_missions_espionage_handler")
        ],
    },
    fallbacks=[
        CallbackQueryHandler(cancel_missions_espionage_handler, pattern="cancel_missions_espionage_handler")
    ]
)


conversation_handler_exploration = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(empire_missions_exploration_handler, pattern="^empire_missions_exploration_handler"),
        CallbackQueryHandler(cancel_missions_exploration_handler, pattern="^cancel_missions_exploration_handler$")
    ],
    states={
        WAITING_RADIUS_FOR_EXPLORATION: [
            CallbackQueryHandler(process_radius_for_exploration_handler, pattern="^missions_exploration_radius_\\d+$"),
            CallbackQueryHandler(cancel_missions_exploration_handler, pattern="^cancel_missions_exploration_handler$")
        ],
        WAITING_COUNT_UNITS_EXPLORATION: [
            MessageHandler(
                filters.TEXT & ~filters.COMMAND, process_count_units_for_exploration_handler
            ),
            CallbackQueryHandler(cancel_missions_exploration_handler, pattern="^cancel_missions_exploration_handler$")
        ],
        CONFIRMATION_FOR_EXPLORATION_EMPIRE: [
            CallbackQueryHandler(confirm_for_exploration_empire_handler, pattern="^confirm_for_exploration_empire_handler"),
            CallbackQueryHandler(cancel_missions_exploration_handler, pattern="^cancel_missions_exploration_handler$")
        ],
    },
    fallbacks=[
        CallbackQueryHandler(cancel_missions_exploration_handler, pattern="^cancel_missions_exploration_handler$")
    ]
)


conversation_handler_attack_location = ConversationHandler(
    entry_points=[CallbackQueryHandler(cluster_map_location_attack, pattern=r"^cluster_map_location_attack_[\w]+$")],
    states={
        WAITING_COUNT_UNITS_ATTACKING_LOCATION: [
            MessageHandler(
                filters.TEXT & ~filters.COMMAND, process_count_units_for_attack_location
            )
        ],
        CONFIRMATION_FOR_ATTACK_LOCATION: [
            CallbackQueryHandler(confirm_for_attack_location_handler, pattern="confirm_for_attack_location_handler"),
            CallbackQueryHandler(cancel_missions_attack_location_handler, pattern="cancel_missions_attack_location_handler")
        ],
    },
    fallbacks=[
        CallbackQueryHandler(cancel_missions_attack_location_handler, pattern="cancel_missions_attack_location_handler")
    ]
)
