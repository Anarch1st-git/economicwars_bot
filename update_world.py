import schedule
import time
from datetime import datetime
from models import Empire, EmpireMission
from handlers import (
    update_mission_progress,
    empire_effects_loop,
    check_building_construction,
    check_research_progress,
    update_market_rates,
    update_resources_and_rating,
    update_unit_production,
    update_empire_resources,
    check_completed_quests,
    deactivate_expired_events,
    generate_season_event_with_pause,
    check_building_upgrade
)
from ai_bot_empire import update_bot_empires
from loop_runner import start_loop_in_background

def update_world():
    """Главная функция обновления мира, проходящая по всем империям и активным миссиям."""
    print(f"🔄 Обновление мира: {datetime.now()}")


    deactivate_expired_events()
    generate_season_event_with_pause()

    empires = Empire.select()
    missions = EmpireMission.select().where(EmpireMission.status == "pending")

    for empire in empires:





        check_building_construction(empire)
        check_building_upgrade(empire)
        check_research_progress(empire)
        update_resources_and_rating(empire)
        check_completed_quests(empire)




    update_unit_production()
    update_empire_resources()

    for mission in missions:
        update_mission_progress(mission)





    update_market_rates()



print("Запускаем фоновый event loop")
start_loop_in_background()


print("TASK_UPDATE_WORLD START")
while True:
    try:
        update_world()
    except Exception as e:
        print(f"Error in UPDATE_WORLD: {e}")
    time.sleep(1)
