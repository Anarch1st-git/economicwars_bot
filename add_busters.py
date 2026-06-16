from handlers import (
    add_busters
)

def init_busters():

    add_busters(
        name="time_attack_50",
        description="time_attack_50_description",
        cost=250,
        category="time_attack",
        value=-0.5,
        base_action_time=3600
    )


    add_busters(
        name="safe_exp_units_50",
        description="safe_exp_units_50_description",
        cost=500,
        category="safety_exp_units",
        value=-0.5,
        base_action_time=3600
    )


    add_busters(
        name="exploration_find_50",
        description="exploration_find_50_description",
        cost=750,
        category="explore_find",
        value=0.5,
        base_action_time=3600
    )


    add_busters(
        name="build_time_50",
        description="build_time_50_description",
        cost=400,
        category="build_time",
        value=-0.5,
        base_action_time=10800
    )
