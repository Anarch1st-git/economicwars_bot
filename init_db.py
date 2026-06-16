from db import (
    initialize_db
)
from models import (
        GameGlobalSettings,
        Resource,
        RatingLayer,
        Research,
        Buildings,
        Items,
        Mission,
        MarketRate
    )
from datetime import datetime




def game_settings():
    GameGlobalSettings.create(key="gold_upkeep_per_unit", value=1.2)





def static_items():

    Items.create(name="item_veteran_sword",level=1,category="attack",value=0.05, source="game")
    Items.create(name="item_hunter_bow",level=1,category="attack",value=0.07, source="game")
    Items.create(name="item_battle_axe",level=1,category="attack",value=0.09, source="game")


    Items.create(name="item_knight_sabre",level=2,category="attack",value=0.12, source="game")
    Items.create(name="item_crossbow_with_sharpened_arrows",level=2,category="attack",value=0.15, source="game")
    Items.create(name="item_breakthrough_shield",level=2,category="attack",value=0.17, source="game")


    Items.create(name="item_winner_s_blade",level=3,category="attack",value=0.2, source="game")
    Items.create(name="item_destruction_catapult",level=3,category="attack",value=0.23, source="game")
    Items.create(name="item_army_mace",level=3,category="attack",value=0.25, source="game")


    Items.create(name="item_battle_magic_wand",level=4,category="attack",value=0.28, source="game")
    Items.create(name="item_army_ballista",level=4,category="attack",value=0.3, source="game")
    Items.create(name="item_diamond_claw",level=4,category="attack",value=0.32, source="game")


    Items.create(name="item_excalibur",level=5,category="attack",value=0.35, source="game")
    Items.create(name="item_phoenix_fire_bow",level=5,category="attack",value=0.38, source="game")
    Items.create(name="item_blazing_battle_mace",level=5,category="attack",value=0.4, source="game")


    Items.create(name="item_dragon_soul_blade", level=5, category="attack", value=0.45, source="game")
    Items.create(name="item_hellfire_crossbow", level=5, category="attack", value=0.47, source="game")
    Items.create(name="item_wrath_of_the_ancients", level=5, category="attack", value=0.5, source="game")


    Items.create(name="item_ranger_s_shield",level=1,category="defence",value=0.03, source="game")
    Items.create(name="item_leather_armor",level=1,category="defence",value=0.05, source="game")
    Items.create(name="item_thorn_barrier",level=1,category="defence",value=0.07, source="game")


    Items.create(name="item_chainmail_armor",level=2,category="defence",value=0.1, source="game")
    Items.create(name="item_stone_wall",level=2,category="defence",value=0.12, source="game")
    Items.create(name="item_magical_barrier",level=2,category="defence",value=0.15, source="game")


    Items.create(name="item_guard_s_plates",level=3,category="defence",value=0.18, source="game")
    Items.create(name="item_protective_amulet",level=3,category="defence",value=0.2, source="game")
    Items.create(name="item_sapphire_bastion",level=3,category="defence",value=0.22, source="game")


    Items.create(name="item_obsidian_shield",level=4,category="defence",value=0.25, source="game")
    Items.create(name="item_protection_cloak",level=4,category="defence",value=0.28, source="game")
    Items.create(name="item_titan_fortress",level=4,category="defence",value=0.3, source="game")


    Items.create(name="item_adamantite_armor",level=5,category="defence",value=0.35, source="game")
    Items.create(name="item_heavenly_guardian_cloak",level=5,category="defence",value=0.38, source="game")
    Items.create(name="item_arcane_shield_of_time",level=5,category="defence",value=0.4, source="game")


    Items.create(name="item_guardian_dragon_armor", level=5, category="defence", value=0.45, source="game")
    Items.create(name="item_celestial_barrier", level=5, category="defence", value=0.47, source="game")
    Items.create(name="item_divine_fortress", level=5, category="defence", value=0.5, source="game")


    Items.create(name="item_scouts_watch",level=1,category="time",value=-0.02, source="game")
    Items.create(name="item_swift_boots",level=1,category="time",value=-0.04, source="game")
    Items.create(name="item_camouflage_cloak",level=1,category="time",value=-0.06, source="game")


    Items.create(name="item_master_s_sand_clock",level=2,category="time",value=-0.08, source="game")
    Items.create(name="item_speed_elixir",level=2,category="time",value=-0.1, source="game")
    Items.create(name="item_amulet_of_swiftness",level=2,category="time",value=-0.12, source="game")


    Items.create(name="item_whirlwind_boots",level=3,category="time",value=-0.15, source="game")
    Items.create(name="item_wind_ring",level=3,category="time",value=-0.18, source="game")
    Items.create(name="item_flying_crossbow",level=3,category="time",value=-0.2, source="game")


    Items.create(name="item_time_lighthouse",level=4,category="time",value=-0.22, source="game")
    Items.create(name="item_dominion_watch",level=4,category="time",value=-0.25, source="game")
    Items.create(name="item_time_sand",level=4,category="time",value=-0.28, source="game")


    Items.create(name="item_acceleration_artifact",level=5,category="time",value=-0.3, source="game")
    Items.create(name="item_fog_mantle",level=5,category="time",value=-0.33, source="game")
    Items.create(name="item_phoenix_wings",level=5,category="time",value=-0.35, source="game")


    Items.create(name="item_time_devourer", level=5, category="time", value=-0.4, source="game")
    Items.create(name="item_infinity_clock", level=5, category="time", value=-0.43, source="game")
    Items.create(name="item_temporal_core", level=5, category="time", value=-0.45, source="game")


    Items.create(name="item_silent_boots",level=1,category="espionage",value=0.03, source="game")
    Items.create(name="item_scouts_mask",level=1,category="espionage",value=0.05, source="game")
    Items.create(name="item_dark_cloak",level=1,category="espionage",value=0.07, source="game")


    Items.create(name="item_invisible_dagger",level=2,category="espionage",value=0.1, source="game")
    Items.create(name="item_light_scout_armor",level=2,category="espionage",value=0.13, source="game")
    Items.create(name="item_concealment_amulet",level=2,category="espionage",value=0.15, source="game")


    Items.create(name="item_dexterity_gloves",level=3,category="espionage",value=0.18, source="game")
    Items.create(name="item_stealth_potion",level=3,category="espionage",value=0.2, source="game")
    Items.create(name="item_shadow_hood",level=3,category="espionage",value=0.23, source="game")


    Items.create(name="item_invisibility_bracelet",level=4,category="espionage",value=0.26, source="game")
    Items.create(name="item_silence_ring",level=4,category="espionage",value=0.29, source="game")
    Items.create(name="item_predator_s_manticape",level=4,category="espionage",value=0.32, source="game")


    Items.create(name="item_shadow_claw",level=4,category="espionage",value=0.35, source="game")
    Items.create(name="item_absolute_invisibility_shawl",level=4,category="espionage",value=0.38, source="game")
    Items.create(name="item_invisible_world_artifact",level=4,category="espionage",value=0.4, source="game")


    Items.create(name="item_dark_mirror", level=5, category="espionage", value=0.45, source="game")
    Items.create(name="item_void_suit", level=5, category="espionage", value=0.47, source="game")
    Items.create(name="item_shadow_dimension_artifact", level=5, category="espionage", value=0.5, source="game")


    Items.create(name="item_protective_amulet",level=1,category="antiespionage",value=0.03, source="game")
    Items.create(name="item_mirror_of_truth",level=1,category="antiespionage",value=0.05, source="game")
    Items.create(name="item_protection_amulet",level=1,category="antiespionage",value=0.07, source="game")


    Items.create(name="item_light_crystal",level=2,category="antiespionage",value=0.1, source="game")
    Items.create(name="item_anti_spying_armor",level=2,category="antiespionage",value=0.13, source="game")
    Items.create(name="item_guard_ring",level=2,category="antiespionage",value=0.15, source="game")


    Items.create(name="item_crusher_shield",level=3,category="antiespionage",value=0.18, source="game")
    Items.create(name="item_mind_s_eye",level=3,category="antiespionage",value=0.2, source="game")
    Items.create(name="item_revealer_s_mask",level=3,category="antiespionage",value=0.22, source="game")


    Items.create(name="item_purifying_light",level=4,category="antiespionage",value=0.25, source="game")
    Items.create(name="item_seal_of_truth",level=4,category="antiespionage",value=0.28, source="game")
    Items.create(name="item_protection_lighthouse",level=4,category="antiespionage",value=0.3, source="game")


    Items.create(name="item_key_of_truth",level=5,category="antiespionage",value=0.33, source="game")
    Items.create(name="item_anti_spying_sphere",level=5,category="antiespionage",value=0.36, source="game")
    Items.create(name="item_revelation_artifact",level=5,category="antiespionage",value=0.4, source="game")


    Items.create(name="item_truth_seeker", level=5, category="antiespionage", value=0.45, source="game")
    Items.create(name="item_eye_of_judgement", level=5, category="antiespionage", value=0.47, source="game")
    Items.create(name="item_divine_revelation", level=5, category="antiespionage", value=0.5, source="game")


    Items.create(name="item_scout_s_compass",level=1,category="explore",value=0.03, source="game")
    Items.create(name="item_seekers_loupe",level=1,category="explore",value=0.05, source="game")
    Items.create(name="item_light_helmet",level=1,category="explore",value=0.07, source="game")


    Items.create(name="item_adventure_map",level=2,category="explore",value=0.1, source="game")
    Items.create(name="item_explorer_s_boots",level=2,category="explore",value=0.13, source="game")
    Items.create(name="item_guide_stone",level=2,category="explore",value=0.15, source="game")


    Items.create(name="item_far_sighted_glasses",level=3,category="explore",value=0.18, source="game")
    Items.create(name="item_magic_binoculars",level=3,category="explore",value=0.2, source="game")
    Items.create(name="item_clairvoyance_sphere",level=3,category="explore",value=0.23, source="game")


    Items.create(name="item_orientation_crystal",level=4,category="explore",value=0.26, source="game")
    Items.create(name="item_observer_s_mantle",level=4,category="explore",value=0.29, source="game")
    Items.create(name="item_truth_seeker_s_feather",level=4,category="explore",value=0.32, source="game")


    Items.create(name="item_tracker_s_heart",level=5,category="explore",value=0.35, source="game")
    Items.create(name="item_observation_wand",level=5,category="explore",value=0.38, source="game")
    Items.create(name="item_omniscience_artifact",level=5,category="explore",value=0.4, source="game")


    Items.create(name="item_seeker_s_instinct", level=5, category="explore", value=0.45, source="game")
    Items.create(name="item_omnivision_goggles", level=5, category="explore", value=0.47, source="game")
    Items.create(name="item_universal_explorer", level=5, category="explore", value=0.5, source="game")


    Items.create(name="item_leather_protection_gloves", level=1, category="safety", value=-0.03, source="game")
    Items.create(name="item_basic_first_aid_kit", level=1, category="safety", value=-0.05, source="game")
    Items.create(name="item_sturdy_boots", level=1, category="safety", value=-0.07, source="game")


    Items.create(name="item_thermal_cloak", level=2, category="safety", value=-0.1, source="game")
    Items.create(name="item_herbal_medicine_bag", level=2, category="safety", value=-0.13, source="game")
    Items.create(name="item_guiding_talisman", level=2, category="safety", value=-0.15, source="game")


    Items.create(name="item_dragonhide_armor", level=3, category="safety", value=-0.18, source="game")
    Items.create(name="item_protective_barrier_totem", level=3, category="safety", value=-0.2, source="game")
    Items.create(name="item_life_preserver_charm", level=3, category="safety", value=-0.23, source="game")


    Items.create(name="item_resurrection_scroll", level=4, category="safety", value=-0.26, source="game")
    Items.create(name="item_watcher_amulet", level=4, category="safety", value=-0.29, source="game")
    Items.create(name="item_guardian_cloak", level=4, category="safety", value=-0.32, source="game")


    Items.create(name="item_luck_crystal", level=5, category="safety", value=-0.35, source="game")
    Items.create(name="item_phantom_shield", level=5, category="safety", value=-0.38, source="game")
    Items.create(name="item_eternal_protection_core", level=5, category="safety", value=-0.4, source="game")


    Items.create(name="item_fate_bender_talisman", level=5, category="safety", value=-0.45, source="game")
    Items.create(name="item_soul_anchor", level=5, category="safety", value=-0.47, source="game")
    Items.create(name="item_divine_intervention_artifact", level=5, category="safety", value=-0.5, source="game")


    Items.create(name="item_woodcutter_s_axe",level=1,category="extraction_forest",value=0.05, source="game")
    Items.create(name="item_forest_backpack",level=1,category="extraction_forest",value=0.07, source="game")
    Items.create(name="item_forest_warrior_s_boots",level=1,category="extraction_forest",value=0.09, source="game")


    Items.create(name="item_master_s_saw",level=2,category="extraction_forest",value=0.12, source="game")
    Items.create(name="item_lumberjack_belt",level=2,category="extraction_forest",value=0.15, source="game")
    Items.create(name="item_ranger_s_cloak",level=2,category="extraction_forest",value=0.17, source="game")


    Items.create(name="item_forest_hammer",level=3,category="extraction_forest",value=0.20, source="game")
    Items.create(name="item_nature_axe",level=3,category="extraction_forest",value=0.23, source="game")
    Items.create(name="item_luck_spells",level=3,category="extraction_forest",value=0.25, source="game")


    Items.create(name="item_growth_spell",level=4,category="extraction_forest",value=0.28, source="game")
    Items.create(name="item_tree_amulet",level=4,category="extraction_forest",value=0.3, source="game")
    Items.create(name="item_wood_carving_tool",level=4,category="extraction_forest",value=0.32, source="game")


    Items.create(name="item_ent_s_strength",level=5,category="extraction_forest",value=0.35, source="game")
    Items.create(name="item_great_tree_staff",level=5,category="extraction_forest",value=0.38, source="game")
    Items.create(name="item_legendary_axe",level=5,category="extraction_forest",value=0.4, source="game")


    Items.create(name="item_heart_of_the_forest", level=5, category="extraction_forest", value=0.45, source="game")
    Items.create(name="item_druid_king_staff", level=5, category="extraction_forest", value=0.47, source="game")
    Items.create(name="item_forest_god_totem", level=5, category="extraction_forest", value=0.5, source="game")


    Items.create(name="item_copper_mace",level=1,category="extraction_gold",value=0.05, source="game")
    Items.create(name="item_light_driller",level=1,category="extraction_gold",value=0.07, source="game")
    Items.create(name="item_seeker_s_helmet",level=1,category="extraction_gold",value=0.09, source="game")


    Items.create(name="item_silver_pickaxe",level=2,category="extraction_gold",value=0.12, source="game")
    Items.create(name="item_gold_prospector_belt",level=2,category="extraction_gold",value=0.15, source="game")
    Items.create(name="item_dexterity_gloves",level=2,category="extraction_gold",value=0.17, source="game")


    Items.create(name="item_magnetic_amulet",level=3,category="extraction_gold",value=0.2, source="game")
    Items.create(name="item_golden_shovel",level=3,category="extraction_gold",value=0.23, source="game")
    Items.create(name="item_ore_amulet",level=3,category="extraction_gold",value=0.25, source="game")


    Items.create(name="item_gold_prospector_mantle",level=4,category="extraction_gold",value=0.28, source="game")
    Items.create(name="item_ore_seeker_artifact",level=4,category="extraction_gold",value=0.3, source="game")
    Items.create(name="item_wealth_resonator",level=4,category="extraction_gold",value=0.32, source="game")


    Items.create(name="item_goldstone_crystal",level=5,category="extraction_gold",value=0.35, source="game")
    Items.create(name="item_mace_of_majesty",level=5,category="extraction_gold",value=0.38, source="game")
    Items.create(name="item_golden_shield",level=5,category="extraction_gold",value=0.4, source="game")


    Items.create(name="item_golden_pharaoh_mask", level=5, category="extraction_gold", value=0.45, source="game")
    Items.create(name="item_king_midas_touch", level=5, category="extraction_gold", value=0.47, source="game")
    Items.create(name="item_endless_gold_vault", level=5, category="extraction_gold", value=0.5, source="game")


    Items.create(name="item_hand_pump",level=1,category="extraction_oil",value=0.05, source="game")
    Items.create(name="item_oil_canister",level=1,category="extraction_oil",value=0.07, source="game")
    Items.create(name="item_oilman_s_leather_jacket",level=1,category="extraction_oil",value=0.9, source="game")


    Items.create(name="item_upgraded_drilling_unit",level=2,category="extraction_oil",value=0.12, source="game")
    Items.create(name="item_resilience_boots",level=2,category="extraction_oil",value=0.15, source="game")
    Items.create(name="item_fortitude_gloves",level=2,category="extraction_oil",value=0.17, source="game")


    Items.create(name="item_oil_strike_talisman",level=3,category="extraction_oil",value=0.2, source="game")
    Items.create(name="item_oil_navigator",level=3,category="extraction_oil",value=0.23, source="game")
    Items.create(name="item_heavy_drilling_armor",level=3,category="extraction_oil",value=0.25, source="game")


    Items.create(name="item_magnet_tank",level=4,category="extraction_oil",value=0.28, source="game")
    Items.create(name="item_oil_baron_s_mantle",level=4,category="extraction_oil",value=0.3, source="game")
    Items.create(name="item_oil_magic_elixir",level=4,category="extraction_oil",value=0.32, source="game")


    Items.create(name="item_black_gold_artifact",level=5,category="extraction_oil",value=0.35, source="game")
    Items.create(name="item_oil_king_s_staff",level=5,category="extraction_oil",value=0.38, source="game")
    Items.create(name="item_oil_lord",level=5,category="extraction_oil",value=0.4, source="game")


    Items.create(name="item_oil_emperor_scepter", level=5, category="extraction_oil", value=0.45, source="game")
    Items.create(name="item_black_throne_artifact", level=5, category="extraction_oil", value=0.47, source="game")
    Items.create(name="item_infinite_reservoir", level=5, category="extraction_oil", value=0.5, source="game")


    Items.create(name="item_prospector_s_pick",level=1,category="extraction_diamond",value=0.05, source="game")
    Items.create(name="item_ruby_amulet",level=1,category="extraction_diamond",value=0.07, source="game")
    Items.create(name="item_jewel_spark_glasses",level=1,category="extraction_diamond",value=0.09, source="game")


    Items.create(name="item_miner_s_headlamp_helmet",level=2,category="extraction_diamond",value=0.12, source="game")
    Items.create(name="item_hardness_belt",level=2,category="extraction_diamond",value=0.15, source="game")
    Items.create(name="item_resilience_sapogi",level=2,category="extraction_diamond",value=0.17, source="game")


    Items.create(name="item_purity_gloves",level=3,category="extraction_diamond",value=0.2, source="game")
    Items.create(name="item_titanium_steel_shovel",level=3,category="extraction_diamond",value=0.23, source="game")
    Items.create(name="item_diamond_band",level=3,category="extraction_diamond",value=0.25, source="game")


    Items.create(name="item_diamond_seeker_sphere",level=4,category="extraction_diamond",value=0.28, source="game")
    Items.create(name="item_jewels_mantle",level=4,category="extraction_diamond",value=0.3, source="game")
    Items.create(name="item_crystal_amulet",level=4,category="extraction_diamond",value=0.32, source="game")


    Items.create(name="item_miner_s_star",level=5,category="extraction_diamond",value=0.35, source="game")
    Items.create(name="item_diamond_king_crown",level=5,category="extraction_diamond",value=0.38, source="game")
    Items.create(name="item_diamond_lord",level=5,category="extraction_diamond",value=0.40, source="game")


    Items.create(name="item_gem_heart", level=5, category="extraction_diamond", value=0.45, source="game")
    Items.create(name="item_diamond_god_eye", level=5, category="extraction_diamond", value=0.47, source="game")
    Items.create(name="item_miracle_diamond_core", level=5, category="extraction_diamond", value=0.5, source="game")


    Items.create(name="item_master_s_handbook", level=1, category="technology_research", value=0.05, source="game")
    Items.create(name="item_wisdom_glasses", level=1, category="technology_research", value=0.07, source="game")
    Items.create(name="item_tech_guide", level=1, category="technology_research", value=0.09, source="game")


    Items.create(name="item_sphere_of_knowledge", level=2, category="technology_research", value=0.12, source="game")
    Items.create(name="item_inventor_s_amulet", level=2, category="technology_research", value=0.15, source="game")
    Items.create(name="item_mind_stone", level=2, category="technology_research", value=0.17, source="game")


    Items.create(name="item_wise_book", level=3, category="technology_research", value=0.20, source="game")
    Items.create(name="item_scholar_s_staff", level=3, category="technology_research", value=0.23, source="game")
    Items.create(name="item_genius_blueprint", level=3, category="technology_research", value=0.25, source="game")


    Items.create(name="item_scholar_s_feather", level=4, category="technology_research", value=0.28, source="game")
    Items.create(name="item_idea_vessel", level=4, category="technology_research", value=0.30, source="game")
    Items.create(name="item_inventor_s_cloak", level=4, category="technology_research", value=0.32, source="game")


    Items.create(name="item_wisdom_elixir", level=5, category="technology_research", value=0.35, source="game")
    Items.create(name="item_knowledge_ring", level=5, category="technology_research", value=0.38, source="game")
    Items.create(name="item_enlightenment_artifact", level=5, category="technology_research", value=0.40, source="game")


    Items.create(name="item_genius_mind_crown", level=5, category="technology_research", value=0.45, source="game")
    Items.create(name="item_codex_of_creation", level=5, category="technology_research", value=0.47, source="game")
    Items.create(name="item_omniscient_relic", level=5, category="technology_research", value=0.5, source="game")


    Items.create(name="item_captain_s_banner", level=1, category="army_training", value=0.05, source="game")
    Items.create(name="item_recruit_s_boots", level=1, category="army_training", value=0.07, source="game")
    Items.create(name="item_courage_flask", level=1, category="army_training", value=0.09, source="game")


    Items.create(name="item_legionnaire_s_spiked_pauldrons", level=2, category="army_training", value=0.12, source="game")
    Items.create(name="item_battle_whistle", level=2, category="army_training", value=0.15, source="game")
    Items.create(name="item_endurance_cloak", level=2, category="army_training", value=0.17, source="game")


    Items.create(name="item_mentor_s_sword", level=3, category="army_training", value=0.20, source="game")
    Items.create(name="item_commander_s_drum", level=3, category="army_training", value=0.23, source="game")
    Items.create(name="item_strength_blade", level=3, category="army_training", value=0.25, source="game")


    Items.create(name="item_war_banner", level=4, category="army_training", value=0.28, source="game")
    Items.create(name="item_courage_armor", level=4, category="army_training", value=0.30, source="game")
    Items.create(name="item_might_gloves", level=4, category="army_training", value=0.32, source="game")


    Items.create(name="item_fighter_s_amulet", level=5, category="army_training", value=0.35, source="game")
    Items.create(name="item_victory_harbinger", level=5, category="army_training", value=0.38, source="game")
    Items.create(name="item_general_s_star", level=5, category="army_training", value=0.40, source="game")


    Items.create(name="item_legendary_commander_helm", level=5, category="army_training", value=0.45, source="game")
    Items.create(name="item_warrior_spirit_banner", level=5, category="army_training", value=0.47, source="game")
    Items.create(name="item_battle_god_mark", level=5, category="army_training", value=0.5, source="game")


    Items.create(name="item_scouts_mantle", level=1, category="spy_training", value=0.05, source="game")
    Items.create(name="item_shadow_bracelet", level=1, category="spy_training", value=0.07, source="game")
    Items.create(name="item_codebook", level=1, category="spy_training", value=0.09, source="game")


    Items.create(name="item_spy_mask", level=2, category="spy_training", value=0.12, source="game")
    Items.create(name="item_stealth_potion", level=2, category="spy_training", value=0.15, source="game")
    Items.create(name="item_silence_dagger", level=2, category="spy_training", value=0.17, source="game")


    Items.create(name="item_illusion_ring", level=3, category="spy_training", value=0.20, source="game")
    Items.create(name="item_hidden_strike_talisman", level=3, category="spy_training", value=0.23, source="game")
    Items.create(name="item_invisibility_cloak", level=3, category="spy_training", value=0.25, source="game")


    Items.create(name="item_inconspicuous_amulet", level=4, category="spy_training", value=0.28, source="game")
    Items.create(name="item_secret_motion_sphere", level=4, category="spy_training", value=0.30, source="game")
    Items.create(name="item_cunning_shadow", level=4, category="spy_training", value=0.32, source="game")


    Items.create(name="item_silence_sign", level=5, category="spy_training", value=0.35, source="game")
    Items.create(name="item_scout_s_staff", level=5, category="spy_training", value=0.38, source="game")
    Items.create(name="item_night_darkness_artifact", level=5, category="spy_training", value=0.40, source="game")


    Items.create(name="item_shadow_training_scroll", level=5, category="spy_training", value=0.45, source="game")
    Items.create(name="item_cloak_of_silence", level=5, category="spy_training", value=0.47, source="game")
    Items.create(name="item_void_mind_amulet", level=5, category="spy_training", value=0.5, source="game")


    Items.create(name="item_revealer_s_talisman", level=1, category="counter_spy_training", value=0.05, source="game")
    Items.create(name="item_sentinel_s_helmet", level=1, category="counter_spy_training", value=0.07, source="game")
    Items.create(name="item_truth_boots", level=1, category="counter_spy_training", value=0.09, source="game")


    Items.create(name="item_light_shield", level=2, category="counter_spy_training", value=0.12, source="game")
    Items.create(name="item_sensitivity_stone", level=2, category="counter_spy_training", value=0.15, source="game")
    Items.create(name="item_revelation_cloak", level=2, category="counter_spy_training", value=0.17, source="game")


    Items.create(name="item_true_sight_amulet", level=3, category="counter_spy_training", value=0.20, source="game")
    Items.create(name="item_defense_blade", level=3, category="counter_spy_training", value=0.23, source="game")
    Items.create(name="item_sentinel_s_sword", level=3, category="counter_spy_training", value=0.25, source="game")


    Items.create(name="item_eye_of_truth", level=4, category="counter_spy_training", value=0.28, source="game")
    Items.create(name="item_scouting_sphere", level=4, category="counter_spy_training", value=0.30, source="game")
    Items.create(name="item_security_armor", level=4, category="counter_spy_training", value=0.32, source="game")


    Items.create(name="item_divine_shield", level=5, category="counter_spy_training", value=0.35, source="game")
    Items.create(name="item_revelation_artifact", level=5, category="counter_spy_training", value=0.38, source="game")
    Items.create(name="item_protection_crystal", level=5, category="counter_spy_training", value=0.40, source="game")


    Items.create(name="item_mind_barrier_relic", level=5, category="counter_spy_training", value=0.45, source="game")
    Items.create(name="item_thought_cage_helm", level=5, category="counter_spy_training", value=0.47, source="game")
    Items.create(name="item_truth_guard_artifact", level=5, category="counter_spy_training", value=0.5, source="game")


    Items.create(name="item_light_map", level=1, category="exploration_preparation", value=0.05, source="game")
    Items.create(name="item_pathfinder_s_boots", level=1, category="exploration_preparation", value=0.07, source="game")
    Items.create(name="item_traveler_s_cloak", level=1, category="exploration_preparation", value=0.09, source="game")


    Items.create(name="item_explorer_s_loupe", level=2, category="exploration_preparation", value=0.12, source="game")
    Items.create(name="item_seeker_s_compass", level=2, category="exploration_preparation", value=0.15, source="game")
    Items.create(name="item_pathfinder_s_mask", level=2, category="exploration_preparation", value=0.17, source="game")


    Items.create(name="item_tracker_s_belt", level=3, category="exploration_preparation", value=0.20, source="game")
    Items.create(name="item_explorer_s_backpack", level=3, category="exploration_preparation", value=0.23, source="game")
    Items.create(name="item_intuition_elixir", level=3, category="exploration_preparation", value=0.25, source="game")


    Items.create(name="item_guide_staff", level=4, category="exploration_preparation", value=0.28, source="game")
    Items.create(name="item_trail_magnet", level=4, category="exploration_preparation", value=0.30, source="game")
    Items.create(name="item_walker_s_mantle", level=4, category="exploration_preparation", value=0.32, source="game")


    Items.create(name="item_greatest_navigator", level=5, category="exploration_preparation", value=0.35, source="game")
    Items.create(name="item_discovery_stone", level=5, category="exploration_preparation", value=0.38, source="game")
    Items.create(name="item_explorer_s_artifact", level=5, category="exploration_preparation", value=0.40, source="game")


    Items.create(name="item_star_path_map", level=5, category="exploration_preparation", value=0.45, source="game")
    Items.create(name="item_void_navigation_orb", level=5, category="exploration_preparation", value=0.47, source="game")
    Items.create(name="item_cosmic_explorer_mark", level=5, category="exploration_preparation", value=0.5, source="game")


    Items.create(name="item_builder_s_hammer", level=1, category="building_construction", value=0.05, source="game")
    Items.create(name="item_master_s_apron", level=1, category="building_construction", value=0.07, source="game")
    Items.create(name="item_tool_belt", level=1, category="building_construction", value=0.09, source="game")


    Items.create(name="item_carpenter_s_axe", level=2, category="building_construction", value=0.12, source="game")
    Items.create(name="item_mason_s_boots", level=2, category="building_construction", value=0.15, source="game")
    Items.create(name="item_construction_plan", level=2, category="building_construction", value=0.17, source="game")


    Items.create(name="item_foundation_stone", level=3, category="building_construction", value=0.20, source="game")
    Items.create(name="item_magic_brick", level=3, category="building_construction", value=0.23, source="game")
    Items.create(name="item_architect_s_armor", level=3, category="building_construction", value=0.25, source="game")


    Items.create(name="item_construction_power_scepter", level=4, category="building_construction", value=0.28, source="game")
    Items.create(name="item_density_artifact", level=4, category="building_construction", value=0.30, source="game")
    Items.create(name="item_protective_network", level=4, category="building_construction", value=0.32, source="game")


    Items.create(name="item_master_s_crystal", level=5, category="building_construction", value=0.35, source="game")
    Items.create(name="item_building_staff", level=5, category="building_construction", value=0.38, source="game")
    Items.create(name="item_architect_s_seal", level=5, category="building_construction", value=0.40, source="game")


    Items.create(name="item_infinity_toolkit", level=5, category="building_construction", value=0.45, source="game")
    Items.create(name="item_architect_god_eye", level=5, category="building_construction", value=0.47, source="game")
    Items.create(name="item_creation_sphere", level=5, category="building_construction", value=0.5, source="game")





def static_resources():
    Resource.create(name="wood")
    Resource.create(name="gold")
    Resource.create(name="oil")
    Resource.create(name="diamond")





def static_rating_layers():
    RatingLayer.create(
        name="borderlands",
        description="descr_borderlands",
        lab_level=1,
        artifact_level=1,
        min_rating_points=0,
        max_rating_points=999
    )

    RatingLayer.create(
        name="golden_valley",
        description="descr_golden_valley",
        lab_level=2,
        artifact_level=2,
        min_rating_points=1000,
        max_rating_points=1999
    )

    RatingLayer.create(
        name="black_wastelands",
        description="descr_black_wastelands",
        lab_level=3,
        artifact_level=3,
        min_rating_points=2000,
        max_rating_points=2999
    )

    RatingLayer.create(
        name="crystal_empire",
        description="descr_crystal_empire",
        lab_level=4,
        artifact_level=4,
        min_rating_points=3000,
        max_rating_points=3999
    )

    RatingLayer.create(
        name="sphere_stars",
        description="descr_sphere_stars",
        lab_level=5,
        artifact_level=5,
        min_rating_points=4000,
        max_rating_points=4999
    )





def static_mission():
    Mission.create(name="attack")
    Mission.create(name="espionage")
    Mission.create(name="exploration")
    Mission.create(name="attack_location")







def add_research_time_attack_speed_up():
    Research.create(
        name="tech_time_attack_speed_up",
        research_type="general",
        extracting_type="none",
        description="tech_time_attack_speed_up_descr",

        total_points=1000
    )



def add_research_time_espionage_speed_up():
    Research.create(
        name="tech_time_espionage_speed_up",
        research_type="general",
        extracting_type="none",
        description="tech_time_espionage_speed_up_descr",

        total_points=1000
    )



def add_research_time_exploration_speed_up():
    Research.create(
        name="tech_time_exploration_speed_up",
        research_type="general",
        extracting_type="none",
        description="tech_time_exploration_speed_up_descr",

        total_points=1000
    )



def add_research_attack_action_up():
    Research.create(
        name="tech_attack_action_up",
        research_type="general",
        extracting_type="none",
        description="tech_attack_action_up_descr",

        total_points=1500
    )



def add_research_defence_action_up():
    Research.create(
        name="tech_defence_action_up",
        research_type="general",
        extracting_type="none",
        description="tech_defence_action_up_descr",

        total_points=2000
    )



def add_research_espionage_action_up():
    Research.create(
        name="tech_espionage_action_up",
        research_type="general",
        extracting_type="none",
        description="tech_espionage_action_up_descr",

        total_points=3000
    )



def add_research_antiespionage_action_up():
    Research.create(
        name="tech_antiespionage_action_up",
        research_type="general",
        extracting_type="none",
        description="tech_antiespionage_action_up_descr",

        total_points=3000
    )



def add_research_explore_find_up():
    Research.create(
        name="tech_explore_find_up",
        research_type="general",
        extracting_type="none",
        description="tech_explore_find_up_descr",

        total_points=4000
    )



def add_research_safety_exp_units_up():
    Research.create(
        name="tech_safety_exp_units_up",
        research_type="general",
        extracting_type="none",
        description="tech_safety_exp_units_up_descr",

        total_points=5500
    )



def add_research_cartography():
    Research.create(
        name="tech_cartography",
        research_type="general",
        extracting_type="none",
        description="tech_cartography_descr",

        total_points=5
    )


def add_research_market():
    Research.create(
        name="tech_market",
        research_type="general",
        extracting_type="none",
        description="tech_market_descr",

        total_points=24
    )


def add_research_espionage():
    Research.create(
        name="tech_spy",
        research_type="general",
        extracting_type="none",
        description="tech_spy_descr",

        total_points=38
    )


def add_research_counterespionage():
    Research.create(
        name="tech_counter_spy",
        research_type="general",
        extracting_type="none",
        description="tech_counter_spy_descr",

        total_points=42
    )


def add_research_military():
    Research.create(
        name="tech_military",
        research_type="general",
        extracting_type="none",
        description="tech_military_descr",

        total_points=25
    )


def add_research_defender():
    Research.create(
        name="tech_defence",
        research_type="general",
        extracting_type="none",
        description="tech_defence_descr",

        total_points=38
    )




def add_research_tech_wood_lumber_improvement():
    Research.create(
        name="tech_wood_lumber_improvement",
        research_type="extracting",
        extracting_type="wood",
        description="tech_wood_lumber_improvement_descr",

        total_points=60
    )


def add_research_tech_wood_multilayer_pressing():
    Research.create(
        name="tech_wood_multilayer_pressing",
        research_type="extracting",
        extracting_type="wood",
        description="tech_wood_multilayer_pressing_descr",

        total_points=110
    )


def add_research_tech_wood_biodiesel_production():
    Research.create(
        name="tech_wood_biodiesel_production",
        research_type="extracting",
        extracting_type="wood",
        description="tech_wood_biodiesel_production_descr",

        total_points=146
    )


def add_research_tech_wood_rare_tree_breeding():
    Research.create(
        name="tech_wood_rare_tree_breeding",
        research_type="extracting",
        extracting_type="wood",
        description="tech_wood_rare_tree_breeding_descr",

        total_points=180
    )


def add_research_tech_wood_creation_forest_nurseries():
    Research.create(
        name="tech_wood_creation_forest_nurseries",
        research_type="extracting",
        extracting_type="wood",
        description="tech_wood_creation_forest_nurseries_descr",

        total_points=214
    )



def add_research_tech_gold_production_optimization():
    Research.create(
        name="tech_gold_production_optimization",
        research_type="extracting",
        extracting_type="gold",
        description="tech_gold_production_optimization_descr",

        total_points=80
    )


def add_research_tech_gold_electrolysis_purification():
    Research.create(
        name="tech_gold_electrolysis_purification",
        research_type="extracting",
        extracting_type="gold",
        description="tech_gold_electrolysis_purification_descr",

        total_points=116
    )


def add_research_tech_gold_automated_minting():
    Research.create(
        name="tech_gold_automated_minting",
        research_type="extracting",
        extracting_type="gold",
        description="tech_gold_automated_minting_descr",

        total_points=166
    )


def add_research_tech_gold_creation_reserves():
    Research.create(
        name="tech_gold_creation_reserves",
        research_type="extracting",
        extracting_type="gold",
        description="tech_gold_creation_reserves_descr",

        total_points=250
    )



def add_research_tech_production_gold_bars_for_trading():
    Research.create(
        name="tech_production_gold_bars_for_trading",
        research_type="extracting",
        extracting_type="diamond",
        description="tech_production_gold_bars_for_trading_descr",

        total_points=460
    )



def add_research_tech_oil_deep_drilling():
    Research.create(
        name="tech_oil_deep_drilling",
        research_type="extracting",
        extracting_type="oil",
        description="tech_oil_deep_drilling_descr",

        total_points=111
    )


def add_research_tech_oil_cracking_petroleum_products():
    Research.create(
        name="tech_oil_cracking_petroleum_products",
        research_type="extracting",
        extracting_type="oil",
        description="tech_oil_cracking_petroleum_products_descr",

        total_points=152
    )


def add_research_tech_oil_production_biodegradable_plastic():
    Research.create(
        name="tech_oil_production_biodegradable_plastic",
        research_type="extracting",
        extracting_type="oil",
        description="tech_oil_production_biodegradable_plastic_descr",

        total_points=191
    )


def add_research_tech_oil_production_synthetic_fibers():
    Research.create(
        name="tech_oil_production_synthetic_fibers",
        research_type="extracting",
        extracting_type="oil",
        description="tech_oil_production_synthetic_fibers_descr",

        total_points=220
    )


def add_research_tech_oil_development_new_polymers():
    Research.create(
        name="tech_oil_development_new_polymers",
        research_type="extracting",
        extracting_type="oil",
        description="tech_oil_development_new_polymers_descr",

        total_points=260
    )



def add_research_tech_diamond_deep_drilling_diamonds():
    Research.create(
        name="tech_diamond_deep_drilling_diamonds",
        research_type="extracting",
        extracting_type="diamond",
        description="tech_diamond_deep_drilling_diamonds_descr",

        total_points=151
    )


def add_research_tech_diamond_laser_cutting_diamonds():
    Research.create(
        name="tech_diamond_laser_cutting_diamonds",
        research_type="extracting",
        extracting_type="diamond",
        description="tech_diamond_laser_cutting_diamonds_descr",

        total_points=190
    )


def add_research_tech_diamond_computer_jewelry_design():
    Research.create(
        name="tech_diamond_computer_jewelry_design",
        research_type="extracting",
        extracting_type="diamond",
        description="tech_diamond_computer_jewelry_design_descr",

        total_points=230
    )


def add_research_tech_diamond_creation_synthetic_diamonds():
    Research.create(
        name="tech_diamond_creation_synthetic_diamonds",
        research_type="extracting",
        extracting_type="diamond",
        description="tech_diamond_creation_synthetic_diamonds_descr",

        total_points=265
    )


def add_research_tech_diamond_synthesis_high_quality():
    Research.create(
        name="tech_diamond_synthesis_high_quality",
        research_type="extracting",
        extracting_type="diamond",
        description="tech_diamond_synthesis_high_quality_descr",

        total_points=302
    )



def add_research_tech_energy_crystalline_solar_panels():
    Research.create(
        name="tech_energy_crystalline_solar_panels",
        research_type="extracting",
        extracting_type="energy",
        description="tech_energy_crystalline_solar_panels_descr",

        total_points=100
    )



def add_research_tech_energy_vertical_wind_turbines():
    Research.create(
        name="tech_energy_vertical_wind_turbines",
        research_type="extracting",
        extracting_type="energy",
        description="tech_energy_vertical_wind_turbines_descr",

        total_points=110
    )



def add_research_tech_energy_small_hydropower_technologies():
    Research.create(
        name="tech_energy_small_hydropower_technologies",
        research_type="extracting",
        extracting_type="energy",
        description="tech_energy_small_hydropower_technologies_descr",

        total_points=120
    )



def add_research_tech_energy_capturing_heat_magma():
    Research.create(
        name="tech_energy_capturing_heat_magma",
        research_type="extracting",
        extracting_type="energy",
        description="tech_energy_capturing_heat_magma_descr",

        total_points=130
    )



def add_research_tech_energy_electrolysis_water():
    Research.create(
        name="tech_energy_electrolysis_water",
        research_type="extracting",
        extracting_type="energy",
        description="tech_energy_electrolysis_water_descr",

        total_points=140
    )



def add_research_tech_energy_creation_smart_networks():
    Research.create(
        name="tech_energy_creation_smart_networks",
        research_type="extracting",
        extracting_type="energy",
        description="tech_energy_creation_smart_networks_descr",

        total_points=150
    )


def create_initial_research():
    add_research_time_attack_speed_up()
    add_research_time_espionage_speed_up()
    add_research_time_exploration_speed_up()
    add_research_attack_action_up()
    add_research_defence_action_up()
    add_research_espionage_action_up()
    add_research_antiespionage_action_up()
    add_research_explore_find_up()
    add_research_safety_exp_units_up()
    add_research_cartography()
    add_research_market()
    add_research_espionage()
    add_research_counterespionage()
    add_research_military()
    add_research_defender()
    add_research_tech_wood_lumber_improvement()
    add_research_tech_wood_multilayer_pressing()
    add_research_tech_wood_biodiesel_production()
    add_research_tech_wood_rare_tree_breeding()
    add_research_tech_wood_creation_forest_nurseries()
    add_research_tech_gold_production_optimization()
    add_research_tech_gold_electrolysis_purification()
    add_research_tech_gold_automated_minting()
    add_research_tech_gold_creation_reserves()
    add_research_tech_production_gold_bars_for_trading()
    add_research_tech_oil_deep_drilling()
    add_research_tech_oil_cracking_petroleum_products()
    add_research_tech_oil_production_biodegradable_plastic()
    add_research_tech_oil_production_synthetic_fibers()
    add_research_tech_oil_development_new_polymers()
    add_research_tech_diamond_deep_drilling_diamonds()
    add_research_tech_diamond_laser_cutting_diamonds()
    add_research_tech_diamond_computer_jewelry_design()
    add_research_tech_diamond_creation_synthetic_diamonds()
    add_research_tech_diamond_synthesis_high_quality()
    add_research_tech_energy_crystalline_solar_panels()
    add_research_tech_energy_vertical_wind_turbines()
    add_research_tech_energy_small_hydropower_technologies()
    add_research_tech_energy_capturing_heat_magma()
    add_research_tech_energy_electrolysis_water()
    add_research_tech_energy_creation_smart_networks()

    print("Research has been initialized.")







def add_building_exploration_corpus():
    Buildings.create(
        name="exp_corpus",
        building_type="social",
        energy_used={
            1: -25,
            2: -50,
            3: -100,
            4: -200,
            5: -400
        },
        base_production=60,
        upgrade_cost={
            1: {"wood": 800, "gold": 150},
            2: {"wood": 3200, "gold": 500},
            3: {"wood": 5500, "gold": 1150, "oil": 20},
            4: {"wood": 8000, "gold": 3200, "oil": 55, "diamond": 3},
            5: {"wood": 14000, "gold": 6000, "oil": 120, "diamond": 20}
        },
        max_level=5,
        base_max_production_capacity=60,

        base_construction_time=300,
        next_building=None,
        unlock_research=Research.get(Research.name == "tech_cartography")
    )


def add_building_market():
    Buildings.create(
        name="market",
        building_type="economic",
        energy_used={
            1: -30
        },
        base_production=0,
        upgrade_cost={
            1: {"wood": 1200, "gold": 520}
        },
        max_level=1,
        base_construction_time=480,
        next_building=None,
        unlock_research=Research.get(Research.name == "tech_market")
    )


def add_building_recon_center():
    Buildings.create(
        name="spy_center",
        building_type="military",
        energy_used={
            1: -50,
            2: -100,
            3: -165,
            4: -215,
            5: -340
        },
        base_production=10,
        upgrade_cost={
            1: {"wood": 1200, "gold": 800},
            2: {"wood": 4400, "gold": 1600},
            3: {"wood": 8000, "gold": 2800, "oil": 200},
            4: {"wood": 12000, "gold": 4000, "oil": 550},
            5: {"wood": 20000, "gold": 12000, "oil": 1000, "diamond": 50}
        },
        max_level=5,
        base_max_production_capacity=25,

        base_construction_time=1800,
        next_building=None,
        unlock_research=Research.get(Research.name == "tech_spy")
    )


def add_building_counterintelligence_center():
    Buildings.create(
        name="conspy_center",
        building_type="military",
        energy_used={
            1: -50,
            2: -100,
            3: -165,
            4: -215,
            5: -340
        },
        base_production=10,
        upgrade_cost={
            1: {"wood": 2200, "gold": 1100, "oil": 10},
            2: {"wood": 5100, "gold": 2600, "oil": 90},
            3: {"wood": 11000, "gold": 6000, "oil": 140},
            4: {"wood": 17000, "gold": 12000, "oil": 250, "diamond": 50},
            5: {"wood": 22000, "gold": 16000, "oil": 500, "diamond": 150}
        },
        max_level=5,
        base_max_production_capacity=30,

        base_construction_time=3600,
        next_building=None,
        unlock_research=Research.get(Research.name == "tech_counter_spy")
    )


def add_building_barracks():
    Buildings.create(
        name="barracks",
        building_type="military",
        energy_used={
            1: -50,
            2: -100,
            3: -165,
            4: -215,
            5: -340
        },
        base_production=30,
        upgrade_cost={
            1: {"wood": 900, "gold": 100},
            2: {"wood": 3000, "gold": 1000},
            3: {"wood": 9000, "gold": 3500, "oil": 600},
            4: {"wood": 21000, "gold": 13000, "oil": 2000, "diamond": 600},
            5: {"wood": 30000, "gold": 20000, "oil": 20000, "diamond": 1100}
        },
        max_level=5,
        base_max_production_capacity=100,

        base_construction_time=1200,
        next_building=None,
        unlock_research=Research.get(Research.name == "tech_military")
    )


def add_building_defender():
    Buildings.create(
        name="defender",
        building_type="military",
        energy_used={
            1: -300,
            2: -460,
            3: -690,
            4: -800,
            5: -1000
        },
        base_production=0,
        upgrade_cost={
            1: {"wood": 1500, "gold": 670, "oil": 30},
            2: {"wood": 3000, "gold": 1340, "oil": 60},
            3: {"wood": 6100, "gold": 3100, "oil": 100},
            4: {"wood": 13000, "gold": 7000, "oil": 300},
            5: {"wood": 26000, "gold": 14000, "oil": 700},
        },
        max_level=5,
        base_max_production_capacity=150,

        base_construction_time=3600,
        next_building=None,
        unlock_research=Research.get(Research.name == "tech_defence")
    )


def add_building_laboratories():
    Buildings.create(
        name="laboratory",
        building_type="social",
        energy_used={
            1: -15,
            2: -25,
            3: -50,
            4: -95,
            5: -130
        },
        base_production=60,
        upgrade_cost={
            1: {},
            2: {"wood": 1500, "gold": 900},
            3: {"wood": 3000, "gold": 1800},
            4: {"wood": 6000, "gold": 3600},
            5: {"wood": 12000, "gold": 7200}
        },
        max_level=5,
        base_construction_time=120,
        next_building=None,
        unlock_research=None
    )



def add_building_sawmill():
    Buildings.create(
        name="sawmill",
        building_type="economic:wood",
        energy_used={
            1: -63
        },
        base_production=300,
        upgrade_cost={1: {"gold": 350}},
        max_level=1,
        base_construction_time=270,
        next_building="woodworking_plant",
        unlock_research=Research.get(Research.name == "tech_wood_lumber_improvement")
    )


def add_building_woodworking_plant():
    Buildings.create(
        name="woodworking_plant",
        building_type="economic:wood",
        energy_used={
            1: -94
        },
        base_production=450,
        upgrade_cost={1: {"wood": 1200, "gold": 750}},
        max_level=1,
        base_construction_time=2160,
        next_building="biofuel_plant",
        unlock_research=Research.get(Research.name == "tech_wood_multilayer_pressing")
    )


def add_building_biofuel_plant():
    Buildings.create(
        name="biofuel_plant",
        building_type="economic:wood",
        energy_used={
            1: -137
        },
        base_production=780,
        upgrade_cost={1: {"wood": 5200, "gold": 1900, "oil": 80}},
        max_level=1,
        base_construction_time=3600,
        next_building="forest_reserve",
        unlock_research=Research.get(Research.name == "tech_wood_biodiesel_production")
    )



def add_building_forest_reserve():
    Buildings.create(
        name="forest_reserve",
        building_type="economic:wood",
        energy_used={
            1: -218
        },
        base_production=1100,
        upgrade_cost={1: {"wood": 12_000, "gold": 4_400, "oil": 120}},
        max_level=1,
        base_construction_time=7_200,
        next_building="forest_bio_center",
        unlock_research=Research.get(Research.name == "tech_wood_rare_tree_breeding")
    )



def add_building_forest_bio_center():
    Buildings.create(
        name="forest_bio_center",
        building_type="economic:wood",
        energy_used={
            1: -313
        },
        base_production=2000,
        upgrade_cost={1: {"wood": 15_000, "gold": 20_000, "oil": 500}},
        max_level=1,
        base_construction_time=7_200,
        next_building=None,
        unlock_research=Research.get(Research.name == "tech_wood_creation_forest_nurseries")
    )



def add_building_gold_mine():
    Buildings.create(
        name="gold_mine",
        building_type="economic:gold",
        energy_used={
            1: -71
        },
        base_production=60,
        upgrade_cost={1: {"wood": 1_200, "oil": 16}},
        max_level=1,
        base_construction_time=1_200,
        next_building="gold_process_plant",
        unlock_research=Research.get(Research.name == "tech_gold_production_optimization")
    )



def add_building_gold_process_plant():
    Buildings.create(
        name="gold_process_plant",
        building_type="economic:gold",
        energy_used={
            1: -102
        },
        base_production=150,
        upgrade_cost={1: {"wood": 8_200, "oil": 1_000}},
        max_level=1,
        base_construction_time=5_400,
        next_building="gold_mint",
        unlock_research=Research.get(Research.name == "tech_gold_electrolysis_purification")
    )



def add_building_gold_mint():
    Buildings.create(
        name="gold_mint",
        building_type="economic:gold",
        energy_used={
            1: -145
        },
        base_production=300,
        upgrade_cost={1: {"wood": 14_800, "gold": 2_000, "oil": 5_000}},
        max_level=1,
        base_construction_time=7_200,
        next_building="jewelry_workshop",
        unlock_research=Research.get(Research.name == "tech_gold_automated_minting")
    )



def add_building_jewelry_workshop():
    Buildings.create(
        name="jewelry_workshop",
        building_type="economic:gold",
        energy_used={
            1: -226
        },
        base_production=600,
        upgrade_cost={1: {"wood": 20_000, "gold": 6_000, "oil": 12_000}},
        max_level=1,
        base_construction_time=10_000,
        next_building="investment_center",
        unlock_research=Research.get(Research.name == "tech_gold_creation_reserves")
    )



def add_building_investment_center():
    Buildings.create(
        name="investment_center",
        building_type="economic:gold",
        energy_used={
            1: -321
        },
        base_production=990,
        upgrade_cost={1: {"wood": 60_000, "gold": 12_000, "oil": 24_000}},
        max_level=1,
        base_construction_time=20_000,
        next_building=None,
        unlock_research=Research.get(Research.name == "tech_production_gold_bars_for_trading")
    )



def add_building_oil_well():
    Buildings.create(
        name="oil_well",
        building_type="economic:oil",
        energy_used={
            1: -79
        },
        base_production=40,
        upgrade_cost={1: {"wood": 2_000, "gold": 4_000}},
        max_level=1,
        base_construction_time=3_600,
        next_building="oil_refinery",
        unlock_research=Research.get(Research.name == "tech_oil_deep_drilling")
    )



def add_building_oil_refinery():
    Buildings.create(
        name="oil_refinery",
        building_type="economic:oil",
        energy_used={
            1: -110
        },
        base_production=100,
        upgrade_cost={1: {"wood": 20_000, "gold": 20_000, "diamond": 300}},
        max_level=1,
        base_construction_time=7_200,
        next_building="plastic_factory",
        unlock_research=Research.get(Research.name == "tech_oil_cracking_petroleum_products")
    )



def add_building_plastic_factory():
    Buildings.create(
        name="plastic_factory",
        building_type="economic:oil",
        energy_used={
            1: -153
        },
        base_production=180,
        upgrade_cost={1: {"wood": 35_000, "gold": 25_000, "diamond": 650}},
        max_level=1,
        base_construction_time=21_600,
        next_building="chemical_plant",
        unlock_research=Research.get(Research.name == "tech_oil_production_biodegradable_plastic")
    )



def add_building_chemical_plant():
    Buildings.create(
        name="chemical_plant",
        building_type="economic:oil",
        energy_used={
            1: -234
        },
        base_production=220,
        upgrade_cost={1: {"wood": 40_000, "gold": 40_000, "diamond": 800}},
        max_level=1,
        base_construction_time=43_200,
        next_building="petrochemical_center",
        unlock_research=Research.get(Research.name == "tech_oil_production_synthetic_fibers")
    )



def add_building_petrochemical_center():
    Buildings.create(
        name="petrochemical_center",
        building_type="economic:oil",
        energy_used={
            1: -329
        },
        base_production=300,
        upgrade_cost={1: {"wood": 80_000, "gold": 80_000, "diamond": 1200}},
        max_level=1,
        base_construction_time=86_400,
        next_building=None,
        unlock_research=Research.get(Research.name == "tech_oil_development_new_polymers")
    )



def add_building_diamond_quarry():
    Buildings.create(
        name="diamond_quarry",
        building_type="economic:diamond",
        energy_used={
            1: -87
        },
        base_production=11,
        upgrade_cost={1: {"wood": 10_000, "gold": 10_000, "oil": 1_000}},
        max_level=1,
        base_construction_time=3_600,
        next_building="cutting_center",
        unlock_research=Research.get(Research.name == "tech_diamond_deep_drilling_diamonds")
    )



def add_building_cutting_center():
    Buildings.create(
        name="cutting_center",
        building_type="economic:diamond",
        energy_used={
            1: -118
        },
        base_production=24,
        upgrade_cost={1: {"wood": 45_100, "gold": 24_000, "oil": 2_500}},
        max_level=1,
        base_construction_time=12_600,
        next_building="jewelry_house",
        unlock_research=Research.get(Research.name == "tech_diamond_laser_cutting_diamonds")
    )



def add_building_jewelry_house():
    Buildings.create(
        name="jewelry_house",
        building_type="economic:diamond",
        energy_used={
            1: -161
        },
        base_production=48,
        upgrade_cost={1: {"wood": 90_000, "gold": 60_000, "oil": 10_000}},
        max_level=1,
        base_construction_time=24_000,
        next_building="innovation_center",
        unlock_research=Research.get(Research.name == "tech_diamond_computer_jewelry_design")
    )



def add_building_innovation_center():
    Buildings.create(
        name="innovation_center",
        building_type="economic:diamond",
        energy_used={
            1: -242
        },
        base_production=90,
        upgrade_cost={1: {"wood": 130_000, "gold": 200_000, "oil": 60_000}},
        max_level=1,
        base_construction_time=48_000,
        next_building="diamond_research_institute",
        unlock_research=Research.get(Research.name == "tech_diamond_creation_synthetic_diamonds")
    )



def add_building_diamond_research_institute():
    Buildings.create(
        name="diamond_research_institute",
        building_type="economic:diamond",
        energy_used={
            1: -337
        },
        base_production=111,
        upgrade_cost={1: {"wood": 250_000, "gold": 400_000, "oil": 120_000, "diamond": 20_000}},
        max_level=1,
        base_construction_time=72_000,
        next_building=None,
        unlock_research=Research.get(Research.name == "tech_diamond_synthesis_high_quality")
    )



def add_building_solar_power_plant():
    Buildings.create(
        name="solar_power_plant",
        building_type="economic:energy",
        energy_used={
            1: 95
        },
        base_production=10,
        upgrade_cost={1: {"wood": 1_000, "gold": 500}},
        max_level=1,
        base_construction_time=300,
        next_building="wind_power_station",
        unlock_research=Research.get(Research.name == "tech_energy_crystalline_solar_panels")
    )



def add_building_wind_power_station():
    Buildings.create(
        name="wind_power_station",
        building_type="economic:energy",
        energy_used={
            1: 126
        },
        base_production=20,
        upgrade_cost={1: {"wood": 2500, "gold": 1500, "oil": 200}},
        max_level=1,
        base_construction_time=600,
        next_building="hydroelectric_station",
        unlock_research=Research.get(Research.name == "tech_energy_vertical_wind_turbines")
    )



def add_building_hydroelectric_station():
    Buildings.create(
        name="hydroelectric_station",
        building_type="economic:energy",
        energy_used={
            1: 169
        },
        base_production=30,
        upgrade_cost={1: {"wood": 5000, "gold": 3000, "oil": 400}},
        max_level=1,
        base_construction_time=1200,
        next_building="thermal_power_plant",
        unlock_research=Research.get(Research.name == "tech_energy_small_hydropower_technologies")
    )



def add_building_thermal_power_plant():
    Buildings.create(
        name="thermal_power_plant",
        building_type="economic:energy",
        energy_used={
            1: 250
        },
        base_production=40,
        upgrade_cost={1: {"wood": 10000, "gold": 6000, "oil": 800}},
        max_level=1,
        base_construction_time=2400,
        next_building="hydrogen_power_plant",
        unlock_research=Research.get(Research.name == "tech_energy_capturing_heat_magma")
    )



def add_building_hydrogen_power_plant():
    Buildings.create(
        name="hydrogen_power_plant",
        building_type="economic:energy",
        energy_used={
            1: 345
        },
        base_production=50,
        upgrade_cost={1: {"wood": 20000, "gold": 12000, "oil": 1600}},
        max_level=1,
        base_construction_time=4800,
        next_building="smart_energy_center",
        unlock_research=Research.get(Research.name == "tech_energy_electrolysis_water")
    )



def add_building_smart_energy_center():
    Buildings.create(
        name="smart_energy_center",
        building_type="economic:energy",
        energy_used={
            1: 353
        },
        base_production=60,
        upgrade_cost={1: {"wood": 50000, "gold": 30000, "oil": 10000}},
        max_level=1,
        base_construction_time=9600,
        next_building=None,
        unlock_research=Research.get(Research.name == "tech_energy_creation_smart_networks")
    )


def create_initial_buildings():
    add_building_exploration_corpus()
    add_building_market()
    add_building_recon_center()
    add_building_counterintelligence_center()
    add_building_barracks()
    add_building_defender()
    add_building_laboratories()
    add_building_sawmill()
    add_building_woodworking_plant()
    add_building_biofuel_plant()
    add_building_forest_reserve()
    add_building_forest_bio_center()
    add_building_gold_mine()
    add_building_gold_process_plant()
    add_building_gold_mint()
    add_building_jewelry_workshop()
    add_building_investment_center()
    add_building_oil_well()
    add_building_oil_refinery()
    add_building_plastic_factory()
    add_building_chemical_plant()
    add_building_petrochemical_center()
    add_building_diamond_quarry()
    add_building_cutting_center()
    add_building_jewelry_house()
    add_building_innovation_center()
    add_building_diamond_research_institute()
    add_building_solar_power_plant()
    add_building_wind_power_station()
    add_building_hydroelectric_station()
    add_building_thermal_power_plant()
    add_building_hydrogen_power_plant()
    add_building_smart_energy_center()

    print("Buildings has been initialized.")


def add_base_price_to_market_rate():
    resources = ["wood", "oil", "diamond"]
    base_prices = {"wood": 120, "oil": 200, "diamond": 500}

    for resource_name in resources:
        resource = Resource.get(Resource.name == resource_name)
        MarketRate.create(
            resource=resource,
            buy_price=base_prices[resource_name],
            sell_price=base_prices[resource_name] - 20,
            updated_at=datetime.now()
        )


def initialize_game_db():

    if not GameGlobalSettings.select().exists():
        game_settings()


    if not Items.select().exists():
        static_items()


    if not Resource.select().exists():
        static_resources()


    if not RatingLayer.select().exists():
        static_rating_layers()


    if not Mission.select().exists():
        static_mission()


    if not Research.select().exists():
        create_initial_research()


    if not Buildings.select().exists():
        create_initial_buildings()

    if not MarketRate.select().exists():
        add_base_price_to_market_rate()

    from add_busters import init_busters
    from add_lootboxes import init_lootboxes
    from add_seasons import init_seasons
    from add_events import init_events
    from add_quests import init_quests

    init_busters()
    init_lootboxes()
    init_seasons()
    init_events()
    init_quests()


initialize_db()
initialize_game_db()
