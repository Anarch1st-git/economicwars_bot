from models import (
    Empire,
    EmpireResource
)
import time
from datetime import datetime




RESOURCE_LIMIT = {
    "wood": 100,
    "gold": 100,
    "oil": 100,
    "diamond": 100,
    "energy": 100
}


RESOURCE_REPLENISH = {
    "wood": 5000,
    "gold": 5000,
    "oil": 5000,
    "diamond": 5000,
    "energy": 5000
}

def replenish_resources():
    """ Проверяет все империи и выдает ресурсы тем, у кого их меньше лимита. """
    while True:

        empires_to_update = EmpireResource.select().where(
            (EmpireResource.wood < RESOURCE_LIMIT["wood"]) |
            (EmpireResource.gold < RESOURCE_LIMIT["gold"]) |
            (EmpireResource.oil < RESOURCE_LIMIT["oil"]) |
            (EmpireResource.diamond < RESOURCE_LIMIT["diamond"]) |
            (EmpireResource.energy < RESOURCE_LIMIT["energy"])
        )


        for empire_res in empires_to_update:
            updates = {}

            for resource, limit in RESOURCE_LIMIT.items():
                if getattr(empire_res, resource) < limit:
                    updates[resource] = getattr(empire_res, resource) + RESOURCE_REPLENISH[resource]


            if updates:
                EmpireResource.update(**updates).where(EmpireResource.id == empire_res.id).execute()


        print(f"{datetime.now()} Выданы ресурсы всем империям")
        time.sleep(1800)


replenish_resources()
