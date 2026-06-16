from handlers import (
    get_user_by_chat_id,
    get_empire_by_user,
    create_building_in_empire,
    can_build,
    get_completed_research_count,
    get_completed_research_names_by_type,
    get_names_pending_researches,
    get_completed_buildings_count,
    get_names_buildings_category,
    get_total_speed_research,
    can_research,
    is_empty_research_by_empire,
    is_all_researches_completed,
    start_research_for_empire,
    get_total_empiries_from_cluster,
    start_mission_exploration,
    start_mission_attack_location,
    get_found_locations_by_empire,
    get_location_by_id,
    generate_items_for_location
)

from models import (
    Research,
    Buildings,
    EmpireResearch,
    EmpireMission
)

import json


def empire_research_extracting_wood_handler(chat_id):
    buildings_name = {
        "Лесопилка":"sawmill",
        "Древообрабатывающий комбинат":"woodworking_plant",
        "Биотопливный завод":"biofuel_plant",
        "Лесной заповедник":"forest_reserve",
        "Центр лесного биоразнообразия":"forest_center"
    }

    user = get_user_by_chat_id(chat_id)
    empire = get_empire_by_user(user)


    wood_buildings = Buildings.select().where(Buildings.building_type == "economic:wood")


    researched_ids = (
        EmpireResearch.select(EmpireResearch.research_id)
        .where((EmpireResearch.empire == empire) & (EmpireResearch.status == "completed"))
    )
    researched_ids = {r.research_id for r in researched_ids}


    available_buildings = []
    for building in wood_buildings:
        if building.unlock_research is None or building.unlock_research not in researched_ids:
            available_buildings.append(building)


    message = (
        f"Для каждой добывающей постройки есть своя ветка технологий. Выберете ветку для:\n"
    )


    keyboard = [
        {
            "name": building.name,
            "callback": f"empire_research_extracting_wood_{buildings_name[building.name]}_handler"
        }
        for building in available_buildings
    ]


    keyboard.append({"name": "Назад", "callback": "empire_research_extracting_handler"})


    print(message)
    for button in keyboard:
        print(f"[{button['name']}] -> {button['callback']}")


def empire_research_extracting_wood_sawmill_handler(chat_id):
    user = get_user_by_chat_id(chat_id)
    empire = get_empire_by_user(user)


    sawmill = Buildings.get_or_none(Buildings.name == "Лесопилка")
    if not sawmill or not sawmill.unlock_research:
        return

    last_research = sawmill.unlock_research

    research_chain = []
    current_research = last_research
    while current_research:
        research_chain.append(current_research)
        current_research = current_research.required_research


    researched_ids = (
        EmpireResearch.select(EmpireResearch.research_id)
        .where((EmpireResearch.empire == empire) & (EmpireResearch.status == "completed"))
    )
    researched_ids = {r.research_id for r in researched_ids}


    CHECK_MARK = "✅"
    CROSS_MARK = "❌"

    completed_researches = []
    pending_researches = []

    for research in reversed(research_chain):
        if research.id in researched_ids:
            completed_researches.append(f"{CHECK_MARK} {research.name}")
        else:
            pending_researches.append((f"{CROSS_MARK} {research.name}", research.id))

    message = (
        f"Изучено {len(completed_researches)}\n\n"
        + "\n".join(completed_researches)
        + "Изучить:\n"
    )


    keyboard = [
        {
            "name": research[0].strip(),
            "callback": f"empire_research_id{research[1]}"
        }
        for research in pending_researches
    ]


    keyboard.append({"name": "Назад", "callback": "empire_research_extracting_wood_handler"})


    print(message)
    for button in keyboard:
        print(f"[{button['name']}] -> {button['callback']}")


def empire_research_extracting_wood_woodworking_plant_handler(chat_id):
    user = get_user_by_chat_id(chat_id)
    empire = get_empire_by_user(user)


    sawmill = Buildings.get_or_none(Buildings.name == "Древообрабатывающий комбинат")
    if not sawmill or not sawmill.unlock_research:
        return

    last_research = sawmill.unlock_research

    research_chain = []
    current_research = last_research
    while current_research:
        research_chain.append(current_research)
        current_research = current_research.required_research


    researched_ids = (
        EmpireResearch.select(EmpireResearch.research_id)
        .where((EmpireResearch.empire == empire) & (EmpireResearch.status == "completed"))
    )
    researched_ids = {r.research_id for r in researched_ids}


    CHECK_MARK = "✅"
    CROSS_MARK = "❌"

    completed_researches = []
    pending_researches = []

    for research in reversed(research_chain):
        if research.id in researched_ids:
            completed_researches.append(f"{CHECK_MARK} {research.name}")
        else:
            pending_researches.append((f"{CROSS_MARK} {research.name}", research.id))

    message = (
        f"Изучено {len(completed_researches)}\n\n"
        + "\n".join(completed_researches)
        + "Изучить:\n"
    )


    keyboard = [
        {
            "name": research[0].strip(),
            "callback": f"empire_research_id{research[1]}"
        }
        for research in pending_researches
    ]


    keyboard.append({"name": "Назад", "callback": "empire_research_extracting_wood_handler"})


    print(message)
    for button in keyboard:
        print(f"[{button['name']}] -> {button['callback']}")


def empire_research_extracting_wood_biofuel_plant_handler(chat_id):
    user = get_user_by_chat_id(chat_id)
    empire = get_empire_by_user(user)


    sawmill = Buildings.get_or_none(Buildings.name == "Биотопливный завод")
    if not sawmill or not sawmill.unlock_research:
        return

    last_research = sawmill.unlock_research

    research_chain = []
    current_research = last_research
    while current_research:
        research_chain.append(current_research)
        current_research = current_research.required_research


    researched_ids = (
        EmpireResearch.select(EmpireResearch.research_id)
        .where((EmpireResearch.empire == empire) & (EmpireResearch.status == "completed"))
    )
    researched_ids = {r.research_id for r in researched_ids}


    CHECK_MARK = "✅"
    CROSS_MARK = "❌"

    completed_researches = []
    pending_researches = []

    for research in reversed(research_chain):
        if research.id in researched_ids:
            completed_researches.append(f"{CHECK_MARK} {research.name}")
        else:
            pending_researches.append((f"{CROSS_MARK} {research.name}", research.id))

    message = (
        f"Изучено {len(completed_researches)}\n\n"
        + "\n".join(completed_researches)
        + "Изучить:\n"
    )


    keyboard = [
        {
            "name": research[0].strip(),
            "callback": f"empire_research_id{research[1]}"
        }
        for research in pending_researches
    ]


    keyboard.append({"name": "Назад", "callback": "empire_research_extracting_wood_handler"})


    print(message)
    for button in keyboard:
        print(f"[{button['name']}] -> {button['callback']}")



def empire_research_extracting_energy_handler(chat_id):
    buildings_name = {
        "Солнечная электростанция": "solar_power",
        "Ветроэлектрическая станция": "wind_power",
        "Гидроэлектрическая станция": "hydro_power",
        "Термальная электростанция": "term_power",
        "Водородная электростанция": "hydrogen_power",
        "Смарт-энергетический центр": "smart_center"
    }

    user = get_user_by_chat_id(chat_id)

    if not user:
        print("Вы не зарегистрированы.")
        return

    empire = get_empire_by_user(user)


    buildings = Buildings.select().where(Buildings.building_type == "economic:energy")


    researched_ids = {
        r.research_id
        for r in EmpireResearch.select(EmpireResearch.research_id)
        .where((EmpireResearch.empire == empire) & (EmpireResearch.status == "completed"))
    }


    available_buildings = []
    for building in buildings:
        if building.unlock_research is None or building.unlock_research not in researched_ids:
            available_buildings.append(building)


    message = (
        "Для каждой добывающей постройки есть своя ветка технологий. Выберете ветку для:\n"
    )


    print(message)
    for idx, building in enumerate(available_buildings):
        print(f"[{idx + 1}] {building.name}")
    print("[0] Назад")


    choice = int(input("Введите номер выбранного варианта: "))
    if choice == 0:
        print("Возврат к предыдущему меню")
    else:
        selected_building = available_buildings[choice - 1]
        print(f"Вы выбрали: {selected_building.name}")



def empire_research_extracting_energy_building_handler(building_key):
    buildings_name_reverse = {
        "solar_power": "Солнечная электростанция",
        "wind_power": "Ветроэлектрическая станция",
        "hydro_power": "Гидроэлектрическая станция",
        "term_power": "Термальная электростанция",
        "hydrogen_power": "Водородная электростанция",
        "smart_center": "Смарт-энергетический центр"
    }


    building_name = buildings_name_reverse.get(building_key)

    if not building_name:
        print("Ошибка: неизвестная постройка!")
        return

    print(f"Выбранное здание: {building_name}")


    chat_id = input("Введите chat_id: ")
    user = get_user_by_chat_id(chat_id)
    empire = get_empire_by_user(user)


    build = Buildings.get_or_none(Buildings.name == building_name)
    if not build or not build.unlock_research:
        print("Для этой постройки нет доступных технологий.")
        return

    last_research = build.unlock_research


    research_chain = []
    current_research = last_research
    while current_research:
        research_chain.append(current_research)
        current_research = current_research.required_research


    researched_ids = {
        r.research_id
        for r in EmpireResearch.select(EmpireResearch.research_id)
        .where((EmpireResearch.empire == empire) & (EmpireResearch.status == "completed"))
    }


    CHECK_MARK = "✅"
    CROSS_MARK = "❌"

    completed_researches = []
    pending_researches = []

    for research in reversed(research_chain):
        if research.id in researched_ids:
            completed_researches.append(f"{CHECK_MARK} {research.name}")
        else:
            pending_researches.append((f"{CROSS_MARK} {research.name}", research.id))

    print(f"Изучено {len(completed_researches)} технологий:")
    print("\n".join(completed_researches))

    print("\nДоступно для изучения:")
    for idx, research in enumerate(pending_researches):
        print(f"[{idx + 1}] {research[0]}")
    print("[0] Назад")


    choice = int(input("Введите номер выбранного варианта: "))
    if choice == 0:
        print("Возврат к предыдущему меню")
    else:
        selected_research = pending_researches[choice - 1]
        print(f"Вы выбрали изучение: {selected_research[0]}")



def empire_research_id(callback_data):

    _, type_resource, research_id = callback_data.split(":")


    chat_id = input("Введите chat_id: ")
    user = get_user_by_chat_id(chat_id)
    empire = get_empire_by_user(user)


    research = Research.get_or_none(Research.id == research_id)
    if not research:
        print("Неверный ID технологии.")
        return


    if not can_research(empire, research.name):
        print("Вы не можете изучить данную технологию.")
        return


    if not start_research_for_empire(empire, research.name):
        print(f"Ошибка начала изучения технологии {research.name}")
        return

    print(f"Вы начали изучать технологию {research.name}")
    print("[0] Назад")


    choice = int(input("Введите номер выбранного варианта: "))
    if choice == 0:
        print("Возврат к предыдущему меню")



def cluster_map_list_empiries(chat_id):
    user = get_user_by_chat_id(chat_id)
    empire = get_empire_by_user(user)
    current_cluster = empire.cluster

    empires_from_cluster = get_total_empiries_from_cluster(current_cluster)

    caption = (
        f"Отчёт о других империях в данном кластере.\n\n"
    )

    for empire in empires_from_cluster:
        empire_id = empire.empire_id
        empire_name = empire.name
        caption += f"Империя {empire_name}. ID {empire_id}\n"

    print(caption)


def confirm_for_exploration_empire_handler(chat_id, count_units_exp, radius):
    user = get_user_by_chat_id(chat_id)
    empire = get_empire_by_user(user)

    mission, msg = start_mission_exploration(empire, count_units_exp, radius)
    if mission is not None:
        print("Миссия начата.")
    else:
        print(f"Ошибка: {msg}")


def cluster_map_finder_locations(chat_id):
    user = get_user_by_chat_id(chat_id)
    empire = get_empire_by_user(user)

    found_locations = get_found_locations_by_empire(empire)

    messages = []

    for location_text, location_id in found_locations:
        messages.append(location_text)

    message = "📜 <b>Отчёт о найденных локациях</b>:\n\n" + "\n\n".join(messages) if messages else "📜 <b>Отчёт о найденных локациях</b>:\n\n❌ Ничего не найдено."

    print(message)


def confirm_for_attack_location_handler(chat_id, location_id, count_units):
    user = get_user_by_chat_id(chat_id)
    empire = get_empire_by_user(user)


    mission, msg = start_mission_attack_location(empire, location_id, count_units)

    if mission is not None:
        print(f"Начата атака на (ID: {location_id})")
    else:
        print(f"Ошибка: {msg}")




confirm_for_attack_location_handler("9942620947", "1653", 10)
