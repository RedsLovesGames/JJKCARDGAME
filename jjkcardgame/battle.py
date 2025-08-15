import pandas as pd
import random
import os
from typing import List, Optional, Dict, Any
from deck import Deck
from character import Character
from player import Player
from datetime import datetime
from ultimate_abilities import get_ultimate_ability
from card_abilities import CardAbility

class Battle:
    def __init__(self, player1: Player, player2: Player):
        if not isinstance(player1.deck, Deck) or not isinstance(player2.deck, Deck):
            raise ValueError("Players must be initialized with proper Deck objects")
        self.player1 = player1
        self.player2 = player2
        self.damage_stats = {
            'direct_damage': {},
            'ultimate_damage': {},
            'effect_damage': {},
            'total_damage': 0
        }
        self.card_damage_tracker = {}  # Add this line
        self.strategy_log = []
        self.ability_usage_tracker = {}
        self.battle_log = []
        self.current_turn = 1
        self.placements_this_turn = {"Player 1": 0, "Player 2": 0}
        self.game_state = {
            'gojo_on_field': False,
            'yuji_on_field': False,
            'rika_on_field': False,
            'solo_creature': False,
            'was_attacked': False,
            'did_attack': False,
            'jackpot_mode': False,
            'dice_roll': 0,
            'damage_reduction': 0,
            'energy_cost_reduction': False,
            'can_see_weakness': False,
            'can_summon': False,
            'can_heal': False,
            'adaptation': False,
            'can_combo_attack': False,
            'ignore_def': False,
            'spell_immunity': False
        }
        
        # Initialize card damage tracker for all cards
        all_cards = set()
        for player in [player1, player2]:
            for card in player.deck.cards:
                all_cards.add(card.name)
        
        for card_name in all_cards:
            self.card_damage_tracker[card_name] = {
                'damage_dealt': 0,
                'times_played': 0,
                'kills': 0
            }
            self.damage_stats['direct_damage'][card_name] = 0
            self.damage_stats['ultimate_damage'][card_name] = 0
            self.damage_stats['effect_damage'][card_name] = 0
            self.ability_usage_tracker[card_name] = {
                'abilities_used': [],
                'times_used': 0
            }

        self.battle_record = {
            'damage_stats': self.damage_stats.copy(),
            'ability_usage_tracker': self.ability_usage_tracker.copy()
        }

        # Initialize players with correct starting values
        self.player1.life_points = 2000  # Starting HP per rules
        self.player2.life_points = 2000
        self.player1.energy = 1    # Start with 1 energy on Turn 1
        self.player2.energy = 1

    def place_character(self, player: Player, character: Character) -> bool:
        if self.placements_this_turn[player.name] >= 2:
            return False
        if player.play_card(character):
            self.placements_this_turn[player.name] += 1
            self.battle_log.append(f"{player.name} placed {character.name} ({character.variant})")
            return True
        return False

    def process_combat(self, attacker: Character, defender: Player):
        """Process combat damage and update statistics."""
        if not isinstance(attacker, Character):
            return
        
        # Check for ultimate ability activation
        ultimate = get_ultimate_ability(attacker.name, attacker.variant)
        
        # Increase the chance of using the ultimate
        if ultimate and defender.field and attacker.energy >= attacker.ultimate_energy_cost:
            if random.random() < 1.0:  # 100% chance to use ultimate
                target = max(defender.field, key=lambda x: x.current_health)
                damage = attacker.use_ultimate(target)
                if damage > 0:
                    self._update_damage_stats(attacker.name, damage, 'ultimate_damage')
                    self.battle_log.append(f"{attacker.name} uses ultimate on {target.name} for {damage} damage")
                    return  # Skip regular attack if ultimate was used

        # Regular combat
        if defender.field:
            target = max(defender.field, key=lambda x: x.atk)
            damage = attacker.atk
            actual_damage = target.take_damage(damage)
            self._update_damage_stats(attacker.name, actual_damage, 'direct_damage')
            self.battle_log.append(f"{attacker.name} attacks {target.name} for {actual_damage} damage")
        else:
            # Direct attack
            damage = attacker.atk
            defender.take_damage(damage)
            self._update_damage_stats(attacker.name, damage, 'direct_damage')
            self.battle_log.append(f"{attacker.name} attacks directly for {damage} damage")

        # Add energy after action
        attacker.add_energy()

    def process_character_combat(self, attacker: Character, defender: Character):
        """Process combat between two characters."""
        damage = attacker.atk
        actual_damage = defender.take_damage(damage)
        
        # Update damage stats
        self._update_damage_stats(attacker.name, actual_damage, 'direct_damage')
        
        # Log the combat
        self.battle_log.append(f"  {attacker.name} attacks {defender.name}")
        self.battle_log.append(f"    Damage dealt: {actual_damage}")
        self.battle_log.append(f"    {defender.name}'s remaining HP: {defender.current_health}")

    def process_turn(self, active_player: Player, opponent: Player) -> bool:
        """Process a single turn according to rules"""
        # Draw Phase
        if active_player.deck.cards_remaining() > 0:
            active_player.draw_cards(1)
        
        # Energy Gain Phase
        active_player.add_energy()
        
        # Action Phase (includes playing cards and combat)
        self._process_actions(active_player, opponent)
        
        # End Phase - Regenerate characters
        for character in active_player.field:
            character.regenerate_health()
        
        # Check for game end
        return opponent.life_points <= 0

    def simulate_battle(self):
        max_turns = 50
        while self.current_turn <= max_turns:
            self.placements_this_turn = {"Player 1": 0, "Player 2": 0}
            
            if self.process_turn(self.player1, self.player2):
                return self.player1
            if self.process_turn(self.player2, self.player1):
                return self.player2
                
            self.current_turn += 1

        return self.player1 if self.player1.life_points > self.player2.life_points else self.player2

    def export_battle_stats(self, filename: str):
        with open(filename, 'w') as f:
            f.write("Battle Statistics\n=================\n\n")
            f.write("Regular Damage Dealt:\n")
            for card_name, damage in self.damage_stats['direct_damage'].items():
                f.write(f"{card_name}: {damage} damage\n")
            f.write("\nUltimate Ability Damage:\n")
            for card_name, damage in self.damage_stats['ultimate_damage'].items():
                if damage > 0:
                    ultimate = get_ultimate_ability(card_name, '')
                    if ultimate:
                        f.write(f"{card_name} - {ultimate.name}: {damage} damage\n")
                        f.write(f"    Damage Multiplier: x{ultimate.damage_multiplier}\n")
                        if ultimate.status_effects:
                            f.write(f"    Status Effects: {', '.join(ultimate.status_effects)}\n")
            f.write("\nAbility Usage and Effects:\n")
            for card_name, stats in self.ability_usage_tracker.items():
                if stats['times_used'] > 0:
                    f.write(f"{card_name}:\n")
                    for ability in stats['abilities_used']:
                        f.write(f"    - {ability}\n")
                    if self.damage_stats['effect_damage'][card_name] > 0:
                        f.write(f"    Ability Damage: {self.damage_stats['effect_damage'][card_name]}\n")
                    f.write(f"    Times Used: {stats['times_used']}\n")
            f.write("\nBattle Log:\n")
            for entry in self.battle_log:
                f.write(f"{entry}\n")

    def update_game_state(self, attacker: Player, defender: Player):
        """Update game state based on field conditions"""
        all_characters = attacker.field + defender.field
        self.game_state.update({
            'gojo_on_field': any(char.name == "Gojo Satoru" for char in all_characters),
            'yuji_on_field': any(char.name == "Yuji Itadori" for char in all_characters),
            'rika_on_field': any(char.name == "Rika" for char in all_characters),
            'solo_creature': len(attacker.field) == 1,
            'dice_roll': random.randint(1, 6)
        })
        
        # Apply abilities for all characters on field
        for char in all_characters:
            card_data = {'Name': char.name, 'Effect': char.effect, 'Variant': char.variant}
            CardAbility.apply_ability(card_data, self.game_state)
            if self.game_state.get('damage_reduction', 0) > 0:
                self.battle_log.append(f"  {char.name}'s ability reduces incoming damage by {self.game_state['damage_reduction']*100}%")
            if self.game_state.get('energy_cost_reduction', False):
                self.battle_log.append(f"  {char.name}'s ability reduces energy costs")

    def apply_passive_abilities(self, character: Character):
        """Apply passive abilities based on character and game state"""
        if character.name == "Gojo Satoru":
            if "Limitless" in character.effect or "The Honored One" in character.variant:
                self.battle_log.append(f"    {character.name}'s Limitless reduces incoming damage")
        
        elif character.name == "Megumi Fushiguro" and "Mahoraga" in character.variant:
            if self.game_state.get('was_attacked', False):
                character.def_val += 50
                self.battle_log.append(f"    Mahoraga adapts: DEF increased to {character.def_val}")
            if self.game_state.get('did_attack', False):
                character.atk += 50
                self.battle_log.append(f"    Mahoraga adapts: ATK increased to {character.atk}")

    def calculate_modified_damage(self, attacker: Character, defender: Character, base_damage: int) -> int:
        """Calculate final damage after all modifiers"""
        damage = base_damage
        
        # Create card data dictionaries for ability processing
        attacker_data = {
            'Name': attacker.name,
            'Effect': attacker.effect,
            'Variant': attacker.variant,
            'ATK': attacker.atk
        }
        
        defender_data = {
            'Name': defender.name,
            'Effect': defender.effect,
            'Variant': defender.variant,
            'DEF': defender.def_val
        }
        
        # Apply abilities and log their effects
        CardAbility.apply_ability(attacker_data, self.game_state)
        CardAbility.apply_ability(defender_data, self.game_state)
        
        # Apply damage modifiers
        if self.game_state.get('damage_reduction', 0) > 0:
            reduction = self.game_state['damage_reduction']
            original_damage = damage
            damage = int(damage * (1 - reduction))
            self.battle_log.append(f"    {defender.name}'s damage reduction reduced damage from {original_damage} to {damage}")
            
        if self.game_state.get('can_combo_attack', False):
            original_damage = damage
            damage = int(damage * 1.5)
            self.battle_log.append(f"    Combo attack increases damage from {original_damage} to {damage}")
            
        if self.game_state.get('ignore_def', False):
            self.battle_log.append(f"    {attacker.name} ignores defense!")
            
        return damage

    def process_pre_attack_abilities(self, attacker: Character, defender: Character):
        """Process abilities that trigger before attack"""
        if attacker.name == "Todo" and "Boogie Woogie Master" in attacker.variant:
            if self.game_state.get('yuji_on_field', False):
                self.battle_log.append(f"    Todo and Yuji combo attack activated!")
                attacker.atk = int(attacker.atk * 1.5)

    def process_post_attack_abilities(self, attacker: Character, defender: Character, damage_dealt: int):
        """Process abilities that trigger after attack"""
        # Update state for adaptation abilities
        self.game_state['was_attacked'] = True
        self.game_state['did_attack'] = True
        
        # Hakari's ability
        if attacker.name == "Kinji Hakari" and "Infinite Jackpot" in attacker.variant:
            if self.game_state['dice_roll'] >= 5:
                self.game_state['jackpot_mode'] = True
                self.battle_log.append(f"    Hakari hits jackpot! Entering immortal mode")

    def _log_active_abilities(self, character: Character):
        """Log all active abilities for a character"""
        ability_effects = []
        
        if self.game_state.get('damage_reduction', 0) > 0:
            ability_effects.append(f"Damage reduction: {self.game_state['damage_reduction']*100}%")
        if self.game_state.get('energy_cost_reduction', False):
            ability_effects.append("Reduced energy costs")
        if self.game_state.get('can_combo_attack', False):
            ability_effects.append("Can perform combo attacks")
        if self.game_state.get('ignore_def', False):
            ability_effects.append("Ignores defense")
        if self.game_state.get('adaptation', False):
            ability_effects.append("Adapts to combat")
        
        if ability_effects:
            self.battle_log.append(f"  {character.name}'s active abilities:")
            for effect in ability_effects:
                self.battle_log.append(f"    - {effect}")

    def _log_damage_stats(self):
        """Log the final damage statistics"""
        self.battle_log.append("\nBattle Statistics")
        self.battle_log.append("=" * 50)
        
        # Only show cards that dealt damage
        active_cards = {name: stats for name, stats in self.damage_stats['direct_damage'].items() 
                       if stats > 0}
        
        if active_cards:
            self.battle_log.append("\nDamage Dealt by Card:")
            self.battle_log.append("-" * 20)
            
            # Sort cards by total damage dealt
            sorted_cards = sorted(active_cards.items(), 
                                key=lambda x: x[1], 
                                reverse=True)
            
            for card_name, damage in sorted_cards:
                self.battle_log.append(f"\n  {card_name}:")
                self.battle_log.append(f"    Damage: {damage}")
        else:
            self.battle_log.append("\nNo damage was dealt during this battle.")

    def _update_damage_stats(self, attacker_name: str, damage: int, damage_type: str = 'direct_damage'):
        """Update damage statistics for a character."""
        if damage <= 0:
            return
            
        if damage_type not in self.damage_stats:
            self.damage_stats[damage_type] = {}
            
        if attacker_name not in self.damage_stats[damage_type]:
            self.damage_stats[damage_type][attacker_name] = 0
            
        self.damage_stats[damage_type][attacker_name] += damage
        self.damage_stats['total_damage'] += damage
        
        # Track ultimate usage if it's an ultimate attack
        if damage_type == 'ultimate_damage':
            if attacker_name not in self.ability_usage_tracker:
                self.ability_usage_tracker[attacker_name] = {
                    'abilities_used': [],
                    'times_used': 0
                }
            self.ability_usage_tracker[attacker_name]['times_used'] += 1

    def _select_optimal_target(self, attacker: Character, targets: List[Character]) -> Character:
        """Select the optimal target based on damage efficiency"""
        target_scores = []
        for target in targets:
            score = 0
            # Prioritize targets that can be destroyed
            if target.current_health <= attacker.atk:
                score += 100
            # Prioritize high-attack targets
            score += target.atk * 0.5
            # Consider target's remaining health
            score += (target.max_health - target.current_health) * 0.3
            target_scores.append((target, score))
        
        return max(target_scores, key=lambda x: x[1])[0]

    def print_battle_statistics(self):
        """Print detailed battle statistics at the end of the game."""
        self.battle_log.append("\nBattle Statistics")
        self.battle_log.append("=" * 50)
        
        total_damage = 0
        for damage_type, damages in self.damage_stats.items():
            if damages:
                self.battle_log.append(f"\n{damage_type.replace('_', ' ').title()}:")
                for char_name, damage in damages.items():
                    self.battle_log.append(f"  {char_name}: {damage}")
                    total_damage += damage
        
        if total_damage == 0:
            self.battle_log.append("\nNo damage was dealt during this battle.")
        else:
            self.battle_log.append(f"\nTotal damage dealt: {total_damage}")

    def _process_combat(self, attacker: Character, defender: Character):
        """Process combat between characters"""
        damage = attacker.atk
        actual_damage = defender.take_damage(damage)
        
        # Update stats
        self._update_damage_stats(attacker.name, actual_damage, 'direct_damage')
        
        # Check if target was defeated
        if not defender.is_alive():
            self.card_damage_tracker[attacker.name]['kills'] += 1

    def _process_end_phase(self, active_player: Player):
        """Process end of turn effects"""
        # Regenerate only characters on the field, not players
        for character in active_player.field:
            if character.is_alive():
                character.regenerate_health()
        
        # Process any end-of-turn effects
        for character in active_player.field:
            for effect in character.status_effects:
                if hasattr(effect, 'process_end_turn'):
                    effect.process_end_turn(character)

    def _process_actions(self, active_player: Player, opponent: Player) -> None:
        """Process the action phase of a turn"""
        # Play cards phase
        playable_cards = [card for card in active_player.hand if card.cost <= active_player.energy]
        
        # Can play up to 2 cards per turn
        for card in playable_cards[:2]:  
            if active_player.energy >= card.cost and len(active_player.field) < 5:
                try:
                    active_player.play_card(card)
                    self.placements_this_turn[active_player.name] += 1
                    
                    # Track card usage
                    if card.name in self.card_damage_tracker:
                        self.card_damage_tracker[card.name]['times_played'] += 1
                    
                    # Log the play
                    self.battle_log.append(f"{active_player.name} plays {card.name}")
                except Exception as e:
                    self.battle_log.append(f"Failed to play {card.name}: {str(e)}")
                    continue
        
        # Combat phase
        for attacker in active_player.field:
            try:
                # First check for ultimate ability
                ultimate = get_ultimate_ability(attacker.name, attacker.variant)
                if (ultimate and opponent.field and 
                    attacker.energy >= attacker.ultimate_energy_cost):
                    target = max(opponent.field, key=lambda x: x.current_health)
                    damage = attacker.use_ultimate(target)
                    if damage > 0:
                        self._update_damage_stats(attacker.name, damage, 'ultimate_damage')
                        self.battle_log.append(f"{attacker.name} uses ultimate on {target.name} for {damage} damage")
                        continue  # Skip regular attack if ultimate was used

                # Regular combat
                if opponent.field:
                    target = max(opponent.field, key=lambda x: x.atk)
                    damage = attacker.atk
                    actual_damage = target.take_damage(damage)
                    self._update_damage_stats(attacker.name, actual_damage, 'direct_damage')
                    self.battle_log.append(f"{attacker.name} attacks {target.name} for {actual_damage} damage")
                else:
                    # Direct attack
                    damage = attacker.atk
                    opponent.take_damage(damage)
                    self._update_damage_stats(attacker.name, damage, 'direct_damage')
                    self.battle_log.append(f"{attacker.name} attacks directly for {damage} damage")

                # Add energy after action
                attacker.add_energy()
                
            except Exception as e:
                self.battle_log.append(f"Combat failed for {attacker.name}: {str(e)}")
                continue

def load_characters(filename='characters.csv'):
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        csv_path = os.path.join(current_dir, filename)
        if not os.path.exists(csv_path):
            print(f"Error: {filename} not found in {current_dir}")
            return None
        df = pd.read_csv(csv_path)
        if df.empty:
            print(f"Error: {filename} is empty")
            return None
        return df
    except pd.errors.EmptyDataError:
        print(f"Error: {filename} is empty")
        return None
    except Exception as e:
        print(f"Error loading characters: {e}")
        return None

def run_menu():
    while True:
        print("\nJJK Card Game Simulator")
        print("=" * 30)
        print("1. Run Battle Simulations")
        print("2. Exit")
        
        choice = input("\nEnter your choice (1-2): ")
        
        if choice == "1":
            try:
                runs = int(input("\nEnter number of runs (1-1000): "))
                runs = max(1, min(1000, runs))
                simulate_battles("characters.csv", runs)
            except ValueError:
                print("Invalid input. Please enter a number between 1 and 1000.")
        elif choice == "2":
            print("\nExiting simulator...")
            break
        else:
            print("\nInvalid choice. Please enter 1 or 2.")

def simulate_battles(card_file: str, num_simulations: int):
    """Run multiple battle simulations and collect statistics"""
    try:
        # Load characters and create decks
        characters = load_characters(card_file)
        if characters is None or characters.empty:
            print("Error: No valid characters loaded")
            return None
            
        # Run simulations and collect stats
        wins = {"Player 1": 0, "Player 2": 0}
        card_stats = {}
        
        for i in range(num_simulations):
            battle = Battle(
                Player("Player 1", Deck(characters)),
                Player("Player 2", Deck(characters))
            )
            winner = battle.simulate_battle()
            if winner:
                wins[winner.name] += 1
                
        # Print results
        print("\nSimulation Results:")
        print(f"Total Battles: {num_simulations}")
        print(f"Player 1 Wins: {wins['Player 1']}")
        print(f"Player 2 Wins: {wins['Player 2']}")
        
        return wins, card_stats
        
    except Exception as e:
        print(f"Error in battle simulation: {e}")
        return None

def calculate_card_strength(row):
    """Estimate a card's strength based on ATK, DEF, Cost and effects."""
    cost = row.get('Cost', 1)
    atk = row.get('ATK', 0)
    defense = row.get('DEF', 0)

    # Base strength calculation with weighted defense
    base_strength = atk + (defense * 0.6)
    expected_strength = 150 * cost  # Simple scaling based on cost

    # Adjust for cost efficiency
    cost_modifier = 1 + (cost - 1) * 0.2

    # Effect strength calculation
    effect_modifier = 1.0
    effect = row.get('Effect', '')
    if isinstance(effect, str):
        effect_lower = effect.lower()
        if 'destroy' in effect_lower or 'negate' in effect_lower:
            effect_modifier *= 1.5
        if 'summon' in effect_lower:
            effect_modifier *= 1.4
        if 'heal' in effect_lower or 'restore' in effect_lower:
            effect_modifier *= 1.3
        if 'draw' in effect_lower:
            effect_modifier *= 1.35

    # Calculate final power ratio with a scaling factor
    power_ratio = (base_strength * effect_modifier * cost_modifier) / expected_strength
    return power_ratio

if __name__ == "__main__":
    run_menu()