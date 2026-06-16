from datetime import datetime
from playhouse.postgres_ext import JSONField
from peewee import (
    Model,
    CharField,
    IntegerField,
    ForeignKeyField,
    DateTimeField,
    FloatField,
    BooleanField,
    PostgresqlDatabase,
    AutoField,
    TextField,
    BigIntegerField,
    DateField
)
from db import db


class BaseModel(Model):
    class Meta:
        database = db


class GameGlobalSettings(BaseModel):
    key = CharField(unique=True)
    value = FloatField()

    class Meta:
        db_table = 'game_global_settings'


class UserData(BaseModel):
    user_id = AutoField(primary_key=True)
    chat_id = BigIntegerField(unique=True)
    username = CharField(default="EW_User")

    subscription_status = BooleanField(default=False)
    subscription_start = DateTimeField(null=True)
    subscription_end = DateTimeField(null=True)
    created_at = DateTimeField(default=datetime.now)

    class Meta:
        db_table = 'userdata'


class UserGameSettings(BaseModel):
    user = ForeignKeyField(UserData)
    notification_status = CharField(default="all")

    class Meta:
        db_table = 'user_game_settings'


class Resource(BaseModel):
    resource_id = AutoField(primary_key=True)
    name = CharField()

    class Meta:
        db_table = 'resources'


class RatingLayer(BaseModel):
    layer_id = AutoField(primary_key=True)
    name = CharField()
    description = TextField()
    lab_level = IntegerField(default=1)
    artifact_level = IntegerField(default=1)
    min_rating_points = IntegerField()
    max_rating_points = IntegerField()

    class Meta:
        db_table = 'rating_layers'


class RatingLayerCluster(BaseModel):
    cluster_id = AutoField()
    layer = ForeignKeyField(RatingLayer, backref='clusters', on_delete='CASCADE')
    is_full = BooleanField(default=False)
    empire_count = IntegerField(default=0)

    class Meta:
        db_table = 'rating_layer_clusters'



class Season(BaseModel):
    season_id = AutoField(primary_key=True)
    name = CharField()
    theme_description = TextField(null=True)
    start_date = DateTimeField(default=datetime.now)
    end_date = DateTimeField()
    reward_description = TextField(null=True)
    top_players = JSONField(null=True)

    class Meta:
        db_table = 'seasons'


class GameEventTemplate(BaseModel):
    name = CharField()
    effect_type = CharField()
    target = CharField(null=True)
    value = FloatField()

    class Meta:
        db_table = 'game_event_templates'


class SeasonEvent(BaseModel):
    season = ForeignKeyField(Season, backref='season_events')
    template = ForeignKeyField(GameEventTemplate, backref='linked_seasons')

    class Meta:
        db_table = 'season_events'


class GameEvents(BaseModel):
    template = ForeignKeyField(GameEventTemplate, backref="instances")
    start_time = DateTimeField()
    end_time = DateTimeField()
    is_active = BooleanField(default=True)
    was_generated_by_system = BooleanField(default=False)

    class Meta:
        db_table = 'game_events'



class Research(BaseModel):
    name = CharField()
    research_type = CharField()
    extracting_type = CharField()
    description = TextField()
    total_points = IntegerField(default=1)

    class Meta:
        db_table = 'research'



class Buildings(BaseModel):
    name = CharField()
    building_type = CharField()
    energy_used = JSONField(null=True)
    base_production = IntegerField(default=0)
    upgrade_cost = JSONField(null=True)
    max_level = IntegerField(default=1)
    base_max_production_capacity = IntegerField(default=0)
    base_construction_time = IntegerField(default=0)
    next_building = CharField(null=True)
    unlock_research = ForeignKeyField(Research, null=True, backref='buildings')

    class Meta:
        db_table = 'buildings'



class Items(BaseModel):
    item_id = AutoField(primary_key=True)
    name = CharField()
    level = IntegerField(default=1)
    category = CharField()
    value = FloatField(default=0.0)
    cost = IntegerField(default=500)
    source = CharField(default="game")

    class Meta:
        db_table = 'items'



class DailyLootbox(BaseModel):
    wood = IntegerField(default=0)
    gold = IntegerField(default=0)

    class Meta:
        db_table = "daily_lootboxes"



class DailyLootLucky(BaseModel):
    wood = IntegerField(default=0)
    gold = IntegerField(default=0)
    oil = IntegerField(default=0)
    diamond = IntegerField(default=0)
    item = ForeignKeyField(Items)

    class Meta:
        db_table = "daily_loot_lucky"



class Empire(BaseModel):
    user = ForeignKeyField(UserData, backref='empire')
    empire_id = CharField(max_length=12, unique=True, null=False)
    name = CharField()
    rating_layer = ForeignKeyField(RatingLayer, backref='empires', on_delete='SET NULL', null=True)
    rating_points = IntegerField(default=0)
    ready_to_upgrade = BooleanField(default=False)
    cluster = ForeignKeyField(RatingLayerCluster, backref='empires', null=True)
    x_position = IntegerField(default=0)
    y_position = IntegerField(default=0)
    level = IntegerField(default=1)
    current_progress_scale = IntegerField(default=0)
    end_progress_scale = IntegerField(default=100)
    has_lootbox = ForeignKeyField(DailyLootbox, null=True)
    has_lootbox_lucky = ForeignKeyField(DailyLootLucky, null=True)
    created_at = DateTimeField(default=datetime.now)

    class Meta:
        db_table = 'empire'


class Busters(BaseModel):
    buster_id = AutoField(primary_key=True)
    name = CharField()
    description = TextField(null=True)
    cost = IntegerField(default=100)
    category = CharField()
    value = FloatField(default=0)
    base_action_time = IntegerField(default=60)

    class Meta:
        db_table = 'busters'


class EmpireBusters(BaseModel):
    empire = ForeignKeyField(Empire, backref='empires_busters')
    buster = ForeignKeyField(Busters)
    start_date = DateTimeField(default=datetime.now)
    end_time = DateTimeField(default=datetime.now)

    class Meta:
        db_table = 'empire_busters'



class EmpireBuildings(BaseModel):
    empire = ForeignKeyField(Empire, backref='common_buildings')
    building = ForeignKeyField(Buildings)
    level = IntegerField(default=1)
    current_energy_used = IntegerField(default=0)
    current_upgrade_cost = JSONField(null=True)
    next_production_time = DateTimeField(null=True)
    current_production_interval = IntegerField(default=0)
    current_production = IntegerField(default=0)
    current_max_production_capacity = IntegerField(default=0)
    units_to_hire = IntegerField(default=0)
    is_producing = BooleanField(default=False)
    produced_but_unhired = IntegerField(default=0)
    construction_start = DateTimeField(default=datetime.now)
    progress = FloatField(default=0.0)
    total_points = IntegerField()
    last_update = DateTimeField()
    status = CharField(default="pending")
    garrison_units = IntegerField(default=0)

    class Meta:
        db_table = 'empire_buildings'



class EmpireResearch(BaseModel):
    empire = ForeignKeyField(Empire, backref='researches')
    research = ForeignKeyField(Research)
    research_start = DateTimeField(default=datetime.now)
    progress = FloatField(default=0.0)
    status = CharField(default="pending")
    total_points = IntegerField(default=1)
    last_update = DateTimeField(default=datetime.now)

    class Meta:
        db_table = 'empire_researches'



class EmpireResource(BaseModel):
    empire = ForeignKeyField(Empire, backref='resources')
    wood = IntegerField(default=0)
    gold = IntegerField(default=0)
    oil = IntegerField(default=0)
    diamond = IntegerField(default=0)
    units_army = IntegerField(default=0)
    units_spy = IntegerField(default=0)
    units_counterspy = IntegerField(default=0)
    units_exploration = IntegerField(default=0)

    class Meta:
        db_table = 'empire_resources'



class EmpireStatus(BaseModel):
    empire = ForeignKeyField(Empire, backref='status', unique=True, on_delete='CASCADE')
    extraction_energy = IntegerField(default=0)
    garrison_units = IntegerField(default=0)
    gold_upkeep_per_hour = IntegerField(default=0)
    defense_bonus = IntegerField(default=0)
    units_army_capacity = IntegerField(default=10)
    units_exploration_cost = IntegerField(default=1)
    units_army_cost = IntegerField(default=2)
    units_spy_cost = IntegerField(default=3)
    units_counterspy_cost = IntegerField(default=3)
    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)

    class Meta:
        db_table = 'empire_status'



class EmpireItems(BaseModel):
    empire = ForeignKeyField(Empire, backref='resources')
    item = ForeignKeyField(Items)

    class Meta:
        db_table = 'empire_items'



class Mission(BaseModel):
    mission_id = AutoField()
    name = CharField()

    class Meta:
        db_table = 'missions'



class EmpireLocations(BaseModel):
    location_id = CharField(max_length=8, unique=True, null=False)
    name = CharField(null=False)
    empire = ForeignKeyField(Empire)
    wood = IntegerField(default=0)
    gold = IntegerField(default=0)
    oil = IntegerField(default=0)
    diamond = IntegerField(default=0)
    item = ForeignKeyField(Items, null=True)
    monsters = IntegerField(default=0)

    @property
    def item_name(self):
        return self.item.name if self.item else None

    class Meta:
        db_table = 'empire_locations'



class EmpireMission(BaseModel):
    mission_id = AutoField()
    empire = ForeignKeyField(Empire, backref='missions')
    mission_type = ForeignKeyField(Mission)
    target = ForeignKeyField(Empire, null=True)
    location = ForeignKeyField(EmpireLocations, null=True, on_delete='SET NULL')
    units_sent = IntegerField(default=0)
    mission_start = DateTimeField(default=datetime.now)
    progress = FloatField(default=0.0)
    total_points = IntegerField(default=3600)
    status = CharField(default="pending")
    last_update = DateTimeField(default=datetime.now)
    radius = IntegerField(default=0, null=True)

    class Meta:
        db_table = 'empire_missions'


class EmpireMissionResult(BaseModel):
    mission_result_id = AutoField()
    empire = ForeignKeyField(Empire)
    description = TextField(default="no_data")
    mission_id = CharField(unique=True)
    success = BooleanField(default=False)
    units_sent = IntegerField(default=0)
    target_units = IntegerField(default=0)
    units_lost = IntegerField(default=0)
    units_return = IntegerField(default=0)
    loot_wood = IntegerField(default=0)
    loot_gold = IntegerField(default=0)
    loot_oil = IntegerField(default=0)
    loot_diamond = IntegerField(default=0)
    loot_item = ForeignKeyField(Items, null=True)
    intel_data = JSONField(null=True)
    created_at = DateTimeField(default=datetime.now)

    class Meta:
        db_table = "empire_mission_results"


class MarketRate(BaseModel):
    resource = ForeignKeyField(Resource, backref='market_rates')
    buy_price = IntegerField(default=100)
    sell_price = IntegerField(default=90)
    updated_at = DateTimeField(default=datetime.now)

    class Meta:
        db_table = 'market_rates'


class Quests(BaseModel):
    name = CharField()
    description = TextField()
    quest_type = CharField()
    objective = CharField()
    target = CharField()
    amount = IntegerField(default=1)
    reward = JSONField()
    next_quest = ForeignKeyField("self", null=True, backref="previous_quest")
    is_repeatable = BooleanField(default=False)
    is_event = BooleanField(default=False)

    class Meta:
        db_table = 'quests'


class EmpireQuests(BaseModel):
    empire = ForeignKeyField(Empire, backref="quests")
    quest = ForeignKeyField(Quests, backref="empires")
    progress = IntegerField(default=0)
    completed = BooleanField(default=False)
    claimed = BooleanField(default=False)
    start_time = DateTimeField(default=datetime.now)
    end_time = DateTimeField(null=True)

    class Meta:
        db_table = "empire_quests"


class News(BaseModel):
    news_id = AutoField()
    date = DateTimeField(default=datetime.now)
    text = TextField(null=False)

    class Meta:
        db_table = "news"


class LogEventUser(BaseModel):
    log_event_user_id = AutoField()
    initiator = CharField(null=False)
    event_data = CharField(null=False)
    event_time = DateTimeField(default=datetime.now)

    class Meta:
        db_table = 'log_event_user'


class LogEventSystem(BaseModel):
    log_event_system_id = AutoField()
    event_data = CharField(null=False)
    event_time = DateTimeField(default=datetime.now)

    class Meta:
        db_table = 'log_event_system'
