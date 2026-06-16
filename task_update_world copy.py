import schedule
import time
import threading
from handlers import (
    calculate_result_for_missions_exploration,
    calculate_result_for_missions_attack,
    calculate_result_for_missions_attack_location,
    update_mission_progress,
    empire_effects_loop,
    check_building_construction,
    check_research_progress,
    update_market_rates,
    update_experience_based_on_resources
)


def run_threaded(job_func):
    thread = threading.Thread(target=job_func)
    thread.start()


schedule.every(1).seconds.do(lambda: run_threaded(calculate_result_for_missions_exploration))
schedule.every(1).seconds.do(lambda: run_threaded(calculate_result_for_missions_attack))
schedule.every(1).seconds.do(lambda: run_threaded(calculate_result_for_missions_attack_location))
schedule.every(1).seconds.do(lambda: run_threaded(update_mission_progress))
schedule.every(1).seconds.do(lambda: run_threaded(empire_effects_loop))
schedule.every(1).seconds.do(lambda: run_threaded(check_building_construction))
schedule.every(1).seconds.do(lambda: run_threaded(check_research_progress))
schedule.every(1).minute.do(lambda: run_threaded(update_market_rates))


print("TASK_UPDATE_WORLD START")
while True:
    print("UPDATE WORLD")
    schedule.run_pending()
    time.sleep(1)
