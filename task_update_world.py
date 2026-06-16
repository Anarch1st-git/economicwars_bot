import schedule
import time
from datetime import datetime
from models import Empire, EmpireMission
from handlers import (
    calculate_result_for_missions_exploration,
    calculate_result_for_missions_attack,
    calculate_result_for_missions_attack_location,
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
    generate_season_event_with_pause
)


def update_world():
    """Главная функция обновления мира"""
    print(f"🔄 Обновление мира: {datetime.now()}")



    deactivate_expired_events()
    generate_season_event_with_pause()

    empires = Empire.select()
    missions = EmpireMission.select().where(EmpireMission.status == "pending")

    for empire in empires:

        empire_effects_loop(empire)
        check_building_construction(empire)
        check_research_progress(empire)
        update_resources_and_rating(empire)
        check_completed_quests(empire)

    update_unit_production()
    update_empire_resources()

    for mission in missions:
        if mission.mission_end <= datetime.now():
            if mission.mission_type.name == "exploration":
                calculate_result_for_missions_exploration(mission)
            elif mission.mission_type.name == "attack":
                calculate_result_for_missions_attack(mission)
            elif mission.mission_type.name == "attack_location":
                calculate_result_for_missions_attack_location(mission)
            update_mission_progress(mission)


    update_market_rates()





schedule.every(1).seconds.do(update_world)

print("TASK_UPDATE_WORLD START")
while True:
    schedule.run_pending()
    time.sleep(1)
