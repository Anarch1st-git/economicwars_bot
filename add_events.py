from seasons_events import event_templates_data
from handlers import create_events

def init_events():
    season_name = "season_prosperity"
    create_events(season_name, event_templates_data)
