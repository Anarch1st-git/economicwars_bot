from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from handlers import (
    get_user_by_chat_id,
    get_empire_by_user,
    get_science_research_speed,
    can_research,
    start_research_for_empire,
    user_has_subscription,
    get_science_modifiers,
    render_progress_bar_emoji,
    cancel_research_for_empire
)
from models import (
    EmpireBuildings,
    EmpireResearch,
    Research,
    Buildings
)
from datetime import datetime
from locales.locales_names import buildings_name
from locales.locales_names import tech_name



async def empire_technologies_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.callback_query.answer()


    chat_id = update.callback_query.from_user.id
    user = get_user_by_chat_id(chat_id)
    empire = get_empire_by_user(user)


    empire_research_count = EmpireResearch.select().where(
        (EmpireResearch.empire == empire) &
        (EmpireResearch.status == "completed")
    ).count()


    total_general = Research.select().where(Research.research_type == "general").count()
    total_extracting = Research.select().where(Research.research_type == "extracting").count()

    completed_general = EmpireResearch.select().join(Research).where(
        (EmpireResearch.empire == empire) &
        (EmpireResearch.status == "completed") &
        (Research.research_type == "general")
    ).count()

    completed_extracting = EmpireResearch.select().join(Research).where(
        (EmpireResearch.empire == empire) &
        (EmpireResearch.status == "completed") &
        (Research.research_type == "extracting")
    ).count()

    empire_researched_general_complete = completed_general == total_general
    empire_researched_extracting_complete = completed_extracting == total_extracting


    empire_research_speed_count = get_science_research_speed(empire)


    message = f"Всего изучено технологий: {empire_research_count}\n"


    empire_pending_researches = EmpireResearch.select().join(Research).where(
        (EmpireResearch.empire == empire) &
        (EmpireResearch.status == "pending")
    )

    if empire_pending_researches.exists():
        message += "В данный момент изучается:\n"
        for research in empire_pending_researches:
            message += f"🔬 {research.research.name}\n"

        message += f"\nТекущая скорость изучения: +{empire_research_speed_count} ед. / час\n"
    elif empire_researched_general_complete and empire_researched_extracting_complete:
        message += "Вы изучили все технологии!\n"
    else:
        message += f"Текущая скорость изучения: +{empire_research_speed_count} ед. / час\n"

    message += "Выберите раздел науки:\n"


    keyboard = []

    if not empire_researched_general_complete:
        keyboard.append([InlineKeyboardButton("Общие науки", callback_data="empire_research_general:0")])

    if not empire_researched_extracting_complete:
        keyboard.append([InlineKeyboardButton("Технологии добычи ресурсов", callback_data="empire_research_extracting_handler")])

    keyboard.append([InlineKeyboardButton("Назад", callback_data="manage_empire_handler")])

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.callback_query.edit_message_text(
        text=message,
        reply_markup=reply_markup,
        parse_mode="HTML"
    )



async def empire_research_general_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.callback_query.answer()

    data = update.callback_query.data
    print(data.split(":"))
    _, page_str = data.split(":")
    page = int(page_str)

    ITEMS_PER_PAGE = 5

    chat_id = update.callback_query.from_user.id
    user = get_user_by_chat_id(chat_id)
    empire = get_empire_by_user(user)

    all_researches = Research.select().where(Research.research_type == "general")


    completed_researches = set()
    in_progress_researches = {}
    empire_researches = EmpireResearch.select().where(EmpireResearch.empire == empire)
    for er in empire_researches:
        if er.status == "completed":
            completed_researches.add(er.research.id)
        elif er.status == "pending":
            in_progress_researches[er.research.id] = er

    available_researches = []
    locked_researches = []

    for research in all_researches:
        if research.id in completed_researches or research.id in in_progress_researches:
            continue
        available_researches.append((f"🔬 {tech_name[research.name]}", research.id))


    lab = (EmpireBuildings
           .select(EmpireBuildings, Buildings)
           .join(Buildings)
           .where(EmpireBuildings.empire == empire, Buildings.name == "laboratory")
           .get_or_none())
    lab_level = lab.level if lab else 0
    base_science_per_hour = lab.current_production * lab_level if lab_level > 0 else 0
    science_modifier = get_science_modifiers(empire)
    actual_science_per_hour = base_science_per_hour * science_modifier

    message = (
        f"<b>Общие технологии</b>\n\n"
        f"Изучено: {len(completed_researches)} / {len(all_researches)}\n\n"
    )

    if in_progress_researches:
        message += "<b>⏳ Текущие исследования:</b>\n"
        for research_id, empire_research in in_progress_researches.items():
            research_obj = empire_research.research
            now = datetime.now()
            time_passed = (now - empire_research.last_update).total_seconds() / 3600
            gained = actual_science_per_hour * time_passed
            current_progress = empire_research.progress + gained
            remaining = max(empire_research.total_points - current_progress, 0)
            percent = min(int((current_progress / empire_research.total_points) * 100), 100)
            if actual_science_per_hour > 0:
                hours_left = remaining / actual_science_per_hour
                h, m, s = int(hours_left), int((hours_left % 1) * 60), int((((hours_left % 1) * 60) % 1) * 60)
            else:
                h, m, s = 99, 59, 59
            progress_bar = render_progress_bar_emoji(current_progress, empire_research.total_points)
            message += f"🔬 {tech_name[research_obj.name]} — {h}ч {m}м {s}сек\n{progress_bar}\n"
        message += "\n"

    message += (
        "<b>🔬 Доступные для изучения:</b>\n" +
        ("\n".join(r[0] for r in available_researches) if available_researches else "Нет доступных технологий.") +
        "\n\n<b>🔒 Недоступные:</b>\n" +
        ("\n".join(locked_researches) if locked_researches else "Все технологии доступны.")
    )


    total_pages = (len(available_researches) + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE
    page = max(0, min(page, total_pages - 1))
    start = page * ITEMS_PER_PAGE
    end = start + ITEMS_PER_PAGE
    page_items = available_researches[start:end]

    keyboard = []


    for research_id, empire_research in in_progress_researches.items():
        research_obj = empire_research.research
        keyboard.append([InlineKeyboardButton(
            f"⏳ {tech_name[research_obj.name]}",
            callback_data=f"research_menu:{research_id}:general"
        )])

    for text, research_id in page_items:
        keyboard.append([InlineKeyboardButton(text, callback_data=f"research_menu:{research_id}:general")])


    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton("⏮ Пред. стр.", callback_data=f"empire_research_general:{page - 1}"))
    if page < total_pages - 1:
        nav_buttons.append(InlineKeyboardButton("⏭ Сл. стр.", callback_data=f"empire_research_general:{page + 1}"))
    if nav_buttons:
        keyboard.append(nav_buttons)

    keyboard.append([InlineKeyboardButton("Назад", callback_data="empire_technologies_handler")])

    print(f"current page: {page}")
    print(f"page_items: {page_items}")
    print(f"keyboard: {[b[0].callback_data for b in keyboard if b]}")

    await update.callback_query.edit_message_text(
        text=message,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="HTML"
    )



async def empire_research_extracting_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.callback_query.answer()

    extracting_types = {
        "wood": "леса",
        "gold": "золота",
        "oil": "нефти",
        "diamond": "алмазов",
        "energy": "энергии"
    }

    message = "Выберите категорию ресурсов для изучения технологий добычи:\n\n"
    keyboard = [
        [InlineKeyboardButton(f"Добыча {resource_name}", callback_data=f"extracting_category:{resource_type}")]
        for resource_type, resource_name in extracting_types.items()
    ]

    keyboard.append([InlineKeyboardButton("Назад", callback_data="empire_technologies_handler")])
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.callback_query.edit_message_text(text=message, reply_markup=reply_markup, parse_mode="HTML")



async def extracting_category_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.callback_query.answer()

    _, resource_type = update.callback_query.data.split(":")
    buildings = Buildings.select().where(Buildings.building_type == f"economic:{resource_type}")

    message = "Выберите здание для изучения технологий:\n"
    keyboard = [
        [InlineKeyboardButton(buildings_name[building.name], callback_data=f"building_research:{building.id}:extracting")]
        for building in buildings
    ]
    keyboard.append([InlineKeyboardButton("Назад", callback_data="empire_research_extracting_handler")])

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.edit_message_text(
        text=message,
        reply_markup=reply_markup,
        parse_mode="HTML"
    )


async def building_research_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.callback_query.answer()

    _, building_id, previous_menu = update.callback_query.data.split(":")
    building = Buildings.get_or_none(Buildings.id == building_id)
    if not building:
        await update.callback_query.edit_message_text("Ошибка: здание не найдено.")
        return

    chat_id = update.callback_query.from_user.id
    user = get_user_by_chat_id(chat_id)
    empire = get_empire_by_user(user)

    research_chain = [building.unlock_research] if building.unlock_research else []

    researched_ids = {
        r.research_id for r in EmpireResearch.select(EmpireResearch.research_id)
        .where((EmpireResearch.empire == empire) & (EmpireResearch.status == "completed"))
    }


    in_progress_researches = {
        r.research_id: r for r in EmpireResearch.select()
        .where((EmpireResearch.empire == empire) & (EmpireResearch.status == "pending"))
    }

    has_subscription = user_has_subscription(user)

    message = f"<b>Технологии для {buildings_name[building.name]}</b>\n\n"


    completed_researches = [f"✅ {tech_name[r.name]}" for r in research_chain if r.id in researched_ids]
    if completed_researches:
        message += "\n".join(completed_researches) + "\n\n"


    message += "<b>Доступны для изучения:</b>\n"
    keyboard = []

    for r in research_chain:
        if r.id in researched_ids:
            continue

        if r.id in in_progress_researches:
            er = in_progress_researches[r.id]


            now = datetime.now()
            time_passed = (now - er.last_update).total_seconds() / 3600

            lab = (
                EmpireBuildings.select(EmpireBuildings, Buildings)
                .join(Buildings)
                .where(EmpireBuildings.empire == empire, Buildings.name == "laboratory")
                .get_or_none()
            )
            lab_level = lab.level if lab else 0
            base_science_per_hour = lab.current_production * lab_level if lab_level > 0 else 0
            science_modifier = get_science_modifiers(empire)
            actual_science_per_hour = base_science_per_hour * science_modifier

            gained = actual_science_per_hour * time_passed
            current_progress = er.progress + gained
            remaining = max(er.total_points - current_progress, 0)

            percent = min(int((current_progress / er.total_points) * 100), 100)
            progress_bar = render_progress_bar_emoji(current_progress, er.total_points)

            if actual_science_per_hour > 0:
                hours_left = remaining / actual_science_per_hour
                h, m, s = int(hours_left), int((hours_left % 1) * 60), int((((hours_left % 1) * 60) % 1) * 60)
            else:
                h, m, s = 99, 59, 59

            message += f"⏳ {r.name} — {h}ч {m}м {s}сек\n{progress_bar}\n"
        else:
            if in_progress_researches and not has_subscription:
                message += f"⚠️ Сейчас уже изучается другая технология. Завершите её или оформите подписку, чтобы изучать несколько технологий одновременно.\n"
                break
            keyboard.append([InlineKeyboardButton(f"🔬 {tech_name[r.name]}", callback_data=f"research_menu:{r.id}:{previous_menu}")])

    back_callback = "extracting_category:" + building.building_type.split(":")[1] if previous_menu == "extracting" else "empire_research_general:0"
    keyboard.append([InlineKeyboardButton("Назад", callback_data=back_callback)])

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.edit_message_text(text=message, reply_markup=reply_markup, parse_mode="HTML")



async def research_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.callback_query.answer()

    callback_data_parts = update.callback_query.data.split(":")
    print(f"callback_data_parts: {callback_data_parts}")

    research_id = callback_data_parts[1]
    previous_menu = callback_data_parts[2] if len(callback_data_parts) > 2 else "general"

    print(f"previous_menu получен как: {previous_menu}")


    research = Research.get_or_none(Research.id == research_id)
    if not research:
        await update.callback_query.edit_message_text("Ошибка: технология не найдена.")
        return


    chat_id = update.callback_query.from_user.id
    user = get_user_by_chat_id(chat_id)
    empire = get_empire_by_user(user)


    is_completed = EmpireResearch.select().where(
        (EmpireResearch.empire == empire) &
        (EmpireResearch.research == research) &
        (EmpireResearch.status == "completed")
    ).exists()


    is_research_in_progress = EmpireResearch.select().where(
        (EmpireResearch.empire == empire) &
        (EmpireResearch.status == "pending")
    ).exists()


    has_subscription = getattr(user, "has_subscription", False)


    unlocked_buildings = Buildings.select().where(Buildings.unlock_research == research)
    buildings_text = "\n".join([buildings_name[b.name] for b in unlocked_buildings]) if unlocked_buildings else "Нет новых зданий."


    message = (
        f"<b>{tech_name[research.name]}</b>\n\n"
        f"{research.description}\n\n"
        f"Открывает здания:\n{buildings_text}\n"
    )


    if not is_completed and is_research_in_progress and not has_subscription:
        message += "\n⚠️ Сейчас уже изучается другая технология. Завершите её или оформите подписку, чтобы изучать несколько технологий одновременно."


    keyboard = []


    this_research_in_progress = EmpireResearch.get_or_none(
        (EmpireResearch.empire == empire) &
        (EmpireResearch.research == research) &
        (EmpireResearch.status == "pending")
    )

    if not is_completed:
        if this_research_in_progress:

            keyboard.append([
                InlineKeyboardButton("❌ Отменить изучение", callback_data=f"cancel_research:{research.id}:{previous_menu}")
            ])
        elif not is_research_in_progress or has_subscription:

            lab = (EmpireBuildings
                .select(EmpireBuildings, Buildings)
                .join(Buildings)
                .where(EmpireBuildings.empire == empire, Buildings.name == "laboratory")
                .get_or_none())

            lab_level = lab.level if lab else 0
            lab_production = lab.current_production if lab else 0

            base_science_per_hour = lab_production * lab_level
            science_modifiers = get_science_modifiers(empire)
            actual_science_per_hour = base_science_per_hour * science_modifiers

            if actual_science_per_hour > 0:
                time_hours = research.total_points / actual_science_per_hour
                hours = int(time_hours)
                minutes = int((time_hours - hours) * 60)
                time_label = f"{hours}ч {minutes}м"
            else:
                time_label = "н/д"

            keyboard.append([
                InlineKeyboardButton(f"Изучить ⏱ {time_label}", callback_data=f"start_research:{research.id}:{previous_menu}")
            ])


    if previous_menu == "extracting":
        keyboard.append([InlineKeyboardButton("Назад", callback_data="empire_research_extracting_handler")])
    else:
        keyboard.append([InlineKeyboardButton("Назад", callback_data="empire_research_general:0")])

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.callback_query.edit_message_text(
        text=message,
        reply_markup=reply_markup,
        parse_mode="HTML"
    )



async def start_research_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.callback_query.answer()

    callback_data_parts = update.callback_query.data.split(":")
    research_id = callback_data_parts[1]
    previous_menu = callback_data_parts[2] if len(callback_data_parts) > 2 else "general"

    research = Research.get_or_none(Research.id == research_id)

    if not research:
        await update.callback_query.edit_message_text("Ошибка: технология не найдена.")
        return

    chat_id = update.callback_query.from_user.id
    user = get_user_by_chat_id(chat_id)
    empire = get_empire_by_user(user)


    research = Research.get_or_none(Research.id == research_id)
    if not research:
        await update.callback_query.edit_message_text(
            text="Неверный ID технологии.",
            parse_mode="HTML"
        )
        return


    result, msg = can_research(empire, research.name)
    if not result:
        await update.callback_query.edit_message_text(
            text=msg,
            parse_mode="HTML"
        )
        return

    result = start_research_for_empire(empire, research.name)


    if previous_menu == "extracting":
        back_callback = "empire_research_extracting_handler"
    else:
        back_callback = "empire_research_general:0"

    keyboard = [[InlineKeyboardButton("Назад", callback_data=back_callback)]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.callback_query.edit_message_text(
        text=result,
        reply_markup=reply_markup
    )


async def cancel_research_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.callback_query.answer()

    callback_data_parts = update.callback_query.data.split(":")
    research_id = int(callback_data_parts[1])


    chat_id = update.callback_query.from_user.id
    user = get_user_by_chat_id(chat_id)
    empire = get_empire_by_user(user)

    result = cancel_research_for_empire(empire, research_id)

    keyboard = []
    keyboard = [[InlineKeyboardButton("Назад", callback_data="empire_technologies_handler")]]
    reply_markup = InlineKeyboardMarkup(keyboard)


    await update.callback_query.edit_message_text(
        text=result,
        reply_markup=reply_markup,
        parse_mode="HTML"
    )
