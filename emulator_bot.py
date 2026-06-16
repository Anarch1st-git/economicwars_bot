from db import (
    initialize_db
)
from handlers import (
    initialize_game_db,
    create_user,
    create_empire,
    get_user_by_chat_id,
    get_empire_by_user,
    get_completed_buildings_count,
    get_completed_research_count,
    get_items_count,
    get_total_resources,
    get_resource_count
)
import random



empire_names = ["Empire of the Phoenix", "Dragon Kingdom", "Star Legion", "Iron Dominion", "Silver Empire"]



def generate_chat_id():
    return ''.join(random.choices('0123456789', k=10))



def generate_empire_name():
    return random.choice(empire_names)


def start_handler(chat_id, username):
    create_user(chat_id, username)



def create_empire_handler(chat_id, empire_name):
    user = get_user_by_chat_id(chat_id)
    create_empire(user, empire_name)



def statistics_handler(chat_id):
    user = get_user_by_chat_id(chat_id)
    empire = get_empire_by_user(user)

    rating_layer = empire.rating_layer.name
    rating_points = empire.rating_points
    level = empire.level
    current_progress_scale = empire.current_progress_scale

    buildings_count = get_completed_buildings_count(empire.empire_id)
    technologies_count = get_completed_buildings_count(empire.empire_id)
    items_count = get_items_count(empire.empire_id)


    message = (
        f"🏰 <b>Имперский отчет</b> 🏰\n\n"
        f"📊 <b>Текущий рейтинг:</b>\n"
        f"🎖️ <i>{rating_layer}</i>\n"
        f"🔹 <b>До следующего слоя:</b> <i>{rating_points} / {0} очков</i>\n\n"
        f"🌟 <b>Уровень империи:</b>\n"
        f"⚔️ <i>{level} уровень</i>\n"
        f"🔹 <b>До следующего уровня:</b> <i>{current_progress_scale} / {0} опыта</i>\n\n"
        f"🏗️ <b>Развитие империи:</b>\n"
        f"🏘️ <b>Построек:</b> <i>{buildings_count} / {0}</i>\n"
        f"📜 <b>Технологий:</b> <i>{technologies_count} / {0}</i>\n"
        f"🎒 <b>Предметов:</b> <i>{items_count}</i>\n\n"
        f"🛡️ Продолжайте развивать вашу империю, чтобы достичь новых высот! 🚀"
    )

    print(message)


for _ in range(83):
    chat_id = generate_chat_id()
    empire_name = generate_empire_name()
    start_handler(chat_id, "username")
    create_empire_handler(chat_id, empire_name)
