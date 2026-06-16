from peewee import DoesNotExist, IntegrityError, fn, JOIN
from datetime import datetime, timedelta
import random
import logging
import json
from collections import Counter
from validations import validate_positive_number
from models import (
    GameGlobalSettings,
    UserGameSettings,
    UserData,
    Busters,
    Resource,
    RatingLayer,
    RatingLayerCluster,
    Season,
    GameEventTemplate,
    SeasonEvent,
    GameEvents,
    Research,
    Buildings,
    DailyLootbox,
    DailyLootLucky,
    Empire,
    EmpireBusters,
    EmpireBuildings,
    EmpireResearch,
    EmpireResource,
    Items,
    EmpireItems,
    Mission,
    EmpireMission,
    EmpireLocations,
    EmpireStatus,
    MarketRate,
    EmpireMissionResult,
    GameEvents,
    Quests,
    EmpireQuests,
    News,
    LogEventUser,
    LogEventSystem
)
from db import db
import uuid
try:
    from send_messages import send_message_sync
except Exception as e:
    print(f"Error import send_message_sync: {e}")
from math import ceil
from locales.locales_names import locations_name, resource_name_count, items_name, quests_name, tech_name, buildings_name


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



def write_news(text: str) -> None:
    MAX_NEWS_COUNT = 50

    News.create(text=text, date=datetime.now())

    extra_count = News.select().count() - MAX_NEWS_COUNT
    if extra_count > 0:
        oldest_news = News.select().order_by(News.date.asc()).limit(extra_count)
        for news in oldest_news:
            news.delete_instance()


def get_news_page(page: int, per_page: int = 5):
    query = (News
             .select()
             .order_by(News.date.desc())
             .paginate(page, per_page))
    return list(query)


def get_news_total_pages(per_page: int = 5):
    total = News.select().count()
    return (total + per_page - 1) // per_page





def save_log_event_user(chat_id, event_data):
    try:
        LogEventUser.create(
            initiator=chat_id,
            event_data=event_data
        )
    except Exception as err:
        print(f"Не удолось сохранить событие для пользователя {chat_id}\nОшибка: {err}")





def save_log_event_system(event_data):
    try:
        LogEventSystem.create(
            event_data=event_data
        )
    except Exception as err:
        print(f"Не удолось сохранить системное событие.\nОшибка: {err}")





def get_all_users():
    try:
        users = UserData.select()
        return users
    except Exception as e:
        print(f"Ошибка получения пользователей: {e}")
        return None





def get_user_by_chat_id(chat_id):
    """
    Получает пользователя по chat_id из базы данных.

    :param chat_id: ID чата пользователя.
    :return: Объект UserData или словарь с информацией об ошибке.
    """
    try:
        user = UserData.get(UserData.chat_id == chat_id)
        return user
    except DoesNotExist:

        return {"error": True, "message": f"Пользователь с чатом {chat_id} не найден."}
    except Exception as e:

        logger.error(f"Ошибка получения пользователя с чатом {chat_id}: {e}")
        return {"error": True, "message": "Произошла ошибка при получении пользователя."}





def get_user_by_empire(empire):
    """Получает пользователя по объекту империи."""
    return empire.user if empire else None





def get_all_empires():
    try:
        empires = Empire.select()
        return empires
    except Exception as e:
        print(f"Ошибка получения империй: {e}")
        return None





def get_empire_by_user(user):
    try:
        empire = Empire.get(Empire.user == user)
        return empire
    except DoesNotExist:
        print(f"Ошибка: Империя для пользователя {user} не найдена.")
        return None
    except Exception as e:
        print(f"Ошибка получения империи для пользователя {user}: {e}")
        return None





def get_empire_by_id(empire_id):
    try:
        empire = Empire.get(Empire.id == empire_id)
        return empire
    except DoesNotExist:
        print(f"Ошибка: Империя с ID {empire_id} не найдена.")
        return None
    except Exception as e:
        print(f"Ошибка получения империи с ID {empire_id}: {e}")
        return None





def get_id_from_empire(empire):
    try:
        return empire.empire_id
    except DoesNotExist:
        print(f"Ошибка: Империя {empire} не найдена.")
        return None
    except Exception as e:
        print(f"Ошибка получения ID империи {empire}: {e}")
        return None





def user_has_subscription(user: UserData):
    return user.subscription_status





def empire_has_subscription(empire: Empire) -> bool:
    user = get_user_by_empire(empire)
    return user_has_subscription(user)


def get_game_settings(user: UserData):
    try:
        user_game_settings = UserGameSettings.get(UserGameSettings.user == user)
        return user_game_settings
    except DoesNotExist:
        print(f"Ошибка: настройки для {user} не найдены.")
        return None
    except Exception as e:
        print(f"Ошибка получения настроек для {user}: {e}")
        return None





def create_user(chat_id: int, username: str):
    """Регистрирует пользователя, избегая дубликатов"""
    try:
        with db.atomic():
            user, created = UserData.get_or_create(chat_id=chat_id, defaults={'username': username})
            return user, created
    except IntegrityError:
        print(f"❌ Ошибка: пользователь с chat_id {chat_id} уже существует.")
        return None, False





def are_empires_in_same_cluster(empire_id1, empire_id2):
    """
    Проверяет, находятся ли две империи в одном и том же кластере.

    :param empire_id1: ID первой империи
    :param empire_id2: ID второй империи
    :return: True, если империи находятся в одном кластере, иначе False.
    :raises DoesNotExist: Если хотя бы одна из империй не найдена.
    """
    try:

        empire1 = Empire.get(Empire.id == empire_id1)
        empire2 = Empire.get(Empire.id == empire_id2)


        if empire1.cluster and empire2.cluster:

            return (
                empire1.cluster == empire2.cluster and
                empire1.cluster.layer == empire2.cluster.layer
            )
        else:
            return False
    except DoesNotExist:
        return False





def get_completed_buildings_count(empire: Empire) -> int:
    """
    Получает количество завершенных построек для империи.
    """
    valid_statuses = ["completed", "producing", "idle", "upgrading"]

    return EmpireBuildings.select().where(
        (EmpireBuildings.empire == empire) &
        (EmpireBuildings.status.in_(valid_statuses))
    ).count()





def get_names_buildings_category(empire: Empire, category: str) -> list[str]:

    if category == "economic":
        buildings = EmpireBuildings.select().join(Buildings).where(
            (EmpireBuildings.empire == empire) & (Buildings.building_type.startswith(category))
        )
    else:
        buildings = EmpireBuildings.select().join(Buildings).where(
            (EmpireBuildings.empire == empire) & (Buildings.building_type == category)
        )
    return [building.building.name for building in buildings]



















































def start_research_for_empire(empire: Empire, research_name: str) -> str:
    try:
        if not has_building_complete(empire, "laboratory"):
            return f"❌ Исследование невозможно: у империи '{empire.name}' нет лаборатории!"

        if EmpireResearch.select().where(
            (EmpireResearch.empire == empire) &
            (EmpireResearch.research.name == research_name) &
            (EmpireResearch.status == "pending")
        ).exists():
            return f"⚙ Исследование '{research_name}' уже выполняется!"

        research = Research.get(Research.name == research_name)

        EmpireResearch.create(
            empire=empire,
            research=research,
            research_start=datetime.now(),
            progress=0.0,
            status="pending",
            total_points=research.total_points,
            last_update=datetime.now()
        )

        formatted_news_text = (
            f"Империя {empire.name} начинает исследование технологии - \"{tech_name[research_name]}\""
        )
        write_news(formatted_news_text)


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

        return f"✅ Исследование '{tech_name[research_name]}' успешно начато для империи '{empire.name}'.\n⏱ Ожидаемое время изучения: {time_label}"
    except Exception as e:
        return f"❌ Ошибка при начале исследования: {e}"





def get_name_researches_category(empire: Empire, category: str) -> list[str]:
    """
    Получает список имен технологий определённой категории империи.

    :param empire: Объект империи.
    :param category: Категория технологий (например, 'general', 'extracting').
    :return: Список имен технологий.
    """
    researches = EmpireResearch.select().join(Research).where(
        (EmpireResearch.empire == empire) & (Research.research_type == category)
    )
    return [research.research.name for research in researches]





def get_completed_research_count(empire: Empire) -> int:
    """
    Получает количество изученных технологий для империи,
    имеющих статус 'completed'.
    """
    return EmpireResearch.select().where(
        (EmpireResearch.empire == empire) &
        (EmpireResearch.status == "completed")
    ).count()





def get_names_pending_researches(empire: Empire) -> int:
    """
    Получает имена изучаемых в данный момент технологий для империи,
    имеющих статус 'pending'.
    """
    return EmpireResearch.select().where(
        (EmpireResearch.empire == empire) &
        (EmpireResearch.status == "pending")
    ).count()





def get_completed_research_names_by_type(empire: Empire, research_type: str) -> list[str]:
    """
    Получает список имен изученных технологий в заданной категории для указанной империи.

    :param empire: Империя, для которой выполняется запрос.
    :param research_type: Тип технологии (значение поля research_type).
    :return: Список имен изученных технологий.
    """
    query = (
        Research.select(Research.name)
        .join(EmpireResearch, on=(Research.id == EmpireResearch.research))
        .where(
            (EmpireResearch.empire == empire) &
            (EmpireResearch.status == "completed") &
            (Research.research_type == research_type)
        )
    )
    return [research.name for research in query]





def is_all_researches_completed(empire: Empire, extracting_type: str) -> bool:

    required_researches = Research.select().where(
        (Research.research_type == "extracting") &
        (Research.extracting_type == extracting_type)
    )


    completed_researches = EmpireResearch.select(EmpireResearch.research).where(
        (EmpireResearch.empire == empire) &
        (EmpireResearch.status == "completed")
    )


    required_ids = {research.id for research in required_researches}
    completed_ids = {research.research.id for research in completed_researches}


    return required_ids.issubset(completed_ids)





def is_empty_research_by_empire(empire: Empire) -> bool:
    return not EmpireResearch.select().where(EmpireResearch.empire == empire).exists()





def can_research(empire: Empire, research_name: str) -> bool:
    """
    Проверяет, может ли империя начать изучение указанной технологии.

    :param empire: Объект империи.
    :param research_name: Название технологии для проверки.
    :return: True, если можно начать изучение, иначе False.
    """
    try:

        research = Research.get_or_none(Research.name == research_name)
        if not research:
            return False, f"Исследование с именем '{research_name}' не найдено."












        existing_research = EmpireResearch.get_or_none(
            (EmpireResearch.empire == empire) &
            (EmpireResearch.research == research)
        )
        if existing_research and existing_research.status in "pending":
            return False, f"Технология '{research_name}' уже находится в процессе изучения."

        return True, None

    except Exception as e:
        return False, f"Ошибка при проверке возможности исследования: {e}"





def get_items_count(empire: Empire) -> int:
    """
    Получает количество предметов в империи.
    """
    return EmpireItems.select().where(EmpireItems.empire == empire).count()





def get_total_resources(empire: Empire) -> dict:
    """
    Получает общее количество всех ресурсов для империи по объекту империи.
    Возвращает словарь с названиями ресурсов и их количеством.
    """
    empire_resources = EmpireResource.get(EmpireResource.empire == empire)

    return {
        "wood": empire_resources.wood,
        "gold": empire_resources.gold,
        "oil": empire_resources.oil,
        "diamond": empire_resources.diamond,

        "units_army": empire_resources.units_army,
        "units_spy": empire_resources.units_spy,
        "units_counterspy": empire_resources.units_counterspy,
        "units_exploration": empire_resources.units_exploration
    }





def get_resource_count(empire: Empire, resource_name: str) -> int:
    """
    Получает количество конкретного ресурса для империи по её ID и имени ресурса.
    """
    resource_field = getattr(EmpireResource, resource_name, None)

    if resource_field:
        empire_resources = EmpireResource.get(EmpireResource.empire == empire)
        return getattr(empire_resources, resource_name)
    else:
        raise ValueError(f"Resource '{resource_name}' does not exist.")


def get_building_requirements(building_name, level=1):
    building = Buildings.get_or_none(Buildings.name == building_name)
    if not building:
        return {"tech": [], "resources": {}}

    tech_requirements = [building.unlock_research.name] if building.unlock_research else []


    upgrade_costs = {int(k): v for k, v in building.upgrade_cost.items()} if building.upgrade_cost else {}


    resource_requirements = upgrade_costs.get(level, {})

    return {"tech": tech_requirements, "resources": resource_requirements}






















































































def create_building_in_empire(empire, building_name):
    try:
        building = Buildings.get_or_none(Buildings.name == building_name)
        if not building:
            return None, f"Здание '{building_name}' не найдено."

        required_technology = building.unlock_research
        if required_technology and not has_required_technology(empire, required_technology.name):
            return None, f"Технология '{required_technology.name}' не изучена. Строительство невозможно."

        existing_building = EmpireBuildings.get_or_none(
            (EmpireBuildings.empire == empire) & (EmpireBuildings.building == building)
        )
        if existing_building:
            return None, f"'{building_name}' уже построено в вашей империи."

        energy_needed = building.energy_used.get("1") or 0
        total_used, total_gen = get_total_energy_usage_and_generation(empire)

        if energy_needed < 0 and (total_gen + energy_needed < total_used):
            return None, f"Недостаточно энергии для строительства '{building_name}'. Увеличьте генерацию энергии."

        required_resources = get_building_requirements(building_name).get("resources", {})
        now = datetime.now()


        if not required_resources:
            new_building = EmpireBuildings.create(
                empire=empire,
                building=building,
                current_energy_used=building.energy_used.get("1"),
                level=1,
                current_upgrade_cost=building.upgrade_cost,
                current_production=building.base_production,
                current_max_production_capacity=building.base_max_production_capacity,
                construction_start=now,
                status="pending",
                progress=0.0,
                total_points=building.base_construction_time,
                last_update=now
            )

            write_news(f"Империя {empire.name} начинает строить здание - \"{buildings_name[building_name]}\"")

            mod = get_building_speed_modifiers(empire)
            seconds = building.base_construction_time / mod
            minutes = int(seconds // 60)

            return new_building, (
                f"Вы начали строительство '{buildings_name[building_name]}'.\n"
                f"Ожидаемое время строительства: {minutes} мин."
            )


        user_resources = get_total_resources(empire)
        for res, amount in required_resources.items():
            if user_resources.get(res, 0) < amount:
                return None, f"Недостаточно ресурса '{res}' для строительства '{buildings_name[building_name]}'."

        resource_changes = {res: -amount for res, amount in required_resources.items()}
        update_resources(empire, resource_changes=resource_changes)


        new_building = EmpireBuildings.create(
            empire=empire,
            building=building,
            current_energy_used=building.energy_used.get("1"),
            level=1,
            current_upgrade_cost=building.upgrade_cost,
            current_production=0,
            current_max_production_capacity=building.base_max_production_capacity,
            construction_start=now,
            status="pending",
            progress=0.0,
            total_points=building.base_construction_time,
            last_update=now
        )

        write_news(f"Империя {empire.name} начинает строить здание - \"{buildings_name[building_name]}\"")

        mod = get_building_speed_modifiers(empire)
        seconds = building.base_construction_time / mod
        minutes = int(seconds // 60)

        return new_building, (
            f"Вы начали строительство '{buildings_name[building_name]}'.\n"
            f"Ожидаемое время строительства: {minutes} мин."
        )

    except Exception as e:
        print(f"Ошибка при строительстве: {e}")
        return None, f"Ошибка при строительстве: {str(e)}"


def cancel_building_in_empire(empire, building_name):
    building = Buildings.get_or_none(Buildings.name == building_name)
    if not building:
        return None, f"Здание '{building_name}' не найдено."

    empire_building = EmpireBuildings.get_or_none(
        (EmpireBuildings.empire == empire) &
        (EmpireBuildings.building == building) &
        (EmpireBuildings.status == "pending")
    )

    if not empire_building:
        return None, f"Строительство '{building_name}' не активно и не может быть отменено."


    requirements = get_building_requirements(building_name)
    resource_costs = requirements.get("resources", {})
    if resource_costs:
        update_resources(empire, resource_changes=resource_costs)

    empire_building.delete_instance()
    write_news(f"Империя {empire.name} отменила строительство здания \"{building.name}\"")

    return True, f"Строительство здания '{building_name}' было отменено."





def upgrade_building_in_empire(empire: Empire, building_name: str):
    try:
        empire_building = (EmpireBuildings
            .select()
            .join(Buildings)
            .where((EmpireBuildings.empire == empire) & (Buildings.name == building_name))
            .get_or_none()
        )

        if not empire_building:
            return None, "Здание не найдено."

        building = empire_building.building
        current_level = empire_building.level

        if empire_building.status == "upgrading":
            return None, "Здание уже улучшается."

        user_resources = get_total_resources(empire)
        now = datetime.now()


        if current_level >= building.max_level and building.next_building:
            next_building = Buildings.get_or_none(Buildings.name == building.next_building)
            if not next_building:
                return None, "Следующее здание не найдено."

            upgrade_cost = next_building.upgrade_cost.get("1", {})
            for res, cost in upgrade_cost.items():
                if user_resources.get(res, 0) < cost:
                    return None, "Недостаточно ресурсов."

            update_resources(empire, {res: -cost for res, cost in upgrade_cost.items()})


            empire_building.building = next_building
            empire_building.level = 1
            empire_building.current_energy_used = next_building.energy_used
            empire_building.current_upgrade_cost = next_building.upgrade_cost
            empire_building.current_production = next_building.base_production
            empire_building.current_max_production_capacity = next_building.base_max_production_capacity
            construction_time = next_building.base_construction_time

        else:

            next_level = current_level + 1
            upgrade_cost = building.upgrade_cost.get(str(next_level), {})
            for res, cost in upgrade_cost.items():
                if user_resources.get(res, 0) < cost:
                    return None, "Недостаточно ресурсов."

            update_resources(empire, {res: -cost for res, cost in upgrade_cost.items()})
            empire_building.level = next_level
            empire_building.current_energy_used = building.energy_used
            empire_building.current_upgrade_cost = building.upgrade_cost
            empire_building.current_production = building.base_production
            empire_building.current_max_production_capacity = building.base_max_production_capacity
            construction_time = building.base_construction_time * next_level


        empire_building.status = "upgrading"
        empire_building.progress = 0.0
        empire_building.total_points = construction_time
        empire_building.last_update = now
        empire_building.construction_start = now

        empire_building.save()

        return empire_building, f"Улучшение '{building_name}' запущено!"

    except Exception as e:
        print(f"Ошибка при улучшении: {e}")
        return None, f"Ошибка при улучшении: {str(e)}"






def can_build(empire: Empire, building_name: str, level: int = 1) -> bool:
    building = Buildings.get_or_none(Buildings.name == building_name)
    if not building:
        return False


    if EmpireBuildings.select().where(
        (EmpireBuildings.empire == empire) &
        (EmpireBuildings.status == "pending")
    ).exists() and not empire_has_subscription(empire):
        print("Ограничение: уже есть строящееся здание, подписка отсутствует.")
        return False

    empire_tech = get_completed_technologies(empire)
    required_tech = [building.unlock_research.name] if building.unlock_research else []

    if not all(tech in empire_tech for tech in required_tech):
        return False

    empire_resources = get_total_resources(empire)
    upgrade_costs = {int(k): v for k, v in building.upgrade_cost.items()} if building.upgrade_cost else {}
    cost = upgrade_costs.get(level, {})

    for resource, required_amount in cost.items():
        if empire_resources.get(resource, 0) < required_amount:
            return False




    projected_energy = get_empire_energy_balance(empire) + building.energy_used["1"]
    print(projected_energy)
    if projected_energy <= 0:
        print("Недостаточно энергии для строительства")
        return False

    return True





def can_upgrade(empire: Empire, building_name: str) -> bool:
    empire_building = (EmpireBuildings
        .select()
        .join(Buildings)
        .where((EmpireBuildings.empire == empire) & (Buildings.name == building_name))
        .get_or_none()
    )

    if not empire_building:
        return False

    if empire_building.status == 'upgrading':
        return False


    if EmpireBuildings.select().where(
        (EmpireBuildings.empire == empire) &
        (EmpireBuildings.status == "upgrading") &
        (EmpireBuildings.id != empire_building.id)
    ).exists() and not empire_has_subscription(empire):
        print("Ограничение: уже идёт улучшение другого здания, подписка отсутствует.")
        return False

    building = empire_building.building
    current_level = empire_building.level
    empire_resources = get_total_resources(empire)


    if current_level >= building.max_level and building.next_building:
        next_building = Buildings.get_or_none(Buildings.name == building.next_building)
        if not next_building:
            return False
        cost = next_building.upgrade_cost.get("1", {})
        projected_energy = get_empire_energy_balance(empire) - empire_building.current_energy_used + next_building.energy_used
    else:
        next_level = current_level + 1
        cost = building.upgrade_cost.get(str(next_level), {})
        projected_energy = get_empire_energy_balance(empire) - empire_building.current_energy_used + building.energy_used

    for res, amount in cost.items():
        if empire_resources.get(res, 0) < amount:
            return False

    if projected_energy < 0:
        print("Недостаточно энергии для улучшения")
        return False

    return True





def has_required_technology(empire, technology_name):
    """
    Проверяет, изучена ли требуемая технология у данной империи.
    """
    completed_research = (EmpireResearch
                          .select()
                          .join(Research, on=(EmpireResearch.research == Research.id))
                          .where(
                              (EmpireResearch.empire == empire) &
                              (Research.name == technology_name) &
                              (EmpireResearch.status == 'completed')
                          )
                          .get_or_none())

    return completed_research is not None





def get_total_empires_from_cluster(empire):
    return Empire.select().where(
        (Empire.cluster == empire.cluster) & (Empire != empire)
    )


def get_random_empire_from_cluster(empire):
    return (Empire.select()
            .where((Empire.cluster == empire.cluster) & (Empire != empire))
            .order_by(fn.Random())
            .first())






def add_lootbox_items():
    Items.create(name="item_excalibur_premium",level=5,category="attack",value=0.65, source="lootbox")
    Items.create(name="item_phoenix_fire_bow_premium",level=5,category="attack",value=0.68, source="lootbox")
    Items.create(name="item_blazing_battle_mace_premium",level=5,category="attack",value=0.7, source="lootbox")





def add_season(name, end_date, theme_description, rewards, start_date=None):
    if start_date is None:
        start_date = datetime.now()

    Season.create(
        name=name,
        start_date=start_date,
        end_date=end_date,
        theme_description=theme_description,
        reward_description=rewards,
        top_players=[]
    )







CLUSTER_SIZE_X = 10
CLUSTER_SIZE_Y = 10

def create_or_find_cluster_for_layer(layer):
    """Находит существующий свободный кластер или создаёт новый для указанного слоя рейтинга."""


    cluster = (RatingLayerCluster
               .select()
               .where(
                   (RatingLayerCluster.layer == layer) &
                   (RatingLayerCluster.is_full == False)
               )
               .first())


    if not cluster:

        cluster = RatingLayerCluster.create(
            layer=layer,
            is_full=False,
            empire_count=0
        )

    return cluster





def place_empire_in_cluster(empire, cluster):
    """Размещает империю в указанном кластере на случайных свободных координатах."""


    used_positions = set((Empire
                          .select(Empire.x_position, Empire.y_position)
                          .where(Empire.cluster == cluster))
                         .tuples())


    while True:
        random_x = random.randint(0, CLUSTER_SIZE_X - 1)
        random_y = random.randint(0, CLUSTER_SIZE_Y - 1)

        if (random_x, random_y) not in used_positions:
            break


    empire.x_position = random_x
    empire.y_position = random_y
    empire.cluster = cluster
    empire.save()

    update_cluster_empire_count(cluster, increment=True)





def update_cluster_empire_count(cluster, increment=True):
    """Обновляет количество империй в кластере, устанавливает is_full, если нужно."""

    if increment:
        cluster.empire_count += 1
    else:
        cluster.empire_count -= 1


    cluster.is_full = cluster.empire_count >= CLUSTER_SIZE_X * CLUSTER_SIZE_Y
    cluster.save()





def place_new_empire_on_layer(empire, layer):
    """Создаёт кластер при необходимости и размещает империю на новом слое рейтинга."""


    cluster = create_or_find_cluster_for_layer(layer)


    place_empire_in_cluster(empire, cluster)





def remove_empire_from_cluster(empire):
    """Удаляет империю из текущего кластера."""
    current_cluster = empire.cluster
    if current_cluster:

        update_cluster_empire_count(current_cluster, increment=False)
        empire.cluster = None
        empire.save()
        print(f"Империя {empire.name} удалена из кластера {current_cluster.cluster_id}")


def is_empire_name_taken(name: str) -> bool:
    try:
        return Empire.select().where(Empire.name == name).exists()
    except Exception as e:
        print(f"Ошибка при проверке имени империи '{name}': {e}")
        return True


def generate_unique_empire_id():
    while True:
        e_id = str(uuid.uuid4())[:12]

        if not Empire.select().where(Empire.empire_id == e_id).exists():
            return e_id




def create_empire(user, empire_name):
    """Создаёт империю для пользователя с проверкой уникальности имени и транзакцией"""
    try:
        with db.atomic():

            existing_empire = Empire.get_or_none(Empire.user == user)
            if existing_empire:
                print("❌ Империя уже существует.")
                return None


            layer = RatingLayer.get_or_none(RatingLayer.name == "borderlands")


            new_empire_id = generate_unique_empire_id()


            empire = Empire.create(
                user=user,
                empire_id=new_empire_id,
                name=empire_name,
                rating_layer=layer,
                level=1
            )


            place_new_empire_on_layer(empire, layer)


            EmpireResource.create(
                empire=empire,
                wood=0,
                gold=0,
                oil=0,
                diamond=0,

                units_army=0,
                units_spy=0,
                units_counterspy=0,
                units_explorer=0
            )

            EmpireStatus.create(
                empire=empire,
                extraction_energy=150,
                garrison_units=0,
                gold_upkeep_per_hour=0,
                defense_bonus=0.0
            )

            UserGameSettings.create(
                user=user,
                notification_status="all"
            )

            formatted_news_text = (
                f"Империя \"{empire_name}\" появляется на мировой экономической арене!"
            )
            write_news(formatted_news_text)


            return empire

    except IntegrityError as e:
        print(f"❌ Ошибка: Имя империи '{empire_name}' уже занято. Error:\n{e}")
    except Exception as e:
        print(f"❌ Ошибка при создании империи: {e}")

    return None


def check_cluster_upgrade(empire):
    """Проверяет, достиг ли игрок нового уровня рейтинга, и уведомляет его."""

    user = get_user_by_empire(empire)

    current_layer = get_current_rating_layer(empire.rating_layer)
    target_layer = get_target_rating_layer(empire.rating_points)


    if target_layer.layer_id < current_layer.layer_id:
        return

    if current_layer.layer_id == target_layer.layer_id:
        return

    if not empire.ready_to_upgrade:


        if user:
            send_message_sync(user.chat_id, "🎖 Вы достигли нового уровня рейтинга!\n🚀 В разделе Статистика и нажмите кнопку для перехода на новый уровень рейтинга.")
        empire.ready_to_upgrade = True
        empire.save()





def update_points_rating_for_empire(empire, value):
    """Обновляет очки рейтинга империи и проверяет необходимость перехода на другой слой рейтинга."""
    try:
        with db.atomic():
            if empire.ready_to_upgrade:
                return

            current_rating_points = empire.rating_points
            target_rating_points = current_rating_points + value
            if target_rating_points < 0:
                empire.rating_points = 0
                empire.save()
            else:
                empire.rating_points += value
                empire.save()


            check_cluster_upgrade(empire)
    except Exception as e:
        print(f"Ошибка при обновлении очков рейтинга для империи {empire.name}: {e}")
        return


def delete_empire_related_data(empire):
    """Удаляет все миссии, результаты миссий и найденные локации для империи."""
    try:
        with db.atomic():

            EmpireMissionResult.delete().where(
                EmpireMissionResult.mission.in_(
                    EmpireMission.select().where(EmpireMission.empire == empire)
                )
            ).execute()
            EmpireMission.delete().where(EmpireMission.empire == empire).execute()


            EmpireLocations.delete().where(EmpireLocations.empire == empire).execute()

            print(f"🗑️ Все миссии, результаты миссий и локации для империи {empire.name} удалены.")
    except Exception as e:
        print(f"❌ Ошибка при удалении данных для империи {empire.name}: {e}")





def check_and_update_rating_layer(empire):
    """Проверяет, нужно ли перевести империю на другой слой рейтинга, и обновляет слой, если это необходимо."""
    current_layer = get_current_rating_layer(empire.rating_layer)
    target_layer = get_target_rating_layer(empire.rating_points)


    max_layer = RatingLayer.select().order_by(RatingLayer.layer_id.desc()).first()
    max_layer_id = max_layer.layer_id if max_layer else None


    if current_layer == target_layer and current_layer.layer_id == max_layer_id:
        return

    if current_layer != target_layer:

        delete_empire_related_data(empire)


        remove_empire_from_cluster(empire)
        move_empire_to_new_layer(empire, target_layer)





def get_current_rating_layer(rating_layer_id):
    """Получает текущий слой рейтинга по ID слоя."""
    try:
        current_layer = RatingLayer.get(RatingLayer.layer_id == rating_layer_id)
        return current_layer
    except RatingLayer.DoesNotExist:
        print(f"Ошибка: Слой рейтинга с ID {rating_layer_id} не найден.")
        return None
    except Exception as e:
        print(f"Ошибка при получении текущего слоя рейтинга: {e}")
        return None





def get_target_rating_layer(rating_points):
    """
    Определяет целевой слой рейтинга для империи на основе текущих очков рейтинга.
    Возвращает первый подходящий слой, в котором очки находятся в диапазоне.
    """
    try:

        target_layer = (RatingLayer
                        .select()
                        .where(RatingLayer.min_rating_points <= rating_points)
                        .order_by(RatingLayer.layer_id.desc())
                        .first())

        if not target_layer:
            target_layer = RatingLayer.select().order_by(RatingLayer.layer_id.desc()).first()

        return target_layer
    except Exception as e:
        print(f"Ошибка при определении целевого слоя рейтинга: {e}")
        return None





def move_empire_to_new_layer(empire, new_layer):
    """Перемещает империю на указанный слой рейтинга и добавляет её в соответствующий кластер."""
    empire.rating_layer = new_layer.layer_id
    cluster = create_or_find_cluster_for_layer(new_layer)
    place_empire_in_cluster(empire, cluster)
    empire.save()





def get_resource_from_empire(empire):
    """
    Получает текущие ресурсы империи.

    :param empire: Объект империи.
    :return: Объект EmpireResource, связанный с данной империей.
    """
    current_resource = EmpireResource.get_or_none(EmpireResource.empire == empire)
    if current_resource is None:
        raise ValueError(f"Для империи {empire.name} ресурсы не найдены.")

    return current_resource





def update_resources(empire, resource_name=None, value=None, resource_changes=None):
    if resource_name is not None:
        print(f"[DEBUG] Начисляем ресурс: {resource_name} для империи {empire.name}")
    else:
        print(f"[DEBUG] Начисляем ресурсы: {resource_changes} для империи {empire.name}")
    """
    Обновляет ресурсы империи.

    :param empire: Империя, ресурсы которой нужно обновить.
    :param resource_name: Название ресурса, который нужно обновить (строка).
    :param value: Значение, на которое нужно изменить ресурс (целое число).
    :param resource_changes: Словарь изменений для нескольких ресурсов.
                             Если переданы resource_name и value, этот параметр игнорируется.
    """

    current_resource = get_resource_from_empire(empire)


    if resource_name and value is not None:
        if hasattr(current_resource, resource_name):
            current_value = getattr(current_resource, resource_name)
            setattr(current_resource, resource_name, max(0, current_value + value))
        else:
            raise ValueError(f"Ресурс '{resource_name}' не существует в модели EmpireResource.")


    elif resource_changes:
        for resource_name, value in resource_changes.items():
            if hasattr(current_resource, resource_name):
                current_value = getattr(current_resource, resource_name)
                setattr(current_resource, resource_name, max(0, current_value + value))
            else:
                raise ValueError(f"Ресурс '{resource_name}' не существует в модели EmpireResource.")

    else:
        raise ValueError("Не указано, что обновлять: либо resource_name и value, либо resource_changes.")


    current_resource.save()


def get_current_season():
    try:
        current_season = Season.get(
            (Season.start_date <= datetime.now()) & (Season.end_date >= datetime.now())
        )
        return current_season
    except DoesNotExist:
        return None


def save_mission_result(
    mission,
    success: bool,
    description: str = "",
    units_sent: int = 0,
    target_units: int = 0,
    units_lost: int = 0,
    units_return: int = 0,
    loot_wood: int = 0,
    loot_gold: int = 0,
    loot_oil: int = 0,
    loot_diamond: int = 0,
    loot_item=None,
    intel_data=None
):
    """Сохранение результата миссии в EmpireMissionResult"""
    EmpireMissionResult.create(
        empire=mission.empire,
        description=description,
        mission_id=mission.mission_id,
        success=success,
        units_sent=units_sent,
        target_units=target_units,
        units_lost=units_lost,
        units_return=units_return,
        loot_wood=loot_wood,
        loot_gold=loot_gold,
        loot_oil=loot_oil,
        loot_diamond=loot_diamond,
        loot_item=loot_item,
        intel_data=intel_data,
        created_at=datetime.now(),
    )



def calculate_time_for_mission_attack(empire, count_units_send):

    def get_active_attack_time_event():
        current_season = get_current_season()
        if not current_season:
            return 0

        active_attack_time_events = GameEvents.select().join(GameEventTemplate).join(SeasonEvent).where(
            (GameEventTemplate.effect_type == "missions_time") &
            (GameEventTemplate.target.in_(["attack", "all"])) &
            (GameEvents.start_time <= datetime.now()) &
            (GameEvents.end_time >= datetime.now()) &
            (GameEvents.is_active == True) &
            (SeasonEvent.season == current_season)
        )


        total_effect = sum(event.template.value for event in active_attack_time_events)
        return total_effect

    def get_empire_time_items(empire):
        items = (EmpireItems
                .select(Items.value)
                .join(Items)
                .where((EmpireItems.empire == empire) & (Items.category == "time")))

        return sum(item.item.value for item in items) if items else 0

    def get_empire_active_busters(empire, category):
        busters = (EmpireBusters
                .select(Busters.value)
                .join(Busters)
                .where(
                    (EmpireBusters.empire == empire) &
                    (Busters.category == category) &
                    (EmpireBusters.start_date <= datetime.now()) &
                    (EmpireBusters.end_time >= datetime.now())
                ))

        return sum(buster.buster.value for buster in busters) if busters else 0

    def is_tech_completed(empire, tech_name):
        query = EmpireResearch.select().join(Research).where(
            (Research.name == tech_name) &
            (EmpireResearch.empire == empire) &
            (EmpireResearch.status == "completed")
        )
        return query.exists()


    attack_time_events_value = get_active_attack_time_event()


    time_mission_value = get_empire_time_items(empire)


    user = get_user_by_empire(empire)


    subscription_effect_value = -0.1 if user.subscription_status else 0


    effect_busters_value = get_empire_active_busters(empire, "time_attack")


    effect_tech_value = -0.03 if is_tech_completed(empire, "tech_time_attack_speed_up") else 0


    base_time = 1800


    total_bonus = (
        attack_time_events_value +
        time_mission_value +
        subscription_effect_value +
        effect_busters_value +
        effect_tech_value
    )


    unit_factor = 0.005 * count_units_send


    final_time = base_time * (1 + unit_factor) * (1 + total_bonus)


    final_time = max(60, final_time)

    return int(final_time)



def calculate_time_for_mission_espionage(empire, count_units_send):
    def get_active_espionage_time_event():
        current_season = get_current_season()
        if not current_season:
            return 0

        active_espionage_time_events = GameEvents.select().join(GameEventTemplate).join(SeasonEvent).where(
            (GameEventTemplate.effect_type == "missions_time") &
            (GameEventTemplate.target.in_(["espionage", "all"])) &
            (GameEvents.start_time <= datetime.now()) &
            (GameEvents.end_time >= datetime.now()) &
            (GameEvents.is_active == True) &
            (SeasonEvent.season == current_season)
        )


        total_effect = sum(event.template.value for event in active_espionage_time_events)
        return total_effect

    def get_empire_time_items(empire):
        items = (EmpireItems
                .select(Items.value)
                .join(Items)
                .where((EmpireItems.empire == empire) & (Items.category == "time")))

        return sum(item.item.value for item in items) if items else 0

    def get_empire_active_busters(empire, category):
        busters = (EmpireBusters
                .select(Busters.value)
                .join(Busters)
                .where(
                    (EmpireBusters.empire == empire) &
                    (Busters.category == category) &
                    (EmpireBusters.start_date <= datetime.now()) &
                    (EmpireBusters.end_time >= datetime.now())
                ))

        return sum(buster.buster.value for buster in busters) if busters else 0

    def is_tech_completed(empire, tech_name):
        query = EmpireResearch.select().join(Research).where(
            (Research.name == tech_name) &
            (EmpireResearch.empire == empire) &
            (EmpireResearch.status == "completed")
        )
        return query.exists()


    event_espionage_time_value = get_active_espionage_time_event()


    time_mission_value = get_empire_time_items(empire)


    user = get_user_by_empire(empire)


    subscription_effect_value = -0.1 if user.subscription_status else 0


    effect_busters_value = get_empire_active_busters(empire, "time_espionage")


    effect_tech_value = -0.03 if is_tech_completed(empire, "tech_time_espionage_speed_up") else 0


    base_time = 1800


    total_bonus = (
        event_espionage_time_value +
        time_mission_value +
        subscription_effect_value +
        effect_busters_value +
        effect_tech_value
    )


    unit_factor = 0.005 * count_units_send


    final_time = base_time * (1 + unit_factor) * (1 + total_bonus)


    final_time = max(60, final_time)

    return int(final_time)



def calculate_time_for_mission_exploration(empire, count_units_send, radius):

    def get_active_exploration_time_event():
        current_season = get_current_season()
        if not current_season:
            return 0

        active_exploration_time_events = GameEvents.select().join(GameEventTemplate).join(SeasonEvent).where(
            (GameEventTemplate.effect_type == "missions_time") &
            (GameEventTemplate.target.in_(["exploration", "all"])) &
            (GameEvents.start_time <= datetime.now()) &
            (GameEvents.end_time >= datetime.now()) &
            (GameEvents.is_active == True) &
            (SeasonEvent.season == current_season)
        )


        total_effect = sum(event.template.value for event in active_exploration_time_events)
        return total_effect

    def get_empire_time_items(empire):
        items = (EmpireItems
                .select(Items.value)
                .join(Items)
                .where((EmpireItems.empire == empire) & (Items.category == "time")))

        return sum(item.item.value for item in items) if items else 0

    def get_empire_active_busters(empire, category):
        busters = (EmpireBusters
                .select(Busters.value)
                .join(Busters)
                .where(
                    (EmpireBusters.empire == empire) &
                    (Busters.category == category) &
                    (EmpireBusters.start_date <= datetime.now()) &
                    (EmpireBusters.end_time >= datetime.now())
                ))

        return sum(buster.buster.value for buster in busters) if busters else 0

    def is_tech_completed(empire, tech_name):
        query = EmpireResearch.select().join(Research).where(
            (Research.name == tech_name) &
            (EmpireResearch.empire == empire) &
            (EmpireResearch.status == "completed")
        )
        return query.exists()


    event_exploration_value = get_active_exploration_time_event()


    time_mission_value = get_empire_time_items(empire)


    user = get_user_by_empire(empire)


    subscription_effect_value = -0.1 if user.subscription_status else 0


    effect_busters_value = get_empire_active_busters(empire, "time_exploration")


    effect_tech_value = -0.03 if is_tech_completed(empire, "tech_time_exploration_speed_up") else 0


    base_time = 1800

    total_bonus = (
        event_exploration_value +
        time_mission_value +
        subscription_effect_value +
        effect_busters_value +
        effect_tech_value
    )

    unit_factor = 0.005 * count_units_send
    final_time = base_time * (1 + unit_factor) * (1 + total_bonus)

    final_time = max(60, final_time)

    return int(final_time)



def calculate_result_for_missions_attack(mission):
    """Обработка атакующей миссии и расчет результата"""


    _DESCRIPTION_ = "UNDEFINED"
    _SUCCESS_ = False
    _UNITS_SENT_ = 0
    _TARGET_UNITS_ = 0
    _UNITS_LOST_ = 0
    _UNITS_RETURN_ = 0
    _LOOT_WOOD_ = 0
    _LOOT_GOLD_ = 0
    _LOOT_OIL_ = 0
    _LOOT_DIAMOND = 0
    _LOOT_ITEMS_ = None
    _INTEL_DATA_ = None

    def get_active_attack_action_event():
        current_season = get_current_season()
        if not current_season:
            return 0

        active_attack_action_events = GameEvents.select().join(GameEventTemplate).join(SeasonEvent).where(
            (GameEventTemplate.effect_type == "missions_action") &
            (GameEventTemplate.target.in_(["attack", "all"])) &
            (GameEvents.start_time <= datetime.now()) &
            (GameEvents.end_time >= datetime.now()) &
            (GameEvents.is_active == True) &
            (SeasonEvent.season == current_season)
        )


        total_effect = sum(event.template.value for event in active_attack_action_events)
        return total_effect

    def get_active_defence_action_event():
        current_season = get_current_season()
        if not current_season:
            return 0

        active_defence_action_events = GameEvents.select().join(GameEventTemplate).join(SeasonEvent).where(
            (GameEventTemplate.effect_type == "defence") &
            (GameEvents.start_time <= datetime.now()) &
            (GameEvents.end_time >= datetime.now()) &
            (GameEvents.is_active == True) &
            (SeasonEvent.season == current_season)
        )


        total_effect = sum(event.template.value for event in active_defence_action_events)
        return total_effect

    def get_empire_attack_items(empire):
        items = (EmpireItems
                .select(Items.value)
                .join(Items)
                .where((EmpireItems.empire == empire) & (Items.category == "attack")))

        return sum(item.item.value for item in items) if items else 0

    def get_empire_defence_items(empire):
        items = (EmpireItems
                .select(Items.value)
                .join(Items)
                .where((EmpireItems.empire == empire) & (Items.category == "defence")))

        return sum(item.item.value for item in items) if items else 0

    def get_empire_active_busters(empire, category):
        busters = (EmpireBusters
                .select(Busters.value)
                .join(Busters)
                .where(
                    (EmpireBusters.empire == empire) &
                    (Busters.category == category) &
                    (EmpireBusters.start_date <= datetime.now()) &
                    (EmpireBusters.end_time >= datetime.now())
                ))

        return sum(buster.buster.value for buster in busters) if busters else 0

    def is_tech_completed(empire, tech_name):
        query = EmpireResearch.select().join(Research).where(
            (Research.name == tech_name) &
            (EmpireResearch.empire == empire) &
            (EmpireResearch.status == "completed")
        )
        return query.exists()

    def get_total_attack_bonus(empire):
        bonus = 1.0
        bonus += get_active_attack_action_event()
        bonus += get_empire_active_busters(empire, "attack")
        bonus += get_empire_attack_items(empire)
        if is_tech_completed(empire, "tech_attack_action_up"):
            bonus += 0.1
        return bonus

    def get_total_defence_bonus(empire):
        bonus = 1.0
        bonus += get_active_defence_action_event()
        bonus += get_empire_active_busters(empire, "defence")
        bonus += get_empire_defence_items(empire)
        if is_tech_completed(empire, "tech_defence_action_up"):
            bonus += 0.1
        return bonus

    attacking_empire = mission.empire
    target_empire = mission.target
    units_sent = mission.units_sent
    status = EmpireStatus.get_or_none(EmpireStatus.empire == attacking_empire)

    if not status:
        print("❌ Статус империи не найден!")
        return

    unit_capacity = status.units_army_capacity or 10
    total_capacity = units_sent * unit_capacity

    _DESCRIPTION_ = f"Вы атаковали империю: {target_empire.name}"
    _UNITS_SENT_ = units_sent

    attacker_resources = EmpireResource.get_or_none(EmpireResource.empire == attacking_empire)
    target_resources = EmpireResource.get_or_none(EmpireResource.empire == target_empire)

    _TARGET_UNITS_ = target_resources.units_army

    if not attacker_resources or not target_resources:
        print("❌ Ресурсы одной из империй отсутствуют!")
        return

    print(f"⚔️ Атака на империю: {target_empire.name} (ID: {target_empire.empire_id})")

    attack_power = int(units_sent * get_total_attack_bonus(attacking_empire))
    defense_power = int(target_resources.units_army * get_total_defence_bonus(target_empire))


    base_chance = attack_power / (attack_power + defense_power) if (attack_power + defense_power) > 0 else 0
    bonus = 0
    if attack_power > defense_power:
        bonus = min(0.2, (attack_power / defense_power - 1) * 0.2)

    chance_to_win = min(1.0, base_chance + bonus)
    print(f"🎲 Шанс победы атакующего: {chance_to_win:.2%}")


    winner = "attacker" if random.random() < chance_to_win else "defender"


    attacker_loss_ratio = max(0.1, 1 - chance_to_win)
    defender_loss_ratio = max(0.1, chance_to_win)

    attacking_units_lost = min(units_sent, ceil(units_sent * attacker_loss_ratio * random.uniform(0.8, 1.2)))
    defending_units_total = target_resources.units_army
    defending_units_lost = min(defending_units_total, ceil(defending_units_total * defender_loss_ratio * random.uniform(0.8, 1.2)))

    _UNITS_LOST_ = attacking_units_lost
    _UNITS_RETURN_ = units_sent - attacking_units_lost

    loot = {"wood": 0, "gold": 0, "oil": 0, "diamond": 0}

    if winner == "attacker":
        _SUCCESS_ = True


        update_resources(target_empire, resource_name="units_army", value=-defending_units_lost)

        loot = {
            "wood": min(target_resources.wood, random.randint(20, 100)),
            "gold": min(target_resources.gold, random.randint(10, 75)),
            "oil": min(target_resources.oil, random.randint(5, 30)),
            "diamond": min(target_resources.diamond, random.randint(1, 10))
        }

        gathered_loot = {k: min(v, total_capacity) for k, v in loot.items()}

        _LOOT_WOOD_ = gathered_loot["wood"]
        _LOOT_GOLD_ = gathered_loot["gold"]
        _LOOT_OIL_ = gathered_loot["oil"]
        _LOOT_DIAMOND = gathered_loot["diamond"]

        update_resources(attacking_empire, resource_changes=gathered_loot)

        update_resources(target_empire, resource_changes={k: -v for k, v in gathered_loot.items()})


        update_resources(attacking_empire, resource_name="units_army", value=-attacking_units_lost)
    else:
        _SUCCESS_ = False

        update_resources(target_empire, resource_name="units_army", value=-defending_units_lost)

        update_resources(attacking_empire, resource_name="units_army", value=-attacking_units_lost)

    save_mission_result(
        mission=mission,
        success=_SUCCESS_,
        description=_DESCRIPTION_,
        units_sent=_UNITS_SENT_,
        target_units=_TARGET_UNITS_,
        units_lost=_UNITS_LOST_,
        units_return=_UNITS_RETURN_,
        loot_wood=_LOOT_WOOD_,
        loot_gold=_LOOT_GOLD_,
        loot_oil=_LOOT_OIL_,
        loot_diamond=_LOOT_DIAMOND,
        loot_item=_LOOT_ITEMS_,
        intel_data=_INTEL_DATA_,
    )

    mission.status = "completed"
    mission.save()


    loot_description = ", ".join(f"{v} {k}" for k, v in gathered_loot.items() if v > 0) or "ничего не удалось захватить"


    if winner == "attacker":
        result_text = (
            f"Империя {attacking_empire.name} атаковала империю {target_empire.name} и одержала победу!\n"
            f"⚔️ Сила: {attack_power} vs {defense_power} (шанс победы: {chance_to_win:.1%})\n"
            f"🪖 Потери: атакующий — {attacking_units_lost}, защитник — {defending_units_lost}\n"
            f"💰 Добыча: {loot_description}"
        )
        process_empire_action(attacking_empire, "attack", {"xp": 100, "rp": 100})
        process_empire_action(target_empire, "attack", {"xp": 25, "rp": -25})
    else:
        result_text = (
            f"Империя {attacking_empire.name} атаковала империю {target_empire.name}, но была отбита!\n"
            f"⚔️ Сила: {attack_power} vs {defense_power} (шанс победы: {chance_to_win:.1%})\n"
            f"🪖 Потери атакующего: {attacking_units_lost} юнитов\n"
            f"💰 Добыча: {loot_description}"
        )
        process_empire_action(attacking_empire, "attack", {"xp": 25, "rp": -25})
        process_empire_action(target_empire, "attack", {"xp": 100, "rp": 75})

    write_news(result_text)

    user = get_user_by_empire(attacking_empire)
    if user:
        try:
            send_message_sync(
                user.chat_id,
                f"🌍 Миссия атаки (ID: {mission.mission_id}) на империю {target_empire.name} завершена!\n"
                f"{'✅ Победа!' if winner == 'attacker' else '❌ Поражение!'}\n"
                f"📦 {loot_description}"
            )
        except Exception as e:
            print(f"Ошибка отправки сообщения: {e}")



def calculate_result_for_missions_attack_location(mission):
    """Обработка атакующих миссий с локациями и расчет результата"""
    from math import ceil


    _DESCRIPTION_ = "UNDEFINED"
    _SUCCESS_ = False
    _UNITS_SENT_ = 0
    _TARGET_UNITS_ = 0
    _UNITS_LOST_ = 0
    _UNITS_RETURN_ = 0
    _LOOT_WOOD_ = 0
    _LOOT_GOLD_ = 0
    _LOOT_OIL_ = 0
    _LOOT_DIAMOND = 0
    _LOOT_ITEMS_ = None
    _INTEL_DATA_ = None

    def store_loot_items(empire, item):
        """Сохранение предметов после атаки в таблицу EmpireItems"""
        if not item:
            return


        item = Items.get_or_none(Items.name == item.name)
        if not item:
            print(f"⚠️ Ошибка: Предмет '{item.name}' не найден в таблице Items!")
            return


        EmpireItems.create(empire=empire, item=item)
        print(f"🎁 Империя {empire.name} получила предмет: {item.name}")

    def get_active_attack_action_event():
        current_season = get_current_season()
        if not current_season:
            return 0

        active_attack_time_events = GameEvents.select().join(GameEventTemplate).join(SeasonEvent).where(
            (GameEventTemplate.effect_type == "missions_action") &
            (GameEventTemplate.target.in_(["attack", "all"])) &
            (GameEvents.start_time <= datetime.now()) &
            (GameEvents.end_time >= datetime.now()) &
            (GameEvents.is_active == True) &
            (SeasonEvent.season == current_season)
        )


        total_effect = sum(event.template.value for event in active_attack_time_events)
        return total_effect

    def get_empire_attack_items(empire):
        items = (EmpireItems
                .select(Items.value)
                .join(Items)
                .where((EmpireItems.empire == empire) & (Items.category == "attack")))

        return sum(item.item.value for item in items) if items else 0

    def get_empire_active_busters(empire, category):
        busters = (EmpireBusters
                .select(Busters.value)
                .join(Busters)
                .where(
                    (EmpireBusters.empire == empire) &
                    (Busters.category == category) &
                    (EmpireBusters.start_date <= datetime.now()) &
                    (EmpireBusters.end_time >= datetime.now())
                ))

        return sum(buster.buster.value for buster in busters) if busters else 0

    def is_tech_completed(empire, tech_name):
        query = EmpireResearch.select().join(Research).where(
            (Research.name == tech_name) &
            (EmpireResearch.empire == empire) &
            (EmpireResearch.status == "completed")
        )
        return query.exists()

    def get_total_attack_bonus(empire):
        bonus = 1.0
        bonus += get_active_attack_action_event()
        bonus += get_empire_active_busters(empire, "attack")
        bonus += get_empire_attack_items(empire)
        if is_tech_completed(empire, "tech_attack_action_up"):
            bonus += 0.1
        return bonus

    attacking_empire = mission.empire
    units_sent = mission.units_sent
    status = EmpireStatus.get_or_none(EmpireStatus.empire == attacking_empire)

    if not status:
        print("❌ Статус империи не найден!")
        return

    unit_capacity = status.units_army_capacity or 10
    total_capacity = units_sent * unit_capacity

    target_location = mission.location
    location_id = target_location.location_id
    location_name = target_location.name
    location_wood_value = target_location.wood
    location_gold_value = target_location.gold
    location_oil_value = target_location.oil
    location_diamond_value = target_location.diamond
    location_item = target_location.item
    location_monsters_value = target_location.monsters

    print(f"⚔️ Атака на локацию: {location_name} (ID: {location_id})")



    _UNITS_SENT_ = units_sent

    _DESCRIPTION_ = "Вы атаковали "

    if location_name == "empire_monster":
        _DESCRIPTION_ += "имерию монстров."

        _TARGET_UNITS_ = location_monsters_value
        attack_power = int(units_sent * get_total_attack_bonus(attacking_empire))
        defense_power = location_monsters_value


        base_chance = attack_power / (attack_power + defense_power)
        bonus = 0
        if attack_power > defense_power:
            bonus = min(0.2, (attack_power / defense_power - 1) * 0.2)

        chance_to_win = min(1.0, base_chance + bonus)
        print(f"🎲 Шанс победы: {chance_to_win:.2%}")

        winner = "attacker" if random.random() < chance_to_win else "defender"


        attacker_loss_ratio = max(0.1, 1 - chance_to_win)

        attacking_units_lost = min(units_sent, ceil(units_sent * attacker_loss_ratio * random.uniform(0.8, 1.2)))

        _UNITS_LOST_ = attacking_units_lost

        remaining_units = max(0, units_sent - attacking_units_lost)

        _UNITS_RETURN_ = remaining_units

        update_resources(attacking_empire, resource_name="units_army", value=remaining_units)

        if winner == "attacker":
            _SUCCESS_ = True

            loot = {
                "wood": location_wood_value,
                "gold": location_gold_value,
                "oil": location_oil_value,
                "diamond": location_diamond_value,
            }

            gathered_loot = {k: min(v, total_capacity) for k, v in loot.items()}

            _LOOT_WOOD_ = gathered_loot["wood"]
            _LOOT_GOLD_ = gathered_loot["gold"]
            _LOOT_OIL_ = gathered_loot["oil"]
            _LOOT_DIAMOND = gathered_loot["diamond"]

            update_resources(attacking_empire, resource_changes=gathered_loot)

            if location_item:
                store_loot_items(attacking_empire, location_item)
                _LOOT_ITEMS_ = location_item

            update_resources(attacking_empire, resource_name="units_army", value=-attacking_units_lost)

            loot_text = ", ".join(f"{v} {resource_name_count[k]}" for k, v in gathered_loot.items() if v > 0) or "ничего"
            item_text = items_name[location_item.name] if location_item else None
            full_loot_text = loot_text + (f"; предметы: {item_text}" if item_text else "")

            write_news(
                f"Империя {attacking_empire.name} атаковала локацию {locations_name[location_name]} и победила монстров!\n"
                f"🪖 Потери: {attacking_units_lost} юнитов.\n"
                f"🎁 Добыча: {full_loot_text}"
            )

        else:
            _SUCCESS_ = False
            update_resources(attacking_empire, resource_name="units_army", value=-attacking_units_lost)

            write_news(
                f"Империя {attacking_empire.name} проиграла бой за локацию {locations_name[location_name]}.\n"
                f"⚔️ Сила атаки: {attack_power}, защита: {defense_power}.\n"
                f"🪖 Потери: {attacking_units_lost} юнитов."
            )

    if location_name == "abandoned_location":
        _DESCRIPTION_ += "заброшенную локацию."

    if location_name == "stash":
        _DESCRIPTION_ += "тайник."

    if location_name == "abandoned_location" or location_name == "stash":
        _SUCCESS_ = True

        loot = {
            "wood": location_wood_value,
            "gold": location_gold_value,
            "oil": location_oil_value,
            "diamond": location_diamond_value,
        }


        gathered_loot = {k: min(v, total_capacity) for k, v in loot.items()}

        _LOOT_WOOD_ = gathered_loot["wood"]
        _LOOT_GOLD_ = gathered_loot["gold"]
        _LOOT_OIL_ = gathered_loot["oil"]
        _LOOT_DIAMOND = gathered_loot["diamond"]

        update_resources(attacking_empire, resource_changes=gathered_loot)
        update_resources(attacking_empire, resource_name="units_army", value=units_sent)
        _UNITS_RETURN_ = units_sent

        loot_text = ", ".join(f"{v} {resource_name_count[k]}" for k, v in gathered_loot.items() if v > 0) or "ничего"

        write_news(
            f"Империя {attacking_empire.name} исследовала локацию {locations_name[location_name]} без боя.\n"
            f"🎁 Добыча: {loot_text}"
        )

    mission.status = "completed"
    mission.save()

    save_mission_result(
        mission=mission,
        success=_SUCCESS_,
        description=_DESCRIPTION_,
        units_sent=_UNITS_SENT_,
        target_units=_TARGET_UNITS_,
        units_lost=_UNITS_LOST_,
        units_return=_UNITS_RETURN_,
        loot_wood=_LOOT_WOOD_,
        loot_gold=_LOOT_GOLD_,
        loot_oil=_LOOT_OIL_,
        loot_diamond=_LOOT_DIAMOND,
        loot_item=_LOOT_ITEMS_,
        intel_data=_INTEL_DATA_,
    )

    target_location.delete_instance()


    user = get_user_by_empire(attacking_empire)
    if user:
        try:
            send_message_sync(
                user.chat_id,
                f"🌍 Миссия атаки (ID: {mission.mission_id}) на локацию {locations_name[location_name]} завершена!\n"
                f"{'✅ Победа!' if location_monsters_value == 0 or winner == 'attacker' else '❌ Поражение!'}\n"
                f"📦 Результаты: {loot_text if location_monsters_value == 0 or winner == 'attacker' else 'ничего не получено'}"
            )
        except Exception as e:
            print(f"Error sending message: {e}")





def calculate_result_for_missions_espionage(mission):

    _DESCRIPTION_ = "UNDEFINED"
    _SUCCESS_ = False
    _UNITS_SENT_ = 0
    _TARGET_UNITS_ = 0
    _UNITS_LOST_ = 0
    _UNITS_RETURN_ = 0
    _LOOT_WOOD_ = 0
    _LOOT_GOLD_ = 0
    _LOOT_OIL_ = 0
    _LOOT_DIAMOND = 0
    _LOOT_ITEMS_ = None
    _INTEL_DATA_ = None

    def get_active_espionage_action_event():
        current_season = get_current_season()
        if not current_season:
            return 0

        active_espionage_action_events = GameEvents.select().join(GameEventTemplate).join(SeasonEvent).where(
            (GameEventTemplate.effect_type == "missions_action") &
            (GameEventTemplate.target.in_(["espionage", "all"])) &
            (GameEvents.start_time <= datetime.now()) &
            (GameEvents.end_time >= datetime.now()) &
            (GameEvents.is_active == True) &
            (SeasonEvent.season == current_season)
        )


        total_effect = sum(event.template.value for event in active_espionage_action_events)
        return total_effect

    def get_active_antiespionage_event():
        current_season = get_current_season()
        if not current_season:
            return 0

        active_antiespionage_events = GameEvents.select().join(GameEventTemplate).join(SeasonEvent).where(
            (GameEventTemplate.effect_type == "antiespionage") &
            (GameEvents.start_time <= datetime.now()) &
            (GameEvents.end_time >= datetime.now()) &
            (GameEvents.is_active == True) &
            (SeasonEvent.season == current_season)
        )


        total_effect = sum(event.template.value for event in active_antiespionage_events)
        return total_effect

    def get_empire_espionage_items(empire):
        items = (EmpireItems
                .select(Items.value)
                .join(Items)
                .where((EmpireItems.empire == empire) & (Items.category == "espionage")))

        return sum(item.item.value for item in items) if items else 0

    def get_empire_antiespionage_items(empire):
        items = (EmpireItems
                .select(Items.value)
                .join(Items)
                .where((EmpireItems.empire == empire) & (Items.category == "antiespionage")))

        return sum(item.item.value for item in items) if items else 0

    def get_empire_active_busters(empire, category):
        busters = (EmpireBusters
                .select(Busters.value)
                .join(Busters)
                .where(
                    (EmpireBusters.empire == empire) &
                    (Busters.category == category) &
                    (EmpireBusters.start_date <= datetime.now()) &
                    (EmpireBusters.end_time >= datetime.now())
                ))

        return sum(buster.buster.value for buster in busters) if busters else 0

    def is_tech_completed(empire, tech_name):
        query = EmpireResearch.select().join(Research).where(
            (Research.name == tech_name) &
            (EmpireResearch.empire == empire) &
            (EmpireResearch.status == "completed")
        )
        return query.exists()

    def get_total_espionage_bonus(empire):
        bonus = 1.0
        bonus += get_active_espionage_action_event()
        bonus += get_empire_active_busters(empire, "espionage")
        bonus += get_empire_espionage_items(empire)
        if is_tech_completed(empire, "tech_espionage_action_up"):
            bonus += 0.1
        return bonus

    def get_total_antiespionage_bonus(empire):
        bonus = 1.0
        bonus += get_active_antiespionage_event()
        bonus += get_empire_active_busters(empire, "antiespionage")
        bonus += get_empire_antiespionage_items(empire)
        if is_tech_completed(empire, "tech_antiespionage_action_up"):
            bonus += 0.1
        return bonus

    espionage_empire = mission.empire
    target_empire = mission.target
    units_sent = mission.units_sent

    _DESCRIPTION_ = f"Вы шпионите за империей: {target_empire.name}"
    _UNITS_SENT_ = units_sent

    attacker_resources = EmpireResource.get_or_none(EmpireResource.empire == espionage_empire)
    target_resources = EmpireResource.get_or_none(EmpireResource.empire == target_empire)

    _TARGET_UNITS_ = target_resources.units_counterspy

    if not attacker_resources or not target_resources:
        print("❌ Отсутствуют ресурсы одной из империй")
        return

    print(f"🕵️‍♂️ Шпионская миссия против: {target_empire.name} (ID: {target_empire.empire_id})")

    espionage_power = int(units_sent * get_total_espionage_bonus(espionage_empire))
    antiespionage_power = int(target_resources.units_counterspy * get_total_antiespionage_bonus(target_empire))

    success = espionage_power > antiespionage_power
    winner = "espionage" if success else "antiespionage"
    print(f"⚖️ Сила: {espionage_power} vs {antiespionage_power} → победа: {winner}")


    espionage_loss_percentage = random.uniform(0.1, 0.3 if success else 0.5)
    antiespionage_loss_percentage = random.uniform(0.3, 0.5 if success else 0.2)

    espionage_units_lost = int(units_sent * espionage_loss_percentage)
    antiespionage_units_lost = int(target_resources.units_counterspy * antiespionage_loss_percentage)

    _UNITS_LOST_ = espionage_units_lost
    _UNITS_RETURN_ = units_sent - espionage_units_lost


    update_resources(espionage_empire, resource_name="units_spy", value=-espionage_units_lost)
    update_resources(target_empire, resource_name="units_counterspy", value=-antiespionage_units_lost)


    info_gathered = {}
    if success:
        _SUCCESS_ = True
        info_gathered = {
            "resources": {
                "wood": target_resources.wood,
                "gold": target_resources.gold,
                "oil": target_resources.oil,
                "diamond": target_resources.diamond,
                "army": target_resources.units_army,
                "spy": target_resources.units_spy,
                "counterspy": target_resources.units_counterspy,
                "exploration": target_resources.units_exploration,
            },
            "buildings": [
                {"name": b.building.name, "level": b.level}
                for b in EmpireBuildings.select().where(EmpireBuildings.empire == target_empire)
            ],
            "research": [
                {"name": r.research.name, "progress": r.progress}
                for r in EmpireResearch.select().where(EmpireResearch.empire == target_empire)
            ],
            "active_missions": [
                {"type": m.mission_type.name, "status": m.status}
                for m in EmpireMission.select().where(
                    (EmpireMission.empire == target_empire) &
                    (EmpireMission.status != "completed")
                )
            ]
        }
        _INTEL_DATA_ = json.dumps(info_gathered)
    else:
        _SUCCESS_ = False


    save_mission_result(
        mission=mission,
        success=_SUCCESS_,
        description=_DESCRIPTION_,
        units_sent=_UNITS_SENT_,
        target_units=_TARGET_UNITS_,
        units_lost=_UNITS_LOST_,
        units_return=_UNITS_RETURN_,
        loot_wood=_LOOT_WOOD_,
        loot_gold=_LOOT_GOLD_,
        loot_oil=_LOOT_OIL_,
        loot_diamond=_LOOT_DIAMOND,
        loot_item=_LOOT_ITEMS_,
        intel_data=_INTEL_DATA_,
    )


    mission.status = "completed"
    mission.save()

    formatted_news_text = None

    if winner == "espionage":
        formatted_news_text = (
            f"Империя {espionage_empire.name} успешно осуществила миссию шпионажа в отношении империи {target_empire.name} и получила доступ к информации."
            f"Потери шпионов: {espionage_units_lost} юнитов. Потери антишпионов: {antiespionage_units_lost} юнитов."
        )
        process_empire_action(espionage_empire, "espionage", {"xp": 35, "rp": 40})
        process_empire_action(target_empire, "espionage", {"xp": 5, "rp": -5})
    else:
        formatted_news_text = (
            f"Империя {espionage_empire.name} провалила миссию шпионажа в отношении империи {target_empire.name}."
            f"Потери шпионов: {espionage_units_lost} юнитов. Потери антишпионов: {antiespionage_units_lost} юнитов."
        )
        process_empire_action(espionage_empire, "espionage", {"xp": 10, "rp": -15})
        process_empire_action(target_empire, "espionage", {"xp": 40, "rp": 55})

    write_news(formatted_news_text)

    user = get_user_by_empire(espionage_empire)

    if user:
        try:
            send_message_sync(user.chat_id,
                f"🕵️‍♂️ Миссия шпионажа (ID: {mission.mission_id}) завершена!\n"
                f"Результат: {'УСПЕХ' if success else 'Провал'}.\n"
                f"Посмотрите: Управление империей → Миссии → Результаты миссий.")
        except Exception as e:
            print(f"Ошибка при отправке сообщения: {e}")


def generate_unique_location_id():
    """Генерация уникального ID для локации во всей таблице."""
    while True:

        obj_id = str(uuid.uuid4())[:8]


        if not EmpireLocations.select().where(EmpireLocations.location_id == obj_id).exists():
            return obj_id

def generate_item_for_location(empire, rating_level):
    """Генерация одного предмета для локации с учётом игрока и подписки."""


    available_items = list(Items.select().where(Items.level <= rating_level + 1))
    owned_items = {item.item.name for item in EmpireItems.select().where(EmpireItems.empire == empire)}


    filtered_items = [item for item in available_items if item.name not in owned_items]


    filtered_items.extend(filtered_items)


    if empire.user.subscription_status:
        print("🔹 Подписка активна — увеличен шанс редких предметов.")
        rare_items = [item for item in available_items if item.level >= rating_level]
        filtered_items.extend(rare_items * 3)


    if filtered_items:
        return random.choice(filtered_items)
    return None

def generate_exploration_result(empire, units_sent, radius, total_find_bonus=1.0):
    print(f"total_find_bonus: {total_find_bonus}")
    empire_level = empire.level
    rating_level = empire.rating_layer.layer_id
    print(f"rating_level: {rating_level}")


    base_chance = (
        0.2 +
        (units_sent / 40) +
        (radius / 10) +
        (empire_level / 30) +
        (rating_level / 5)
    ) * total_find_bonus
    base_chance = min(base_chance, 0.95)

    print(f"📍 Шанс находки (с учетом бонусов): {base_chance:.2f}")


    max_objects = int(
        min(7, (1 + (units_sent / 30) + (radius / 7) + (empire_level / 3)) * total_find_bonus)
    )
    objects = random.randint(1, max(1, max_objects))

    print(f"🎯 Найдено объектов: {objects} из макс {max_objects}")

    found_objects = []

    object_weights = {
        "stash": 60,
        "abandoned_location": 30,
        "empire_monster": 10
    }

    weighted_object_types = (
        ["stash"] * object_weights["stash"] +
        ["abandoned_location"] * object_weights["abandoned_location"] +
        ["empire_monster"] * object_weights["empire_monster"]
    )

    for _ in range(objects):
        if random.random() < base_chance:
            obj_type = random.choice(weighted_object_types)
            obj_id = generate_unique_location_id()
            obj_data = {"name": obj_type, "ID": str(obj_id), "info": {}}


            resources = {
                "wood": random.randint(100, 700) + empire_level * 5,
                "gold": random.randint(100, 500) + rating_level * 10
            }
            if random.random() < 0.8:
                resources["oil"] = random.randint(20, 80) + rating_level * 3
            if random.random() < 0.6:
                resources["diamond"] = random.randint(2, 8) + rating_level


            if obj_type == "abandoned_location":
                resources = {key: int(value * 1.3) for key, value in resources.items()}


            if obj_type == "empire_monster":
                for k in resources:
                    resources[k] = int(resources[k] * 1.5)

            obj_data["info"]["resources"] = resources


            if obj_type == "empire_monster":
                obj_data["info"]["monsters"] = random.randint(10, 50) * rating_level
                item = generate_item_for_location(empire, rating_level)
                obj_data["info"]["item"] = item

            found_objects.append(obj_data)

    find_objects_names = []

    for obj in found_objects:
        res = obj["info"].get("resources", {})
        item_obj = obj["info"].get("item")

        EmpireLocations.create(
            location_id=obj["ID"],
            name=obj["name"],
            empire=empire,
            wood=res.get("wood", 0),
            gold=res.get("gold", 0),
            oil=res.get("oil", 0),
            diamond=res.get("diamond", 0),
            item=item_obj,
            monsters=obj["info"].get("monsters", 0)
        )

        find_objects_names.append(obj["name"])

    return find_objects_names

def calculate_result_for_missions_exploration(mission):
    """Обработка миссии исследования с учетом бонусов и событий"""

    _DESCRIPTION_ = "UNDEFINED"
    _SUCCESS_ = False
    _UNITS_SENT_ = 0
    _TARGET_UNITS_ = 0
    _UNITS_LOST_ = 0
    _UNITS_RETURN_ = 0
    _LOOT_WOOD_ = 0
    _LOOT_GOLD_ = 0
    _LOOT_OIL_ = 0
    _LOOT_DIAMOND = 0
    _LOOT_ITEMS_ = None
    _INTEL_DATA_ = None

    def get_active_exploration_find_event():
        current_season = get_current_season()
        if not current_season:
            return 0

        active_exploration_find_events = GameEvents.select().join(GameEventTemplate).join(SeasonEvent).where(
            (GameEventTemplate.effect_type == "missions_action") &
            (GameEventTemplate.target.in_(["exploration_find"])) &
            (GameEvents.start_time <= datetime.now()) &
            (GameEvents.end_time >= datetime.now()) &
            (GameEvents.is_active == True) &
            (SeasonEvent.season == current_season)
        )


        total_effect = sum(event.template.value for event in active_exploration_find_events)
        return total_effect

    def get_active_exploration_save_event():
            current_season = get_current_season()
            if not current_season:
                return 0

            active_exploration_save_events = GameEvents.select().join(GameEventTemplate).join(SeasonEvent).where(
                (GameEventTemplate.effect_type == "missions_action") &
                (GameEventTemplate.target.in_(["exploration_save"])) &
                (GameEvents.start_time <= datetime.now()) &
                (GameEvents.end_time >= datetime.now()) &
                (GameEvents.is_active == True) &
                (SeasonEvent.season == current_season)
            )


            total_effect = sum(event.template.value for event in active_exploration_save_events)
            return total_effect

    def get_empire_exploration_find_items(empire):
            items = (EmpireItems
                    .select(Items.value)
                    .join(Items)
                    .where((EmpireItems.empire == empire) & (Items.category == "explore")))

            return sum(item.item.value for item in items) if items else 0

    def get_empire_exploration_save_items(empire):
            items = (EmpireItems
                    .select(Items.value)
                    .join(Items)
                    .where((EmpireItems.empire == empire) & (Items.category == "safety")))

            return sum(item.item.value for item in items) if items else 0

    def get_empire_active_busters(empire, category):
        busters = (EmpireBusters
                .select(Busters.value)
                .join(Busters)
                .where(
                    (EmpireBusters.empire == empire) &
                    (Busters.category == category) &
                    (EmpireBusters.start_date <= datetime.now()) &
                    (EmpireBusters.end_time >= datetime.now())
                ))

        return sum(buster.buster.value for buster in busters) if busters else 0

    def is_tech_completed(empire, tech_name):
        query = EmpireResearch.select().join(Research).where(
            (Research.name == tech_name) &
            (EmpireResearch.empire == empire) &
            (EmpireResearch.status == "completed")
        )
        return query.exists()

    def get_total_exploration_find_bonus(empire):
        bonus = 1.0
        bonus += get_active_exploration_find_event()
        bonus += get_empire_exploration_find_items(empire)
        bonus += get_empire_active_busters(empire, "explore_find")
        if is_tech_completed(empire, "tech_explore_find_up"):
            bonus += 0.1
        return bonus

    def get_total_exploration_save_bonus(empire):
        bonus = 1.0
        bonus += get_active_exploration_save_event()
        bonus += get_empire_exploration_save_items(empire)
        bonus += get_empire_active_busters(empire, "safety_exp_units")
        if is_tech_completed(empire, "tech_safety_exp_units_up"):
            bonus -= 0.1
        return max(0.5, bonus)

    _DESCRIPTION_ = "Вы исследовали местность"
    _SUCCESS_ = True

    empire = mission.empire
    radius = mission.radius
    units_sent = mission.units_sent

    _UNITS_SENT_ = units_sent

    exploration_empire_resources = EmpireResource.get_or_none(EmpireResource.empire == empire)

    if not exploration_empire_resources:
        print(f"❌ Ресурсы империи {empire.name} не найдены!")
        return


    find_bonus = get_total_exploration_find_bonus(empire)
    save_bonus = get_total_exploration_save_bonus(empire)




    final_loss_chance = min(0.1 + (radius / 100), 0.5)
    adjusted_loss_chance = final_loss_chance * save_bonus

    exploration_units_lost = int(units_sent * adjusted_loss_chance)

    _UNITS_LOST_ = exploration_units_lost

    remaining_units = max(0, exploration_empire_resources.units_exploration + (units_sent - exploration_units_lost))

    _UNITS_RETURN_ = remaining_units

    exploration_empire_resources.units_exploration = remaining_units
    exploration_empire_resources.save()


    results = generate_exploration_result(empire, units_sent, radius, find_bonus)


    object_counts = Counter(results)


    mission.status = "completed"
    mission.save()


    save_mission_result(
        mission=mission,
        success=_SUCCESS_,
        description=_DESCRIPTION_,
        units_sent=_UNITS_SENT_,
        target_units=_TARGET_UNITS_,
        units_lost=_UNITS_LOST_,
        units_return=_UNITS_RETURN_,
        loot_wood=_LOOT_WOOD_,
        loot_gold=_LOOT_GOLD_,
        loot_oil=_LOOT_OIL_,
        loot_diamond=_LOOT_DIAMOND,
        loot_item=_LOOT_ITEMS_,
        intel_data=_INTEL_DATA_,
    )


    found_objects_str = ", ".join(
        f"{count} {name}" for name, count in object_counts.items()
    )

    formatted_news_text = (
        f"Империя {empire.name} завершила миссию исследования и нашла: {found_objects_str}. Потери исследователей составили: {exploration_units_lost} юнитов."
    )

    write_news(formatted_news_text)

    user = get_user_by_empire(empire)
    if user:
        if object_counts:
            total_found = sum(object_counts.values())
            message = (
                f"🌍 Миссия исследования (ID: {mission.mission_id}) завершена!\n"
                f"🔎 Найдено локаций: {total_found}\n"
                f"💀 Потери юнитов: {exploration_units_lost} из {units_sent}\n"
                f"🗺 Посмотрите: Карта кластера → Найденные локации."
            )
        else:
            message = (
                f"🌍 Миссия исследования (ID: {mission.mission_id}) завершена!\n"
                f"⚠️ К сожалению, ничего не было найдено.\n"
                f"💀 Потери юнитов: {exploration_units_lost} из {units_sent}"
            )

        try:
            send_message_sync(user.chat_id, message)
        except Exception as e:
            print(f"Error in calculate_result_for_missions_exploration: {e}")

    update_quest_progress(empire, "mission", "exploration", 1)

    process_empire_action(empire, "explore", {"xp": 25, "rp": 5})





def start_mission_attack(empire, target_id, units_to_send):

    mission_type = Mission.get_or_none(Mission.name == "attack")
    if mission_type is None:
        raise ValueError(f"Тип миссии {mission_type} не найден в таблице Mission")


    target_empire = Empire.get_or_none(Empire.id == target_id)
    if target_empire == empire:
        return None, "Вы не можете атаковать свою империю!"
    if target_empire is None:
        return None, f"Империя с ID {target_id} не найдена"


    count_units_army = EmpireResource.get_or_none(EmpireResource.empire == empire).units_army

    if count_units_army < units_to_send:
        return None, f"Империя {empire.name} не имеет достаточно юнитов для атаки!"


    existing_mission = EmpireMission.get_or_none(
        (EmpireMission.empire == empire) &
        (EmpireMission.mission_type == mission_type) &
        (EmpireMission.status == "pending") &
        (EmpireMission.target == target_empire)
    )
    if existing_mission:
        return None, "Миссия такого типа уже выполняется для этой цели."

    total_points = calculate_time_for_mission_attack(empire, units_to_send)


    update_resources(empire, resource_name='units_army', value=-units_to_send)


    empire_mission = EmpireMission.create(
        empire=empire,
        mission_type=mission_type,
        target=target_empire,
        units_sent=units_to_send,
        mission_start=datetime.now(),
        total_points=total_points,
        status="pending",
        result=None
    )

    formatted_news_text = (
        f"Империя {empire.name} начала миссию атака на империю {target_empire.name}!"
    )
    write_news(formatted_news_text)

    return empire_mission, None


def start_mission_attack_location(empire, location_id, units_to_send):
    """Запуск миссии атаки на локацию"""


    mission_type = Mission.get_or_none(Mission.name == "attack_location")
    if not mission_type:
        raise ValueError("Тип миссии 'attack_location' не найден!")


    target_location = EmpireLocations.get_or_none(
        (EmpireLocations.empire == empire) &
        (EmpireLocations.id == location_id)
    )

    if not target_location:
        return None, f"❌ Локация с ID {location_id} не найдена у империи {empire.name}!"


    empire_resources = EmpireResource.get_or_none(EmpireResource.empire == empire)
    if not empire_resources or empire_resources.units_army < units_to_send:
        return None, f"❌ Недостаточно юнитов для атаки!"


    existing_mission = EmpireMission.get_or_none(
        (EmpireMission.empire == empire) &
        (EmpireMission.mission_type == mission_type) &
        (EmpireMission.status == "pending") &
        (EmpireMission.location == target_location)
    )
    if existing_mission:
        return None, "⚠️ Атака на эту локацию уже выполняется!"


    total_points = calculate_time_for_mission_attack(empire, units_to_send)


    update_resources(empire, resource_name="units_army", value=-units_to_send)


    empire_mission = EmpireMission.create(
        empire=empire,
        mission_type=mission_type,
        location=target_location,
        units_sent=units_to_send,
        mission_start=datetime.now(),
        total_points=total_points,
        status="pending"
    )

    return empire_mission, None





def start_mission_espionage(empire, target_id, units_to_send):

    mission_type = Mission.get_or_none(Mission.name == "espionage")
    if mission_type is None:
        raise ValueError(f"Тип миссии {mission_type} не найден в таблице Mission")


    target_empire = Empire.get_or_none(Empire.empire_id == target_id)
    if target_empire == empire:
        return None, "Вы не можете посылать шпионов в свою империю!"
    if target_empire is None:
        return None, f"Империя с ID {target_id} не найдена"


    count_units_spy = EmpireResource.get_or_none(EmpireResource.empire == empire).units_spy

    if count_units_spy < units_to_send:
        return None, f"Империя {empire.name} не имеет достаточно шпионов!"


    existing_mission = EmpireMission.get_or_none(
        (EmpireMission.empire == empire) &
        (EmpireMission.mission_type == mission_type) &
        (EmpireMission.status == "pending") &
        (EmpireMission.target == target_empire)
    )
    if existing_mission:
        return None, "Миссия такого типа уже выполняется для этой цели."

    total_points = calculate_time_for_mission_espionage(empire, units_to_send)


    empire_mission = EmpireMission.create(
        empire=empire,
        mission_type=mission_type,
        target=target_empire,
        units_sent=units_to_send,
        mission_start=datetime.now(),
        total_points=total_points,
        status="pending",
        result=None
    )


    update_resources(empire, resource_name="units_spy", value=-units_to_send)

    formatted_news_text = (
        f"Империя {empire.name} начала миссию шпионаж в отношении империи {target_empire.name}!"
    )
    write_news(formatted_news_text)

    return empire_mission, None





def start_mission_exploration(empire, count_units, radius):
    mission_type = Mission.get_or_none(Mission.name == "exploration")
    if mission_type is None:
        raise ValueError(f"Тип миссии {mission_type} не найден в таблице Mission")

    existing_mission = EmpireMission.get_or_none(
        (EmpireMission.empire == empire) &
        (EmpireMission.mission_type == mission_type) &
        (EmpireMission.status == "pending")
    )
    if existing_mission:
        return None, "Миссия такого типа уже выполняется."

    total_points = calculate_time_for_mission_exploration(empire, count_units, radius)

    update_resources(empire, resource_name='units_exploration', value=-count_units)

    empire_mission = EmpireMission.create(
        empire=empire,
        mission_type=mission_type,
        target=None,
        units_sent=count_units,
        mission_start=datetime.now(),
        total_points=total_points,
        status="pending",
        radius=radius
    )

    write_news(f"Империя {empire.name} начала миссию исследования")

    return empire_mission, None





def get_all_chat_id_by_empires():
    return (
        UserData
        .select(UserData.chat_id)
        .join(Empire)
        .distinct()
    )





def get_upkeep_units_in_garrison():
    gold_upkeep = GameGlobalSettings.get(GameGlobalSettings.key == "gold_upkeep_per_unit").value
    return gold_upkeep





def get_found_locations_by_empire(empire):
    locations = EmpireLocations.select().where(EmpireLocations.empire == empire)
    mission_type = Mission.get_or_none(Mission.name == "attack_location")
    if mission_type is None:
        raise ValueError(f"Тип миссии {mission_type} не найден в таблице Mission")

    found_locations = []
    for loc in locations:

        is_under_attack = EmpireMission.select().where(
            (EmpireMission.location == loc) &
            (EmpireMission.mission_type == mission_type) &
            (EmpireMission.status == "pending")
        ).exists()

        resources = {
            "🌲 Древесина": loc.wood,
            "🪙 Золото": loc.gold,
            "🛢 Нефть": loc.oil,
            "💎 Алмазы": loc.diamond,
            "⚡ Энергия": loc.energy
        }
        items = loc.items.split(",") if loc.items else []

        location_report = f"📍 <b>{loc.name}</b> (ID: {loc.location_id})\n"

        if is_under_attack:
            location_report += "\n🔥 <b>Локация атакуется!</b>"

        if loc.monsters > 0:
            location_report += f"\n⚔️ <b>Монстры:</b> {loc.monsters}"

        if any(resources.values()):
            resource_text = "\n".join([f"{key}: {value}" for key, value in resources.items() if value > 0])
            location_report += f"\n\n💰 <b>Ресурсы:</b>\n{resource_text}"

        if items:
            item_text = "\n".join([f"🎁 {item.strip()}" for item in items])
            location_report += f"\n\n🎁 <b>Найденные предметы:</b>\n{item_text}"

        found_locations.append((location_report, loc.location_id, is_under_attack))

    return found_locations





def get_location_by_id(empire, location_id):
    """Получает локацию по ID, принадлежащую данной империи"""
    return EmpireLocations.get_or_none((EmpireLocations.empire == empire) & (EmpireLocations.id == location_id))





def get_current_missions_by_empire(empire):
    """Возвращает список активных миссий империи."""
    return EmpireMission.select().where(
        (EmpireMission.empire == empire) &
        (EmpireMission.status == "pending")
    )


def get_mission_speed_modifiers(empire):
    modifiers = 1.0






    return modifiers





def update_mission_progress(mission: EmpireMission):
    now = datetime.now()
    time_passed = (now - mission.last_update).total_seconds()


    base_speed = 1.0
    modifiers = get_mission_speed_modifiers(mission.empire)
    actual_speed = base_speed * modifiers

    progress_gained = actual_speed * time_passed
    mission.progress += progress_gained
    mission.last_update = now
    mission.save()

    if mission.progress >= mission.total_points:
        mission.status = "completed"
        mission.mission_end = now
        mission.save()


        if mission.mission_type.name == "exploration":
            calculate_result_for_missions_exploration(mission)
        elif mission.mission_type.name == "attack":
            calculate_result_for_missions_attack(mission)
        elif mission.mission_type.name == "attack_location":
            calculate_result_for_missions_attack_location(mission)
        elif mission.mission_type.name == "espionage":
            calculate_result_for_missions_espionage(mission)


def calculate_next_level_xp(level):
    """Формула для расчёта необходимого XP для следующего уровня."""
    return int(100 * (1.2 ** level))


def update_experience(empire, xp_value):
    """Обновляет опыт империи и проверяет необходимость повышения уровня."""
    try:
        with db.atomic():
            empire.current_progress_scale += xp_value


            if empire.current_progress_scale >= empire.end_progress_scale:
                empire.level += 1
                empire.current_progress_scale = 0
                empire.end_progress_scale = calculate_next_level_xp(empire.level)
                empire.save()

                user = get_user_by_empire(empire)

                user_game_settings = get_game_settings(user)
                if user_game_settings.notification_status == "all":

                    if user:
                        try:
                            message = (
                                f"Вы достигли уровня: {empire.level}!"
                            )
                            send_message_sync(user.chat_id, message)
                        except Exception as e:
                            print(f"Error in update_experience for send_message_sync: {e}")


                update_points_rating_for_empire(empire, 50)

            empire.save()
    except Exception as e:
        print(f"Ошибка при обновлении опыта для империи {empire.name}: {e}")


def process_empire_action(empire, action, params):
    """
    Обрабатывает действие игрока, начисляет RP и XP.
    :param empire: объект империи
    :param action: действие (строка)
    :param params: словарь параметров (например, { "enemy_level": 3, "units_lost": 10 })
    """
    xp_gain = 0
    rp_gain = 0

    if action == "build":
        xp_gain = params.get("xp", 10)
        rp_gain = params.get("rp", 5)

    elif action == "research":
        xp_gain = params.get("xp", 20)
        rp_gain = params.get("rp", 10)

    elif action == "explore":
        xp_gain = params.get("xp", 15)
        rp_gain = params.get("rp", 8)

    elif action == "attack":
        enemy_level = params.get("enemy_level", 1)
        success = params.get("success", False)
        xp_gain = 30 + (enemy_level * 2)
        rp_gain = 20 + (enemy_level * 5) if success else 0

    elif action == "defend":
        attacker_level = params.get("attacker_level", 1)
        xp_gain = 25 + (attacker_level * 3)
        rp_gain = 15 + (attacker_level * 4)

    elif action == "spy":
        success = params.get("success", False)
        xp_gain = 10 if success else 5
        rp_gain = 7 if success else 0

    elif action == "trade":
        quantity = params.get("quantity", 1)
        xp_per_unit = params.get("xp_per_unit", 1)
        xp_gain = int(quantity * xp_per_unit)
        rp_gain = 0


    update_experience(empire, xp_gain)

    update_points_rating_for_empire(empire, rp_gain)









def get_total_buildings_count():
    """Возвращает общее количество доступных построек в игре"""
    return Buildings.select().count()









def get_total_technologies_count():
    """Возвращает общее количество доступных технологий в игре"""
    return Research.select().count()



def get_empire_items_count(empire):
    """Возвращает количество предметов у империи"""
    return EmpireItems.select().where(EmpireItems.empire == empire).count()


def get_outgoing_attacks_count(empire):
    """Возвращает количество активных атакующих миссий, инициированных данной империей."""
    return EmpireMission.select().where(
        (EmpireMission.empire == empire) &
        (EmpireMission.mission_type.name == 'attack') &
        (EmpireMission.status == 'pending')
    ).count()


def get_incoming_attacks_count(empire):
    """Возвращает количество активных атакующих миссий, направленных против данной империи."""
    return EmpireMission.select().where(
        (EmpireMission.target == empire) &
        (EmpireMission.mission_type.name == 'attack') &
        (EmpireMission.status == 'pending')
    ).count()


def get_science_research_speed(empire):
    """
    Рассчитывает общую скорость изучения науки для империи,
    суммируя вклад всех лабораторий.
    """
    try:

        labs = (EmpireBuildings
                .select(EmpireBuildings, Buildings)
                .join(Buildings)
                .where(
                    (EmpireBuildings.empire == empire) &
                    (Buildings.name == "laboratory") &
                    (EmpireBuildings.status.in_(["completed", "producing"]))
                ))


        total_science_speed = sum(lab.level * lab.building.base_production for lab in labs)

        return total_science_speed
    except Exception as e:
        print(f"Ошибка при расчёте скорости науки: {e}")
        return 0


def place_units_to_garrison(empire: Empire, count_units_army: int):
    """Размещает юнитов в гарнизоне империи."""
    if not validate_positive_number(count_units_army):
        return None, "Некорректное количество юнитов."

    empire_status, _ = EmpireStatus.get_or_create(empire=empire)


    current_count_units_army = get_resource_count(empire, "units_army")
    if current_count_units_army < count_units_army:
        return None, "Недостаточно юнитов для размещения в гарнизоне."


    empire_status.garrison_units += count_units_army
    update_resources(empire, resource_name='units_army', value=-count_units_army)


    gold_upkeep = empire_status.garrison_units * get_upkeep_units_in_garrison()
    empire_status.gold_upkeep_per_hour = gold_upkeep


    empire_status.defense_bonus = empire_status.garrison_units * 0.005


    empire_status.save()

    return True, f"Вы разместили {count_units_army} юнитов в гарнизоне."


def empire_effects_loop(empire):
    """Обновление эффектов для конкретной империи"""
    empire_status = EmpireStatus.get_or_none(empire=empire)
    empire_resources = EmpireResource.get_or_none(empire=empire)

    if not empire_status or not empire_resources:
        print(f"❌ Не найдены данные для империи {empire.name}!")
        return


    gold_upkeep = empire_status.gold_upkeep_per_hour / 60
    if empire_resources.gold >= gold_upkeep:
        empire_resources.gold -= gold_upkeep
    else:
        empire_status.garrison_units = 0

    empire_status.updated_at = datetime.now()

    empire_status.save()
    empire_resources.save()


def get_empire_defense_info(empire):

    empire_status = EmpireStatus.get_or_none(EmpireStatus.empire == empire)

    if empire_status:
        defense_bonus = empire_status.defense_bonus
        gold_upkeep_per_hour = empire_status.gold_upkeep_per_hour
    else:
        defense_bonus = 0
        gold_upkeep_per_hour = 0

    return defense_bonus, gold_upkeep_per_hour


def get_production_report(empire: Empire):
    """Формирует отчёт о производстве ресурсов в час для заданной империи."""
    production_report = {}


    production_buildings = EmpireBuildings.select().where(EmpireBuildings.empire == empire)

    print(f"🔍 Найдено {len(production_buildings)} зданий в империи {empire.name}")

    for empire_building in production_buildings:
        building = empire_building.building
        production_per_hour = empire_building.current_production

        print(f"🏗️ Здание: {building.name}, Тип: {building.building_type}, Производство: {production_per_hour}")

        if production_per_hour > 0:
            if building.building_type not in production_report:
                production_report[building.building_type] = 0
            production_report[building.building_type] += production_per_hour

    print(f"📊 Итоговый отчёт: {production_report}")

    return production_report


def get_unit_production_report(empire: Empire):
    """Формирует отчёт о найме юнитов в час для заданной империи."""
    unit_production_report = {}

    production_units_map = {
        "exp_corpus": "units_exploration",
        "spy_center": "units_spy",
        "conspy_center": "units_counterspy",
        "barracks": "units_army",
    }

    unit_buildings = EmpireBuildings.select().where(EmpireBuildings.empire == empire)

    for b in unit_buildings:
        building_name = b.building.name
        unit_type = production_units_map.get(building_name)
        if not unit_type:
            continue

        if b.is_producing and b.current_production_interval > 0:
            units_per_hour = 3600 // b.current_production_interval
        else:
            units_per_hour = 0

        if units_per_hour > 0:
            unit_production_report.setdefault(unit_type, 0)
            unit_production_report[unit_type] += units_per_hour

    return unit_production_report


def get_completed_technologies(empire):
    """
    Возвращает список технологий, которые изучены империей.
    """
    return [
        research.research.name
        for research in EmpireResearch.select().where(
            (EmpireResearch.empire == empire) & (EmpireResearch.status == "completed")
        )
    ]


def has_quest_success(empire, quest_name):
    try:
        quest = Quests.get(Quests.name == quest_name)
        empire_quest = EmpireQuests.get_or_none(
            (EmpireQuests.empire == empire) &
            (EmpireQuests.quest == quest)
        )
        return empire_quest.completed if empire_quest else False
    except Exception as e:
        print(f"❌ Ошибка в has_quest_success: {e}")
        return False


def get_building_speed_modifiers(empire):
    modifiers = 1.0
    now = datetime.now()


    active_busters = (EmpireBusters
                      .select()
                      .join(Busters)
                      .where(
                          (EmpireBusters.empire == empire) &
                          (EmpireBusters.start_date <= now) &
                          (EmpireBusters.end_time >= now)
                      ))

    for eb in active_busters:
        if eb.buster.category == 'building_speed':
            modifiers *= (1 + eb.buster.value)


    building_speed_research_bonuses = {
        "Faster Construction I": 0.01,
        "Faster Construction II": 0.02,
        "Advanced Building Techniques": 0.05,

    }

    completed_researches = (EmpireResearch
                            .select()
                            .join(Research)
                            .where(
                                (EmpireResearch.empire == empire) &
                                (EmpireResearch.status == 'completed')
                            ))

    for er in completed_researches:
        bonus = building_speed_research_bonuses.get(er.research.name)
        if bonus:
            modifiers *= (1 + bonus)


    empire_items = (EmpireItems
                    .select()
                    .join(Items)
                    .where(EmpireItems.empire == empire))

    for ei in empire_items:
        if ei.item.category == 'building_speed':
            modifiers *= (1 + ei.item.value)


    active_events = (GameEvents
                     .select()
                     .join(GameEventTemplate)
                     .where(
                         (GameEvents.is_active == True) &
                         (GameEvents.start_time <= now) &
                         (GameEvents.end_time >= now) &
                         (GameEventTemplate.target == 'building_speed')
                     ))

    for event in active_events:
        modifiers *= (1 + event.template.value)

    return max(modifiers, 0.01)


def check_building_construction(empire):
    now = datetime.now()

    unit_production_buildings = {"barracks", "exp_corpus", "spy_center", "conspy_center"}

    pending_buildings = EmpireBuildings.select().where(
        (EmpireBuildings.empire == empire) &
        (EmpireBuildings.status == "pending")
    )

    build_speed_modifiers = get_building_speed_modifiers(empire)

    for building in pending_buildings:
        time_passed = (now - building.last_update).total_seconds()

        base_speed = 1.0
        actual_speed = base_speed * build_speed_modifiers

        progress_gained = actual_speed * time_passed
        building.progress += progress_gained
        building.last_update = now
        building.save()

        print(f"🏗️ {building.building.name}: {building.progress:.2f} / {building.total_points}")

        if building.progress >= building.total_points:
            building.status = (
                "completed" if building.building.name in unit_production_buildings else "producing"
            )
            building.current_production=building.building.base_production if building.status == "producing" else 0
            building.next_production_time = now + timedelta(
                seconds=int(3600 / (building.building.base_production or 10))
            ) if building.status == "producing" else None

            write_news(f"Империя {empire.name} завершает строительство здания \"{building.building.name}\"")
            update_quest_progress(empire, "build", building.building.name, 1)

            print(f"✅ {building.building.name} завершено в {empire.name}")
            building.save()

            process_empire_action(empire, "build", {"xp": 50, "rp": 0})

            user = get_user_by_empire(empire)

            user_game_settings = get_game_settings(user)
            if user_game_settings.notification_status == "all":

                if user:
                    try:
                        message = (
                            f"Строительство здания {building.building.name} завершено."
                        )
                        send_message_sync(user.chat_id, message)
                    except Exception as e:
                        print(f"Error in check_building_construction for send_message_sync: {e}")











































def get_science_modifiers(empire):
    """Возвращает множитель науки (например, 1.1 = +10%, 0.9 = -10%)."""
    modifiers = 1.0
    now = datetime.now()


    active_busters = (EmpireBusters
                      .select()
                      .join(Busters)
                      .where(
                          (EmpireBusters.empire == empire) &
                          (EmpireBusters.start_date <= now) &
                          (EmpireBusters.end_time >= now)
                      ))

    for eb in active_busters:
        if eb.buster.category == 'research_speed':
            modifiers *= (1 + eb.buster.value)


    empire_items = (EmpireItems
                    .select()
                    .join(Items)
                    .where(EmpireItems.empire == empire))

    for ei in empire_items:
        if ei.item.category == 'research_speed':
            modifiers *= (1 + ei.item.value)


    active_events = (GameEvents
                     .select()
                     .join(GameEventTemplate)
                     .where(
                         (GameEvents.is_active == True) &
                         (GameEvents.start_time <= now) &
                         (GameEvents.end_time >= now) &
                         (GameEventTemplate.target == 'research_speed')
                     ))

    for event in active_events:
        modifiers *= (1 + event.template.value)

    return max(modifiers, 0.01)


def check_research_progress(empire):
    now = datetime.now()
    researches_pending = EmpireResearch.select().where(
        (EmpireResearch.empire == empire) & (EmpireResearch.status == "pending")
    )

    lab = (EmpireBuildings
           .select(EmpireBuildings, Buildings)
           .join(Buildings)
           .where(EmpireBuildings.empire == empire, Buildings.name == "laboratory")
           .get_or_none())

    lab_level = lab.level if lab else 0
    if lab_level == 0:
        print("⚠️ Внимание! У империи нет лаборатории, исследования не проводятся.")
        return

    base_science_per_hour = lab.current_production * lab_level
    science_modifiers = get_science_modifiers(empire)
    actual_science_per_hour = base_science_per_hour * science_modifiers

    for research in researches_pending:
        time_passed = (now - research.last_update).total_seconds() / 3600
        science_gained = actual_science_per_hour * time_passed

        research.progress += science_gained
        research.last_update = now
        research.save()

        print(f"📚 Исследование {research.research.name}: {research.progress:.2f} / {research.total_points}")

        if research.progress >= research.total_points:
            research.status = "completed"
            research.save()

            update_quest_progress(empire, "research", research.research.name, 1)

            formatted_news_text = (
                f"Империя {empire.name} завершила исследование технологии {research.research.name}"
            )
            write_news(formatted_news_text)

            print(f"🎓 Исследование {research.research.name} завершено!")

            process_empire_action(empire, "research", {"xp": 40, "rp": 0})

            user = get_user_by_empire(empire)

            user_game_settings = get_game_settings(user)
            if user_game_settings.notification_status == "all":

                if user:
                    try:
                        message = (
                            f"Исследование технологии {research.research.name} завершено."
                        )
                        send_message_sync(user.chat_id, message)
                    except Exception as e:
                        print(f"Error in check_research_progress for send_message_sync: {e}")



















def update_market_rates():
    for rate in MarketRate.select():
        rate.buy_price = max(50, rate.buy_price + random.randint(-10, 10))
        rate.sell_price = max(40, rate.sell_price + random.randint(-10, 10))
        rate.updated_at = datetime.now()
        rate.save()


def get_mission_by_id(mission_id: int) -> EmpireMission | None:
    return EmpireMission.get_or_none(EmpireMission.mission_id == mission_id)


def update_resources_and_rating(empire):
    """Пересчитывает рейтинг на основе всех юнитов, включая находящихся в миссиях, и обновляет его при необходимости."""


    empire_resources = EmpireResource.get_or_none(EmpireResource.empire == empire)
    if not empire_resources:
        return


    active_missions = EmpireMission.select().where(
        (EmpireMission.empire == empire) & (EmpireMission.status != "completed")
    )

    units_in_missions = sum(mission.units_sent for mission in active_missions)


    total_points_army = empire_resources.units_army + units_in_missions


    A, B, C, D = 1.1, 1.05, 1.025, 1.007


    new_rating = (
        A * total_points_army +
        B * empire_resources.units_spy +
        C * empire_resources.units_counterspy +
        D * empire_resources.units_exploration
    )


    rating_difference = int(new_rating) - empire.rating_points


    if rating_difference != 0:
        update_points_rating_for_empire(empire, rating_difference)


def update_unit_production():
    now = datetime.now()

    production_units_map = {
        "exp_corpus": "units_exploration",
        "spy_center": "units_spy",
        "conspy_center": "units_counterspy",
        "barracks": "units_army",
    }

    buildings = EmpireBuildings.select().where(EmpireBuildings.is_producing == True)

    for b in buildings:
        if b.current_production >= b.current_max_production_capacity:
            continue

        unit_type = production_units_map.get(b.building.name)
        if not unit_type:
            continue

        time_diff = (now - b.next_production_time).total_seconds()
        if time_diff < 0:
            continue


        remaining = b.units_to_hire - b.current_production
        if remaining <= 0:
            b.is_producing = False
            b.status = "idle"
            b.save()
            continue


        production_cycles = int(time_diff // b.current_production_interval)
        if production_cycles < 1:
            continue

        units_to_produce = min(production_cycles, remaining)


        empire_resource = EmpireResource.get(empire=b.empire)
        setattr(empire_resource, unit_type, getattr(empire_resource, unit_type) + units_to_produce)
        empire_resource.save()


        b.current_production += units_to_produce
        b.produced_but_unhired += units_to_produce
        b.next_production_time += timedelta(seconds=units_to_produce * b.current_production_interval)

        print(f"✅ {b.building.name} произвел {units_to_produce} {unit_type} для {b.empire.name}!")


        if b.current_production >= b.units_to_hire:
            b.is_producing = False
            b.status = "idle"
            b.produced_but_unhired = 0
            b.current_production = 0

        b.save()


def add_units_to_hire(empire_building: EmpireBuildings, count: int):
    if empire_building.produced_but_unhired < count:
        print("❌ Нельзя дозаказать больше, чем уже произведено")
        return False

    empire_building.units_to_hire += count
    empire_building.produced_but_unhired -= count
    empire_building.save()
    print(f"➕ Дозаказано {count} юнитов. Всего теперь: {empire_building.units_to_hire}")
    return True


def get_production_modifiers(empire, resource_type: str) -> float:
    """
    Возвращает множитель к добыче ресурса (wood, gold, oil, diamond) с учётом всех активных модификаторов.
    """
    now = datetime.now()
    modifier = 1.0


    active_busters = (
        EmpireBusters
        .select()
        .join(Busters)
        .where(
            (EmpireBusters.empire == empire) &
            (EmpireBusters.start_date <= now) &
            (EmpireBusters.end_time >= now)
        )
    )

    for eb in active_busters:
        if eb.buster.category in [f'production_{resource_type}', 'production_all']:
            modifier *= (1 + eb.buster.value)


    research_bonus_map = {
        'Improved Wood Cutting': ('wood', 0.05),
        'Gold Extraction Efficiency': ('gold', 0.05),
        'Oil Drilling Tech': ('oil', 0.05),
        'Diamond Cracking': ('diamond', 0.05),
        'Advanced Logistics': ('all', 0.03)
    }

    completed_researches = (
        EmpireResearch
        .select()
        .join(Research)
        .where(
            (EmpireResearch.empire == empire) &
            (EmpireResearch.status == 'completed')
        )
    )

    for er in completed_researches:
        res_type, bonus = research_bonus_map.get(er.research.name, (None, 0))
        if res_type == resource_type or res_type == 'all':
            modifier *= (1 + bonus)


    empire_items = (
        EmpireItems
        .select()
        .join(Items)
        .where(EmpireItems.empire == empire)
    )

    for ei in empire_items:
        if ei.item.category in [f'production_{resource_type}', 'production_all']:
            modifier *= (1 + ei.item.value)


    active_events = (
        GameEvents
        .select()
        .join(GameEventTemplate)
        .where(
            (GameEvents.is_active == True) &
            (GameEvents.start_time <= now) &
            (GameEvents.end_time >= now) &
            (GameEventTemplate.target.in_([resource_type, 'all'])) &
            (GameEventTemplate.effect_type == 'resource_production')
        )
    )

    for event in active_events:
        modifier *= (1 + event.template.value)


    user = get_user_by_empire(empire)
    if user.subscription_status:
        modifier *= 1.10

    return max(modifier, 0.01)


def update_empire_resources():
    now = datetime.now()

    for empire_building in EmpireBuildings.select().where(EmpireBuildings.status == "producing"):
        building = empire_building.building
        empire_resources = EmpireResource.get(EmpireResource.empire == empire_building.empire)

        resource_production_map = {
            "sawmill": "wood",
            "woodworking_plant": "wood",
            "biofuel_plant": "wood",
            "forest_reserve": "wood",
            "forest_bio_center": "wood",
            "gold_mine": "gold",
            "gold_process_plant": "gold",
            "gold_mint": "gold",
            "jewelry_workshop": "gold",
            "gold_invest_center": "gold",
            "oil_well": "oil",
            "oil_refinery": "oil",
            "plastic_factory": "oil",
            "chemical_plant": "oil",
            "petrochemical_center": "oil",
            "diamond_quarry": "diamond",
            "cutting_center": "diamond",
            "jewelry_house": "diamond",
            "innovation_center": "diamond",
            "diamond_research_institute": "diamond"
        }

        if building.name not in resource_production_map:
            continue

        resource_type = resource_production_map[building.name]
        rate = building.base_production
        interval = int(3600 / rate) if rate else 0

        if interval == 0:
            continue


        time_diff = (now - empire_building.next_production_time).total_seconds()
        if time_diff < 0:
            continue

        production_cycles = int(time_diff // interval)
        if production_cycles < 1:
            continue


        modifier = get_production_modifiers(empire_building.empire, resource_type)
        production_amount = int(production_cycles * modifier)


        setattr(empire_resources, resource_type,
                getattr(empire_resources, resource_type) + production_amount)
        empire_resources.save()


        empire_building.next_production_time += timedelta(seconds=production_cycles * interval)
        empire_building.save()

        print(f"🪵 {building.name} произвёл {production_cycles} ед. {resource_type} для {empire_building.empire.name}")


def has_building_pending(empire: Empire, building_name: str) -> bool:
    return (
        EmpireBuildings
        .select()
        .join(Buildings)
        .where((EmpireBuildings.empire == empire) & (Buildings.name == building_name) & (EmpireBuildings.status == "pending"))
        .exists()
    )


def has_building_complete(empire: Empire, building_name: str) -> bool:
    return (
        EmpireBuildings
        .select()
        .join(Buildings)
        .where(
            (EmpireBuildings.empire == empire) &
            (Buildings.name == building_name) &
            ((EmpireBuildings.status == "completed") | (EmpireBuildings.status == "producing") | (EmpireBuildings.status == "idle"))
        )
        .exists()
    )


def has_researched(empire: Empire, research_name: str) -> bool:
    """Проверяет, есть ли у империи технология с указанным названием"""
    return (
        EmpireResearch
        .select()
        .join(Research)
        .where((EmpireResearch.empire == empire) & (Research.name == research_name))
        .exists()
    )


def start_train_units(empire: Empire, building_name: str, units_to_produce: int):
    building = Buildings.get_or_none(Buildings.name == building_name)
    empire_building = EmpireBuildings.get_or_none(
        (EmpireBuildings.empire == empire) & (EmpireBuildings.building == building)
    )

    if not empire_building or empire_building.status == "pending":
        print("❌ Здание ещё не построено!")
        return

    production_units_map = {
        "exp_corpus": ("units_exploration", 1),
        "spy_center": ("units_spy", 3),
        "conspy_center": ("units_counterspy", 3),
        "barracks": ("units_army", 2),
    }

    if building_name not in production_units_map:
        print("❌ Это здание не производит юнитов!")
        return

    if empire_building.status == "producing":
        print("⚙ Производство уже идет!")
        return

    if empire_building.current_production >= empire_building.current_max_production_capacity:
        print("Здание заполнено юнитами.")
        return


    unit_type, unit_cost = production_units_map[building_name]


    empire_resources = EmpireResource.get_or_none(EmpireResource.empire == empire)
    available_gold = empire_resources.gold if empire_resources else 0


    affordable_units = available_gold // unit_cost if unit_cost else 0
    available_capacity = empire_building.current_max_production_capacity - empire_building.current_production
    hireable_units = min(units_to_produce, affordable_units, available_capacity)

    if hireable_units <= 0:
        print("❌ Недостаточно золота или вместимости для найма.")
        return


    empire_resources.gold -= hireable_units * unit_cost
    empire_resources.save()


    units_per_hour = building.base_production or 10
    interval = int(3600 / units_per_hour)

    empire_building.units_to_hire = hireable_units
    empire_building.current_production = 0
    empire_building.current_production_interval = interval
    empire_building.produced_but_unhired = 0
    empire_building.is_producing = True
    empire_building.status = "producing"
    empire_building.next_production_time = datetime.now() + timedelta(seconds=interval)
    empire_building.save()

    unit_type_map = {
        "units_army": "юнитов армии",
        "units_exploration": "исследователей",
        "units_spy": "разведки",
        "units_counterspy": "контрразведки"
    }

    unit_text = unit_type_map.get(unit_type, "неизвестных юнитов")
    formatted_news_text = f"Империя {empire.name} начала производство {unit_text}."
    write_news(formatted_news_text)


def is_building_under_construction(empire: Empire, building_name: str) -> bool:
    """Проверяет, находится ли здание в процессе строительства."""
    return (
        EmpireBuildings
        .select()
        .join(Buildings)
        .where(
            (EmpireBuildings.empire == empire) &
            (Buildings.name == building_name) &
            (EmpireBuildings.status == "pending")
        )
        .exists()
    )


def is_research_pending(empire: Empire, research_name: str) -> bool:
    """Проверяет, находится ли технология в процессе изучения."""
    return (
        EmpireResearch
        .select()
        .join(Research)
        .where(
            (EmpireResearch.empire == empire) &
            (Research.name == research_name) &
            (EmpireResearch.status == "pending")
        )
        .exists()
    )


def is_mission_active(empire: Empire, mission_type: str) -> bool:
    """Проверяет, есть ли уже активная миссия данного типа."""
    return (
        EmpireMission
        .select()
        .join(Mission)
        .where(
            (EmpireMission.empire == empire) &
            (Mission.name == mission_type) &
            (EmpireMission.status == "pending")
        )
        .exists()
    )


def is_unit_production_active(empire: Empire, building_name: str) -> bool:
    """Проверяет, запущено ли производство юнитов в здании."""
    return (
        EmpireBuildings
        .select()
        .join(Buildings)
        .where(
            (EmpireBuildings.empire == empire) &
            (Buildings.name == building_name) &
            (EmpireBuildings.status == "producing")
        )
        .exists()
    )


def has_item(empire, item_name):
    """Проверяет, есть ли у империи предмет с указанным именем."""
    return (EmpireItems
            .select()
            .join(Items)
            .where(EmpireItems.empire == empire, Items.name == item_name)
            .exists())











































































def get_next_building(building_name):
    building = Buildings.get_or_none(Buildings.name == building_name)
    if building and building.next_building:
        return Buildings.get_or_none(Buildings.name == building.next_building)
    return None


def get_empire_position(empire):
    query = (Empire
             .select(Empire, RatingLayer.name.alias('rating_layer_name'))
             .join(RatingLayer, JOIN.LEFT_OUTER)
             .order_by(Empire.rating_points.desc()))

    ranking_list = list(query)

    for position, ranked_empire in enumerate(ranking_list, 1):
        if ranked_empire == empire:
            return position, empire.rating_points, empire.rating_layer.name if empire.rating_layer else "Без рейтинга"

    return None


def add_quest(name, description, quest_type, objective, target, amount, reward, next_quest_id=None, is_repeatable=False, is_event=False):
    """
    Добавляет новый квест в таблицу Quests.

    :param name: Название квеста
    :param description: Описание квеста
    :param quest_type: Тип квеста (main, daily, weekly, event)
    :param objective: Что нужно сделать (build, upgrade, produce, attack)
    :param target: Конкретная цель (например, "Farm", "level_5", "1000_wood")
    :param amount: Количество, которое нужно выполнить
    :param reward: JSON-словарь с наградами (например, {"gold": 100, "wood": 500})
    :param next_quest_id: ID следующего квеста в цепочке (по умолчанию None)
    :param is_repeatable: Можно ли выполнять повторно
    :param is_event: Является ли частью события
    :return: Объект квеста, если успешно добавлен, иначе None
    """
    try:
        next_quest = Quests.get_or_none(id=next_quest_id) if next_quest_id else None

        quest = Quests.create(
            name=name,
            description=description,
            quest_type=quest_type,
            objective=objective,
            target=target,
            amount=amount,
            reward=reward,
            next_quest=next_quest,
            is_repeatable=is_repeatable,
            is_event=is_event
        )
        return quest
    except IntegrityError:
        print(f"Ошибка: квест '{name}' уже существует!")
        return None


def check_completed_quests(empire):
    """
    Проверяет выполненные квесты, выдаёт награду и отправляет уведомление в бота.

    :param empire: Объект империи
    """
    completed_quests = EmpireQuests.select().where(
        (EmpireQuests.empire == empire) &
        (EmpireQuests.completed == True) &
        (EmpireQuests.claimed == False)
    )

    for quest in completed_quests:

        reward = quest.quest.reward
        update_resources(empire, resource_changes=reward)


        quest.claimed = True
        quest.save()

        process_empire_action(empire, "quest", {"xp": 65, "rp": 0})








def update_quest_progress(empire, objective, target, amount=1):
    """
    Обновляет прогресс квеста для указанной империи.

    :param empire: Империя, которой принадлежит квест.
    :param objective: Тип задания (например, "build", "upgrade").
    :param target: Цель задания (например, "laboratory").
    :param amount: Количество прогресса, добавляемого за выполнение действия.
    """

    active_quests = EmpireQuests.select().join(Quests).where(
        (EmpireQuests.empire == empire) &
        (Quests.objective == objective) &
        (Quests.target == target) &
        (EmpireQuests.completed == False)
    )

    updated_quests = set()

    for empire_quest in active_quests:
        if empire_quest.id in updated_quests:
            continue


        empire_quest.progress += amount
        print(f"📈 Прогресс квеста '{empire_quest.quest.name}' для {empire.name}: {empire_quest.progress}/{empire_quest.quest.amount}")


        if empire_quest.progress >= empire_quest.quest.amount:
            empire_quest.completed = True
            empire_quest.save()
            updated_quests.add(empire_quest.id)
            print(f"✅ Квест '{empire_quest.quest.name}' завершён для {empire.name}!")

            update_experience(empire, 50)

            user = get_user_by_empire(empire)


            if user:
                try:
                    message = (
                        f"Вы успешно выполнили задание {quests_name[empire_quest.quest.name]}!\n\n"
                        f"Ваша награда:\n"
                        f"{empire_quest.quest.reward}"
                    )
                    send_message_sync(user.chat_id, message)
                except Exception as e:
                    print(f"Error in update_quest_progress for send_message_sync: {e}")

            formatted_news_text = (
                f"Империя {empire.name} успешно выполняет квест {quests_name[empire_quest.quest.name]}"
            )
            write_news(formatted_news_text)

        if has_quest_success(empire, "build_lab_name_quest") and not has_quest_success(empire, "research_cartography_name_quest"):
            assign_quest_to_empire(empire, "research_cartography_name_quest")

        if has_quest_success(empire, "research_cartography_name_quest") and not has_quest_success(empire, "build_exp_corpus_name_quest"):
            assign_quest_to_empire(empire, "build_exp_corpus_name_quest")

        if has_quest_success(empire, "build_exp_corpus_name_quest") and not has_quest_success(empire, "mission_exploration_name_quest"):
            assign_quest_to_empire(empire, "mission_exploration_name_quest")


def assign_quest_to_empire(empire, quest_name):
    """
    Назначает квест империи по названию квеста.

    :param empire: Объект империи (Empire)
    :param quest_name: Название квеста (строка)
    :return: Объект EmpireQuests, если успешно добавлен, иначе None
    """
    quest = Quests.get_or_none(Quests.name == quest_name)
    if not quest:
        print(f"Ошибка: квест '{quest_name}' не найден.")
        return None

    existing_quest = EmpireQuests.get_or_none((EmpireQuests.empire == empire) & (EmpireQuests.quest == quest))
    if existing_quest:
        print(f"Империя '{empire.name}' уже имеет квест '{quest_name}'.")
        return None

    try:
        EmpireQuests.create(
            empire=empire,
            quest=quest,
            progress=0,
            completed=False,
            claimed=False,
            start_time=datetime.now(),
            end_time=datetime.now() + timedelta(days=1) if quest.is_repeatable else None
        )


        user = get_user_by_empire(empire)

        if user:
            try:
                message = (
                    f"Уважаемый правитель! Вам назначено новое задание: {quests_name[quest_name]}"
                )
                send_message_sync(user.chat_id, message)
            except Exception as e:
                print(f"Error in update_quest_progress for send_message_sync: {e}")

        print(f"Квест '{quest_name}' успешно назначен империи '{empire.name}'.")
    except IntegrityError:
        print(f"Ошибка при назначении квеста '{quest_name}' империи '{empire.name}'.")
        return None


def add_busters(name, description, cost, category, value, base_action_time):
    Busters.create(
        name=name,
        description=description,
        cost=cost,
        category=category,
        value=value,
        base_action_time=base_action_time
    )


def create_events(season_name, event_templates_data):
    try:
        season = Season.get(Season.name == season_name)
    except Season.DoesNotExist:
        print(f"❌ Сезон с именем '{season_name}' не найден.")
        return

    for data in event_templates_data:
        template, created = GameEventTemplate.get_or_create(
            name=data["name"],
            defaults={
                "effect_type": data["effect_type"],
                "target": data["target"],
                "value": data["value"]
            }
        )
        if created:
            print(f"🌱 Добавлен шаблон события: {template.name}")
        else:
            print(f"🔁 Уже существует шаблон события: {template.name}")


        SeasonEvent.get_or_create(
            season=season,
            template=template
        )
        print(f"🔗 Связь события '{template.name}' с сезоном подтверждена.")

    print("🎉 Наполнение сезона завершено.")


def deactivate_expired_events():
    GameEvents.update(is_active=False).where(
        (GameEvents.end_time < datetime.now()) &
        (GameEvents.is_active == True)
    ).execute()


def generate_season_event():
    current_season = get_current_season()
    if not current_season:
        return


    has_active = GameEvents.select().where(
        (GameEvents.start_time <= datetime.now()) &
        (GameEvents.end_time >= datetime.now()) &
        (GameEvents.is_active == True)
    ).exists()

    if has_active:
        return


    season_event_templates = [se.template for se in current_season.season_events]
    if not season_event_templates:
        return


    selected_template = random.choice(season_event_templates)


    duration_days = random.choice([1, 2, 3])
    now = datetime.now()


    GameEvents.create(
        template=selected_template,
        start_time=now,
        end_time=now + timedelta(days=duration_days),
        is_active=True
    )

    print(f"🌟 Активировано сезонное событие: {selected_template.name} на {duration_days} дн.")


def get_last_system_event():
    return (GameEvents
            .select()
            .where(GameEvents.was_generated_by_system == True)
            .order_by(GameEvents.end_time.desc())
            .first())


def can_generate_new_event():
    PAUSE_DAYS_RANGE = (1, 7)

    current_time = datetime.now()


    active = GameEvents.select().where(
        (GameEvents.start_time <= current_time) &
        (GameEvents.end_time >= current_time) &
        (GameEvents.is_active == True)
    ).exists()

    if active:
        return False


    last_event = get_last_system_event()
    if not last_event:
        return True


    last_event_duration = (last_event.end_time - last_event.start_time).days


    min_days, max_days = PAUSE_DAYS_RANGE
    pause_days = random.randint(min_days, max_days)


    if pause_days < last_event_duration:
        print(f"⚠️ Пауза между событиями слишком мала. Ожидаем минимум {last_event_duration} дня.")
        pause_days = last_event_duration


    next_possible_time = last_event.end_time + timedelta(days=pause_days)

    return current_time >= next_possible_time


def generate_season_event_with_pause():
    if not can_generate_new_event():
        return

    current_season = get_current_season()
    if not current_season:
        return

    season_event_templates = [se.template for se in current_season.season_events]
    if not season_event_templates:
        return

    selected_template = random.choice(season_event_templates)
    duration_days = random.choice([1, 2, 3])
    now = datetime.now()

    GameEvents.create(
        template=selected_template,
        start_time=now,
        end_time=now + timedelta(days=duration_days),
        is_active=True,
        was_generated_by_system=True
    )

    print(f"🌟 Новое сезонное событие: {selected_template.name} на {duration_days} дн.")


def get_max_production_capacity_from_building(empire: Empire, building_name: str):
    building = Buildings.get_or_none(Buildings.name == building_name)
    if not building:
        print(f"Не найдено здание с именем: {building_name}")
        return

    empire_building = EmpireBuildings.get_or_none(
        (EmpireBuildings.empire == empire) & (EmpireBuildings.building == building)
    )

    if not empire_building:
        print(f"Для империи {empire.name} не существует здания {building.name}")
        return

    return empire_building.current_max_production_capacity


def check_building_upgrade(empire):
    now = datetime.now()

    upgrading_buildings = EmpireBuildings.select().where(
        (EmpireBuildings.empire == empire) &
        (EmpireBuildings.status == "upgrading")
    )

    upgrade_speed_modifiers = get_building_speed_modifiers(empire)

    unit_production_buildings = {"barracks", "exp_corpus", "spy_center", "conspy_center"}

    for empire_building in upgrading_buildings:
        time_passed = (now - empire_building.last_update).total_seconds()
        actual_speed = 1.0 * upgrade_speed_modifiers
        progress_gained = actual_speed * time_passed

        empire_building.progress += progress_gained
        empire_building.last_update = now
        empire_building.save()

        print(f"🛠️ Улучшение {empire_building.building.name}: {empire_building.progress:.2f} / {empire_building.total_points}")
        progress_bar = render_progress_bar(empire_building.progress, empire_building.total_points)
        progress_bar_emoji = render_progress_bar_emoji(empire_building.progress, empire_building.total_points)
        print(f"📚 {empire_building.building.name} {progress_bar}")
        print(f"📚 {empire_building.building.name} {progress_bar_emoji}")

        if empire_building.progress >= empire_building.total_points:
            building = empire_building.building
            old_level = empire_building.level

            if old_level < building.max_level:
                empire_building.level += 1
                empire_building.status = "completed" if building.name in unit_production_buildings else "producing"

                empire_building.current_production = building.base_production * empire_building.level
                empire_building.current_max_production_capacity = building.base_max_production_capacity * empire_building.level

                if empire_building.status == "producing":
                    interval = int(3600 / empire_building.current_production) if empire_building.current_production else 3600
                    empire_building.next_production_time = now + timedelta(seconds=interval)

                formatted_news_text = (
                    f"Империя {empire.name} завершает улучшение здания \"{building.name}\" до уровня {empire_building.level}!"
                )
                write_news(formatted_news_text)

            elif building.next_building:
                next_building = Buildings.get_or_none(Buildings.name == building.next_building)
                if next_building:
                    empire_building.building = next_building
                    empire_building.level = 1
                    empire_building.status = "completed" if next_building.name in unit_production_buildings else "producing"
                    empire_building.current_production = next_building.base_production
                    empire_building.current_max_production_capacity = next_building.base_max_production_capacity

                    if empire_building.status == "producing":
                        interval = int(3600 / next_building.base_production) if next_building.base_production else 3600
                        empire_building.next_production_time = now + timedelta(seconds=interval)

                    formatted_news_text = (
                        f"Империя {empire.name} завершает переход здания \"{building.name}\" в новое здание \"{next_building.name}\"!"
                    )
                    write_news(formatted_news_text)
                else:
                    print(f"⚠️ Не найдено здание {building.next_building} для замены {building.name}")
            else:
                empire_building.status = "completed"

            empire_building.save()
            update_quest_progress(empire, "upgrade", empire_building.building.name, 1)

            process_empire_action(empire, "build", {"xp": 60, "rp": 0})

            user = get_user_by_empire(empire)

            user_game_settings = get_game_settings(user)
            if user_game_settings.notification_status == "all":

                if user:
                    try:
                        message = (
                            f"Улучшение здания {building.building.name} завершено."
                        )
                        send_message_sync(user.chat_id, message)
                    except Exception as e:
                        print(f"Error in check_building_upgrade for send_message_sync: {e}")


def get_empire_energy_balance(empire: Empire) -> int:
    buildings = EmpireBuildings.select().where(
        (EmpireBuildings.empire == empire) & (EmpireBuildings.status == "active")
    )

    total_energy = sum(b.current_energy_used for b in buildings)

    empire_status = EmpireStatus.get_or_none(EmpireStatus.empire == empire)
    if empire_status:
        total_energy += empire_status.extraction_energy

    return total_energy


def render_progress_bar_emoji(progress: float, total: float, bar_length: int = 10) -> str:
    percent = max(0, min(progress / total if total else 0, 1))
    filled = int(round(bar_length * percent))
    bar = "🟩" * filled + "⬛" * (bar_length - filled)
    return f"{bar} {int(percent * 100)}%"


def render_progress_bar(progress: float, total: float, bar_length: int = 10) -> str:
    """
    Возвращает строку прогресс-бара вида: [██████░░░░░░] 60%

    :param progress: Текущее значение прогресса
    :param total: Общее значение прогресса
    :param bar_length: Длина прогресс-бара (количество блоков)
    :return: Строка с прогресс-баром
    """
    if total == 0:
        return "[░" * bar_length + f"] 0%"

    percent = max(0, min(progress / total, 1))
    filled_length = int(round(bar_length * percent))
    bar = "█" * filled_length + "░" * (bar_length - filled_length)
    percent_text = int(percent * 100)

    return f"[{bar}] {percent_text}%"


def get_energy_value(building: EmpireBuildings) -> int:
    """
    Возвращает значение энергии, соответствующее текущему уровню здания.
    """
    energy_data = building.current_energy_used
    if isinstance(energy_data, dict):
        return energy_data.get(str(building.level)) or energy_data.get(building.level) or 0
    return 0


def get_total_energy_usage_and_generation(empire: Empire):
    buildings = EmpireBuildings.select().where(
        (EmpireBuildings.empire == empire) &
        ((EmpireBuildings.status == "completed") | (EmpireBuildings.status == "producing") | (EmpireBuildings.status == "idle"))
    )
    used = sum(get_energy_value(b) for b in buildings if get_energy_value(b) < 0)
    produced = sum(get_energy_value(b) for b in buildings if get_energy_value(b) > 0)

    empire_status = EmpireStatus.get_or_none(EmpireStatus.empire == empire)
    if empire_status:
        produced += empire_status.extraction_energy

    return abs(used), produced


def render_energy_status(empire: Empire) -> str:
    buildings = EmpireBuildings.select().where(
        (EmpireBuildings.empire == empire) &
        ((EmpireBuildings.status == "completed") | (EmpireBuildings.status == "producing") | (EmpireBuildings.status == "idle"))
    )

    total_consumption = sum(get_energy_value(b) for b in buildings if get_energy_value(b) < 0)
    total_generation = sum(get_energy_value(b) for b in buildings if get_energy_value(b) > 0)

    empire_status = EmpireStatus.get_or_none(EmpireStatus.empire == empire)
    if empire_status:
        total_generation += empire_status.extraction_energy

    consumption_abs = abs(total_consumption)

    if total_generation >= consumption_abs:
        icon = "🟢"
    elif total_generation >= 0.8 * consumption_abs:
        icon = "🟡"
    else:
        icon = "🔴"

    return f"⚡ Энергия: {consumption_abs} / {total_generation} {icon}"




def get_today_lootbox():
    """
    Возвращает текущий ежедневный стандартный лутбокс.
    """
    return DailyLootbox.select().order_by(DailyLootbox.id.desc()).first()


def get_today_lootlucky():
    """
    Возвращает текущий ежедневный 'удачный' лутбокс.
    """
    return DailyLootLucky.select().order_by(DailyLootLucky.id.desc()).first()


def can_claim_lootbox(empire):
    """
    Проверяет, может ли империя получить лутбокс.
    Возвращает False, если хотя бы один из лутбоксов уже получен.
    """
    return not (empire.has_lootbox or empire.has_lootbox_lucky)


def format_lootbox_content(box, title):
    parts = [f"{title}"]
    resources = {
        "🌲 Лес": box.wood,
        "🏅 Золото": box.gold
    }

    for name, value in resources.items():
        if value > 0:
            parts.append(f"{name}: <b>{value}</b>")

    if hasattr(box, 'item') and box.item:
        parts.append(f"🎁 Предмет: <b>{box.item.name}</b> (уровень {box.item.level})")

    return "\n".join(parts)


def generate_daily_lootboxes():
    Empire.update(has_lootbox=None, has_lootbox_lucky=None).execute()

    DailyLootbox.delete().execute()
    DailyLootLucky.delete().execute()

    all_items = list(Items.select().where(Items.source == "lootbox"))


    lootbox_data = {
        "wood": random.randint(50, 300),
        "gold": random.randint(20, 200)
    }
    DailyLootbox.create(**lootbox_data)


    item_lucky = random.choice(all_items)
    lootlucky_data = {
        "wood": random.randint(20, 30),
        "gold": random.randint(10, 20),
        "oil": random.randint(5, 7),
        "diamond": random.randint(1, 2),
        "item": item_lucky
    }
    DailyLootLucky.create(**lootlucky_data)


def add_loot_to_empire_from_box(empire, lootbox):

    res, _ = EmpireResource.get_or_create(empire=empire)


    res.wood += lootbox.wood
    res.gold += lootbox.gold
    res.save()


def pick_random_lucky_item():
    """
    Возвращает случайную награду из строки меню удачи.
    Ресурсы учитываются только если они > 0.
    """
    loot = DailyLootLucky.get_or_none()
    if not loot:
        return None

    choices = []


    if loot.wood > 0:
        choices.append(("wood", loot.wood))
    if loot.gold > 0:
        choices.append(("gold", loot.gold))
    if loot.oil > 0:
        choices.append(("oil", loot.oil))
    if loot.diamond > 0:
        choices.append(("diamond", loot.diamond))


    choices.append(("item", loot.item))

    return random.choice(choices)


def add_lootlucky_to_empire_from_box(empire, item=None, resource_name=None, amount=0):
    res, _ = EmpireResource.get_or_create(empire=empire)

    if item and isinstance(item, Items):

        EmpireItems.get_or_create(empire=empire, item=item)
    elif resource_name in ("wood", "gold", "oil", "diamond"):

        current_value = getattr(res, resource_name, 0)
        setattr(res, resource_name, current_value + amount)

    res.save()


    empire.has_lootbox_lucky = DailyLootLucky.get()
    empire.save()


def get_all_busters():
    return list(Busters.select())


def get_active_buster_ids(empire):
    return {
        eb.buster.buster_id
        for eb in EmpireBusters.select().where(EmpireBusters.empire == empire)
    }


def get_buster_by_id(buster_id):
    return Busters.get_or_none(Busters.buster_id == buster_id)


def deduct_balance(userdata: UserData, amount: int):
    if userdata.balance < amount:
        raise ValueError("Недостаточно средств.")
    userdata.balance -= amount
    userdata.save()


def apply_buster_to_empire(empire, buster: Busters):
    now = datetime.now()
    end_time = now + timedelta(seconds=buster.base_action_time)
    EmpireBusters.create(
        empire=empire,
        buster=buster,
        start_date=now,
        end_time=end_time
    )


def cleanup_expired_busters():
    now = datetime.now()
    expired = EmpireBusters.delete().where(EmpireBusters.end_time < now)
    deleted_count = expired.execute()
    if deleted_count > 0:
        print(f"[{now}] Удалено {deleted_count} истёкших бустеров.")


def get_units_army(empire):
    try:
        resource = EmpireResource.get(EmpireResource.empire == empire)
        return resource.units_army
    except EmpireResource.DoesNotExist:
        return 0


def get_units_spy(empire):
    try:
        resource = EmpireResource.get(EmpireResource.empire == empire)
        return resource.units_spy
    except EmpireResource.DoesNotExist:
        return 0


def get_units_counterspy(empire):
    try:
        resource = EmpireResource.get(EmpireResource.empire == empire)
        return resource.units_counterspy
    except EmpireResource.DoesNotExist:
        return 0


def get_units_exploration(empire):
    try:
        resource = EmpireResource.get(EmpireResource.empire == empire)
        return resource.units_exploration
    except EmpireResource.DoesNotExist:
        return 0


def has_completed_barracks(empire):
    return EmpireBuildings.select().join(Buildings).where(
        (EmpireBuildings.empire == empire) &
        (EmpireBuildings.status.in_(["completed", "producing", "idle"])) &
        (Buildings.name == "barracks")
    ).exists()


def has_completed_spy_center(empire):
    return EmpireBuildings.select().join(Buildings).where(
        (EmpireBuildings.empire == empire) &
        (EmpireBuildings.status.in_(["completed", "producing", "idle"])) &
        (Buildings.name == "spy_center")
    ).exists()


def has_completed_conspy_center(empire):
    return EmpireBuildings.select().join(Buildings).where(
        (EmpireBuildings.empire == empire) &
        (EmpireBuildings.status.in_(["completed", "producing", "idle"])) &
        (Buildings.name == "conspy_center")
    ).exists()


def has_completed_exp_corpus(empire):
    return EmpireBuildings.select().join(Buildings).where(
        (EmpireBuildings.empire == empire) &
        (EmpireBuildings.status.in_(["completed", "producing", "idle"])) &
        (Buildings.name == "exp_corpus")
    ).exists()


def is_research_completed(empire, research_name: str) -> bool:
    try:
        research = Research.get(Research.name == research_name)
        return EmpireResearch.select().where(
            (EmpireResearch.empire == empire) &
            (EmpireResearch.research == research) &
            (EmpireResearch.status == "completed")
        ).exists()
    except Research.DoesNotExist:
        return False


def perform_market_transaction(empire, action: str, resource_id: int, quantity: int) -> tuple[bool, str]:
    """
    Обрабатывает сделку на рынке: покупка или продажа ресурса.

    :param empire: объект империи
    :param action: "buy" или "sell"
    :param resource_id: ID ресурса
    :param quantity: количество
    :return: (успех, сообщение для пользователя)
    """
    from models import MarketRate, Resource, EmpireResource
    resource = Resource.get_by_id(resource_id)
    rate = MarketRate.get(MarketRate.resource == resource)
    empire_resources = EmpireResource.get(EmpireResource.empire == empire)
    resource_name = resource.name.lower()

    if action == "buy":
        total_price = rate.buy_price * quantity
        if empire_resources.gold < total_price:
            return False, "❌ Недостаточно золота!"
        empire_resources.gold -= total_price
        setattr(empire_resources, resource_name, getattr(empire_resources, resource_name) + quantity)
        action_text = f"Вы купили {quantity} {resource.name} за {total_price} золота."

    elif action == "sell":
        if getattr(empire_resources, resource_name) < quantity:
            return False, "❌ Недостаточно ресурсов для продажи!"
        total_price = rate.sell_price * quantity
        empire_resources.gold += total_price
        setattr(empire_resources, resource_name, getattr(empire_resources, resource_name) - quantity)
        action_text = f"Вы продали {quantity} {resource.name} за {total_price} золота."

    else:
        return False, "❌ Неверное действие!"

    empire_resources.save()


    process_empire_action(empire, "trade", {
        "quantity": quantity,
        "xp_per_unit": 0.35
    })

    return True, f"✅ {action_text}\n💰 Ваш новый баланс: {empire_resources.gold} золота"


def cancel_mission_by_id(empire, mission):
    if not mission:
        return None, "Миссия не найдена."

    if mission.status != "pending":
        return None, "Миссия уже завершена или отменена."


    update_mission_progress(mission)

    now = datetime.now()
    remaining_seconds = max(mission.total_points - mission.progress, 0) / get_mission_speed_modifiers(empire)

    if remaining_seconds < 300:
        return None, "Миссию нельзя отменить — осталось меньше 5 минут до завершения."


    update_resources(empire, resource_name="units_army", value=mission.units_sent)


    mission.status = "cancelled"
    mission.mission_end = now
    mission.save()

    write_news(f"Империя {empire.name} отменила миссию «{mission.mission_type.name}»")

    return True, f"Миссия «{mission.mission_type.name}» успешно отменена."


def cancel_research_for_empire(empire: Empire, research_id: int) -> str:
    try:
        research = Research.get_or_none(Research.id == research_id)
        if not research:
            return "❌ Технология не найдена."

        er = EmpireResearch.get_or_none(
            (EmpireResearch.empire == empire) &
            (EmpireResearch.research == research) &
            (EmpireResearch.status == "pending")
        )

        if not er:
            return "❌ Исследование не найдено или уже завершено."

        er.delete_instance()

        return f"❌ Исследование «{research.name}» было отменено."
    except Exception as e:
        return f"❌ Ошибка при отмене исследования: {e}"


def get_empire_items_list(empire: Empire) -> list[Items]:
    return [ei.item for ei in EmpireItems.select().where(EmpireItems.empire == empire).join(Items)]














def get_active_empire_busters(empire):
    now = datetime.now()
    return (EmpireBusters
            .select(EmpireBusters, Busters)
            .join(Busters)
            .where((EmpireBusters.empire == empire) & (EmpireBusters.end_time > now)))

def get_completed_empire_researches(empire):
    return (EmpireResearch
            .select(EmpireResearch, Research)
            .join(Research)
            .where((EmpireResearch.empire == empire) & (EmpireResearch.status == "done")))

def get_empire_items(empire):
    return (EmpireItems
            .select(EmpireItems, Items)
            .join(Items)
            .where(EmpireItems.empire == empire))


def get_current_season() -> Season | None:
    """Возвращает текущий активный сезон (если есть)."""
    now = datetime.now()
    return (
        Season.select()
        .where((Season.start_date <= now) & (Season.end_date >= now))
        .first()
    )


def get_active_event() -> GameEvents | None:
    """Возвращает текущее активное событие (если есть)."""
    now = datetime.now()
    return (
        GameEvents.select()
        .where(
            (GameEvents.is_active == True) &
            (GameEvents.start_time <= now) &
            (GameEvents.end_time >= now)
        )
        .first()
    )


def get_empire_rank(empire):
    query = (Empire
             .select(Empire)
             .order_by(Empire.rating_points.desc()))

    for position, ranked_empire in enumerate(query, 1):
        if ranked_empire.id == empire.id:
            return position

    return None
