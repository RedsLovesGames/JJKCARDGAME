import pandas as pd
import random
import os
from typing import List, Optional, Dict, Any, Callable, Protocol, Union
from deck import Deck
from character import Character
from player import Player
from datetime import datetime
from ultimate_abilities import get_ultimate_ability, ULTIMATE_ABILITY_FUNCTIONS
from card_abilities import CardAbility, ABILITY_MAP
from character_ids import normalize_character_name, report_binding_validation


class BattlePolicy(Protocol):
    """Decision interface used by a Battle during the action phase."""

    def choose_play(self, player: Player, battle: 'Battle') -> Optional[Character]:
        """Return the next card to play from hand, or None to stop playing cards."""

    def choose_attack_target(
        self,
        attacker: Character,
        opponent: Player,
        battle: 'Battle'
    ) -> Optional[Character]:
        """Return attack target on opponent field, or None for direct attack."""

    def choose_ultimate_target(
        self,
        attacker: Character,
        opponent: Player,
        battle: 'Battle'
    ) -> Optional[Character]:
        """Return target for ultimate activation, or None to skip using ultimate."""


class AIPolicy:
    """Heuristic policy for card play, targeting and ultimate timing."""

    def choose_play(self, player: Player, battle: 'Battle') -> Optional[Character]:
        playable_cards = [card for card in player.hand if player.can_play_card(card)]
        if not playable_cards or len(player.field) >= 5:
            return None

        # Prioritize strongest immediately playable card with mild cost efficiency bias.
        return max(
            playable_cards,
            key=lambda card: (card.atk + int(card.def_val * 0.4)) - card.cost * 5
        )

    def choose_attack_target(
        self,
        attacker: Character,
        opponent: Player,
        battle: 'Battle'
    ) -> Optional[Character]:
        if not opponent.field:
            return None
        return battle._select_optimal_target(attacker, opponent.field)

    def choose_ultimate_target(
        self,
        attacker: Character,
        opponent: Player,
        battle: 'Battle'
    ) -> Optional[Character]:
        if not opponent.field:
            return None

        can_use_ultimate = (
            get_ultimate_ability(attacker.name, attacker.variant) is not None
            and attacker.energy >= attacker.ultimate_energy_cost
        )
        if not can_use_ultimate:
            return None

        # Use ultimate when it is likely to secure a KO or when board pressure is high.
        high_threat = max(opponent.field, key=lambda c: c.atk)
        killable = [target for target in opponent.field if target.current_health <= attacker.ultimate_damage]
        if killable:
            return min(killable, key=lambda c: c.current_health)
        if high_threat.atk >= attacker.atk * 1.2:
            return high_threat
        return None


class HumanPolicy:
    """Policy adapter that accepts decisions from UI/web callbacks or console input."""

    def __init__(
        self,
        decision_provider: Optional[
            Callable[[str, Dict[str, Any]], Optional[Union[int, Character]]]
        ] = None
    ):
        self.decision_provider = decision_provider

    def _request(self, action: str, payload: Dict[str, Any]) -> Optional[Union[int, Character]]:
        if self.decision_provider:
            return self.decision_provider(action, payload)
        return None

    def choose_play(self, player: Player, battle: 'Battle') -> Optional[Character]:
        playable_cards = [card for card in player.hand if player.can_play_card(card)]
        if not playable_cards or len(player.field) >= 5:
            return None

        decision = self._request('choose_play', {'player': player, 'playable_cards': playable_cards, 'battle': battle})
        if isinstance(decision, Character) and decision in playable_cards:
            return decision
        if isinstance(decision, int) and 0 <= decision < len(playable_cards):
            return playable_cards[decision]

        # Console fallback for local manual play.
        for idx, card in enumerate(playable_cards):
            print(f"[{idx}] {card.name} (Cost {card.cost}, ATK {card.atk}, DEF {card.def_val})")
        raw = input(f"{player.name}: choose card index to play or Enter to skip: ").strip()
        if raw == '':
            return None
        if raw.isdigit() and int(raw) < len(playable_cards):
            return playable_cards[int(raw)]
        return None

    def choose_attack_target(
        self,
        attacker: Character,
        opponent: Player,
        battle: 'Battle'
    ) -> Optional[Character]:
        if not opponent.field:
            return None

        decision = self._request('choose_attack_target', {'attacker': attacker, 'opponent': opponent, 'battle': battle})
        if isinstance(decision, Character) and decision in opponent.field:
            return decision
        if isinstance(decision, int) and 0 <= decision < len(opponent.field):
            return opponent.field[decision]

        for idx, card in enumerate(opponent.field):
            print(f"[{idx}] {card.name} (HP {card.current_health}, ATK {card.atk})")
        raw = input(f"Choose attack target for {attacker.name} or Enter for default: ").strip()
        if raw.isdigit() and int(raw) < len(opponent.field):
            return opponent.field[int(raw)]
        return max(opponent.field, key=lambda x: x.atk)

    def choose_ultimate_target(
        self,
        attacker: Character,
        opponent: Player,
        battle: 'Battle'
    ) -> Optional[Character]:
        if not opponent.field:
            return None

        decision = self._request('choose_ultimate_target', {'attacker': attacker, 'opponent': opponent, 'battle': battle})
        if isinstance(decision, Character) and decision in opponent.field:
            return decision
        if isinstance(decision, int) and 0 <= decision < len(opponent.field):
            return opponent.field[decision]
        if decision is None and self.decision_provider:
            return None

        raw = input(f"Use ultimate with {attacker.name}? (y/N): ").strip().lower()
        if raw != 'y':
            return None
        return max(opponent.field, key=lambda x: x.current_health)

class Battle:
    def __init__(
        self,
        player1: Player,
        player2: Player,
        player1_policy: Optional[BattlePolicy] = None,
        player2_policy: Optional[BattlePolicy] = None
    ):
        if not isinstance(player1.deck, Deck) or not isinstance(player2.deck, Deck):
            raise ValueError("Players must be initialized with proper Deck objects")
        self.player1 = player1
        self.player2 = player2
        self.policies: Dict[str, BattlePolicy] = {
            player1.name: player1_policy or AIPolicy(),
            player2.name: player2_policy or AIPolicy()
        }
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
        self.placements_this_turn = {self.player1.name: 0, self.player2.name: 0}
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

    def _find_owner(self, character: Character) -> Optional[Player]:
        if character in self.player1.field:
            return self.player1
        if character in self.player2.field:
            return self.player2
        return None

    def _tick_effects(self, state_obj: Any):
        active_effects = getattr(state_obj, 'active_effects', None)
        if not active_effects:
            return

        for timed in list(active_effects['timed_effects']):
            timed['remaining_turns'] -= 1
            if timed['remaining_turns'] <= 0:
                modifier = timed.get('modifier')
                amount = timed.get('amount', 0)
                if modifier in active_effects['modifiers']:
                    active_effects['modifiers'][modifier] -= amount
                active_effects['timed_effects'].remove(timed)

        for status, turns in list(active_effects['statuses'].items()):
            if turns <= 1:
                del active_effects['statuses'][status]
            else:
                active_effects['statuses'][status] = turns - 1

    def resolve_effects(self, effects, source, target, state):
        """Apply structured effects onto player/character local state containers."""
        if target is None:
            return
        if not hasattr(target, 'active_effects'):
            return

        for effect in effects:
            if isinstance(effect, BuffATK):
                target.active_effects['modifiers']['atk'] += effect.amount
                if effect.duration > 0:
                    target.active_effects['timed_effects'].append({
                        'modifier': 'atk',
                        'amount': effect.amount,
                        'remaining_turns': effect.duration,
                    })
            elif isinstance(effect, BuffDEF):
                target.active_effects['modifiers']['def'] += effect.amount
                if effect.duration > 0:
                    target.active_effects['timed_effects'].append({
                        'modifier': 'def',
                        'amount': effect.amount,
                        'remaining_turns': effect.duration,
                    })
            elif isinstance(effect, DamageReduction):
                target.active_effects['modifiers']['damage_reduction'] += effect.reduction
                if effect.duration > 0:
                    target.active_effects['timed_effects'].append({
                        'modifier': 'damage_reduction',
                        'amount': effect.reduction,
                        'remaining_turns': effect.duration,
                    })
            elif isinstance(effect, Stun):
                target.active_effects['statuses']['stunned'] = max(
                    effect.duration,
                    target.active_effects['statuses'].get('stunned', 0)
                )
            elif isinstance(effect, SummonToken):
                owner = target if isinstance(target, Player) else self._find_owner(target)
                if owner and len(owner.field) < 5:
                    owner.field.append(Character(effect.name, "Token", 0, effect.atk, effect.def_, "Token", "", 0))
            elif isinstance(effect, FlagEffect):
                if effect.one_time:
                    target.active_effects['one_time_triggers'].add(effect.flag)
                else:
                    target.active_effects['flags'][effect.flag] = effect.value

    def place_character(self, player: Player, character: Character) -> bool:
        if self.placements_this_turn[player.name] >= 2:
            return False
        if player.play_card(character):
            self.placements_this_turn[player.name] += 1
            self.battle_log.append(f"{player.name} placed {character.name} ({character.variant})")
            return True
        return False

    def process_combat(
        self,
        attacker: Character,
        defender: Player,
        policy: Optional[BattlePolicy] = None
    ):
        """Resolve one attacker action via the centralized combat rules engine."""
        if not isinstance(attacker, Character):
            return

        policy = policy or AIPolicy()

        # Ultimate decision is delegated to policy; rules remain centralized here.
        ultimate_target = policy.choose_ultimate_target(attacker, defender, self)
        if ultimate_target and ultimate_target in defender.field:
            damage = attacker.use_ultimate(ultimate_target)
            if damage > 0:
                self._update_damage_stats(attacker.name, damage, 'ultimate_damage')
                self.battle_log.append(
                    f"{attacker.name} uses ultimate on {ultimate_target.name} for {damage} damage"
                )
                if not ultimate_target.is_alive():
                    defender.field.remove(ultimate_target)
                    self.card_damage_tracker[attacker.name]['kills'] += 1
                attacker.add_energy()
                return

        attack_target = policy.choose_attack_target(attacker, defender, self)
        if attack_target and attack_target in defender.field:
            actual_damage = attack_target.take_damage(attacker.atk)
            self._update_damage_stats(attacker.name, actual_damage, 'direct_damage')
            self.battle_log.append(f"{attacker.name} attacks {attack_target.name} for {actual_damage} damage")
            if not attack_target.is_alive():
                defender.field.remove(attack_target)
                self.card_damage_tracker[attacker.name]['kills'] += 1
        else:
            damage = attacker.atk
            opponent.take_damage(damage)
            self._update_damage_stats(attacker.name, damage, 'direct_damage')
            self.battle_log.append(f"{attacker.name} attacks directly for {damage} damage")

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
        """Process a single turn according to rules."""
        policy = self.policies.get(active_player.name, AIPolicy())

        # Draw Phase
        if active_player.deck.cards_remaining() > 0:
            active_player.draw_cards(1)

        # Energy Gain Phase
        active_player.add_energy()

        # Action Phase (decisions via policy, resolution via battle engine)
        self._process_actions(active_player, opponent, policy)

        # End Phase - Regenerate characters
        for character in active_player.field:
            character.regenerate_health()

        # Check for game end
        return opponent.life_points <= 0

    def simulate_battle(self):
        max_turns = 50
        while self.current_turn <= max_turns:
            self.placements_this_turn = {self.player1.name: 0, self.player2.name: 0}
            
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
                        if ultimate.effects:
                            f.write(f"    Effects: {ultimate.effects}\n")
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
            effects = CardAbility.apply_ability(card_data, self.game_state)
            self.resolve_effects(effects, source=char, target=char, state=self.game_state)
            if char.active_effects['modifiers'].get('damage_reduction', 0) > 0:
                pct = int(char.active_effects['modifiers']['damage_reduction'] * 100)
                self.battle_log.append(f"  {char.name}'s ability reduces incoming damage by {pct}%")

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
        self.resolve_effects(CardAbility.apply_ability(attacker_data, self.game_state), attacker, attacker, self.game_state)
        self.resolve_effects(CardAbility.apply_ability(defender_data, self.game_state), defender, defender, self.game_state)
        
        # Apply damage modifiers
        reduction = defender.get_damage_reduction() if hasattr(defender, 'get_damage_reduction') else 0
        if reduction > 0:
            original_damage = damage
            damage = int(damage * (1 - reduction))
            self.battle_log.append(f"    {defender.name}'s damage reduction reduced damage from {original_damage} to {damage}")
            
        if attacker.active_effects['flags'].get('can_combo_attack', False):
            original_damage = damage
            damage = int(damage * 1.5)
            self.battle_log.append(f"    Combo attack increases damage from {original_damage} to {damage}")
            
        if attacker.active_effects['flags'].get('ignore_def', False):
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

    def _process_actions(
        self,
        active_player: Player,
        opponent: Player,
        policy: BattlePolicy
    ) -> None:
        """Process action phase using policy decisions and centralized combat resolution."""
        # Play phase: up to 2 placements by policy.
        for _ in range(2):
            if self.placements_this_turn[active_player.name] >= 2 or len(active_player.field) >= 5:
                break
            try:
                card = policy.choose_play(active_player, self)
                if card is None:
                    break
                if not active_player.play_card(card):
                    self.battle_log.append(f"{active_player.name} failed to play {card.name}")
                    break

                self.placements_this_turn[active_player.name] += 1
                if card.name in self.card_damage_tracker:
                    self.card_damage_tracker[card.name]['times_played'] += 1
                self.battle_log.append(f"{active_player.name} plays {card.name}")
            except Exception as e:
                self.battle_log.append(f"Failed play decision for {active_player.name}: {str(e)}")
                break

        # Combat phase: each field character acts through the same engine.
        for attacker in list(active_player.field):
            if not attacker.is_alive():
                continue
            try:
                self.process_combat(attacker, opponent, policy)
            except Exception as e:
                self.battle_log.append(f"Combat failed for {attacker.name}: {str(e)}")

def load_characters(filename='characters.csv'):
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        csv_path = os.path.join(current_dir, filename)
        if not os.path.exists(csv_path):
            print(f"Error: {filename} not found in {current_dir}")
            return None
        df = pd.read_csv(csv_path)
        report_binding_validation(csv_path, tuple(ABILITY_MAP.keys()), tuple(ULTIMATE_ABILITY_FUNCTIONS.keys()))
        if 'Name' in df.columns:
            df['Name'] = df['Name'].apply(normalize_character_name)
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


def _build_mode_policies(game_mode: str):
    mode = (game_mode or 'ai_vs_ai').lower()
    if mode == 'human_vs_ai':
        return HumanPolicy(), AIPolicy()
    if mode == 'human_vs_human':
        return HumanPolicy(), HumanPolicy()
    return AIPolicy(), AIPolicy()

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
                mode = input("Game mode (ai_vs_ai/human_vs_ai/human_vs_human) [ai_vs_ai]: ").strip() or "ai_vs_ai"
                simulate_battles("characters.csv", runs, game_mode=mode)
            except ValueError:
                print("Invalid input. Please enter a number between 1 and 1000.")
        elif choice == "2":
            print("\nExiting simulator...")
            break
        else:
            print("\nInvalid choice. Please enter 1 or 2.")

def simulate_battles(card_file: str, num_simulations: int, game_mode: str = "ai_vs_ai"):
    """Run battles for selected game mode: ai_vs_ai, human_vs_ai, human_vs_human."""
    try:
        # Load characters and create decks
        characters = load_characters(card_file)
        if characters is None or characters.empty:
            print("Error: No valid characters loaded")
            return None
            
        # Run simulations and collect stats
        wins = {"Player 1": 0, "Player 2": 0}
        card_stats = {}
        
        p1_policy, p2_policy = _build_mode_policies(game_mode)

        for i in range(num_simulations):
            battle = Battle(
                Player("Player 1", Deck(characters)),
                Player("Player 2", Deck(characters)),
                player1_policy=p1_policy,
                player2_policy=p2_policy
            )
            winner = battle.simulate_battle()
            if winner:
                wins[winner.name] += 1
                
        # Print results
        print(f"\nSimulation Results ({game_mode}):")
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
