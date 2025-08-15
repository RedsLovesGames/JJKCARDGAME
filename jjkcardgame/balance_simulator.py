"""
Balance Simulator for JJK Card Game
This module handles the automatic balancing of card stats through iterative battle simulations.
It uses a combination of win rates, damage output, and cost efficiency to adjust card parameters.
"""

import pandas as pd
import numpy as np
from battle import Battle, Player, Deck, load_characters, Character
from typing import Dict, List, Tuple, Optional
import copy
import json
import os
from datetime import datetime
import random
from character import Character

# Add these constants at the top of the file, after the imports
MAX_STAT_VALUE = 800
COST_DISTRIBUTION_TOLERANCE = 0.1  # Allow 10% deviation in cost distribution
ULTIMATE_POWER_FACTOR = 0.3  # How much ultimate abilities affect balance calculations

class BalanceSimulator:
    """
    A class that handles automatic card balancing through battle simulations.
    
    The simulator runs multiple iterations of battles, tracks card performance,
    and makes adjustments to card stats based on win rates and damage output.
    It maintains both the original and modified card data, saving progress
    to a separate file to preserve the original data.
    """

    def __init__(self, initial_cards_df: pd.DataFrame, target_win_rate: float = 0.5, 
                 win_rate_tolerance: float = 0.05):
        """
        Initialize the balance simulator with card data and target metrics.
        """
        # Store original cards but never modify them
        self.original_cards = initial_cards_df.copy()
        
        # Working file will always be balanced_chars.csv
        self.working_file = 'balanced_chars.csv'
        
        # Create a working copy for modifications
        self.cards_df = initial_cards_df.copy()
        
        # Initialize tracking variables
        self.target_win_rate = target_win_rate
        self.win_rate_tolerance = win_rate_tolerance
        self.card_stats = {}
        self.iteration_history = []
        self.best_balance = None
        self.best_balance_score = float('inf')
        self.stat_changes = []
        self.card_balance_scores = {}
        
        # Load or create working file
        self._initialize_working_file()

    def _initialize_working_file(self):
        """Initialize the working file with proper error handling"""
        try:
            if os.path.exists(self.working_file):
                try:
                    self.cards_df = pd.read_csv(self.working_file)
                    print(f"Loaded existing {self.working_file}")
                except pd.errors.EmptyDataError:
                    self._create_new_working_file()
                except Exception as e:
                    print(f"Error loading {self.working_file}: {str(e)}")
                    self._create_new_working_file()
            else:
                self._create_new_working_file()
        except Exception as e:
            print(f"Error initializing working file: {str(e)}")
            raise

    def _create_new_working_file(self):
        """Create a new working file from original cards"""
        try:
            self.cards_df = self.original_cards.copy()
            self.cards_df.to_csv(self.working_file, index=False)
            print(f"Created new {self.working_file}")
        except Exception as e:
            print(f"Error creating new working file: {str(e)}")
            raise

    def run_balance_iterations(self, num_iterations: int, battles_per_iteration: int):
        """Run multiple iterations of battle simulations to balance cards."""
        try:
            print(f"\nStarting balance simulation with {num_iterations} iterations")
            print(f"Each iteration will run {battles_per_iteration} battles")
            
            all_battle_records = []
            best_iteration_stats = None
            
            # Initialize current_stats
            self.current_stats = {
                'card_stats': {},
                'ultimate_stats': {
                    'total_uses': {},
                    'games_used': {},
                    'total_games': 0,
                    'total_damage': {},
                    'ultimate_success': {}
                },
                'battle_records': []
            }
            
            for iteration in range(num_iterations):
                print(f"\nIteration {iteration + 1}/{num_iterations}")
                
                iteration_stats = self._run_single_iteration(battles_per_iteration)
                
                if iteration_stats:
                    # Merge iteration stats into current_stats
                    for card_id, stats in iteration_stats['card_stats'].items():
                        if card_id not in self.current_stats['card_stats']:
                            self.current_stats['card_stats'][card_id] = stats
                        else:
                            # Update existing stats
                            for key, value in stats.items():
                                if key in self.current_stats['card_stats'][card_id]:
                                    self.current_stats['card_stats'][card_id][key] += value
                                else:
                                    self.current_stats['card_stats'][card_id][key] = value
                    
                    # Update ultimate stats
                    self.current_stats['ultimate_stats']['total_games'] += iteration_stats['ultimate_stats']['total_games']
                    for key in ['total_uses', 'games_used', 'total_damage', 'ultimate_success']:
                        for char_name, value in iteration_stats['ultimate_stats'].get(key, {}).items():
                            if char_name not in self.current_stats['ultimate_stats'][key]:
                                self.current_stats['ultimate_stats'][key][char_name] = value
                            else:
                                self.current_stats['ultimate_stats'][key][char_name] += value
                    
                    # Calculate balance score and adjust cards
                    balance_score = self.calculate_balance_score(iteration_stats)
                    print(f"  Balance score: {balance_score:.2f}/100")
                    
                    if balance_score > self.best_balance_score:
                        self.best_balance_score = balance_score
                        self.best_balance = self.cards_df.copy()
                        best_iteration_stats = dict(self.current_stats)
                        print(f"  New best balance score: {balance_score:.2f}")
                    
                    self.adjust_card_stats(iteration_stats)
                    self._save_progress()
                
                # Collect battle records
                all_battle_records.extend(iteration_stats.get('battle_records', []))
            
            # Use best iteration stats for final analysis
            if best_iteration_stats:
                self.current_stats = best_iteration_stats
            
            # Generate final analysis
            self._generate_final_analysis(all_battle_records)
            
            return self.best_balance
            
        except Exception as e:
            print(f"Error in balance simulation: {str(e)}")
            return None

    def _run_single_iteration(self, battles_per_iteration: int) -> dict:
        """Run a single iteration of battles and collect stats"""
        iteration_stats = {
            'battle_records': [],
            'card_stats': {}
        }
        battles_completed = 0
        
        while battles_completed < battles_per_iteration:
            try:
                # Create new battle instance
                deck1 = Deck(self.cards_df)
                deck2 = Deck(self.cards_df)
                player1 = Player("Player 1", deck1)
                player2 = Player("Player 2", deck2)
                battle = Battle(player1, player2)
                
                # Run battle
                winner = battle.simulate_battle()
                
                if winner:
                    iteration_stats['battle_records'].append(battle)
                    updated_stats = self.collect_battle_stats(winner, player1, player2, battle, iteration_stats)
                    if updated_stats:
                        iteration_stats = updated_stats
                    battles_completed += 1
                    
            except Exception as e:
                print(f"  Battle failed: {str(e)}")
                continue
        
        return iteration_stats

    def _save_progress(self):
        """Save current progress to working file with error handling"""
        try:
            self.cards_df.to_csv(self.working_file, index=False)
        except Exception as e:
            print(f"Error saving progress: {str(e)}")

    def _generate_final_analysis(self, battle_records):
        """Generate final analysis and save to summary file"""
        try:
            if not hasattr(self, 'current_stats') or not self.current_stats:
                print("No stats available for analysis")
                return

            # Generate reports
            balance_report = self.generate_balance_report(self.current_stats)
            ultimate_analysis = self.analyze_ultimate_usage(battle_records)
            changes_report = self.generate_detailed_changes()

            # Combine reports
            full_report = (
                "JJK CARD GAME BALANCE SUMMARY\n" +
                "=" * 50 + "\n" +
                f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n" +
                balance_report + "\n\n" +
                "CARD CHANGES\n" +
                "-" * 20 + "\n" +
                "\n".join(changes_report) + "\n\n" +
                ultimate_analysis
            )

            # Write to file
            try:
                with open("balance_summary.txt", "w", encoding='utf-8') as f:
                    f.write(full_report)
                print("\nBalance summary has been written to balance_summary.txt")
            except Exception as e:
                print(f"Error writing to file: {str(e)}")
                raise

        except Exception as e:
            print(f"Error generating final analysis: {str(e)}")
            raise

    def collect_battle_stats(self, winner, player1, player2, battle, iteration_stats):
        """
        Collect and aggregate statistics from a single battle.
        """
        try:
            # Initialize stats structure if not present
            if 'card_stats' not in iteration_stats:
                iteration_stats['card_stats'] = {}
            if 'ultimate_stats' not in iteration_stats:
                iteration_stats['ultimate_stats'] = {
                    'total_uses': {},
                    'total_damage': {},
                    'total_games': 0
                }
            
            # Increment total games
            iteration_stats['ultimate_stats']['total_games'] += 1

            # Get all unique cards that participated
            all_cards = set()
            for player in [player1, player2]:
                if hasattr(player, 'hand'):
                    all_cards.update(f"{card.name} ({card.variant})" for card in player.hand)
                    all_cards.update(f"{card.name} ({card.variant})" for card in player.field)

            # Process each card's stats
            for card_id in all_cards:
                if card_id not in iteration_stats['card_stats']:
                    iteration_stats['card_stats'][card_id] = {
                        'wins': 0,
                        'plays': 0,
                        'total_damage': 0,
                        'battles': 0
                    }
                
                stats = iteration_stats['card_stats'][card_id]
                stats['battles'] += 1
                
                # Update damage stats
                card_name = card_id.split(" (")[0]
                direct_damage = battle.damage_stats['direct_damage'].get(card_name, 0)
                ultimate_damage = battle.damage_stats['ultimate_damage'].get(card_name, 0)
                effect_damage = battle.damage_stats['effect_damage'].get(card_name, 0)
                
                stats['total_damage'] += (direct_damage + ultimate_damage + effect_damage)
                
                # Check if card was played
                for player in [player1, player2]:
                    if any(f"{card.name} ({card.variant})" == card_id for card in player.field):
                        stats['plays'] += 1
                        if winner == player:
                            stats['wins'] += 1
                        break

                # Update ultimate stats using damage_stats
                if ultimate_damage > 0:
                    iteration_stats['ultimate_stats']['total_uses'][card_name] = iteration_stats['ultimate_stats']['total_uses'].get(card_name, 0) + 1
                    iteration_stats['ultimate_stats']['total_damage'][card_name] = iteration_stats['ultimate_stats']['total_damage'].get(card_name, 0) + ultimate_damage

        except Exception as e:
            print(f"Stats collection error: {str(e)}")
            return None

        return iteration_stats

    def calculate_balance_score(self, stats: Dict) -> float:
        """Calculate overall balance score based on collected statistics"""
        card_scores = {}
        
        for card_id, card_stats in stats['card_stats'].items():
            if card_id in ["Player 1", "Player 2"] or card_stats['plays'] < 5:
                continue
            
            # Calculate all the scores as before
            win_rate = card_stats['wins'] / card_stats['plays'] if card_stats['plays'] > 0 else 0
            win_rate_score = 40 if abs(win_rate - self.target_win_rate) <= 0.1 else 0
            
            total_damage = card_stats.get('total_damage', 0)
            damage_score = min(30, (total_damage / card_stats['plays']) / 10) if card_stats['plays'] > 0 else 0
            
            total_plays = sum(s['plays'] for s in stats['card_stats'].values() if isinstance(s, dict))
            play_rate = card_stats['plays'] / total_plays if total_plays > 0 else 0
            play_rate_score = min(20, play_rate * 200)
            
            name = card_id.split(" (")[0]
            card_data = self.cards_df[self.cards_df['Name'] == name].iloc[0].to_dict()
            cost_efficiency = self._calculate_cost_efficiency(card_data)
            
            card_scores[card_id] = win_rate_score + damage_score + play_rate_score + cost_efficiency
        
        # Return average score
        return sum(card_scores.values()) / len(card_scores) if card_scores else 0

    def generate_balance_report(self, stats: Dict) -> str:
        """Generate detailed balance report"""
        output_lines = ["CARD BALANCE SCORES\n", "=" * 50 + "\n"]
        
        for card_id, card_stats in stats['card_stats'].items():
            if card_id in ["Player 1", "Player 2"] or card_stats['plays'] < 5:
                continue
            
            # Calculate all the scores
            win_rate = card_stats['wins'] / card_stats['plays'] if card_stats['plays'] > 0 else 0
            win_rate_score = 40 if abs(win_rate - self.target_win_rate) <= 0.1 else 0
            
            total_damage = card_stats.get('total_damage', 0)
            damage_score = min(30, (total_damage / card_stats['plays']) / 10) if card_stats['plays'] > 0 else 0
            
            total_plays = sum(s['plays'] for s in stats['card_stats'].values() if isinstance(s, dict))
            play_rate = card_stats['plays'] / total_plays if total_plays > 0 else 0
            play_rate_score = min(20, play_rate * 200)
            
            name = card_id.split(" (")[0]
            card_data = self.cards_df[self.cards_df['Name'] == name].iloc[0].to_dict()
            cost_efficiency = self._calculate_cost_efficiency(card_data)
            
            # Calculate total score
            total_score = win_rate_score + damage_score + play_rate_score + cost_efficiency
            
            # Format card report with rounded values
            output_lines.extend([
                f"\n{card_id}:",
                f"  Total Score: {total_score:.1f}/100",
                f"  Win Rate: {win_rate:.2%} (Score: {win_rate_score})",
                f"  Damage Output: {total_damage/card_stats['plays']:.1f} avg (Score: {damage_score:.2f})",
                f"  Play Rate: {play_rate:.2%} (Score: {play_rate_score:.2f})",
                f"  Cost Efficiency: {cost_efficiency}"
            ])
        
        return "\n".join(output_lines)

    def get_cost_distribution(self, df):
        """Calculate the distribution of card costs"""
        total_cards = len(df)
        return {
            cost: len(df[df['Cost'] == cost]) / total_cards 
            for cost in range(1, 7)
        }

    def round_to_nearest_50(self, value):
        """Round a value to the nearest 50, with minimum of 100"""
        return max(100, round(value / 50) * 50)

    def get_max_total_stats(self, cost):
        """Calculate maximum total stats (ATK + DEF) allowed for a given energy cost"""
        return cost * 200

    def adjust_card_stats(self, stats: Dict):
        """Adjust card statistics while maintaining cost distribution and considering ultimate abilities"""
        adjustments = []
        
        # First normalize all existing stats
        for idx in self.cards_df.index:
            current_cost = self.cards_df.at[idx, 'Cost']
            current_atk = self.cards_df.at[idx, 'ATK']
            current_def = self.cards_df.at[idx, 'DEF']
            total_stats = current_atk + current_def
            max_allowed = self.get_max_total_stats(current_cost)
            
            # If total stats exceed maximum allowed, scale them down
            if total_stats > max_allowed:
                scale_factor = max_allowed / total_stats
                new_atk = self.round_to_nearest_50(current_atk * scale_factor)
                new_def = self.round_to_nearest_50(current_def * scale_factor)
                
                self.cards_df.at[idx, 'ATK'] = new_atk
                self.cards_df.at[idx, 'DEF'] = new_def
                
                adjustments.append({
                    'card_idx': idx,
                    'cost_adjust': 0,
                    'atk_adjust': new_atk - current_atk,
                    'def_adjust': new_def - current_def,
                    'reason': f"Scaled down stats to meet energy cost limit ({max_allowed} total)"
                })
        
        # Rest of the adjustment logic...
        # When making stat adjustments, ensure we don't exceed the energy-based limits
        for card_id, card_stats in stats['card_stats'].items():
            if card_id in ["Player 1", "Player 2"] or card_stats['plays'] < 5:
                continue
            
            # Find card in DataFrame
            name = card_id.split(" (")[0]
            variant = card_id[card_id.find("(")+1:card_id.find(")")]
            card_mask = (self.cards_df['Name'] == name) & (self.cards_df['Variant'] == variant)
            
            if not any(card_mask):
                continue
            
            card_idx = self.cards_df[card_mask].index[0]
            current_card = self.cards_df.iloc[card_idx]
            current_cost = current_card['Cost']
            max_allowed = self.get_max_total_stats(current_cost)
            
            # When making stat adjustments, ensure we don't exceed max total stats
            def calculate_safe_stat_adjustment(current_atk, current_def, proposed_atk_adj, proposed_def_adj):
                new_total = (current_atk + proposed_atk_adj) + (current_def + proposed_def_adj)
                if new_total > max_allowed:
                    scale_factor = max_allowed / new_total
                    return (
                        self.round_to_nearest_50(current_atk + proposed_atk_adj * scale_factor) - current_atk,
                        self.round_to_nearest_50(current_def + proposed_def_adj * scale_factor) - current_def
                    )
                return proposed_atk_adj, proposed_def_adj

            # Parse card info
            name = card_id.split(" (")[0]
            variant = card_id[card_id.find("(")+1:card_id.find(")")]
            
            # Find card in DataFrame
            card_mask = (self.cards_df['Name'] == name) & (self.cards_df['Variant'] == variant)
            if not any(card_mask):
                continue
                
            card_idx = self.cards_df[card_mask].index[0]
            current_card = self.cards_df.iloc[card_idx]
            
            # Calculate win rate and performance metrics
            win_rate = card_stats['wins'] / card_stats['plays']
            win_rate_diff = win_rate - self.target_win_rate
            avg_damage = card_stats['total_damage'] / card_stats['plays'] if 'total_damage' in card_stats else 0
            
            # Get ultimate power for this card
            ultimate_power, recommended_cost = self.evaluate_ultimate_power(name)
            
            # Adjust win rate expectations based on ultimate power
            expected_win_rate = self.target_win_rate * (1 + (ultimate_power * ULTIMATE_POWER_FACTOR))
            win_rate_diff = win_rate - expected_win_rate
            
            # Modify stat adjustments based on ultimate power
            stat_adjustment_factor = 1.0 - (ultimate_power * 0.5)  # Reduce stat changes for strong ultimates
            
            # Only adjust if win rate difference is significant
            if abs(win_rate_diff) > self.win_rate_tolerance:
                current_atk = current_card['ATK']
                current_def = current_card['DEF']
                
                if win_rate_diff > 0:  # Card is too strong
                    # Check if increasing cost would maintain distribution
                    if current_cost < 6:
                        new_dist = self.get_cost_distribution(self.cards_df)
                        new_dist[current_cost] = new_dist.get(current_cost, 0) - 1/len(self.cards_df)
                        new_dist[current_cost + 1] = new_dist.get(current_cost + 1, 0) + 1/len(self.cards_df)
                        
                        # Only allow cost increase if it doesn't deviate too much from original distribution
                        cost_change_allowed = all(
                            abs(new_dist.get(cost, 0) - self.get_cost_distribution(self.original_cards).get(cost, 0)) <= COST_DISTRIBUTION_TOLERANCE
                            for cost in range(1, 7)
                        )
                        
                        if cost_change_allowed and avg_damage > current_cost * (100 * (1 - ultimate_power)):
                            # Adjust cost threshold based on ultimate power
                            adjustments.append({
                                'card_idx': card_idx,
                                'cost_adjust': 1,
                                'atk_adjust': 0,
                                'def_adjust': 0,
                                'reason': f"High damage output with ultimate consideration"
                            })
                        else:
                            # Reduce stats more conservatively for cards with strong ultimates
                            new_atk, new_def = calculate_safe_stat_adjustment(current_atk, current_def, 0, 0)
                            
                            if new_atk < current_atk or new_def < current_def:
                                adjustments.append({
                                    'card_idx': card_idx,
                                    'cost_adjust': 0,
                                    'atk_adjust': new_atk - current_atk,
                                    'def_adjust': new_def - current_def,
                                    'reason': f"Reducing ATK (ultimate power: {ultimate_power:.2f})"
                                })
                else:  # Card is too weak
                    # Similar distribution check for cost decrease
                    if current_cost > 1:
                        new_dist = self.get_cost_distribution(self.cards_df)
                        new_dist[current_cost] = new_dist.get(current_cost, 0) - 1/len(self.cards_df)
                        new_dist[current_cost - 1] = new_dist.get(current_cost - 1, 0) + 1/len(self.cards_df)
                        
                        cost_change_allowed = all(
                            abs(new_dist.get(cost, 0) - self.get_cost_distribution(self.original_cards).get(cost, 0)) <= COST_DISTRIBUTION_TOLERANCE
                            for cost in range(1, 7)
                        )
                        
                        if cost_change_allowed and avg_damage < current_cost * (75 * (1 - ultimate_power)):
                            adjustments.append({
                                'card_idx': card_idx,
                                'cost_adjust': -1,
                                'atk_adjust': 0,
                                'def_adjust': 0,
                                'reason': f"Low damage considering ultimate power"
                            })
                        else:
                            # Buff stats more conservatively for cards with strong ultimates
                            new_atk, new_def = calculate_safe_stat_adjustment(current_atk, current_def, 0, 0)
                            
                            if new_atk > current_atk or new_def > current_def:
                                adjustments.append({
                                    'card_idx': card_idx,
                                    'cost_adjust': 0,
                                    'atk_adjust': new_atk - current_atk,
                                    'def_adjust': new_def - current_def,
                                    'reason': f"Buffing stats (ultimate power: {ultimate_power:.2f})"
                                })
        
        # Store adjustments for reporting
        self.current_adjustments = adjustments
        
        # Apply adjustments
        for adj in adjustments:
            idx = adj['card_idx']
            # Apply cost adjustment
            if adj['cost_adjust'] != 0:
                self.cards_df.at[idx, 'Cost'] = max(1, min(6, self.cards_df.at[idx, 'Cost'] + adj['cost_adjust']))
            
            # Apply stat adjustments
            if adj['atk_adjust'] != 0:
                current_atk = self.cards_df.at[idx, 'ATK']
                self.cards_df.at[idx, 'ATK'] = self.round_to_nearest_50(current_atk + adj['atk_adjust'])
            if adj['def_adjust'] != 0:
                current_def = self.cards_df.at[idx, 'DEF']
                self.cards_df.at[idx, 'DEF'] = self.round_to_nearest_50(current_def + adj['def_adjust'])
        
        # Final normalization to ensure all stats are proper multiples and within caps
        for idx in self.cards_df.index:
            current_cost = self.cards_df.at[idx, 'Cost']
            current_atk = self.cards_df.at[idx, 'ATK']
            current_def = self.cards_df.at[idx, 'DEF']
            total_stats = current_atk + current_def
            max_allowed = self.get_max_total_stats(current_cost)
            
            # If total stats exceed maximum allowed, scale them down
            if total_stats > max_allowed:
                scale_factor = max_allowed / total_stats
                new_atk = self.round_to_nearest_50(current_atk * scale_factor)
                new_def = self.round_to_nearest_50(current_def * scale_factor)
                
                self.cards_df.at[idx, 'ATK'] = new_atk
                self.cards_df.at[idx, 'DEF'] = new_def
        
        # Save current state to CSV after each adjustment
        self.cards_df.to_csv(self.working_file, index=False)

    def generate_detailed_changes(self):
        """Generate a detailed report of all card changes compared to original data"""
        changes = []
        
        # Compare each card in the balanced data with original
        for idx, balanced_card in self.cards_df.iterrows():
            original_card = self.original_cards[
                (self.original_cards['Name'] == balanced_card['Name']) & 
                (self.original_cards['Variant'] == balanced_card['Variant'])
            ].iloc[0]
            
            # Calculate differences
            atk_diff = balanced_card['ATK'] - original_card['ATK']
            def_diff = balanced_card['DEF'] - original_card['DEF']
            cost_diff = balanced_card['Cost'] - original_card['Cost']
            
            # Create Character instance to access ultimate ability
            character = self.create_character_from_data(balanced_card)
            ultimate = character.get_ultimate_ability()  # Now using Character instance
            
            # Only include cards that have changed
            if atk_diff != 0 or def_diff != 0 or cost_diff != 0 or ultimate:
                change_str = f"\n{balanced_card['Name']} ({balanced_card['Variant']})\n"
                change_str += "=" * 50 + "\n"
                
                # Format stat changes
                if atk_diff != 0:
                    change_str += f"ATK: {original_card['ATK']} -> {balanced_card['ATK']} "
                    change_str += f"({'+' if atk_diff > 0 else ''}{atk_diff})\n"
                
                if def_diff != 0:
                    change_str += f"DEF: {original_card['DEF']} -> {balanced_card['DEF']} "
                    change_str += f"({'+' if def_diff > 0 else ''}{def_diff})\n"
                
                if cost_diff != 0:
                    change_str += f"Cost: {original_card['Cost']} -> {balanced_card['Cost']} "
                    change_str += f"({'+' if cost_diff > 0 else ''}{cost_diff})\n"
                
                # Add ultimate ability info
                if ultimate:
                    change_str += "\nUltimate Ability:\n"
                    change_str += f"  Name: {ultimate.name}\n"
                    if hasattr(ultimate, 'damage_multiplier'):
                        change_str += f"  Damage Multiplier: x{ultimate.damage_multiplier}\n"
                    if hasattr(ultimate, 'healing'):
                        change_str += f"  Healing: {ultimate.healing}\n"
                    if hasattr(ultimate, 'status_effects'):
                        change_str += f"  Status Effects: {', '.join(ultimate.status_effects)}\n"
                    if hasattr(ultimate, 'cooldown'):
                        change_str += f"  Cooldown: {ultimate.cooldown} turns\n"
                
                changes.append(change_str)
        
        return changes

    def export_final_summary(self):
        """Export final balance summary to file"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        with open("balance_summary.txt", "w") as f:
            f.write("JJK CARD GAME BALANCE SUMMARY\n")
            f.write("=" * 50 + "\n")
            f.write(f"Generated: {timestamp}\n\n")
            f.write("CARD BALANCE SCORES\n")
            f.write("=" * 50 + "\n\n")
            
            # Sort cards by total score for display
            sorted_cards = sorted(self.card_balance_scores.items(), 
                                key=lambda x: x[1]['total_score'],
                                reverse=True)
            
            for card_name, scores in sorted_cards:
                f.write(f"\n{card_name}:\n")
                f.write(f"  Total Score: {scores['total_score']:.1f}/100\n")
                f.write(f"  Win Rate: {scores['win_rate']:.2f}% (Score: {scores['win_rate_score']})\n")
                f.write(f"  Damage Output: {scores['damage_output']:.1f} avg (Score: {scores['damage_score']:.2f})\n")
                f.write(f"  Play Rate: {scores['play_rate']:.2f}% (Score: {scores['play_rate_score']:.2f})\n")
                f.write(f"  Cost Efficiency: {scores['cost_efficiency']}\n")
                
                # Add Ultimate Ability Stats if they exist
                if card_name in self.current_stats['ultimate_stats']['total_uses']:
                    total_uses = self.current_stats['ultimate_stats']['total_uses'].get(card_name, 0)
                    total_damage = self.current_stats['ultimate_stats']['total_damage'].get(card_name, 0)
                    games_used = self.current_stats['ultimate_stats']['games_used'].get(card_name, 0)
                    total_games = self.current_stats['ultimate_stats']['total_games']
                    
                    avg_damage = total_damage / total_uses if total_uses > 0 else 0
                    usage_rate = (games_used / total_games * 100) if total_games > 0 else 0
                    
                    f.write(f"  Ultimate Stats:\n")
                    f.write(f"    Times Used: {total_uses}\n")
                    f.write(f"    Usage Rate: {usage_rate:.1f}% of games\n")
                    f.write(f"    Avg Damage: {avg_damage:.1f}\n")
                f.write("\n")

    def evaluate_ultimate_power(self, card_name: str) -> tuple[float, int]:
        """
        Evaluate the relative power level of a card's ultimate ability.
        Returns (power_score, recommended_energy_cost)
        """
        try:
            # Get card data from DataFrame
            card_data = self.cards_df[self.cards_df['Name'] == card_name]
            if card_data.empty:
                return (0.0, 1)
            
            # Convert Series to dict and create Character instance
            character = Character.from_card_data(card_data.iloc[0].to_dict())
            
            # Get ultimate ability
            ultimate = character.get_ultimate_ability()
            if not ultimate:
                return (0.0, 1)
            
            # Base power score on ultimate ability attributes
            power_score = 0.0
            
            # Consider damage multiplier
            power_score += min(ultimate.damage_multiplier / 3.0, 0.4)  # Cap at 0.4
            
            # Consider effects
            if ultimate.effects:
                # Add score for each effect
                for effect, value in ultimate.effects.items():
                    if effect == 'flat_damage':
                        power_score += min(value / 1000, 0.3)
                    elif effect == 'aoe_damage':
                        power_score += 0.3
                    elif effect == 'heal_self':
                        power_score += min(value / 500, 0.2)
                    elif effect == 'ignore_defense':
                        power_score += 0.2
                    elif effect == 'stun':
                        power_score += 0.2
                    elif effect == 'summon':
                        power_score += 0.3
                    else:
                        power_score += 0.1  # Default score for other effects
            
            # Calculate recommended energy cost based on power score
            recommended_cost = 1
            if power_score > 0.7:
                recommended_cost = 3
            elif power_score > 0.4:
                recommended_cost = 2
            
            return (min(power_score, 1.0), recommended_cost)
            
        except Exception as e:
            print(f"Error evaluating ultimate for {card_name}: {str(e)}")
            return (0.0, 1)

    def display_initial_menu(self) -> str:
        """Display menu and get simulation parameters."""
        print("\nJJK Card Game Balance Simulator")
        print("=" * 35)
        print(f"1. Balance Original Cards (characters.csv)")
        print(f"2. Re-balance Existing Balance (balanced_chars.csv)")
        print("3. View Current Balance Summary")
        print("4. Exit")
        
        choice = input("\nEnter your choice (1-4): ")
        
        if choice in ['1', '2']:
            try:
                print("\nEnter simulation parameters (higher values = longer runtime)")
                print("Recommended: 5 iterations, 20 battles per iteration")
                iterations = int(input("Number of iterations (1-100): "))
                battles = int(input("Battles per iteration (5-200): "))
                
                # Validate inputs within allowed ranges
                iterations = max(1, min(100, iterations))
                battles = max(5, min(200, battles))
                return choice, iterations, battles
                
            except ValueError:
                print("Invalid input. Using recommended values: 5 iterations, 20 battles")
                return choice, 5, 20
        
        return choice, None, None

    def run_single_detailed_battle(self) -> None:
        """Run a single battle with detailed logging of all events"""
        print("\nRunning Detailed Battle Simulation")
        print("=" * 50)
        
        # Initialize decks and players
        deck1 = Deck.load_deck(self.working_file)
        deck2 = Deck.load_deck(self.working_file)
        player1 = Player("Player 1", deck1)
        player2 = Player("Player 2", deck2)
        battle = Battle(player1, player2)
        
        # Initialize game log
        game_log = []
        game_log.append("JJK Card Game - Detailed Battle Log")
        game_log.append("=" * 50 + "\n")
        
        turn_counter = 1
        
        while True:  # Remove turn limit
            # Add player HP and energy status at start of turn
            turn_header = f"\nTurn {turn_counter}"
            status = (f"Player 1 LP: {player1.life_points}/2000 | Energy: {player1.energy}\n"
                     f"Player 2 LP: {player2.life_points}/2000 | Energy: {player2.energy}")
            
            print(turn_header)
            print("-" * 20)
            print(status)
            
            game_log.append(turn_header)
            game_log.append("-" * 20)
            game_log.append(status)
            
            # Process field state
            field_state = self._get_field_state(player1, player2)
            print(field_state)
            game_log.append(field_state)
            
            # Process hand state
            hand_state = self._get_hand_state(player1, player2)
            print(hand_state)
            game_log.append(hand_state)
            
            # Process turn for each player
            for active_player, defending_player in [(player1, player2), (player2, player1)]:
                if active_player.life_points <= 0 or defending_player.life_points <= 0:
                    continue
                
                phase_header = f"\n{active_player.name}'s Phase"
                print(phase_header)
                game_log.append(phase_header)
                
                phase_separator = "-" * 15
                print(phase_separator)
                game_log.append(phase_separator)
                
                # Draw phase
                drawn_card = active_player.draw_cards(1)
                if drawn_card and isinstance(drawn_card, list) and drawn_card:
                    draw_msg = f"Drew: {drawn_card[0].name} ({drawn_card[0].variant})"
                    print(draw_msg)
                    game_log.append(draw_msg)
                
                # Energy update
                old_energy = active_player.energy
                active_player.add_energy()
                energy_msg = f"Energy: {old_energy} -> {active_player.energy}"
                print(energy_msg)
                game_log.append(energy_msg)
                
                # Play cards
                play_log = self._process_card_playing(active_player)
                print(play_log)
                game_log.append(play_log)
                
                # Remove dead characters before combat
                active_player.field = [char for char in active_player.field if char.is_alive()]
                defending_player.field = [char for char in defending_player.field if char.is_alive()]
                
                # Combat phase
                combat_log = self._process_detailed_combat(active_player, defending_player, battle)
                print(combat_log)
                game_log.append(combat_log)
                
                # Check for game end
                if defending_player.life_points <= 0:
                    end_msg = f"\n{active_player.name} wins!"
                    print(end_msg)
                    game_log.append(end_msg)
                    
                    # Add ultimate usage stats to final stats
                    stats = []  # Initialize stats as a list
                    if battle.ability_usage_tracker:
                        stats.append("\nUltimate Ability Usage:")
                        for char_name, data in battle.ability_usage_tracker.items():
                            if data['times_used'] > 0:
                                stats.append(f"  {char_name}: {data['times_used']} times")
                                if data['abilities_used']:
                                    stats.append(f"    Abilities: {', '.join(data['abilities_used'])}")
                    
                    print("\n".join(stats))
                    game_log.append("\n".join(stats))
                    
                    # Write game log to file
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    log_file = f"game_log_{timestamp}.txt"
                    with open(log_file, 'w', encoding='utf-8') as f:
                        f.write('\n'.join(game_log))
                    print(f"\nDetailed game log saved to: {log_file}")
                    return
            
            # Cleanup phase - regenerate health for surviving characters
            for player in [player1, player2]:
                for char in player.field:
                    if char.is_alive():
                        char.regenerate_health()
            
            turn_counter += 1

    def _get_field_state(self, player1: Player, player2: Player) -> str:
        """Get field state as formatted string"""
        lines = ["\nField State:"]
        for player in [player1, player2]:
            lines.append(f"\n{player.name}'s Field:")
            if not player.field:
                lines.append("  Empty")
            for char in player.field:
                lines.append(f"  {char.name} ({char.variant})")
                lines.append(f"    HP: {char.current_health}/{char.def_val}")
                lines.append(f"    ATK: {char.atk}")
                ultimate = char.get_ultimate_ability()
                if ultimate:
                    lines.append(f"    Ultimate: {ultimate.name} (x{ultimate.damage_multiplier} damage)")
                    if ultimate.status_effects:
                        lines.append(f"    Status Effects: {', '.join(ultimate.status_effects)}")
        return '\n'.join(lines)

    def _get_hand_state(self, player1: Player, player2: Player) -> str:
        """Get hand state as formatted string"""
        lines = ["\nHand State:"]
        for player in [player1, player2]:
            lines.append(f"\n{player.name}'s Hand ({len(player.hand)} cards):")
            for card in player.hand:
                lines.append(f"  {card.name} ({card.variant}) - Cost: {card.cost}")
        return '\n'.join(lines)

    def _process_card_playing(self, player: Player) -> str:
        """Process card playing and return log string"""
        lines = ["\nPlaying Cards:"]
        playable_cards = [card for card in player.hand if card.cost <= player.energy]
        if not playable_cards:
            lines.append("  No playable cards")
            return '\n'.join(lines)
            
        for card in playable_cards[:2]:  # Can play up to 2 cards
            if player.energy >= card.cost:
                player.play_card(card)
                lines.append(f"  Played {card.name} ({card.variant})")
                lines.append(f"  Energy remaining: {player.energy}")
        return '\n'.join(lines)

    def _process_detailed_combat(self, attacker: Player, defender: Player, battle: Battle) -> str:
        """Process combat and return detailed log"""
        lines = ["\nCombat Phase:"]
        
        # Sort attackers by their readiness to use ultimates
        attackers = sorted(attacker.field, 
                          key=lambda x: (
                              1 if (x.get_ultimate_ability() and 
                                   x.energy >= x.ultimate_energy_cost) else 0,
                          x.atk
                      ),
                          reverse=True)
        
        for character in attackers:
            ultimate = character.get_ultimate_ability()
            
            # Check if ultimate can be used with increased likelihood
            if ultimate and defender.field and attacker.energy >= attacker.ultimate_energy_cost:
                print(f"{attacker.name} is attempting to use ultimate: {ultimate.name} with energy: {attacker.energy}")
                if random.random() < 1.0:  # 100% chance to use ultimate
                    print(f"{attacker.name} successfully uses ultimate: {ultimate.name}")
                    target = max(defender.field, 
                                key=lambda x: x.current_health)  # Target highest HP
                    
                    # Use ultimate
                    damage = character.use_ultimate(target)
                    if damage > 0:
                        # Track ultimate usage and damage
                        battle.damage_stats['ultimate_damage'][character.name] = \
                            battle.damage_stats['ultimate_damage'].get(character.name, 0) + damage
                        battle.damage_stats['total_damage'] += damage
                        
                        # Update ability usage tracker
                        if character.name in battle.ability_usage_tracker:
                            battle.ability_usage_tracker[character.name]['times_used'] += 1
                            battle.ability_usage_tracker[character.name]['abilities_used'].append(ultimate.name)
                        
                        # Log the ultimate usage
                        lines.extend([
                            f"  {character.name} uses ultimate ability!",
                            f"  Ultimate damage: {damage}",
                            f"  {target.name}'s remaining HP: {target.current_health}",
                            f"  Remaining energy: {character.energy}"
                        ])
                        continue  # Skip regular attack if ultimate was used

        # Regular attack logic
        if defender.field:
            target = max(defender.field, key=lambda x: x.atk)
            damage = character.atk
            actual_damage = target.take_damage(damage)
            battle.damage_stats['direct_damage'][character.name] = \
                battle.damage_stats['direct_damage'].get(character.name, 0) + actual_damage
            battle.damage_stats['total_damage'] += actual_damage
            
            lines.append(f"  {character.name} attacks {target.name} for {actual_damage} damage")
            lines.append(f"  {target.name}'s remaining HP: {target.current_health}")
        else:
            # Direct attack to player
            damage = character.atk
            defender.take_damage(damage)
            battle.damage_stats['direct_damage'][character.name] = \
                battle.damage_stats['direct_damage'].get(character.name, 0) + damage
            battle.damage_stats['total_damage'] += damage
            
            lines.append(f"  {character.name} attacks directly for {damage} damage")
            lines.append(f"  {defender.name}'s remaining LP: {defender.life_points}")
        
        # Add energy after attacking
        character.add_energy()
        print(f"{character.name} gains energy (now {character.energy})")
        
        return '\n'.join(lines)

    def _get_final_stats(self, battle: Battle) -> str:
        """Get final battle statistics as formatted string."""
        stats = ["\nBattle Statistics", "=" * 50]
        
        # Process direct damage (only show characters that dealt damage)
        active_chars = {name: damage for name, damage in battle.damage_stats['direct_damage'].items() 
                       if damage > 0}
        if active_chars:
            stats.append("\nDirect Damage:")
            for char_name, damage in sorted(active_chars.items(), key=lambda x: x[1], reverse=True):
                stats.append(f"  {char_name}: {damage}")
        
        # Process ultimate damage (only show characters that used ultimates)
        ultimate_chars = {name: damage for name, damage in battle.damage_stats['ultimate_damage'].items() 
                         if damage > 0}
        if ultimate_chars:
            stats.append("\nUltimate Damage:")
            for char_name, damage in sorted(ultimate_chars.items(), key=lambda x: x[1], reverse=True):
                stats.append(f"  {char_name}: {damage}")
        
        # Process effect damage (only show characters that dealt effect damage)
        effect_chars = {name: damage for name, damage in battle.damage_stats['effect_damage'].items() 
                       if damage > 0}
        if effect_chars:
            stats.append("\nEffect Damage:")
            for char_name, damage in sorted(effect_chars.items(), key=lambda x: x[1], reverse=True):
                stats.append(f"  {char_name}: {damage}")
        
        # Add ultimate usage statistics if any were used
        if battle.ability_usage_tracker:
            ultimate_usage = {name: data for name, data in battle.ability_usage_tracker.items() 
                             if data['times_used'] > 0}
            if ultimate_usage:
                stats.append("\nUltimate Ability Usage:")
                for char_name, data in sorted(ultimate_usage.items(), 
                                            key=lambda x: x[1]['times_used'], 
                                            reverse=True):
                    stats.append(f"  {char_name}: {data['times_used']} times")
                    if data['abilities_used']:
                        stats.append(f"    Abilities: {', '.join(data['abilities_used'])}")
        
        # Add total damage at the end
        total_damage = battle.damage_stats['total_damage']
        if total_damage > 0:
            stats.append(f"\nTotal Damage Dealt: {total_damage}")
        else:
            stats.append("\nNo damage was dealt during this battle.")
        
        return '\n'.join(stats)

    def analyze_ultimate_usage(self, battle_records: List[Dict]) -> str:
        """Analyze ultimate ability usage across all simulated battles."""
        ultimate_stats = {
            'total_uses': {},        # Total times each ultimate was used
            'games_used': {},        # Number of games where each ultimate was used
            'total_games': len(battle_records),
            'total_damage': {},      # Total damage dealt by each ultimate
            'avg_damage_per_use': {},# Average damage per ultimate use
            'ultimate_success': {},  # Track successful ultimate activations
            'ultimate_attempts': {}  # Track total ultimate attempts
        }
        
        # Process each battle's records
        for battle in battle_records:
            used_in_game = set()  # Track which ultimates were used in this game
            
            # Process ultimate damage stats
            for char_name, damage in battle.damage_stats['ultimate_damage'].items():
                if damage > 0:
                    # Update total uses and damage
                    ultimate_stats['total_uses'][char_name] = ultimate_stats['total_uses'].get(char_name, 0) + 1
                    ultimate_stats['total_damage'][char_name] = ultimate_stats['total_damage'].get(char_name, 0) + damage
                    used_in_game.add(char_name)
            
            # Update games_used counter
            for char_name in used_in_game:
                ultimate_stats['games_used'][char_name] = ultimate_stats['games_used'].get(char_name, 0) + 1
            
            # Track attempts and successes from ability usage tracker
            for char_name, data in battle.ability_usage_tracker.items():
                if data['times_used'] > 0:
                    ultimate_stats['ultimate_success'][char_name] = ultimate_stats['ultimate_success'].get(char_name, 0) + data['times_used']
        
        # Calculate averages and format report
        report = ["\nUltimate Ability Usage Analysis", "=" * 50]
        
        if ultimate_stats['total_uses']:
            # Calculate average uses per game for all ultimates
            total_ultimate_uses = sum(ultimate_stats['total_uses'].values())
            avg_ultimates_per_game = total_ultimate_uses / ultimate_stats['total_games']
            report.append(f"\nAverage Ultimate Uses Per Game: {avg_ultimates_per_game:.2f}")
            
            # Sort characters by total uses
            sorted_chars = sorted(ultimate_stats['total_uses'].items(), 
                                key=lambda x: x[1], 
                                reverse=True)
            
            report.append("\nDetailed Ultimate Usage Statistics:")
            report.append("-" * 30)
            
            for char_name, total_uses in sorted_chars:
                games_used = ultimate_stats['games_used'][char_name]
                total_damage = ultimate_stats['total_damage'].get(char_name, 0)
                avg_damage = total_damage / total_uses if total_uses > 0 else 0
                usage_rate = (games_used / ultimate_stats['total_games']) * 100
                success_rate = ultimate_stats['ultimate_success'].get(char_name, 0)
                
                report.extend([
                    f"\n{char_name}:",
                    f"  Total Ultimate Uses: {total_uses}",
                    f"  Games Used: {games_used}/{ultimate_stats['total_games']} ({usage_rate:.1f}%)",
                    f"  Average Damage Per Ultimate: {avg_damage:.1f}",
                    f"  Total Ultimate Damage: {total_damage}",
                    f"  Successful Activations: {success_rate}"
                ])
        else:
            report.append("\nNo ultimate abilities were used during the simulation.")
        
        return '\n'.join(report)

    def _calculate_cost_efficiency(self, card_data: Dict) -> float:
        """Calculate cost efficiency score for a card"""
        cost = card_data.get('Cost', 1)
        atk = card_data.get('ATK', 0)
        def_ = card_data.get('DEF', 0)
        
        # Base power calculation
        base_power = atk + (def_ * 0.6)
        expected_power = {
            1: 150,
            2: 200,
            3: 300,
            4: 450,
            5: 650,
            6: 900,
            7: 1200
        }.get(cost, 150)
        
        # Calculate efficiency ratio
        efficiency = base_power / expected_power if expected_power > 0 else 0
        
        # Convert to 0-10 score
        score = min(10, max(0, efficiency * 10))
        return score

    def create_character_from_data(self, card_data: dict) -> Character:
        """Create a Character instance from card data."""
        try:
            # Convert Series to dict if needed
            if hasattr(card_data, 'to_dict'):
                card_data = card_data.to_dict()
            
            # Create character instance using the from_card_data method
            character = Character.from_card_data(card_data)
            
            return character
        
        except Exception as e:
            print(f"Error creating character from data: {str(e)}")
            raise

    def load_characters(self, csv_file: str) -> pd.DataFrame:
        """Load character data from CSV file."""
        try:
            df = pd.read_csv(csv_file)
            required_columns = ['Name', 'Variant', 'Cost', 'ATK', 'DEF', 'Effect', 'Ultimate Move', 'Ultimate Cost']
            
            # Verify all required columns exist
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                raise ValueError(f"Missing required columns: {missing_columns}")
            
            # Ensure Ultimate Cost is numeric and has valid values
            df['Ultimate Cost'] = pd.to_numeric(df['Ultimate Cost'], errors='coerce').fillna(1)
            df['Ultimate Cost'] = df['Ultimate Cost'].astype(int)
            
            # Validate Ultimate Cost values
            invalid_costs = df[~df['Ultimate Cost'].between(1, 4)]
            if not invalid_costs.empty:
                print(f"Warning: Found invalid Ultimate Costs. Setting to default value 1 for: {invalid_costs['Name'].tolist()}")
                df.loc[invalid_costs.index, 'Ultimate Cost'] = 1
            
            print(df.head())  # Log the first few rows of the DataFrame
            return df
        
        except Exception as e:
            raise ValueError(f"Error loading character data: {str(e)}")

    def run_detailed_battle(self, player1: Player, player2: Player) -> str:
        """Run a single detailed battle with full logging"""
        battle = Battle(player1, player2)
        
        # Initialize log
        log = ["DETAILED BATTLE LOG", "=" * 50, ""]
        
        # Initial state
        log.append(self._get_field_state(player1, player2))
        log.append(self._get_hand_state(player1, player2))
        
        # Process turns until game ends
        turn = 1
        while turn <= 50:  # Max 50 turns
            log.append(f"\nTurn {turn}")
            log.append("-" * 20)
            
            # Player 1's turn
            log.append(f"\n{player1.name}'s Turn:")
            log.append(self._process_card_playing(player1))
            log.append(self._process_detailed_combat(player1, player2, battle))
            
            if player2.life_points <= 0:
                log.append(f"\n{player1.name} wins!")
                break
            
            # Player 2's turn
            log.append(f"\n{player2.name}'s Turn:")
            log.append(self._process_card_playing(player2))
            log.append(self._process_detailed_combat(player2, player1, battle))
            
            if player1.life_points <= 0:
                log.append(f"\n{player2.name} wins!")
                break
            
            turn += 1
        
        # Add final statistics
        log.append(self._get_final_stats(battle))
        
        return "\n".join(log)

def run_balance_simulator(dataset_choice: str):
    """Run the balance simulator with the selected dataset"""
    if dataset_choice == "1":
        initial_cards = load_characters("characters.csv")
        print("\nLoading original characters from characters.csv")
    elif dataset_choice == "2":
        if os.path.exists("balanced_chars.csv"):
            initial_cards = pd.read_csv("balanced_chars.csv")
            print("\nLoading previously balanced characters from balanced_chars.csv")
        else:
            print("\nNo balanced_chars.csv found. Please run option 1 first.")
            return None
    else:
        print("Invalid choice. Please enter 1 or 2.")
        return None

    if initial_cards is None:
        print("Failed to load the selected dataset.")
        return None

    print("\nLoading original characters from characters.csv\n")
    print("Initializing balance simulator...")
    print("Created new balanced_chars.csv\n")
    print("Enter simulation parameters:")
    print("Recommended: 5 iterations, 20 battles per iteration")
    num_iterations = int(input("Number of iterations (1-100): "))  # Increased from 20
    num_iterations = max(1, min(100, num_iterations))
    
    battles_per_iteration = int(input("Battles per iteration (5-200): "))  # Increased from 50
    battles_per_iteration = max(5, min(200, battles_per_iteration))
    
    print("\nRunning balance iterations...")
    print("Note: Original characters.csv will be preserved")
    print("      All balance changes will be saved to balanced_chars.csv")
    
    simulator = BalanceSimulator(
        initial_cards,
        target_win_rate=0.5,
        win_rate_tolerance=0.05
    )
    
    balanced_cards = simulator.run_balance_iterations(
        num_iterations=num_iterations,
        battles_per_iteration=battles_per_iteration
    )
    
    if balanced_cards is not None:
        simulator.export_final_summary()
        print(f"\nBalance simulation complete!")
        print(f"Original characters.csv remains unchanged")
        print(f"Balanced cards saved to: {simulator.working_file}")
        print(f"Complete summary saved to: balance_summary.txt")
    else:
        print("\nBalance simulation failed!")

def show_menu():
    """Display the balance simulator menu"""
    while True:
        print("\nJJK Card Game Balance Simulator")
        print("=" * 35)
        print("1. Balance Original Cards (characters.csv)")
        print("2. Re-balance Existing Balance (balanced_chars.csv)")
        print("3. View Current Balance Summary")
        print("4. Run Detailed Single Battle")
        print("5. Exit")
        
        choice = input("\nEnter your choice (1-5): ")
        
        if choice == "1" or choice == "2":
            run_balance_simulator(choice)
        elif choice == "3":
            if os.path.exists("balance_summary.txt"):
                print("\nCurrent Balance Summary:")
                print("=" * 25)
                with open("balance_summary.txt", 'r') as f:
                    print(f.read())
            else:
                print("\nNo balance summary available. Run a balance simulation first.")
        elif choice == "4":
            simulator = BalanceSimulator(pd.read_csv("characters.csv"))
            simulator.run_single_detailed_battle()
        elif choice == "5":
            print("\nExiting balance simulator...")
            break
        else:
            print("\nInvalid choice. Please enter a number between 1 and 5.")

if __name__ == "__main__":
    show_menu() 