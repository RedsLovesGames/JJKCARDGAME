"""
Character Class for JJK Card Game
Represents a playable character card with stats, abilities, and battle mechanics.
Handles character creation, ability application, and combat interactions.
"""

from base_types import BaseCharacter
from typing import Dict, Any, Optional
from ultimate_abilities import UltimateAbilities, UltimateAbility

class Character(BaseCharacter):
    """
    Represents a playable character in the JJK Card Game.
    
    Each character has base stats (ATK, DEF, Cost), special abilities,
    and an ultimate move. Characters can be created from card data and
    can have passive abilities applied based on their variant.
    """

    # Pre-defined character abilities and their effects
    ABILITIES = {
        'Gojo Satoru': {
            'Limitless': {'damage_reduction': 0.5},      # Takes half damage
            'Six Eyes': {'energy_cost_reduction': True}  # Reduced energy costs
        },
        'Sukuna': {
            'King of Curses': {'atk_multiplier': 1.5}   # 50% more attack power
        },
        'Megumi Fushiguro': {
            'Ten Shadows': {
                'can_summon': True,
                'summon_limit': 2
            }
        },
        'Yuji Itadori': {
            'Divergent Fist': {'double_hit': True}      # Can attack twice
        },
        'Yuta Okkotsu': {
            'Rika': {'copy_ability': True}              # Can copy other abilities
        }
    }

    @classmethod
    def from_card_data(cls, card: Dict[str, Any]) -> 'Character':
        """
        Create a Character instance from card data dictionary.
        
        Args:
            card_data: Dictionary containing card attributes
                      Must include: Name, Variant, Cost, ATK, DEF
                      Optional: Effect, Ultimate Move
        """
        try:
            # Create the character instance
            character = cls(
                name=card['Name'],
                variant=card.get('Variant', 'Standard'),  # Default to 'Standard' if not provided
                cost=card['Cost'],
                atk=card['ATK'],
                def_=card['DEF'],
                effect=card.get('Effect', ''),
                ultimate=card.get('Ultimate Move', ''),
                ultimate_cost=card.get('Ultimate Cost', 1)  # Use the Ultimate Cost from CSV
            )
            
            # Now use the character instance to get the ultimate ability
            ultimate = character.get_ultimate_ability()  # Call the new method
            
            # Set the ultimate ability to the character
            character.ultimate = ultimate
            
            return character
        
        except Exception as e:
            raise ValueError(f"Error creating character: {e}")

    def get_ultimate_ability(self) -> Optional[UltimateAbility]:
        """Retrieve the ultimate ability for this character based on its name and variant."""
        character_name = self.name.lower()
        
        # Map character names to their respective ultimate methods
        ultimate_methods = {
            'gojo satoru': UltimateAbilities.gojo_satoru_ultimate,
            'fushiguro megumi': UltimateAbilities.fushiguro_megumi_ultimate,
            'kugisaki nobara': UltimateAbilities.kugisaki_nobara_ultimate,
            'nanami kento': UltimateAbilities.nanami_kento_ultimate,
            'kenjaku': UltimateAbilities.kenjaku_ultimate,
            'naoya zenin': UltimateAbilities.naoya_zenin_ultimate,
            # Add other characters as needed
        }
        
        # Get the appropriate ultimate method based on character name
        ultimate_method = ultimate_methods.get(character_name)
        if ultimate_method:
            return ultimate_method(self, None, None)  # Pass character data as needed
        
        return None

    def __init__(self, name, variant, cost, atk, def_, effect='', ultimate='', ultimate_cost=1):
        """
        Initialize a new Character instance.
        
        Args:
            name: Character's name
            variant: Character variant/version
            cost: Energy cost to play
            atk: Attack power
            def_: Defense points
            effect: Special effect description
            ultimate: Ultimate move description
            ultimate_cost: Energy cost to use the ultimate move
        """
        super().__init__(name, variant, cost, atk, def_, effect, ultimate)
        self.energy = 0  # Start with 0 energy
        self.ultimate_energy_cost = ultimate_cost
        self.ultimate_damage = self.parse_ultimate_damage()
        self.current_health = def_  # Use def_ as starting health
        self.max_health = def_     # Store max health
        self.cannot_attack_next_turn = False
        self.status_effects = []
        self.regen_rate = 1.0

    def apply_passive_ability(self):
        """
        Apply character-specific passive abilities based on name and variant.
        
        Checks the ABILITIES dictionary for matching abilities and applies
        their effects to the character. Effects can include damage reduction,
        attack multipliers, and special abilities.
        """
        if self.name in self.ABILITIES:
            for variant, effects in self.ABILITIES[self.name].items():
                if variant in self.variant or variant in self.effect:
                    for attr, value in effects.items():
                        setattr(self, attr, value)
                    if 'atk_multiplier' in effects:
                        self.atk = int(self.atk * effects['atk_multiplier'])

    def parse_ultimate_damage(self) -> int:
        """Calculate the base ultimate damage for this character"""
        ultimate = self.get_ultimate_ability()
        if ultimate:
            return int(self.atk * ultimate.damage_multiplier)
        return self.atk  # Default to regular attack if no ultimate found

    def take_damage(self, amount):
        """Process incoming damage with damage reduction if applicable."""
        actual_damage = min(amount, self.current_health)
        self.current_health -= actual_damage
        return actual_damage

    def use_ultimate(self, target):
        """
        Attempt to use ultimate move on target.
        
        Args:
            target: Character to target with ultimate
            
        Returns:
            int: Damage dealt (0 if not enough energy)
        """
        if self.energy >= self.ultimate_energy_cost:
            self.energy -= self.ultimate_energy_cost
            return target.take_damage(self.ultimate_damage)
        return 0

    def is_alive(self):
        """Check if character is still alive (has defense points)."""
        return self.current_health > 0

    def heal(self, amount):
        """
        Heal character's defense points.
        
        Args:
            amount: Amount to heal
        """
        self.def_val = min(self.def_val, self.def_val + amount)

    def add_energy(self):
        """Add energy points according to game rules."""
        self.energy = min(self.energy + 1, 10)  # Max 10 energy, +1 per turn

    def regenerate_health(self):
        """Regenerate HP at end of turn - only for characters, not players"""
        if self.is_alive() and not any(effect for effect in self.status_effects if effect.prevents_healing):
            self.current_health = self.max_health  # Full heal unless prevented

    # ... rest of the Character class methods from battle.py ... 