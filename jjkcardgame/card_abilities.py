from typing import Dict, Any

class CardAbility:
    @staticmethod
    def apply_ability(card: Dict[str, Any], game_state: Dict[str, Any]) -> None:
        ability_map = {
            "Fushiguro Megumi": CardAbility.megumi_ability,
            "Akari Nitta": CardAbility.akari_ability,
            "Kiyotaka Ijichi": CardAbility.ijichi_ability,
            "Panda": CardAbility.panda_ability,
            "Shoko Ieiri": CardAbility.shoko_ability,
            "Kasumi Miwa": CardAbility.miwa_ability,
            "Rin Amai": CardAbility.amai_ability,
            "Toge Inumaki": CardAbility.inumaki_ability,
            "Kokichi Muta": CardAbility.muta_ability,
            "Tsumiki Fushiguro": CardAbility.tsumiki_ability,
            "Fumihiko Takaba": CardAbility.takaba_ability,
            "Kirara Hoshi": CardAbility.kirara_ability,
            "Momo Nishimiya": CardAbility.momo_ability,
            "Masamichi Yaga": CardAbility.yaga_ability,
            "Mai Zenin": CardAbility.mai_ability,
            "Maki Zenin": CardAbility.maki_ability,
            "Takuma Ino": CardAbility.ino_ability,
            "Yoshinobu Gakuganji": CardAbility.gakuganji_ability,
            "Haba": CardAbility.haba_ability,
            "Kinji Hakari": CardAbility.hakari_ability,
            "Suguru Geto": CardAbility.geto_ability,
            "Aoi Todo": CardAbility.todo_ability,
            "Mei Mei": CardAbility.mei_mei_ability,
            "Hana Kurusu": CardAbility.kurusu_ability,
            "Takako Uro": CardAbility.uro_ability,
            "Noritoshi Kamo": CardAbility.kamo_ability,
            "Naoya Zenin": CardAbility.naoya_ability,
            "Kento Nanami": CardAbility.nanami_ability,
            "Hiromi Higuruma": CardAbility.higuruma_ability,
            "Kenjaku": CardAbility.kenjaku_ability,
            "Hajime Kashimo": CardAbility.kashimo_ability,
            "Ryu Ishigori": CardAbility.ishigori_ability,
            "Master Tengen": CardAbility.tengen_ability,
            "Ryomen Sukuna": CardAbility.sukuna_ability,
            "Yuki Tsukumo": CardAbility.tsukumo_ability,
            "Ryu": CardAbility.ryu_ability,
            "Reggie": CardAbility.reggie_ability,
            "Dhruv": CardAbility.dhruv_ability,
            "Kurourushi": CardAbility.kurourushi_ability,
            "Charles": CardAbility.charles_ability,
            "Yaga": CardAbility.yaga_ability,
            "UI": CardAbility.ui_ability,
            "Brain": CardAbility.brain_ability,
            "Gojo Satoru": CardAbility.gojo_ability
        }
        
        if card['Name'] in ability_map:
            ability_map[card['Name']](card, game_state)

    @staticmethod
    def gojo_ability(card: Dict[str, Any], game_state: Dict[str, Any]) -> None:
        if "Limitless" in card.get('Effect', ''):
            game_state['damage_reduction'] = 0.5
        elif "The Honored One" in card.get('Variant', ''):
            game_state['damage_reduction'] = 0.5
            if game_state.get('solo_creature', False):
                card['ATK'] += 100
                card['DEF'] += 100
        elif "Toji Incident" in card.get('Variant', ''):
            game_state['one_time_revival'] = True
        elif "Shibuya Incident" in card.get('Variant', ''):
            game_state['damage_reduction'] = 0.5
        elif "Six Eyes Master" in card.get('Variant', ''):
            game_state['energy_cost_reduction'] = True
            game_state['can_see_weakness'] = True

    @staticmethod
    def sukuna_ability(card: Dict[str, Any], game_state: Dict[str, Any]) -> None:
        if "King of Curses" in card.get('Variant', ''):
            if game_state.get('overlaid_from_yuji_or_megumi', False):
                card['ATK'] += 100
                card['DEF'] += 100
        elif "Golden Era" in card.get('Variant', ''):
            game_state['damage_all_enemies'] = 100
        elif "Fuega" in card.get('Variant', ''):
            game_state['splash_damage'] = 150
        elif "Malevolent Shrine" in card.get('Variant', ''):
            game_state['domain_expansion'] = True
            game_state['guaranteed_hit'] = True

    @staticmethod
    def megumi_ability(card: Dict[str, Any], game_state: Dict[str, Any]) -> None:
        if "Child" in card.get('Variant', ''):
            if game_state.get('gojo_on_field', False):
                card['ATK'] += 50
                card['DEF'] += 50
        elif "Detention Center" in card.get('Variant', ''):
            game_state['can_summon'] = True
            game_state['summon_token'] = {'ATK': 100, 'DEF': 100}
        elif "Shibuya Arc" in card.get('Variant', ''):
            game_state['can_summon_elephant'] = True
            game_state['elephant_stats'] = {'ATK': 300, 'DEF': 250}
        elif "Mahoraga" in card.get('Variant', ''):
            game_state['adaptation'] = True
            game_state['permanent_stat_growth'] = True
            if game_state.get('was_attacked', False):
                card['DEF'] += 50
            if game_state.get('did_attack', False):
                card['ATK'] += 50

    @staticmethod
    def yuta_ability(card: Dict[str, Any], game_state: Dict[str, Any]) -> None:
        if "Bound by Rika" in card.get('Effect', ''):
            if game_state.get('rika_on_field', False):
                card['ATK'] += 100
                card['DEF'] += 100
        elif "Culling Games" in card.get('Variant', ''):
            game_state['can_summon_rika'] = True
        elif "Reverse Cursed" in card.get('Effect', ''):
            game_state['can_heal'] = True

    @staticmethod
    def hakari_ability(card: Dict[str, Any], game_state: Dict[str, Any]) -> None:
        if "Pachinko Bet" in card.get('Effect', ''):
            roll = game_state.get('dice_roll', 0)
            if roll >= 4:
                card['ATK'] += 100
                card['DEF'] += 100
        elif "Infinite Jackpot" in card.get('Variant', ''):
            if game_state.get('jackpot_mode', False):
                game_state['cannot_be_destroyed'] = True
        elif "Jackpot Loop" in card.get('Effect', ''):
            if game_state.get('dice_roll', 0) >= 5:
                game_state['jackpot_mode'] = True

    @staticmethod
    def todo_ability(card: Dict[str, Any], game_state: Dict[str, Any]) -> None:
        if "Tactical Genius" in card.get('Effect', ''):
            game_state['can_swap_positions'] = True
        elif "Best Friend Buff" in card.get('Effect', ''):
            if game_state.get('yuji_on_field', False):
                card['ATK'] += 100
        elif "Boogie Woogie Master" in card.get('Variant', ''):
            if game_state.get('yuji_on_field', False):
                game_state['can_combo_attack'] = True

    @staticmethod
    def panda_ability(card: Dict[str, Any], game_state: Dict[str, Any]) -> None:
        if "Beast Transformation" in card.get('Effect', ''):
            game_state['can_switch_cores'] = True
        elif "Triclops Mode" in card.get('Variant', ''):
            game_state['core_abilities'] = True

    @staticmethod
    def maki_ability(card: Dict[str, Any], game_state: Dict[str, Any]) -> None:
        if "Heavenly Restriction" in card.get('Variant', ''):
            game_state['ignore_def'] = True
            game_state['spell_immunity'] = True
        elif "Curse Tool Mastery" in card.get('Effect', ''):
            if game_state.get('has_curse_tool', False):
                card['ATK'] += 100
                game_state['ignore_def'] = True

    @staticmethod
    def kenjaku_ability(card: Dict[str, Any], game_state: Dict[str, Any]) -> None:
        if "Body Hopping" in card.get('Effect', ''):
            game_state['can_possess_enemy'] = True
        elif "Thousand Years of Planning" in card.get('Effect', ''):
            game_state['curse_manipulation'] = True
        elif "Master Schemer" in card.get('Variant', ''):
            game_state['can_steal_technique'] = True

    @staticmethod
    def inumaki_ability(card: Dict[str, Any], game_state: Dict[str, Any]) -> None:
        if "Cursed Speech: Stop" in card.get('Effect', ''):
            game_state['disable_enemy_abilities'] = True
        elif "Cursed Speech: Halt" in card.get('Effect', ''):
            game_state['can_prevent_attack'] = True

    @staticmethod
    def nanami_ability(card: Dict[str, Any], game_state: Dict[str, Any]) -> None:
        if "Ratio Calculation" in card.get('Effect', ''):
            game_state['ratio_bonus'] = True
        elif "Overtime Efficiency" in card.get('Effect', ''):
            game_state['can_attack_twice'] = True

    @staticmethod
    def uro_ability(card: Dict[str, Any], game_state: Dict[str, Any]) -> None:
        if "Sky Manipulation" in card.get('Effect', ''):
            game_state['reduce_melee_damage'] = 50
        elif "Spatial Distortion" in card.get('Effect', ''):
            game_state['can_move_enemy'] = True
        elif "Space Manipulator" in card.get('Variant', ''):
            game_state['all_enemies_lose_stats'] = {'ATK': 100, 'DEF': 100}

    @staticmethod
    def kashimo_ability(card: Dict[str, Any], game_state: Dict[str, Any]) -> None:
        if "Thunder God's Wrath" in card.get('Effect', ''):
            game_state['splash_damage'] = 100
        elif "Electromagnetic Charge" in card.get('Effect', ''):
            game_state['apply_shock'] = True
            game_state['shock_energy_cost'] = 1
        elif "Electric God" in card.get('Variant', ''):
            game_state['spell_bonus_damage'] = 50

    @staticmethod
    def geto_ability(card: Dict[str, Any], game_state: Dict[str, Any]) -> None:
        if "Cursed Army" in card.get('Effect', ''):
            if game_state.get('enemy_destroyed', False):
                game_state['summon_lesser_spirit'] = True
                game_state['spirit_stats'] = {'ATK': 150, 'DEF': 150}
        elif "The Ultimate Curse User" in card.get('Effect', ''):
            cursed_spirits = game_state.get('cursed_spirits', [])
            for spirit in cursed_spirits:
                spirit['ATK'] += 100
                spirit['DEF'] += 100
        elif "Shibuya Incident" in card.get('Variant', ''):
            game_state['can_summon_special_grade'] = True
            game_state['special_grade_stats'] = {'ATK': 400, 'DEF': 400}

    @staticmethod
    def akari_ability(card: Dict[str, Any], game_state: Dict[str, Any]) -> None:
        if "Jujutsu High Assistant Supervisor" in card.get('Variant', ''):
            if game_state.get('tokyo_jujutsu_high_count', 0) > 0:
                game_state['extra_draw'] = True
        elif "Kyoto Jujutsu High Principal" in card.get('Variant', ''):
            kyoto_creatures = game_state.get('kyoto_creatures', [])
            for creature in kyoto_creatures:
                creature['ATK'] += 50

    @staticmethod
    def ijichi_ability(card: Dict[str, Any], game_state: Dict[str, Any]) -> None:
        if "Tactical Support" in card.get('Effect', ''):
            game_state['ultimate_cost_reduction'] = True
        elif "Desperate Escape" in card.get('Effect', ''):
            game_state['one_time_survival'] = True
            if game_state.get('would_be_destroyed', False):
                card['DEF'] += 100

    @staticmethod
    def shoko_ability(card: Dict[str, Any], game_state: Dict[str, Any]) -> None:
        if "Medical Expertise" in card.get('Effect', ''):
            game_state['can_heal_ally'] = True
            game_state['heal_amount'] = 100
        elif "Reverse Cursed Energy Surge" in card.get('Effect', ''):
            game_state['heal_all_allies'] = 50

    @staticmethod
    def miwa_ability(card: Dict[str, Any], game_state: Dict[str, Any]) -> None:
        if "Sniper's Precision" in card.get('Effect', ''):
            game_state['can_attack_back_row'] = True
        elif "Dedicated Swordsmanship" in card.get('Effect', ''):
            if game_state.get('did_attack', False):
                card['ATK'] += 50
        elif "Quick Draw" in card.get('Effect', ''):
            if game_state.get('played_this_turn', False):
                game_state['bonus_damage'] = 50

    @staticmethod
    def amai_ability(card: Dict[str, Any], game_state: Dict[str, Any]) -> None:
        if "Survival Tactics" in card.get('Effect', ''):
            if game_state.get('ally_in_front', False):
                game_state['cannot_be_attacked'] = True
        elif "Survivor's Instinct" in card.get('Effect', ''):
            game_state['damage_reduction'] = 0.5
        elif "Aerial Maneuver" in card.get('Effect', ''):
            game_state['melee_damage_reduction'] = 0.5

    @staticmethod
    def muta_ability(card: Dict[str, Any], game_state: Dict[str, Any]) -> None:
        if "Remote Puppet Control" in card.get('Effect', ''):
            game_state['can_check_deck_top'] = True
        elif "Mode Change: Full Armor" in card.get('Effect', ''):
            game_state['energy_shield'] = 200
        elif "Ultimate Mechamaru Mode" in card.get('Variant', ''):
            game_state['artillery_mode'] = True
            game_state['bonus_damage'] = 100

    @staticmethod
    def tsumiki_ability(card: Dict[str, Any], game_state: Dict[str, Any]) -> None:
        if "Protective Instinct" in card.get('Effect', ''):
            game_state['can_redirect_attack'] = True
        elif "Awakened Flight" in card.get('Effect', ''):
            game_state['immune_to_melee'] = True
        elif "Reincarnated Sorcerer" in card.get('Variant', ''):
            game_state['flight_active'] = True

    @staticmethod
    def takaba_ability(card: Dict[str, Any], game_state: Dict[str, Any]) -> None:
        if "Comedic Timing" in card.get('Effect', ''):
            game_state['coin_flip_defense'] = True
        elif "Reality Warper" in card.get('Effect', ''):
            if game_state.get('solo_creature', False):
                game_state['damage_reduction'] = 0.5
        elif "Comedic Omnipotence" in card.get('Effect', ''):
            game_state['choose_effect'] = ['double_atk', 'negate_effects', 'heal_ally']

    @staticmethod
    def kirara_ability(card: Dict[str, Any], game_state: Dict[str, Any]) -> None:
        if "Celestial Attraction" in card.get('Effect', ''):
            game_state['can_lock_position'] = True
        elif "Love Connection" in card.get('Effect', ''):
            game_state['shared_damage'] = True
        elif "Space-Time Attraction" in card.get('Variant', ''):
            game_state['mark_enemy'] = True

    @staticmethod
    def momo_ability(card: Dict[str, Any], game_state: Dict[str, Any]) -> None:
        if "Aerial Combat" in card.get('Effect', ''):
            game_state['immune_to_melee'] = True
        elif "Tactical Aerial Support" in card.get('Effect', ''):
            game_state['can_buff_ally'] = True
            game_state['spell_immunity'] = True
        elif "Flying Broom User" in card.get('Variant', ''):
            game_state['can_push_back'] = True

    @staticmethod
    def yaga_ability(card: Dict[str, Any], game_state: Dict[str, Any]) -> None:
        if "Master Puppeteer" in card.get('Effect', ''):
            game_state['can_summon_corpse'] = True
            game_state['corpse_stats'] = {'ATK': 150, 'DEF': 150}
            game_state['corpse_duration'] = 2
        elif "Cursed Corpse" in card.get('Effect', ''):
            game_state['can_summon_puppet'] = True
            game_state['puppet_stats'] = {'ATK': 150, 'DEF': 150}
        elif "Ultimate Puppet" in card.get('Effect', ''):
            if game_state.get('puppet_count', 0) >= 3:
                game_state['puppet_boost'] = True
        elif "Principal's Authority" in card.get('Variant', ''):
            game_state['boost_all_puppets'] = {'ATK': 50, 'DEF': 50}

    @staticmethod
    def mai_ability(card: Dict[str, Any], game_state: Dict[str, Any]) -> None:
        if "Family Burden" in card.get('Effect', ''):
            if game_state.get('maki_on_field', False):
                card['ATK'] -= 50
                card['DEF'] -= 50
                game_state['ignore_def'] = True

    @staticmethod
    def ino_ability(card: Dict[str, Any], game_state: Dict[str, Any]) -> None:
        if "Junior Hero" in card.get('Effect', ''):
            if game_state.get('high_grade_on_field', False):
                card['ATK'] += 50

    @staticmethod
    def gakuganji_ability(card: Dict[str, Any], game_state: Dict[str, Any]) -> None:
        if "Strict Leadership" in card.get('Effect', ''):
            kyoto_creatures = game_state.get('kyoto_creatures', [])
            for creature in kyoto_creatures:
                creature['ATK'] += 50

    @staticmethod
    def haba_ability(card: Dict[str, Any], game_state: Dict[str, Any]) -> None:
        if "Cursed Tool Specialist" in card.get('Effect', ''):
            game_state['tool_damage_bonus'] = 50
        elif "Weapon Master" in card.get('Effect', ''):
            if game_state.get('has_curse_tool', False):
                card['ATK'] += 100

    @staticmethod
    def kurusu_ability(card: Dict[str, Any], game_state: Dict[str, Any]) -> None:
        if "Angel's Grace" in card.get('Effect', ''):
            game_state['negate_next_effect'] = True
        elif "Purifying Light" in card.get('Effect', ''):
            game_state['curse_spirit_debuff'] = True
        elif "Heaven's Judgment" in card.get('Variant', ''):
            game_state['can_banish_cursed_technique'] = True

    @staticmethod
    def kamo_ability(card: Dict[str, Any], game_state: Dict[str, Any]) -> None:
        if "Blood Manipulation" in card.get('Effect', ''):
            game_state['can_sacrifice_health'] = True
            game_state['health_to_damage'] = 2
        elif "Flowing Red Scale" in card.get('Effect', ''):
            game_state['piercing_damage'] = True
        elif "Blood Technique Master" in card.get('Variant', ''):
            game_state['lifesteal'] = 0.5

    @staticmethod
    def naoya_ability(card: Dict[str, Any], game_state: Dict[str, Any]) -> None:
        if "Projection Sorcery" in card.get('Effect', ''):
            game_state['speed_frames'] = 24
            game_state['bonus_attacks'] = 1
        elif "Speed Master" in card.get('Effect', ''):
            if game_state.get('consecutive_attacks', 0) > 0:
                game_state['bonus_damage'] = 50
        elif "Cursed Spirit" in card.get('Variant', ''):
            game_state['mach_speed'] = True
            game_state['ignore_defense'] = True

    @staticmethod
    def higuruma_ability(card: Dict[str, Any], game_state: Dict[str, Any]) -> None:
        if "Judgeman's Court" in card.get('Effect', ''):
            game_state['can_confiscate_effect'] = True
        elif "Death Sentence" in card.get('Effect', ''):
            if game_state.get('judgment_passed', False):
                game_state['execution_mode'] = True
        elif "Lawyer's Domain" in card.get('Variant', ''):
            game_state['disable_enemy_abilities'] = True

    @staticmethod
    def ishigori_ability(card: Dict[str, Any], game_state: Dict[str, Any]) -> None:
        if "Strongest Output" in card.get('Effect', ''):
            if game_state.get('target_def_higher_than_atk', False):
                game_state['bonus_damage'] = 50
        elif "Satisfaction Always Comes Last" in card.get('Effect', ''):
            if game_state.get('solo_creature', False):
                card['ATK'] += 100
                card['DEF'] += 100
        elif "High-Calorie Resilience" in card.get('Effect', ''):
            game_state['heal_per_turn'] = 50

    @staticmethod
    def tengen_ability(card: Dict[str, Any], game_state: Dict[str, Any]) -> None:
        if "Star Plasma Vessel" in card.get('Effect', ''):
            game_state['barrier_strength'] = 200
        elif "Immortal Sorcerer" in card.get('Effect', ''):
            game_state['cannot_be_destroyed'] = True
        elif "Master of Barriers" in card.get('Variant', ''):
            game_state['global_protection'] = True
            game_state['all_allies_barrier'] = 100
        elif "Barrier Expansion" in card.get('Effect', ''):
            game_state['global_damage_reduction'] = 50

    @staticmethod
    def tsukumo_ability(card: Dict[str, Any], game_state: Dict[str, Any]) -> None:
        if "Carefree Powerhouse" in card.get('Effect', ''):
            game_state['immune_to_atk_reduction'] = True
        elif "Anti-Curse Supremacy" in card.get('Effect', ''):
            if game_state.get('target_is_curse_spirit', False):
                game_state['bonus_damage'] = 100
        elif "Star Rage Technique" in card.get('Variant', ''):
            game_state['can_banish_curse_spirit'] = True

    @staticmethod
    def mei_mei_ability(card: Dict[str, Any], game_state: Dict[str, Any]) -> None:
        if "Bird Strike" in card.get('Effect', ''):
            game_state['can_summon_birds'] = True
            game_state['bird_stats'] = {'ATK': 100, 'DEF': 50}
        elif "Mercenary Spirit" in card.get('Effect', ''):
            if game_state.get('enemy_destroyed', False):
                game_state['bonus_energy'] = 1
        elif "Ultimate Mercenary" in card.get('Variant', ''):
            game_state['bird_swarm'] = True
            game_state['bird_count'] = 3

    @staticmethod
    def yuji_ability(card: Dict[str, Any], game_state: Dict[str, Any]) -> None:
        if "Divergent Fist" in card.get('Effect', ''):
            game_state['double_impact'] = True
        elif "Black Flash Master" in card.get('Effect', ''):
            if game_state.get('consecutive_hits', 0) >= 3:
                game_state['black_flash_bonus'] = 150
        elif "Sukuna Vessel" in card.get('Variant', ''):
            game_state['can_transform'] = True
            game_state['transform_cost'] = 3

    @staticmethod
    def choso_ability(card: Dict[str, Any], game_state: Dict[str, Any]) -> None:
        if "Blood Manipulation" in card.get('Effect', ''):
            game_state['blood_control'] = True
        elif "Death Painting" in card.get('Effect', ''):
            game_state['poison_damage'] = 50
        elif "Cursed Womb" in card.get('Variant', ''):
            game_state['can_summon_brothers'] = True
            game_state['brother_stats'] = {'ATK': 200, 'DEF': 200}

    @staticmethod
    def mahito_ability(card: Dict[str, Any], game_state: Dict[str, Any]) -> None:
        if "Idle Transfiguration" in card.get('Effect', ''):
            game_state['can_transform_enemy'] = True
        elif "Soul Manipulation" in card.get('Effect', ''):
            game_state['soul_damage'] = True
        elif "Evolved Form" in card.get('Variant', ''):
            game_state['self_transform'] = True
            game_state['bonus_stats'] = {'ATK': 200, 'DEF': 200}

    @staticmethod
    def jogo_ability(card: Dict[str, Any], game_state: Dict[str, Any]) -> None:
        if "Volcanic Eruption" in card.get('Effect', ''):
            game_state['area_damage'] = 100
        elif "Maximum: Meteor" in card.get('Effect', ''):
            game_state['can_summon_meteor'] = True
        elif "Disaster Flame" in card.get('Variant', ''):
            game_state['burn_damage'] = 50
            game_state['burn_duration'] = 3

    @staticmethod
    def hanami_ability(card: Dict[str, Any], game_state: Dict[str, Any]) -> None:
        if "Flower Field" in card.get('Effect', ''):
            game_state['curse_energy_drain'] = True
        elif "Root Growth" in card.get('Effect', ''):
            game_state['can_restrict_movement'] = True
        elif "Disaster Plant" in card.get('Variant', ''):
            game_state['heal_from_damage'] = True

    @staticmethod
    def dagon_ability(card: Dict[str, Any], game_state: Dict[str, Any]) -> None:
        if "Water Formation" in card.get('Effect', ''):
            game_state['flood_field'] = True
        elif "Horizon of the Captivating Skandha" in card.get('Effect', ''):
            game_state['domain_active'] = True
            game_state['guaranteed_hit'] = True
        elif "Death Swarm" in card.get('Variant', ''):
            game_state['summon_fish'] = True
            game_state['fish_stats'] = {'ATK': 50, 'DEF': 50}
            game_state['fish_count'] = 5

    @staticmethod
    def toji_ability(card: Dict[str, Any], game_state: Dict[str, Any]) -> None:
        if "Heavenly Restriction" in card.get('Effect', ''):
            game_state['immune_to_cursed_energy'] = True
            card['ATK'] += 200
        elif "Curse Tool Arsenal" in card.get('Effect', ''):
            game_state['weapon_master'] = True
            game_state['bonus_damage'] = 100
        elif "Perfect Preparation" in card.get('Variant', ''):
            game_state['ignore_barriers'] = True
            game_state['first_strike'] = True

    @staticmethod
    def ryu_ability(card: Dict[str, Any], game_state: Dict[str, Any]) -> None:
        if "Granite Blast" in card.get('Effect', ''):
            game_state['piercing_damage'] = True
        elif "Cursed Energy Control" in card.get('Effect', ''):
            if game_state.get('max_output', False):
                card['ATK'] *= 2
        elif "Dessert Enthusiast" in card.get('Variant', ''):
            if game_state.get('solo_creature', False):
                card['ATK'] += 100
                card['DEF'] += 100

    @staticmethod
    def reggie_ability(card: Dict[str, Any], game_state: Dict[str, Any]) -> None:
        if "Comedian's Luck" in card.get('Effect', ''):
            game_state['random_effect'] = True
        elif "Reality Manipulation" in card.get('Effect', ''):
            game_state['can_change_gamestate'] = True
        elif "Perfect Understanding" in card.get('Variant', ''):
            game_state['immune_to_effects'] = True

    @staticmethod
    def dhruv_ability(card: Dict[str, Any], game_state: Dict[str, Any]) -> None:
        if "Constellation Array" in card.get('Effect', ''):
            game_state['can_place_stars'] = True
        elif "Stellar Formation" in card.get('Effect', ''):
            if game_state.get('star_count', 0) >= 3:
                game_state['damage_bonus'] = 150
        elif "Master of the Stars" in card.get('Variant', ''):
            game_state['star_damage'] = 50
            game_state['star_limit'] = 5

    @staticmethod
    def kurourushi_ability(card: Dict[str, Any], game_state: Dict[str, Any]) -> None:
        if "Festering Life" in card.get('Effect', ''):
            game_state['decay_damage'] = True
        elif "Rot Spreader" in card.get('Effect', ''):
            game_state['infection_spread'] = True
        elif "Queen of Rot" in card.get('Variant', ''):
            game_state['can_summon_larvae'] = True
            game_state['larvae_stats'] = {'ATK': 50, 'DEF': 50}

    @staticmethod
    def charles_ability(card: Dict[str, Any], game_state: Dict[str, Any]) -> None:
        if "Mangaka's Determination" in card.get('Effect', ''):
            if game_state.get('near_death', False):
                card['ATK'] *= 2
        elif "Comic Panel Creation" in card.get('Effect', ''):
            game_state['can_trap_enemy'] = True
        elif "Perfect Panel" in card.get('Variant', ''):
            game_state['instant_defeat'] = True

    @staticmethod
    def ui_ability(card: Dict[str, Any], game_state: Dict[str, Any]) -> None:
        if "Simple Domain" in card.get('Effect', ''):
            game_state['negate_domain'] = True
        elif "New Shadow Style" in card.get('Effect', ''):
            game_state['counter_attack'] = True
        elif "Zen Master" in card.get('Variant', ''):
            game_state['immune_to_domains'] = True

    @staticmethod
    def brain_ability(card: Dict[str, Any], game_state: Dict[str, Any]) -> None:
        if "Ancient Sorcerer" in card.get('Effect', ''):
            game_state['technique_copy'] = True
        elif "Body Collector" in card.get('Effect', ''):
            if game_state.get('enemy_destroyed', False):
                game_state['gain_technique'] = True
        elif "Curse Manipulator" in card.get('Variant', ''):
            game_state['control_cursed_spirits'] = True
            game_state['spirit_bonus'] = {'ATK': 100, 'DEF': 100}

# Update the ABILITIES dictionary to include game_state
ABILITIES = {
    "Fushiguro Megumi": lambda char, game_state={}: CardAbility.megumi_ability(char, game_state),
    "Akari Nitta": lambda char, game_state={}: CardAbility.akari_ability(char, game_state),
    "Kiyotaka Ijichi": lambda char, game_state={}: CardAbility.ijichi_ability(char, game_state),
    "Panda": lambda char, game_state={}: CardAbility.panda_ability(char, game_state),
    "Shoko Ieiri": lambda char, game_state={}: CardAbility.shoko_ability(char, game_state),
    "Kasumi Miwa": lambda char, game_state={}: CardAbility.miwa_ability(char, game_state),
    "Rin Amai": lambda char, game_state={}: CardAbility.amai_ability(char, game_state),
    "Toge Inumaki": lambda char, game_state={}: CardAbility.inumaki_ability(char, game_state),
    "Kokichi Muta": lambda char, game_state={}: CardAbility.muta_ability(char, game_state),
    "Tsumiki Fushiguro": lambda char, game_state={}: CardAbility.tsumiki_ability(char, game_state),
    "Fumihiko Takaba": lambda char, game_state={}: CardAbility.takaba_ability(char, game_state),
    "Kirara Hoshi": lambda char, game_state={}: CardAbility.kirara_ability(char, game_state),
    "Momo Nishimiya": lambda char, game_state={}: CardAbility.momo_ability(char, game_state),
    "Masamichi Yaga": lambda char, game_state={}: CardAbility.yaga_ability(char, game_state),
    "Mai Zenin": lambda char, game_state={}: CardAbility.mai_ability(char, game_state),
    "Maki Zenin": lambda char, game_state={}: CardAbility.maki_ability(char, game_state),
    "Takuma Ino": lambda char, game_state={}: CardAbility.ino_ability(char, game_state),
    "Yoshinobu Gakuganji": lambda char, game_state={}: CardAbility.gakuganji_ability(char, game_state),
    "Haba": lambda char, game_state={}: CardAbility.haba_ability(char, game_state),
    "Kinji Hakari": lambda char, game_state={}: CardAbility.hakari_ability(char, game_state),
    "Suguru Geto": lambda char, game_state={}: CardAbility.geto_ability(char, game_state),
    "Aoi Todo": lambda char, game_state={}: CardAbility.todo_ability(char, game_state),
    "Mei Mei": lambda char, game_state={}: CardAbility.mei_mei_ability(char, game_state),
    "Hana Kurusu": lambda char, game_state={}: CardAbility.kurusu_ability(char, game_state),
    "Takako Uro": lambda char, game_state={}: CardAbility.uro_ability(char, game_state),
    "Noritoshi Kamo": lambda char, game_state={}: CardAbility.kamo_ability(char, game_state),
    "Naoya Zenin": lambda char, game_state={}: CardAbility.naoya_ability(char, game_state),
    "Kento Nanami": lambda char, game_state={}: CardAbility.nanami_ability(char, game_state),
    "Hiromi Higuruma": lambda char, game_state={}: CardAbility.higuruma_ability(char, game_state),
    "Kenjaku": lambda char, game_state={}: CardAbility.kenjaku_ability(char, game_state),
    "Hajime Kashimo": lambda char, game_state={}: CardAbility.kashimo_ability(char, game_state),
    "Ryu Ishigori": lambda char, game_state={}: CardAbility.ishigori_ability(char, game_state),
    "Master Tengen": lambda char, game_state={}: CardAbility.tengen_ability(char, game_state),
    "Ryomen Sukuna": lambda char, game_state={}: CardAbility.sukuna_ability(char, game_state),
    "Yuki Tsukumo": lambda char, game_state={}: CardAbility.tsukumo_ability(char, game_state),
    "Ryu": lambda char, game_state={}: CardAbility.ryu_ability(char, game_state),
    "Reggie": lambda char, game_state={}: CardAbility.reggie_ability(char, game_state),
    "Dhruv": lambda char, game_state={}: CardAbility.dhruv_ability(char, game_state),
    "Kurourushi": lambda char, game_state={}: CardAbility.kurourushi_ability(char, game_state),
    "Charles": lambda char, game_state={}: CardAbility.charles_ability(char, game_state),
    "Yaga": lambda char, game_state={}: CardAbility.yaga_ability(char, game_state),
    "UI": lambda char, game_state={}: CardAbility.ui_ability(char, game_state),
    "Brain": lambda char, game_state={}: CardAbility.brain_ability(char, game_state),
    "Gojo Satoru": lambda char, game_state={}: CardAbility.gojo_ability(char, game_state)
}
