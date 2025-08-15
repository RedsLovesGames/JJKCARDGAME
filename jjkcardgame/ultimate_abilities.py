from typing import Dict, Any, List, Optional
import random

class UltimateAbility:
    def __init__(
        self,
        name: str,
        damage_multiplier: float = 1.0,
        effects: Dict[str, Any] = None
    ):
        """
        :param name: Name of the ultimate ability
        :param damage_multiplier: A multiplier to base damage (if you use a formula based on the character's ATK)
        :param effects: Additional custom effects, e.g.
            {
                'flat_damage': 300,
                'aoe_damage': True,
                'destroy_target': True,
                'ignore_defense': True,
                'heal_self': 100,
                'stun': 1,
                'summon': { ... },
                ...
            }
        """
        self.name = name
        self.damage_multiplier = damage_multiplier
        self.effects = effects or {}

class UltimateAbilities:
    """
    A central class where each method returns an UltimateAbility for a given
    character + variant. Your game engine can pick the right function based
    on the character's base name, then check char.variant to figure out which
    branch to use.
    """

    @staticmethod
    def gojo_satoru_ultimate(char, active_player: Any, defending_player: Any) -> UltimateAbility:
        """
        Covers:
          - Gojo Satoru (Young)
          - Gojo Satoru (Shibuya Incident)
          - Gojo Satoru (Toji Incident)
          - Gojo Satoru (The Honored One - Culling Games)
        """
        variant = (char.variant or "").lower()
        name = "Hollow Purple"
        dmg_mult = 2.5
        effects = {'ignore_defense': True}

        if "young" in variant:
            name = "Reversal Red"
            effects = {'flat_damage': 300, 'single_target': True}
        elif "shibuya" in variant:
            name = "Hollow Purple"
            dmg_mult = 0
            effects = {'destroy_primary_target': True, 'aoe_damage': 200}
        elif "toji incident" in variant:
            name = "Hollow Purple"
            dmg_mult = 0
            effects = {'flat_damage': 400, 'single_target': True}
        elif "honored one" in variant or "culling games" in variant:
            name = "Hollow Purple: Divine Wrath"
            dmg_mult = 0
            effects = {
                'flat_damage': 500,
                'single_target': True,
                'conditional_aoe': {'damage_if_kill': 250}
            }

        return UltimateAbility(name, dmg_mult, effects)

    @staticmethod
    def fushiguro_megumi_ultimate(char: Any, active_player: Any, defending_player: Any) -> UltimateAbility:
        """
        Covers:
          - Fushiguro Megumi (Child)
          - Fushiguro Megumi (Detention Center)
          - Fushiguro Megumi (Shibuya Arc)
          - Fushiguro Megumi (Mahoraga)
        """
        variant = (char.variant or "").lower()
        name = "Chimera Shadow Garden"
        dmg_mult = 1.5
        effects = {}

        if "child" in variant:
            name = "Shadow Step"
            dmg_mult = 0
            effects = {'dodge_next_attack': True, 'temp_atk_boost': 50}
        elif "detention center" in variant:
            name = "Divine Dog: Totality"
            dmg_mult = 0
            effects = {'buff_token': 150, 'immediate_attack': True}
        elif "shibuya" in variant:
            name = "Chimera Shadow Garden"
            dmg_mult = 0
            effects = {'double_token_stats': True}
        elif "mahoraga" in variant:
            name = "Eight-Handled Sword Divergent Sila Divine General"
            dmg_mult = 0
            effects = {
                'summon': {
                    'name': 'Mahoraga',
                    'duration': 2,
                    'on_leave_aoe_damage': 300
                }
            }

        return UltimateAbility(name, dmg_mult, effects)

    @staticmethod
    def kugisaki_nobara_ultimate(char: Any, active_player: Any, defending_player: Any) -> UltimateAbility:
        """
        Covers e.g.:
          - Kugisaki Nobara (Child)
          - Kugisaki Nobara (Exchange Event)
          - Kugisaki Nobara (Shinjuku Showdown) or similar
        """
        variant = (char.variant or "").lower()
        name = "Hairpin"
        dmg_mult = 1.5
        effects = {}

        if "child" in variant:
            name = "Simple Strike"
            dmg_mult = 1.2
            effects = {}
        elif "exchange" in variant:
            name = "Hairpin: Resonance"
            dmg_mult = 0
            effects = {'flat_damage': 250, 'stun': 1}
        elif "shinjuku" in variant or "showdown" in variant:
            name = "Hairpin: Final Nail"
            dmg_mult = 0
            effects = {
                'flat_damage': 350,
                'stun': 1
            }

        return UltimateAbility(name, dmg_mult, effects)

    @staticmethod
    def yuta_okkotsu_ultimate(char: Any, active_player: Any, defending_player: Any) -> UltimateAbility:
        """
        Covers:
          - Yuta Okkotsu (First Year)
          - Yuta Okkotsu (Shibuya)
          - Yuta Okkotsu (Culling Games)
        """
        variant = (char.variant or "").lower()
        name = "Rika's Protection"
        dmg_mult = 1.0
        effects = {}

        if "first year" in variant:
            name = "Rika's Protection"
            dmg_mult = 0
            effects = {
                'negate_next_attack': True,
                'restore_def': 100
            }
        elif "shibuya" in variant:
            name = "Copy Technique"
            dmg_mult = 0
            effects = {
                'copy_enemy_effect': True
            }
        elif "culling games" in variant:
            name = "Rika's Rampage"
            dmg_mult = 0
            effects = {
                'conditional_destroy': True,
                'aoe_damage': 200
            }

        return UltimateAbility(name, dmg_mult, effects)

    @staticmethod
    def panda_ultimate(char: Any, active_player: Any, defending_player: Any) -> UltimateAbility:
        """
        Covers:
          - Panda (Abrupt Mutated)
          - Panda (Second Year Student)
          - Panda (Triclops Mode)
        """
        variant = (char.variant or "").lower()
        name = "Unbreakable Blow"
        dmg_mult = 1.0
        effects = {}

        if "abrupt mutated" in variant:
            name = "Unbreakable Blow"
            dmg_mult = 0
            effects = {
                'flat_damage': 250,
                'ignore_defense': True
            }
        elif "second year" in variant:
            name = "Heavy Strike"
            dmg_mult = 0
            effects = {
                'flat_damage': 200,
                'stun': 1
            }
        elif "triclops" in variant:
            name = "Three-Core Rampage"
            dmg_mult = 0
            effects = {
                'multi_attack': 3,
                'mode_shift_each_hit': True
            }

        return UltimateAbility(name, dmg_mult, effects)

    @staticmethod
    def hakari_kinji_ultimate(char: Any, active_player: Any, defending_player: Any) -> UltimateAbility:
        """
        Covers:
          - Kinji Hakari (Third Year)
          - Kinji Hakari (Culling Games)
          - Kinji Hakari (Infinite Jackpot)
        
        (We demonstrate the idea with a single method returning different results
         based on the variant, plus the random 'jackpot' concept.)
        """
        variant = (char.variant or "").lower()

        jackpot_chance = 0.3
        name = "Probability Manipulation"
        base_mult = 1.2
        jackpot_mult = 3.0

        if "third year" in variant:
            name = "Jackpot Burst"
            is_jackpot = (random.random() < jackpot_chance)
            dmg_mult = jackpot_mult if is_jackpot else base_mult
            effects = {'aoe_damage': 300 if is_jackpot else 0}
            return UltimateAbility(name, dmg_mult, effects)

        elif "culling games" in variant:
            name = "Infinite Jackpot"
            is_jackpot = (random.random() < jackpot_chance)
            dmg_mult = jackpot_mult if is_jackpot else base_mult
            effects = {
                'heal_full_def': is_jackpot,
                'flat_damage': 400 if is_jackpot else 0
            }
            return UltimateAbility(name, dmg_mult, effects)

        elif "infinite jackpot" in variant:
            name = "Idle Death Rush"
            is_jackpot = True
            dmg_mult = 0
            effects = {
                'aoe_damage': 500
            }
            return UltimateAbility(name, dmg_mult, effects)

        return UltimateAbility(name, base_mult, {})

    @staticmethod
    def maki_zenin_ultimate(char: Any, active_player: Any, defending_player: Any) -> UltimateAbility:
        """
        Covers:
          - Maki Zenin (Second Year)
          - Maki Zenin (Awakening)
          - Maki Zenin (Heavenly Restriction)
        """
        variant = (char.variant or "").lower()
        name = "Dragon Bone Strike"
        dmg_mult = 1.0
        effects = {}

        if "second year" in variant:
            name = "Dragon Bone Strike"
            dmg_mult = 0
            effects = {
                'flat_damage': 250,
                'conditional_curse_tool_bonus': 50
            }
        elif "awakening" in variant:
            name = "Cursed Clan Eradication"
            dmg_mult = 0
            effects = {
                'aoe_damage': 999,
                'stack_bonus_for_kills': 50
            }
        elif "heavenly restriction" in variant:
            name = "Total Rejection"
            dmg_mult = 0
            effects = {
                'destroy_target': True,
                'conditional_permanent_buff': {
                    'condition': 'target_def>target_atk',
                    'atk_buff': 100
                }
            }

        return UltimateAbility(name, dmg_mult, effects)

    @staticmethod
    def todo_aoi_ultimate(char: Any, active_player: Any, defending_player: Any) -> UltimateAbility:
        """
        Covers:
          - Aoi Todo (Third Year)
          - Aoi Todo (Exchange Event)
          - Aoi Todo (Boogie Woogie Master)
        """
        variant = (char.variant or "").lower()

        if "third year" in variant:
            return UltimateAbility(
                name="Black Flash",
                damage_multiplier=0,
                effects={'flat_damage': 350}
            )
        elif "exchange event" in variant:
            return UltimateAbility(
                name="Boogie Woogie",
                damage_multiplier=0,
                effects={'switch_positions': True, 'flat_damage': 200}
            )
        elif "boogie woogie master" in variant:
            return UltimateAbility(
                name="Boogie Woogie Combo",
                damage_multiplier=0,
                effects={'team_combo': True, 'aoe_damage': True}
            )

        return UltimateAbility("Boogie Woogie", 1.0)

    @staticmethod
    def kirara_hoshi_ultimate(char: Any, active_player: Any, defending_player: Any) -> UltimateAbility:
        """
        Covers:
          - Kirara Hoshi (Third Year)
          - Kirara Hoshi (Space-Time Attraction)
        """
        variant = (char.variant or "").lower()
        if "third year" in variant:
            return UltimateAbility(
                name="Star Pull",
                damage_multiplier=0,
                effects={'reposition_enemy': True, 'atk_debuff': 100}
            )
        elif "space-time" in variant:
            return UltimateAbility(
                name="Star Chain",
                damage_multiplier=0,
                effects={'mark_enemy_disable': True}
            )
        return UltimateAbility("Celestial Attraction", 1.0, {})

    @staticmethod
    def inumaki_toge_ultimate(char: Any, active_player: Any, defending_player: Any) -> UltimateAbility:
        """
        Covers:
          - Toge Inumaki (Second Year)
          - Toge Inumaki (Cursed Speech User)
        """
        variant = (char.variant or "").lower()
        if "second year" in variant:
            return UltimateAbility(
                name="Cursed Speech: Blast Away",
                damage_multiplier=0,
                effects={'flat_damage': 250, 'push_back': 1}
            )
        elif "cursed speech user" in variant:
            return UltimateAbility(
                name="Cursed Speech: Explode",
                damage_multiplier=0,
                effects={'aoe_damage': 300, 'self_def_debuff': 100}
            )
        return UltimateAbility("Cursed Speech", 1.0, {})

    @staticmethod
    def geto_suguru_ultimate(char: Any, active_player: Any, defending_player: Any) -> UltimateAbility:
        """
        Covers:
          - Suguru Geto (Tokyo High Student)
          - Suguru Geto (Cursed Spirit Collector)
          - Suguru Geto (Shibuya Incident)
        """
        variant = (char.variant or "").lower()
        name = "Uzumaki"
        dmg_mult = 0
        effects = {}

        if "tokyo high" in variant:
            name = "Uzumaki"
            effects = {
                'sacrifice_own_spirits': True,
                'each_spirit_damage': 150
            }
        elif "cursed spirit collector" in variant:
            name = "Maximum Uzumaki"
            effects = {
                'absorb_spirits': True,
                'aoe_damage': 250
            }
        elif "shibuya incident" in variant:
            name = "Summon Vengeful Spirit"
            effects = {
                'summon': {
                    'name': 'Special Grade Spirit',
                    'atk': 400,
                    'def_': 400,
                    'duration': 3
                }
            }

        return UltimateAbility(name, dmg_mult, effects)

    @staticmethod
    def yaga_masamichi_ultimate(char: Any, active_player: Any, defending_player: Any) -> UltimateAbility:
        """
        Covers:
          - Masamichi Yaga (Jujutsu High Principal)
          - Masamichi Yaga (Cursed Corpses Creator)
        """
        variant = (char.variant or "").lower()
        if "principal" in variant:
            return UltimateAbility(
                name="Cursed Corpse Enhancement",
                damage_multiplier=0,
                effects={'enhance_corpse': 100}
            )
        elif "creator" in variant:
            return UltimateAbility(
                name="Ultimate Cursed Puppet: Panda",
                damage_multiplier=0,
                effects={
                    'summon': {
                        'name': 'Panda',
                        'atk': 300,
                        'def_': 300,
                        'duration': 3
                    }
                }
            )
        return UltimateAbility("Cursed Corpses", 1.0, {})

    @staticmethod
    def shoko_ieiri_ultimate(char: Any, active_player: Any, defending_player: Any) -> UltimateAbility:
        """
        Covers:
          - Shoko Ieiri (Tokyo Jujutsu High Doctor)
          - Shoko Ieiri (Reverse Curse Master)
        """
        variant = (char.variant or "").lower()
        if "doctor" in variant:
            return UltimateAbility(
                name="Emergency Treatment",
                damage_multiplier=0,
                effects={'full_heal_ally_def': True}
            )
        elif "reverse curse master" in variant:
            return UltimateAbility(
                name="Total Restoration",
                damage_multiplier=0,
                effects={
                    'team_heal': 200,
                    'cleanse_debuffs': True
                }
            )
        return UltimateAbility("Medical Expertise", 1.0, {})

    @staticmethod
    def kamo_noritoshi_ultimate(char: Any, active_player: Any, defending_player: Any) -> UltimateAbility:
        """
        Covers:
          - Noritoshi Kamo (Third Year)
          - Noritoshi Kamo (Blood Manipulation Specialist)
        """
        variant = (char.variant or "").lower()
        if "third year" in variant:
            return UltimateAbility(
                name="Piercing Blood",
                damage_multiplier=0,
                effects={'flat_damage': 250, 'ignore_defense': True}
            )
        elif "blood manipulation specialist" in variant:
            return UltimateAbility(
                name="Convergence: Crimson Binding",
                damage_multiplier=0,
                effects={
                    'flat_damage': 300,
                    'atk_debuff': 50,
                    'atk_debuff_duration': 2
                }
            )
        return UltimateAbility("Blood Manipulation", 1.0, {})

    @staticmethod
    def mai_zenin_ultimate(char: Any, active_player: Any, defending_player: Any) -> UltimateAbility:
        """
        Covers:
          - Mai Zenin (Second Year)
          - Mai Zenin (Zenin Heir)
          - Mai Zenin (Creation Technique User)
        """
        variant = (char.variant or "").lower()
        if "second year" in variant:
            return UltimateAbility(
                name="Expert Marksman",
                damage_multiplier=0,
                effects={
                    'flat_damage': 250,
                    'extra_damage_condition': {
                        'def_less_than_atk': 50
                    }
                }
            )
        elif "zenin heir" in variant:
            return UltimateAbility(
                name="Fatal Shot",
                damage_multiplier=0,
                effects={
                    'conditional_flat_damage': [
                        {'condition': 'self_def<50%', 'damage': 400}
                    ],
                    'base_damage': 300
                }
            )
        elif "creation technique" in variant:
            return UltimateAbility(
                name="Last Stand Bullet",
                damage_multiplier=0,
                effects={
                    'sacrifice_self_def': True,
                    'damage_per_100_def_lost': 150
                }
            )
        return UltimateAbility("Sniper's Precision", 1.0, {})

    @staticmethod
    def naoya_zenin_ultimate(char: Any, active_player: Any, defending_player: Any) -> UltimateAbility:
        """
        Covers:
          - Naoya Zenin (Zenin Clan Heir)
          - Naoya Zenin (Projection Sorcery Master)
        """
        variant = (char.variant or "").lower()
        if "zenin clan heir" in variant:
            return UltimateAbility(
                name="Warp Strike",
                damage_multiplier=0,
                effects={
                    'flat_damage': 300,
                    'switch_with_target': True
                }
            )
        elif "projection sorcery master" in variant:
            return UltimateAbility(
                name="Time Compression Strike",
                damage_multiplier=2.0,
                effects={'ignore_defense_if_continuous': True}
            )
        return UltimateAbility("Projection Sorcery", 1.0, {})

    @staticmethod
    def nanami_kento_ultimate(char: Any, active_player: Any, defending_player: Any) -> UltimateAbility:
        """
        Covers:
          - Kento Nanami (Grade 1 Sorcerer)
          - Kento Nanami (Ratio Master)
          - Kento Nanami (Shibuya Incident)
        """
        variant = (char.variant or "").lower()

        if "grade 1" in variant:
            return UltimateAbility(
                name="Ratio Strike",
                damage_multiplier=0,
                effects={
                    'conditional_flat_damage': [
                        {'condition': 'target_def>target_atk', 'damage': 350}
                    ],
                    'base_damage': 300
                }
            )
        elif "ratio master" in variant:
            return UltimateAbility(
                name="Overtime Finisher",
                damage_multiplier=2.0,
                effects={'ignore_defense_if_condition': True}
            )
        elif "shibuya incident" in variant:
            return UltimateAbility(
                name="Last Ratio Strike",
                damage_multiplier=0,
                effects={
                    'flat_damage': 400,
                    'self_def_debuff': 100
                }
            )
        return UltimateAbility("Overtime", 2.0, {'critical_hit': True})

    @staticmethod
    def kenjaku_ultimate(char: Any, active_player: Any, defending_player: Any) -> UltimateAbility:
        """
        Covers:
          - Kenjaku (Golden Era)
          - Kenjaku (Cursed Womb)
          - Kenjaku (Shibuya Incident)
          - Kenjaku (The Culling Games)
        """
        variant = (char.variant or "").lower()
        name = "Ancient Knowledge"
        effects = {}

        if "golden era" in variant:
            return UltimateAbility(
                name="Ancient Knowledge",
                damage_multiplier=0,
                effects={'reduce_cost': 1}
            )
        elif "cursed womb" in variant:
            return UltimateAbility(
                name="Cursed Womb",
                damage_multiplier=0,
                effects={
                    'summon': {
                        'name': 'Cursed Spirit',
                        'atk': 300,
                        'def_': 300,
                        'duration': 3
                    }
                }
            )
        elif "shibuya" in variant:
            return UltimateAbility(
                name="Shibuya Incident",
                damage_multiplier=0,
                effects={
                    'flat_damage': 500,
                    'heal_self': 200
                }
            )
        elif "culling games" in variant:
            return UltimateAbility(
                name="Culling Games",
                damage_multiplier=0,
                effects={
                    'aoe_damage': 300,
                    'gain_energy': 2
                }
            )

        return UltimateAbility(name, 1.0, effects)

def get_ultimate_ability(character_name: str, variant: str = 'Standard') -> Optional[UltimateAbility]:
    """
    Get the ultimate ability for a given character and variant.
    
    Args:
        character_name: Name of the character
        variant: Variant of the character (default: 'Standard')
        
    Returns:
        UltimateAbility object if one exists for the character, None otherwise
    """
    # Define ultimate abilities for different characters
    ultimate_abilities = {
        'Gojo Satoru': {
            'Standard': UltimateAbility(
                name="Hollow Purple",
                damage_multiplier=2.5,
                cooldown=3
            )
        },
        'Yuji Itadori': {
            'Standard': UltimateAbility(
                name="Black Flash",
                damage_multiplier=2.0,
                cooldown=2
            )
        },
        'Megumi Fushiguro': {
            'Standard': UltimateAbility(
                name="Divine Dogs",
                damage_multiplier=1.8,
                status_effects=['Bind'],
                cooldown=2
            )
        }
        # Add more characters and their ultimate abilities here
    }
    
    # Return the ultimate ability if it exists
    return ultimate_abilities.get(character_name, {}).get(variant)
