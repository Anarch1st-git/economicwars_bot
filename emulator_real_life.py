import random
import time
import threading
from emulator_generate_data import (
    generate_unique_chat_id,
    generate_empire_name
)
from handlers import (
    get_user_by_chat_id,
    create_user,
    create_empire,
    assign_quest_to_empire
)

TIMEOUT_VALUE = 1
WEIGHT_PROBABILITY_REGISTRATION = 0.1
MAX_SIMULTANEOUS_REGISTRATIONS = 20

print("🔥 EMULATOR LIFE START")

def register_user():
    """Функция для регистрации одного пользователя (запускается в потоке)"""
    chat_id = generate_unique_chat_id()
    username = f"User_{str(chat_id)[-4:]}"
    empire_name = generate_empire_name()

    try:
        new_user, created = create_user(chat_id, username)
        if not created:
            print(f"❌ Пользователь {username} уже зарегистрирован!")
            return

        user = get_user_by_chat_id(chat_id)
        if not user:
            print(f"❌ Ошибка: Пользователь {username} не найден.")
            return

        empire = create_empire(user, empire_name)
        assign_quest_to_empire(empire, "build_lab_name_quest")
        print(f"✅ Империя {empire_name} создана для пользователя {username}!")

    except Exception as err:
        print(f"❌ Ошибка при регистрации: {err}")

while True:
    timeout = random.uniform(TIMEOUT_VALUE, TIMEOUT_VALUE + 1)
    print(f"# timeout: {timeout}")
    time.sleep(timeout)
    print("# update_life")

    if random.uniform(0, 1) > WEIGHT_PROBABILITY_REGISTRATION:
        print("! registration event")

        num_threads = 1
        threads = []

        for _ in range(num_threads):
            thread = threading.Thread(target=register_user)
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        print(f"🌍 {num_threads} регистраций завершено!")
