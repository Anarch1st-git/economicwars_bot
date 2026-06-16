import asyncio
import time
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from handlers import calculate_result_for_missions_exploration

async def run_exploration_missions():
    while True:
        calculate_result_for_missions_exploration()
        await asyncio.sleep(60)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    scheduler = AsyncIOScheduler()


    scheduler.add_job(calculate_result_for_missions_exploration, "interval", minutes=1)

    scheduler.start()

    try:
        loop.run_forever()
    except (KeyboardInterrupt, SystemExit):
        pass
