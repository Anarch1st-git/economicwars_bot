import os
from dotenv import load_dotenv
from peewee import PostgresqlDatabase

load_dotenv()

DB_CONFIG = {
    "database": os.getenv("DB_NAME", "ew_game_data"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", ""),
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", "5432")),
}

db = PostgresqlDatabase(**DB_CONFIG)


def initialize_db():
    """Подключение к базе данных и создание таблиц при первом запуске."""
    from models import (
        GameGlobalSettings,
        UserGameSettings,
        UserData,
        Busters,
        Resource,
        RatingLayer,
        RatingLayerCluster,
        Season,
        GameEventTemplate,
        SeasonEvent,
        GameEvents,
        Research,
        Buildings,
        DailyLootbox,
        DailyLootLucky,
        Empire,
        EmpireBusters,
        EmpireBuildings,
        EmpireResearch,
        EmpireResource,
        EmpireStatus,
        Items,
        EmpireItems,
        Mission,
        EmpireMission,
        EmpireLocations,
        EmpireMissionResult,
        MarketRate,
        Quests,
        EmpireQuests,
        News,
        LogEventUser,
        LogEventSystem,
    )

    db.connect(reuse_if_open=True)

    if not UserData.table_exists():
        db.create_tables(
            [
                GameGlobalSettings,
                UserGameSettings,
                UserData,
                Busters,
                Resource,
                RatingLayer,
                RatingLayerCluster,
                Season,
                GameEventTemplate,
                SeasonEvent,
                GameEvents,
                Research,
                Buildings,
                DailyLootbox,
                DailyLootLucky,
                Empire,
                EmpireBusters,
                EmpireBuildings,
                EmpireResearch,
                EmpireResource,
                EmpireStatus,
                Items,
                EmpireItems,
                Mission,
                EmpireMission,
                EmpireLocations,
                EmpireMissionResult,
                MarketRate,
                Quests,
                EmpireQuests,
                News,
                LogEventUser,
                LogEventSystem,
            ]
        )
