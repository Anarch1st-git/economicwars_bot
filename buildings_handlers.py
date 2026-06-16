from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    KeyboardButton
)

from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ConversationHandler,
    ContextTypes
)

from handlers import (
    get_user_by_chat_id,
    get_empire_by_user,
    get_completed_buildings_count,
    get_production_report,
    get_unit_production_report,
    get_building_requirements,
    get_completed_technologies,
    get_total_resources,
    can_build,
    create_building_in_empire,
    can_upgrade,
    user_has_subscription,
    start_train_units,
    upgrade_building_in_empire,
    render_progress_bar_emoji,
    get_building_speed_modifiers,
    cancel_building_in_empire,
    get_total_energy_usage_and_generation
)

from models import (
    EmpireBuildings,
    Buildings,
    EmpireStatus,
    EmpireResource
)

from datetime import datetime, timedelta

from locales.locales_names import (
    buildings_name
)

from i18n import I18N

i18n = I18N("ru")



async def empire_buildings_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.callback_query.answer()


    chat_id = update.callback_query.from_user.id
    user = get_user_by_chat_id(chat_id)
    empire = get_empire_by_user(user)


    empire_buildings_count = get_completed_buildings_count(empire)


    resource_report = get_production_report(empire)
    unit_report = get_unit_production_report(empire)


    message_parts = [
        i18n.t("render.empire_buildings.line_01"),
        i18n.t("render.empire_buildings.line_02", empire_buildings_count=empire_buildings_count),
        i18n.t("render.empire_buildings.line_03"),
        i18n.t("render.empire_buildings.line_04", resource_report_wood=resource_report.get('economic:wood', 0)),
        i18n.t("render.empire_buildings.line_05", resource_report_gold=resource_report.get('economic:gold', 0)),
        i18n.t("render.empire_buildings.line_06", resource_report_oil=resource_report.get('economic:oil', 0)),
        i18n.t("render.empire_buildings.line_07", resource_report_diamond=resource_report.get('economic:diamond', 0)),

        i18n.t("render.empire_buildings.line_09"),
        i18n.t("render.empire_buildings.line_10", unit_report_army=unit_report.get('units_army', 0)),
        i18n.t("render.empire_buildings.line_11", unit_report_spy=unit_report.get('units_spy', 0)),
        i18n.t("render.empire_buildings.line_12", unit_report_counterspy=unit_report.get('units_counterspy', 0)),
        i18n.t("render.empire_buildings.line_13", unit_report_exploration=unit_report.get('units_exploration', 0)),
        i18n.t("render.empire_buildings.line_14")
    ]

    message = "".join(message_parts)


    keyboard = [
        [InlineKeyboardButton(i18n.t("buttons.bld_social"), callback_data="empire_buildings_social_handler")],
        [InlineKeyboardButton(i18n.t("buttons.bld_military"), callback_data="empire_buildings_military_handler")],
        [InlineKeyboardButton(i18n.t("buttons.bld_economic"), callback_data="empire_buildings_economics_handler")],
        [InlineKeyboardButton(i18n.t("buttons.back"), callback_data="manage_empire_handler")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.callback_query.edit_message_text(
        text=message,
        reply_markup=reply_markup,
        parse_mode="HTML"
    )


async def empire_buildings_social_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.callback_query.answer()
    chat_id = update.callback_query.from_user.id
    user = get_user_by_chat_id(chat_id)
    empire = get_empire_by_user(user)

    buildings_list = ["laboratory", "exp_corpus"]

    def get_remaining_build_time_dynamic(building, empire):
        now = datetime.now()
        time_passed = (now - building.last_update).total_seconds()

        speed_modifier = get_building_speed_modifiers(empire)
        current_progress = building.progress + time_passed * speed_modifier
        remaining_points = max(building.total_points - current_progress, 0)

        if speed_modifier > 0:
            return remaining_points / speed_modifier, min(int((current_progress / building.total_points) * 100), 100)
        return float("inf"), 0


    under_construction = EmpireBuildings.select().join(Buildings).where(
        (EmpireBuildings.empire == empire) &
        (EmpireBuildings.status == "pending") &
        (Buildings.building_type == "social")
    )


    under_upgrading = EmpireBuildings.select().join(Buildings).where(
        (EmpireBuildings.empire == empire) &
        (EmpireBuildings.status == "upgrading") &
        (Buildings.building_type == "social")
    )

    message = i18n.t("render.empire_buildings.menu_social")

    if under_construction.exists():
        message += i18n.t("render.empire_buildings.pending_build")
        for building in under_construction:
            remaining_time, progress_percent = get_remaining_build_time_dynamic(building, empire)
            hours = int(remaining_time // 3600)
            minutes = int((remaining_time % 3600) // 60)
            seconds = int(remaining_time % 60)

            progress_bar = render_progress_bar_emoji(progress_percent, 100)

            message += i18n.t(
                "render.empire_buildings.time_remained_build",
                building_name=buildings_name[building.building.name],
                building_level=building.level,
                hours=hours,
                minutes=minutes,
                seconds=seconds,
                progress_bar=progress_bar
            )

    if under_upgrading.exists():
        message += i18n.t("render.empire_buildings.upgrade_build")
        for b in under_upgrading:
            remaining_time, progress_percent = get_remaining_build_time_dynamic(b, empire)
            hours = int(remaining_time // 3600)
            minutes = int((remaining_time % 3600) // 60)
            seconds = int(remaining_time % 60)

            progress_bar = render_progress_bar_emoji(progress_percent, 100)

            building = b.building
            if b.level < building.max_level:
                message += i18n.t(
                    "render.empire_buildings.time_remained_build",
                    building_name=buildings_name[building.building.name],
                    b_level=b.level,
                    hours=hours,
                    minutes=minutes,
                    seconds=seconds,
                    progress_bar=progress_bar
                )
            elif building.next_building:
                message += i18n.t(
                    "render.empire_buildings.time_remained_upgr_next_build",
                    building_name=buildings_name[building.name],
                    next_building=building.next_building,
                    hours=hours,
                    minutes=minutes,
                    seconds=seconds,
                    progress_bar=progress_bar
                )
            else:
                message += i18n.t(
                    "render.empire_buildings.time_remained_upgr_max_lvl",
                    building_name=buildings_name[building.name],
                    hours=hours,
                    minutes=minutes,
                    seconds=seconds,
                    progress_bar=progress_bar
                )

    if not under_construction.exists() and not under_upgrading.exists():
        message += i18n.t("render.empire_buildings.not_have_build_pending")

    keyboard = [
        [InlineKeyboardButton(text=buildings_name[name], callback_data=f"empire_building_menu_handler:{name}")]
        for name in buildings_list
    ]
    keyboard.append([InlineKeyboardButton(text=i18n.t("buttons.back"), callback_data="empire_buildings_handler")])

    await update.callback_query.edit_message_text(
        text=message,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="HTML"
    )



async def empire_buildings_military_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.callback_query.answer()
    chat_id = update.callback_query.from_user.id
    user = get_user_by_chat_id(chat_id)
    empire = get_empire_by_user(user)

    buildings_list = ["spy_center", "conspy_center", "barracks", "defender"]

    def get_remaining_build_time_dynamic(building, empire):
        now = datetime.now()
        time_passed = (now - building.last_update).total_seconds()

        speed_modifier = get_building_speed_modifiers(empire)
        current_progress = building.progress + time_passed * speed_modifier
        remaining_points = max(building.total_points - current_progress, 0)

        if speed_modifier > 0:
            return remaining_points / speed_modifier, min(int((current_progress / building.total_points) * 100), 100)
        return float("inf"), 0


    under_construction = EmpireBuildings.select().join(Buildings).where(
        (EmpireBuildings.empire == empire) &
        (EmpireBuildings.status == "pending") &
        (Buildings.building_type == "military")
    )

    under_upgrading = EmpireBuildings.select().join(Buildings).where(
        (EmpireBuildings.empire == empire) &
        (EmpireBuildings.status == "upgrading") &
        (Buildings.building_type == "military")
    )

    message = i18n.t("render.empire_buildings.menu_military")

    if under_construction.exists():
        message += i18n.t("render.empire_buildings.pending_build")
        for building in under_construction:
            remaining_time, progress_percent = get_remaining_build_time_dynamic(building, empire)
            hours = int(remaining_time // 3600)
            minutes = int((remaining_time % 3600) // 60)
            seconds = int(remaining_time % 60)

            progress_bar = render_progress_bar_emoji(progress_percent, 100)

            message += i18n.t(
                "render.empire_buildings.time_remained_build",
                building_name=buildings_name[building.building.name],
                building_level=building.level,
                hours=hours,
                minutes=minutes,
                seconds=seconds,
                progress_bar=progress_bar
            )

    if under_upgrading.exists():
        message += i18n.t("render.empire_buildings.upgrade_build")
        for b in under_upgrading:
            remaining_time, progress_percent = get_remaining_build_time_dynamic(b, empire)
            hours = int(remaining_time // 3600)
            minutes = int((remaining_time % 3600) // 60)
            seconds = int(remaining_time % 60)

            progress_bar = render_progress_bar_emoji(progress_percent, 100)

            building = b.building
            if b.level < building.max_level:
                message += i18n.t(
                    "render.empire_buildings.time_remained_build",
                    building_name=buildings_name[building.building.name],
                    b_level=b.level,
                    hours=hours,
                    minutes=minutes,
                    seconds=seconds,
                    progress_bar=progress_bar
                )
            elif building.next_building:
                message += i18n.t(
                    "render.empire_buildings.time_remained_upgr_next_build",
                    building_name=buildings_name[building.name],
                    next_building=building.next_building,
                    hours=hours,
                    minutes=minutes,
                    seconds=seconds,
                    progress_bar=progress_bar
                )
            else:
                message += i18n.t(
                    "render.empire_buildings.time_remained_upgr_max_lvl",
                    building_name=buildings_name[building.name],
                    hours=hours,
                    minutes=minutes,
                    seconds=seconds,
                    progress_bar=progress_bar
                )

    if not under_construction.exists() and not under_upgrading.exists():
        message += i18n.t("render.empire_buildings.not_have_build_pending")

    keyboard = [
        [InlineKeyboardButton(text=buildings_name[name], callback_data=f"empire_building_menu_handler:{name}")]
        for name in buildings_list
    ]
    keyboard.append([InlineKeyboardButton(text=i18n.t("buttons.back"), callback_data="empire_buildings_handler")])

    await update.callback_query.edit_message_text(
        text=message,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="HTML"
    )



async def empire_buildings_economics_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.callback_query.answer()
    chat_id = update.callback_query.from_user.id
    user = get_user_by_chat_id(chat_id)
    empire = get_empire_by_user(user)

    buildings_list = [
        "market",
        "sawmill",
        "gold_mine",
        "oil_well",
        "diamond_quarry",
        "solar_power_plant"
    ]

    def get_remaining_build_time_dynamic(building, empire):
        now = datetime.now()
        time_passed = (now - building.last_update).total_seconds()

        speed_modifier = get_building_speed_modifiers(empire)
        current_progress = building.progress + time_passed * speed_modifier
        remaining_points = max(building.total_points - current_progress, 0)

        if speed_modifier > 0:
            return remaining_points / speed_modifier, min(int((current_progress / building.total_points) * 100), 100)
        return float("inf"), 0


    under_construction = EmpireBuildings.select().join(Buildings).where(
        (EmpireBuildings.empire == empire) &
        (EmpireBuildings.status == "pending") &
        (Buildings.building_type.startswith("economic"))
    )

    under_upgrading = EmpireBuildings.select().join(Buildings).where(
        (EmpireBuildings.empire == empire) &
        (EmpireBuildings.status == "upgrading") &
        (Buildings.building_type == "economic")
    )

    message = i18n.t("render.empire_buildings.menu_economic")

    if under_construction.exists():
        message += i18n.t("render.empire_buildings.pending_build")
        for building in under_construction:
            remaining_time, progress_percent = get_remaining_build_time_dynamic(building, empire)
            hours = int(remaining_time // 3600)
            minutes = int((remaining_time % 3600) // 60)
            seconds = int(remaining_time % 60)

            progress_bar = render_progress_bar_emoji(progress_percent, 100)

            message += i18n.t(
                "render.empire_buildings.time_remained_build",
                building_name=buildings_name[building.building.name],
                building_level=building.level,
                hours=hours,
                minutes=minutes,
                seconds=seconds,
                progress_bar=progress_bar
            )

    if under_upgrading.exists():
        message += i18n.t("render.empire_buildings.upgrade_build")
        for b in under_upgrading:
            remaining_time, progress_percent = get_remaining_build_time_dynamic(b, empire)
            hours = int(remaining_time // 3600)
            minutes = int((remaining_time % 3600) // 60)
            seconds = int(remaining_time % 60)

            progress_bar = render_progress_bar_emoji(progress_percent, 100)

            building = b.building
            if b.level < building.max_level:
                message += i18n.t(
                    "render.empire_buildings.time_remained_build",
                    building_name=buildings_name[building.building.name],
                    b_level=b.level,
                    hours=hours,
                    minutes=minutes,
                    seconds=seconds,
                    progress_bar=progress_bar
                )
            elif building.next_building:
                message += i18n.t(
                    "render.empire_buildings.time_remained_upgr_next_build",
                    building_name=buildings_name[building.name],
                    next_building=building.next_building,
                    hours=hours,
                    minutes=minutes,
                    seconds=seconds,
                    progress_bar=progress_bar
                )
            else:
                message += i18n.t(
                    "render.empire_buildings.time_remained_upgr_max_lvl",
                    building_name=buildings_name[building.name],
                    hours=hours,
                    minutes=minutes,
                    seconds=seconds,
                    progress_bar=progress_bar
                )

    if not under_construction.exists() and not under_upgrading.exists():
        message += i18n.t("render.empire_buildings.not_have_build_pending")

    keyboard = [
        [InlineKeyboardButton(text=buildings_name[name], callback_data=f"empire_building_menu_handler:{name}")]
        for name in buildings_list
    ]
    keyboard.append([InlineKeyboardButton(text=i18n.t("buttons.back"), callback_data="empire_buildings_handler")])

    await update.callback_query.edit_message_text(
        text=message,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="HTML"
    )


async def empire_building_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    _, building_name = query.data.split(":")
    chat_id = query.from_user.id
    user = get_user_by_chat_id(chat_id)
    empire = get_empire_by_user(user)


    status = EmpireStatus.get_or_none(EmpireStatus.empire == empire)

    if not status:
        print("❌ Статус империи не найден!")
        return

    units_exploration_cost = status.units_exploration_cost or 1
    units_army_cost = status.units_army_cost or 2
    units_spy_cost = status.units_spy_cost or 3
    units_counterspy_cost = status.units_counterspy_cost or 3

    building = Buildings.get_or_none(Buildings.name == building_name)
    if not building:
        await query.edit_message_text(
            text=i18n.t("render.empire_building_other.build_not_found")
        )
        return

    empire_building = EmpireBuildings.get_or_none(
        (EmpireBuildings.empire == empire) & (EmpireBuildings.building == building)
    )

    has_subscription = user_has_subscription(user)
    requirements = get_building_requirements(building_name)
    user_tech = get_completed_technologies(empire)
    user_resources = get_total_resources(empire)

    building_in_progress = EmpireBuildings.select().where(
        (EmpireBuildings.empire == empire) & (EmpireBuildings.status == "pending")
    ).exists()

    message = f"<b>🏗 {buildings_name[building_name]}</b>\n\n"
    keyboard = []

    if empire_building and empire_building.status in ["completed", "producing", "idle"]:
        message_parts = [
            i18n.t("render.empire_building_menu.build_done"),
            i18n.t("render.empire_building_menu.build_level", level=empire_building.level, max_level=building.max_level)
        ]
        message += "".join(message_parts)

        if building.next_building:
            next_building = Buildings.get_or_none(Buildings.name == building.next_building)
            if next_building:
                message += i18n.t("render.empire_building_menu.next_building_after_upgr", next_building_name=buildings_name[next_building.name])
                message += i18n.t("render.empire_building_menu.bonus_extraction", production=next_building.base_production)


        production_units_map = {
            "exp_corpus": "units_exploration",
            "spy_center": "units_spy",
            "conspy_center": "units_counterspy",
            "barracks": "units_army",
        }

        if building_name in production_units_map:
            unit_type = production_units_map[building_name]

            unit_cost = 1
            if unit_type == "units_exploration":
                unit_cost = units_exploration_cost
            if unit_type == "units_army_cost":
                unit_cost = units_army_cost
            if unit_type == "units_spy_cost":
                unit_cost = units_spy_cost
            if unit_type == "units_counterspy_cost":
                unit_cost = units_counterspy_cost

            message += i18n.t("render.empire_building_menu.units_production")
            message += i18n.t("render.empire_building_menu.units_type", unit_type=unit_type.replace('_', ' ').capitalize())

            ready_units = empire_building.current_production
            total_order = empire_building.units_to_hire
            max_capacity = empire_building.current_max_production_capacity

            message += i18n.t("render.empire_building_menu.hire_limit", max_capacity=max_capacity)
            message += i18n.t("render.empire_building_menu.ready_value", ready_units=ready_units, total_order=total_order)

            empire_resources = EmpireResource.get_or_none(EmpireResource.empire == empire)
            available_gold = empire_resources.gold if empire_resources else 0

            if not empire_building.is_producing:
                affordable_units = available_gold // unit_cost if unit_cost else 0
                available_capacity = max_capacity - empire_building.current_production
                hireable_units = min(affordable_units, available_capacity)

                if hireable_units > 0:
                    cost_units = hireable_units * unit_cost
                    keyboard.append([
                        InlineKeyboardButton(
                            text=f"⚒ Нанять юнитов ({hireable_units}) [{cost_units} золота]",
                            callback_data=f"hire_units:{building_name}:{hireable_units}"
                        )
                    ])
                else:
                    keyboard.append([
                        InlineKeyboardButton(
                            text="Недостаточно золота для найма",
                            callback_data="empire_buildings_handler"
                        )
                    ])
            elif ready_units > 0:
                affordable_units = available_gold // unit_cost if unit_cost else 0
                hireable_units = min(affordable_units, ready_units)

                if hireable_units > 0:
                    cost_units = hireable_units * unit_cost
                    keyboard.append([
                        InlineKeyboardButton(
                            text=f"⚒ Нанять юнитов ({hireable_units}) [{cost_units} золота]",
                            callback_data=f"hire_units:{building_name}:{hireable_units}"
                        )
                    ])
                else:
                    keyboard.append([
                        InlineKeyboardButton(
                            text="Недостаточно золота для найма готовых юнитов",
                            callback_data="empire_buildings_handler"
                        )
                    ])


        if empire_building.level < building.max_level:
            next_level = empire_building.level + 1
            upgrade_cost = building.upgrade_cost.get(str(next_level), {})
            used_energy = building.energy_used.get(str(next_level)) or 0

            another_upgrading = EmpireBuildings.select().where(
                (EmpireBuildings.empire == empire) &
                (EmpireBuildings.status == "upgrading") &
                (EmpireBuildings.id != empire_building.id)
            ).exists()

            if upgrade_cost and isinstance(upgrade_cost, dict) and len(upgrade_cost) > 0:
                message += i18n.t("render.empire_building_menu.cost_upgrading")
                for res, amount in upgrade_cost.items():
                    user_amount = user_resources.get(res, 0)
                    status = "✅" if user_amount >= amount else "❌"
                    message += f"{status} {res}: {user_amount}/{amount}\n"
                    if used_energy is not None:
                        message += f"Потребление энергии: {used_energy}\n"

                if not another_upgrading or has_subscription:

                    build_speed_mod = get_building_speed_modifiers(empire)
                    effective_speed = 1.0 * build_speed_mod
                    time_seconds = building.base_construction_time / effective_speed
                    hours, minutes = int(time_seconds // 3600), int((time_seconds % 3600) // 60)
                    time_label = f"{hours}ч {minutes}м"

                    total_used, total_gen = get_total_energy_usage_and_generation(empire)
                    if used_energy < 0 and (total_gen + used_energy < total_used):
                        message += i18n.t("render.empire_building_menu.warning_energy_limit_exceeded")
                    else:
                        keyboard.append([
                            InlineKeyboardButton(
                                text=i18n.t("buttons.upgrade_before", next_level=next_level) + f" ⏱ {time_label}",
                                callback_data=f"upgrade:{building_name}"
                            )
                        ])
                else:
                    message += i18n.t("render.empire_building_menu.warning_not_subscribe_upgrade")
        elif building.next_building:

            next_building = Buildings.get_or_none(Buildings.name == building.next_building)
            if next_building:
                message += i18n.t("render.empire_building_menu.next_building_after_upgr", next_building_name=buildings_name[next_building.name])
                message += i18n.t("render.empire_building_menu.bonus_extraction", production=next_building.base_production)

                upgrade_cost = next_building.upgrade_cost.get("next_type", {})
                used_energy = next_building.energy_used.get(1)
                if upgrade_cost:
                    message += i18n.t("render.empire_building_menu.cost_upgrading")
                    for res, amount in upgrade_cost.items():
                        user_amount = user_resources.get(res, 0)
                        status = "✅" if user_amount >= amount else "❌"
                        message += f"{status} {res}: {user_amount}/{amount}\n"
                        message += f"Потребление энергии: {used_energy}"

                    if not building_in_progress or has_subscription:
                        build_speed_mod = get_building_speed_modifiers(empire)
                        effective_speed = 1.0 * build_speed_mod
                        time_seconds = next_building.base_construction_time / effective_speed
                        hours, minutes = int(time_seconds // 3600), int((time_seconds % 3600) // 60)
                        time_label = f"{hours}ч {minutes}м"

                        keyboard.append([
                            InlineKeyboardButton(
                                text=i18n.t("buttons.upgrade_next_building", next_building_name=buildings_name[next_building.name]) + f" ⏱ {time_label}",
                                callback_data=f"upgrade_next_type:{building.name}"
                            )
                        ])
        else:
            message += i18n.t("render.empire_building_menu.ready_max_level")

    elif empire_building and empire_building.status == "pending":
        keyboard.append([
            InlineKeyboardButton(
                text="❌ Отменить строительство",
                callback_data=f"cancel_build:{building_name}"
            )
        ])


        if empire_building.progress >= empire_building.total_points:
            remaining_seconds = 0
        else:
            remaining_points = empire_building.total_points - empire_building.progress
            build_speed_modifiers = get_building_speed_modifiers(empire)
            base_speed = 1.0
            actual_speed = base_speed * build_speed_modifiers
            remaining_seconds = remaining_points / actual_speed

        hours, minutes, seconds = int(remaining_seconds // 3600), int((remaining_seconds % 3600) // 60), int(remaining_seconds % 60)
        message += i18n.t("render.empire_building_menu.pending_build", hours=hours, minutes=minutes, seconds=seconds)

    else:
        message += i18n.t("render.empire_building_menu.build_not_done")
        message += i18n.t("render.empire_building_menu.requirements_build")

        required_tech = requirements.get("tech", [])
        if required_tech:
            message += i18n.t("render.empire_building_menu.tech_list")
            for tech in required_tech:
                status = "✅" if tech in user_tech else "❌"
                message += f"{status} {tech}\n"

        required_resources = requirements.get("resources", {})
        used_energy = building.energy_used.get("1") or 0
        if required_resources:
            message += i18n.t("render.empire_building_menu.resources_list")
            for res, amount in required_resources.items():
                user_amount = user_resources.get(res, 0)
                status = "✅" if user_amount >= amount else "❌"
                message += f"{status} {res}: {amount} / {user_amount}\n"
                message += f"Потребление энергии: {used_energy}"

        can_build = all(tech in user_tech for tech in required_tech) and \
                    all(user_resources.get(res, 0) >= amount for res, amount in required_resources.items())

        if can_build:
            if not building_in_progress or has_subscription:


                build_speed_mod = get_building_speed_modifiers(empire)
                effective_speed = 1.0 * build_speed_mod
                time_seconds = building.base_construction_time / effective_speed
                hours, minutes = int(time_seconds // 3600), int((time_seconds % 3600) // 60)
                time_label = f"{hours}ч {minutes}м"

                energy_needed = building.energy_used.get("1") or 0
                total_used, total_gen = get_total_energy_usage_and_generation(empire)

                if energy_needed < 0 and (total_gen + energy_needed < total_used):
                    message += i18n.t("render.empire_building_menu.warning_energy_limit_exceeded")
                else:
                    keyboard.append([
                        InlineKeyboardButton(
                            text=i18n.t("buttons.build_create") + f" ⏱ {time_label}",
                            callback_data=f"build:{building_name}"
                        )
                    ])
            else:
                message += i18n.t("render.empire_building_menu.warning_not_subscribe_build")
        else:
            message += i18n.t("render.empire_building_menu.not_success_conditions_build")

    keyboard.append([InlineKeyboardButton(text=i18n.t("buttons.back"), callback_data="empire_buildings_handler")])


    message = message.encode("utf-16", "surrogatepass").decode("utf-16")

    await query.edit_message_text(
        text=message,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="HTML"
    )


async def empire_build_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    _, building_name = query.data.split(":")
    print(building_name)
    chat_id = query.from_user.id
    user = get_user_by_chat_id(chat_id)
    empire = get_empire_by_user(user)

    if not can_build(empire, building_name):
        await query.edit_message_text(
            text=i18n.t("errors.cond_not_met"),
            reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton(text=i18n.t("buttons.back"), callback_data=f"building_menu:{building_name}")]
        ]))
        return

    result, message = create_building_in_empire(empire, building_name)
    await query.edit_message_text(
        text=message,
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text=i18n.t("buttons.back"), callback_data="empire_buildings_handler")]])
    )


async def upgrade_building_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    _, building_name = query.data.split(":")
    chat_id = query.from_user.id
    user = get_user_by_chat_id(chat_id)
    empire = get_empire_by_user(user)

    building = Buildings.get_or_none(Buildings.name == building_name)
    if not building:
        await query.edit_message_text(
            text=i18n.t("render.empire_building_other.build_not_found")
        )
        return

    empire_building = EmpireBuildings.get_or_none(
        (EmpireBuildings.empire == empire) & (EmpireBuildings.building == building)
    )

    if not can_upgrade(empire, building_name, empire_building.level):
        await query.edit_message_text(
            text=i18n.t("render.empire_building_other.upgr_not_possible"),
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text=i18n.t("buttons.back"), callback_data="empire_buildings_handler")]])
        )
        return

    result, message = upgrade_building_in_empire(empire, building_name)
    await query.edit_message_text(
        text=message,
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text=i18n.t("buttons.back"), callback_data="empire_buildings_handler")]])
    )


async def hire_units_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    _, building_name, hire_count = query.data.split(":")
    hire_count = int(hire_count)
    chat_id = query.from_user.id
    user = get_user_by_chat_id(chat_id)
    empire = get_empire_by_user(user)


    status = EmpireStatus.get_or_none(EmpireStatus.empire == empire)

    if not status:
        print("❌ Статус империи не найден!")
        return

    units_exploration_cost = status.units_exploration_cost or 1
    units_army_cost = status.units_army_cost or 2
    units_spy_cost = status.units_spy_cost or 3
    units_counterspy_cost = status.units_counterspy_cost or 3

    building = Buildings.get_or_none(name=building_name)

    if building:
        empire_building = EmpireBuildings.get_or_none(
            (EmpireBuildings.empire == empire) & (EmpireBuildings.building == building)
        )
    else:
        empire_building = None

    if not empire_building or empire_building.status not in ["completed", "producing", "idle"]:
        await query.edit_message_text(
            text=i18n.t("render.empire_building_other.hire_unit_build_not_found")
        )
        return

    production_units_map = {
        "exp_corpus": "units_exploration",
        "spy_center": "units_spy",
        "conspy_center": "units_counterspy",
        "barracks": "units_army",
    }

    if building_name not in production_units_map:
        await query.edit_message_text(
            text=i18n.t("render.empire_building_other.hire_unit_not_possible")
        )
        return

    unit_type = production_units_map[building_name]

    unit_cost = 1
    if unit_type == "units_exploration":
        unit_cost = units_exploration_cost
    if unit_type == "units_army_cost":
        unit_cost = units_army_cost
    if unit_type == "units_spy_cost":
        unit_cost = units_spy_cost
    if unit_type == "units_counterspy_cost":
        unit_cost = units_counterspy_cost

    empire_resources = EmpireResource.get_or_none(EmpireResource.empire == empire)

    if not empire_resources:
        await query.edit_message_text(
            text=i18n.t("render.empire_building_other.not_found_resources")
        )
        return

    max_affordable_units = empire_resources.gold // unit_cost
    max_capacity = empire_building.current_max_production_capacity
    available_capacity = max_capacity - empire_building.current_production

    hire_count = min(max_affordable_units, available_capacity)

    if hire_count <= 0:
        await query.edit_message_text(
            text="У вас недостаточно золота или вместимость здания исчерпана."
        )
        return


    empire_resources.gold -= hire_count * unit_cost
    empire_resources.save()

    start_train_units(empire, building_name, hire_count)

    await query.edit_message_text(
        text=i18n.t("render.empire_building_other.start_producing_units", hire_count=hire_count, unit_type=unit_type.replace('_', ' ')),
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text=i18n.t("buttons.back"), callback_data="empire_buildings_handler")]])
    )


async def cancel_build_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    _, building_name = query.data.split(":")
    chat_id = query.from_user.id
    user = get_user_by_chat_id(chat_id)
    empire = get_empire_by_user(user)

    result, message = cancel_building_in_empire(empire, building_name)

    await query.edit_message_text(
        text=message,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton(i18n.t("buttons.back"), callback_data="empire_buildings_handler")]
        ])
    )
