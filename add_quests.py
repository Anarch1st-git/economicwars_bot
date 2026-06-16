from handlers import (
    add_quest
)

def init_quests():
    quests = []

    quests.append(add_quest(
        name="build_lab_name_quest",
        description="build_lab_descr_quest",
        quest_type="main",
        objective="build",
        target="laboratory",
        amount=1,
        reward={"wood": 500, "gold": 100},
        is_repeatable=False
    ))

    quests.append(add_quest(
        name="research_cartography_name_quest",
        description="research_cartography_descr_quest",
        quest_type="main",
        objective="research",
        target="tech_cartography",
        amount=1,
        reward={"wood": 350, "gold": 100},
        is_repeatable=False
    ))

    quests.append(add_quest(
        name="build_exp_corpus_name_quest",
        description="build_exp_corpus_descr_quest",
        quest_type="main",
        objective="build",
        target="exp_corpus",
        amount=1,
        reward={"wood": 100, "gold": 50, "units_exploration": 5},
        is_repeatable=False
    ))

    quests.append(add_quest(
        name="mission_exploration_name_quest",
        description="mission_exploration_descr_quest",
        quest_type="main",
        objective="mission",
        target="exploration",
        amount=1,
        reward={"wood": 1000, "gold": 500, "oil": 3},
        is_repeatable=False
    ))

    for quest in quests:
        if quest:
            print(f"Квест '{quest.name}' успешно добавлен!")
