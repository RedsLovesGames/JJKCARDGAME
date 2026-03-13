from __future__ import annotations

from character_ids import normalize_character_name

class CardAbility:
    @staticmethod
    def apply_ability(card: Dict[str, Any], game_state: Dict[str, Any]) -> None:
        canonical_name = normalize_character_name(card.get('Name'))
        ability_func = ABILITY_MAP.get(canonical_name)
        if ability_func:
            ability_func(card, game_state)

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


@dataclass(frozen=True)
class AbilityEffect:
    duration: int = 0


@dataclass(frozen=True)
class BuffATK(AbilityEffect):
    amount: int = 0


@dataclass(frozen=True)
class BuffDEF(AbilityEffect):
    amount: int = 0


@dataclass(frozen=True)
class DamageReduction(AbilityEffect):
    reduction: float = 0.0


@dataclass(frozen=True)
class Stun(AbilityEffect):
    pass


@dataclass(frozen=True)
class SummonToken(AbilityEffect):
    name: str = "Token"
    atk: int = 0
    def_: int = 0


@dataclass(frozen=True)
class FlagEffect(AbilityEffect):
    flag: str = ""
    value: Any = True
    one_time: bool = False


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
    "Yuta Okkotsu": lambda char, game_state={}: CardAbility.yuta_ability(char, game_state),
    "Naobito Zenin": lambda char, game_state={}: CardAbility.naobito_ability(char, game_state),
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

ABILITY_MAP = {
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
    "Yuta Okkotsu": CardAbility.yuta_ability,
    "Naobito Zenin": CardAbility.naobito_ability,
    "Gojo Satoru": CardAbility.gojo_ability,
    # Legacy keys retained for backward compatibility
    "Reggie": CardAbility.reggie_ability,
    "Dhruv": CardAbility.dhruv_ability,
    "Kurourushi": CardAbility.kurourushi_ability,
    "Charles": CardAbility.charles_ability,
    "UI": CardAbility.ui_ability,
    "Brain": CardAbility.brain_ability,
}

