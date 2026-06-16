from handlers import (
    add_season
)
from datetime import datetime

def init_seasons():
    add_season(
        name="season_prosperity",
        end_date=datetime(2025, 8, 31, 0, 0),
        theme_description="",
        rewards="Алмазы: 500 ед. Предмет: Клинок души дракона 5 ур. +45% к атаке.",
        start_date=datetime(2025, 6, 1, 0, 0)
    )








