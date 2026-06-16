


import random
from datetime import datetime, timedelta
from models import Empire
from handlers import (
    has_building_complete,
    create_building_in_empire,
    has_researched,
    start_research_for_empire,
    get_resource_count,
    start_train_units,
    is_building_under_construction,
    is_research_pending,
    is_unit_production_active,
    is_mission_active,
    start_mission_exploration,
    get_random_empire_from_cluster,
    start_mission_attack,
    start_mission_espionage,
    get_max_production_capacity_from_building
)


class BotEmpire:
    def __init__(self, empire: Empire):
        self.empire = empire
        self.memory = []
        self.rules = {
            "build:laboratory": self.rule_no_repeat
        }

    def rule_no_repeat(self, action_key: str) -> bool:
        return action_key not in self.memory

    def remember(self, action_key: str):
        self.memory.append(action_key)

    def build_structure(self, building_name: str):
        if is_building_under_construction(self.empire, building_name):
            print(f"🚧 Здание {building_name} уже строится.")
            return

        created, message = create_building_in_empire(self.empire, building_name)
        if not created:
            print(message)
            return
        print(f"🤖 Бот {self.empire.name} начал строить {building_name}")

    def research_technology(self, technology_name: str):
        if is_research_pending(self.empire, technology_name):
            print(f"🧪 Технология {technology_name} уже изучается.")
            return

        result = start_research_for_empire(self.empire, technology_name)
        print(result)


    def train_units(self, building_name: str):
        """Проверяет возможность тренировки юнитов и запускает процесс"""
        if is_unit_production_active(self.empire, building_name):
            print(f"⚙ Производство уже идет в {building_name}!")
            return

        max_production_capacity = get_max_production_capacity_from_building(self.empire, building_name)

        start_train_units(self.empire, building_name, max_production_capacity)
        print(f"🤖 Бот {self.empire.name} начал производство юнитов в {building_name}")

    def start_mission(self, mission_type: str, target = None):
        if is_mission_active(self.empire, mission_type):
            print(f"🚀 Миссия {mission_type} уже выполняется.")
            return

        if mission_type == "exploration":
            count_units_exp = get_resource_count(self.empire, "units_exploration")
            start_mission_exploration(self.empire, count_units_exp, self.empire.level)
            print(f"🤖 Бот {self.empire.name} отправил миссию {mission_type}")

        if mission_type == "attack":
            count_units_army = get_resource_count(self.empire, "units_army")
            mission, msg = start_mission_attack(self.empire, target, count_units_army)
            print(f"🤖 Бот {self.empire.name} отправил миссию {mission_type}")
            print(f"Информация о миссии:\nmission: {mission}, msg: {msg}")

        if mission_type == "spy":
            count_units_spy = get_resource_count(self.empire, "units_spy")
            mission, msg = start_mission_espionage(self.empire, target, count_units_spy)
            print(f"🤖 Бот {self.empire.name} отправил миссию {mission_type}")
            print(f"Информация о миссии:\nmission: {mission}, msg: {msg}")

    def find_targets_for_spy(self):
        return get_random_empire_from_cluster(self.empire).empire_id

    def find_targets_for_attack(self):
        return get_random_empire_from_cluster(self.empire).empire_id


    def execute_strategy(self):
        """Выполняет стратегию бота по шагам."""
        if not has_building_complete(self.empire, "laboratory"):
            print("Бот выбрал действие: Построить Лабораторию")
            self.build_structure("laboratory")

        if has_building_complete(self.empire, "laboratory") and not has_researched(self.empire, "tech_cartography"):
            print("Бот выбрал действие: Изучить технологию Картография")
            self.research_technology("tech_cartography")

        if not has_building_complete(self.empire, "exp_corpus") and has_researched(self.empire, "tech_cartography"):
            print("Бот выбрал действие: Построить Исследовательский корпус")
            self.build_structure("exp_corpus")

        if has_building_complete(self.empire, "exp_corpus") and get_resource_count(self.empire, "units_exploration") < 10:
            print("Бот выбрал действие: Тренировка юнитов исследователей")
            self.train_units("exp_corpus")

        if get_resource_count(self.empire, "units_exploration") > 0 and random.random() < 0.5:
            print("Бот выбрал действие: миссия исследования")
            self.start_mission("exploration")

        if has_building_complete(self.empire, "laboratory") and not has_researched(self.empire, "tech_military"):
            print("Бот выбрал действие: Изучить технологию Военное дело")
            self.research_technology("tech_military")

        if not has_building_complete(self.empire, "barracks") and has_researched(self.empire, "tech_military"):
            print("Бот выбрал действие: Построить Казармы")
            self.build_structure("barracks")

        if has_building_complete(self.empire, "laboratory") and not has_researched(self.empire, "tech_spy"):
            print("Бот выбрал действие: Изучить технологию Шпионаж")
            self.research_technology("tech_spy")

        if not has_building_complete(self.empire, "spy_center") and has_researched(self.empire, "tech_spy"):
            print("Бот выбрал действие: Построить Разведывательй центр")
            self.build_structure("spy_center")

        if has_building_complete(self.empire, "spy_center") and get_resource_count(self.empire, "units_spy") < 5:
            print("Бот выбрал действие: Тренировка юнитов разведки")
            self.train_units("spy_center")

        if get_resource_count(self.empire, "units_spy") > 5 and (target := self.find_targets_for_spy()):
            print("Бот выбрал действие: Поиск целей и шпионаж")
            self.start_mission("spy", target)

        if has_building_complete(self.empire, "barracks") and get_resource_count(self.empire, "units_army") < 10:
            print("Бот выбрал действие: Тренировка юнитов армии")
            self.train_units("barracks")

        if get_resource_count(self.empire, "units_army") > 5 and (target := self.find_targets_for_attack()):
            print("Бот выбрал действие: Поиск целей и атака")
            self.start_mission("attack", target)
















    def think(self):
        """Определяет, какое действие предпринять, возвращает ключ действия и саму функцию."""
        possible_actions = [
            ("build:laboratory", lambda: self.build_structure("laboratory")),
            ("research:cartography", lambda: self.research_technology("Картография")),
        ]

        for action_key, action_func in possible_actions:
            rule = self.rules.get(action_key, lambda x: True)
            if rule(action_key):
                return action_key, action_func

        return None, None



def update_bot_empires():
    bot_empires = Empire.select()
    for bot in bot_empires:
        bot_instance = BotEmpire(bot)
        bot_instance.execute_strategy()
