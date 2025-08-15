import random
from typing import List, Dict, Any
import pandas as pd
from base_types import BaseDeck
from character import Character

class Deck(BaseDeck):
    # Ideal distribution of cards by cost (total should be 40)
    COST_DISTRIBUTION = {
        1: 8,  # 8 one-cost cards
        2: 10, # 10 two-cost cards
        3: 8,  # 8 three-cost cards
        4: 6,  # 6 four-cost cards
        5: 4,  # 4 five-cost cards
        6: 3,  # 3 six-cost cards
        7: 1   # 1 seven-cost card
    }

    def __init__(self, cards_df: pd.DataFrame, size: int = 40):
        self.cards_df = self.standardize_column_names(cards_df)
        self.size = size
        self.cards = self.build_initial_deck(self.cards_df)
        self.graveyard = []  # Add graveyard list
        self.win_rates = {}  # Format: {'card_name': {'total': 0.0, 'by_frequency': 0.0}}
        self.play_counts = {}
        
    def standardize_column_names(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df.columns = [col.lower() for col in df.columns]
        df = df.loc[:, ~df.columns.duplicated(keep='first')]
        
        column_mapping = {
            'name': 'Name', 'variant': 'Variant', 'cost': 'Cost', 'atk': 'ATK', 'def': 'DEF',
            'effect': 'Effect', 'ultimate': 'Ultimate Move', 'ultimate_move': 'Ultimate Move',
            'ultimate ability': 'Ultimate Move', 'ultimate_ability': 'Ultimate Move',
            'ultimatemove': 'Ultimate Move', 'ultimate attack': 'Ultimate Move'
        }
        
        for old_name, new_name in column_mapping.items():
            if old_name in df.columns:
                df = df.rename(columns={old_name: new_name})
        
        required_columns = {'Name', 'Variant', 'Cost', 'ATK', 'DEF', 'Effect', 'Ultimate Move'}
        for col in required_columns - set(df.columns):
            if col == 'Effect':
                df[col] = ''
            elif col == 'Variant':
                df[col] = 'Standard'
            elif col == 'Ultimate Move':
                df[col] = df.apply(lambda row: f"{row['Name']}'s Ultimate -- 200 damage", axis=1)
        
        df['Cost'] = pd.to_numeric(df['Cost'], errors='coerce').fillna(1).astype(int)
        df['ATK'] = pd.to_numeric(df['ATK'], errors='coerce').fillna(0).astype(int)
        df['DEF'] = pd.to_numeric(df['DEF'], errors='coerce').fillna(0).astype(int)
        df['Effect'] = df['Effect'].fillna('')
        df['Variant'] = df['Variant'].fillna('Standard')
        
        return df
        
    def build_initial_deck(self, cards_df: pd.DataFrame) -> List[Character]:
        """Build the initial deck from the provided cards DataFrame."""
        print("Building initial deck...")  # Debug output
        cards_df = cards_df.copy()
        valid_cards = cards_df[cards_df['ATK'].notna() & cards_df['DEF'].notna()].to_dict('records')
        
        if not valid_cards:
            raise ValueError("No valid cards found in the deck")
        
        print(f"Found {len(valid_cards)} valid cards")  # Debug output
        
        selected_cards = []
        card_counts = {}
        
        # Group cards by cost
        cards_by_cost = {}
        for card in valid_cards:
            cost = min(max(card.get('Cost', 1), 1), 7)  # Safely get cost with default
            if cost not in cards_by_cost:
                cards_by_cost[cost] = []
            cards_by_cost[cost].append(card)
        
        print(f"Cards by cost: {[f'Cost {k}: {len(v)}' for k,v in cards_by_cost.items()]}")  # Debug output
        
        # Fill deck according to cost distribution
        for cost, target_count in self.COST_DISTRIBUTION.items():
            if cost not in cards_by_cost or not cards_by_cost[cost]:
                print(f"Warning: No cards available for cost {cost}")  # Debug output
                continue
                
            cost_cards = cards_by_cost[cost]
            cards_added = 0
            attempts = 0
            max_attempts = target_count * 3
            
            while cards_added < target_count and attempts < max_attempts:
                card = random.choice(cost_cards)
                card_id = f"{card['Name']} ({card.get('Variant', 'Standard')})"
                
                if card_counts.get(card_id, 0) < 3:  # Maximum 3 copies of each card
                    try:
                        character = self.create_character_from_data(card)
                        selected_cards.append(character)
                        card_counts[card_id] = card_counts.get(card_id, 0) + 1
                        cards_added += 1
                    except Exception as e:
                        print(f"Error creating character from card {card_id}: {str(e)}")  # Debug output
                attempts += 1
            
            if cards_added < target_count:
                print(f"Warning: Only added {cards_added}/{target_count} cards for cost {cost}")  # Debug output
        
        # If we don't have enough cards, fill with valid cards
        while len(selected_cards) < self.size:
            # Get all available costs
            available_costs = sorted(cards_by_cost.keys())
            if not available_costs:
                break
            
            cost = random.choice(available_costs)
            card = random.choice(cards_by_cost[cost])
            card_id = f"{card['Name']} ({card.get('Variant', 'Standard')})"
            
            if card_counts.get(card_id, 0) < 3:
                try:
                    character = self.create_character_from_data(card)
                    selected_cards.append(character)
                    card_counts[card_id] = card_counts.get(card_id, 0) + 1
                except Exception as e:
                    print(f"Error creating character from card {card_id}: {str(e)}")  # Debug output
                    continue
        
        print(f"Final deck size: {len(selected_cards)}")  # Debug output
        if len(selected_cards) < self.size:
            print(f"Warning: Could only create {len(selected_cards)}/{self.size} cards")
        
        random.shuffle(selected_cards)
        return selected_cards
    
    def adjust_deck(self, win_rate_threshold: float = 0.45):
        for card_name, win_rate in self.win_rates.items():
            if win_rate < win_rate_threshold and self.play_counts[card_name] > 5:
                self.replace_card(card_name)
    
    def replace_card(self, card_name: str):
        for i, character in enumerate(self.cards):
            if character.name == card_name:
                cost = character.cost
                potential_replacements = [c for c in self.cards_df.to_dict('records') 
                                       if c['Cost'] == cost and c['Name'] != card_name]
                if potential_replacements:
                    try:
                        replacement_card = random.choice(potential_replacements)
                        self.cards[i] = self.create_character_from_data(replacement_card)
                    except Exception:
                        continue
                break
    
    def update_card_performance(self, card_name: str, variant: str, won: bool):
        """Update both total and frequency-adjusted win rates"""
        card_id = f"{card_name} ({variant})"
        if card_id not in self.play_counts:
            self.play_counts[card_id] = 0
            self.win_rates[card_id] = {'total': 0.0, 'by_frequency': 0.0}
            
        self.play_counts[card_id] += 1
        total_plays = self.play_counts[card_id]
        
        # Update total win rate
        current_wins = self.win_rates[card_id]['total'] * (total_plays - 1)
        new_wins = current_wins + (1 if won else 0)
        self.win_rates[card_id]['total'] = new_wins / total_plays
        
        # Update frequency-adjusted win rate
        frequency = total_plays / sum(self.play_counts.values())
        self.win_rates[card_id]['by_frequency'] = self.win_rates[card_id]['total'] / frequency
    
    def draw(self, count: int) -> List[Character]:
        if not self.cards:
            return []
        count = min(count, len(self.cards))
        drawn_cards = self.cards[:count]
        self.cards = self.cards[count:]
        return drawn_cards
    
    def shuffle(self):
        random.shuffle(self.cards)
    
    def add_cards(self, cards: List[Character]):
        self.cards.extend(cards)
        self.shuffle()

    def cards_remaining(self) -> int:
        return len(self.cards)

    def send_to_graveyard(self, card: Character):
        """Send a card to the graveyard"""
        self.graveyard.append(card)
        
    def get_card_count(self, card_name: str, variant: str) -> int:
        """Get the count of a specific card (including variant) in the deck"""
        return sum(1 for card in self.cards 
                  if card.name == card_name and card.variant == variant)

    @staticmethod
    def load_deck(file_path: str) -> 'Deck':
        try:
            cards_df = pd.read_csv(file_path)
            return Deck(cards_df)
        except Exception as e:
            raise ValueError(f"Error loading deck: {e}")

    def draw_card(self):
        return self.cards.pop() if self.cards else None

    def create_character_from_data(self, card_data: dict) -> Character:
        """Create a Character instance from card data."""
        character = Character(
            name=card_data['Name'],
            variant=card_data.get('Variant', 'Standard'),  # Ensure variant is retrieved correctly
            cost=card_data['Cost'],
            atk=card_data['ATK'],
            def_=card_data['DEF'],
            effect=card_data.get('Effect', ''),
            ultimate=card_data.get('Ultimate Move', ''),
            ultimate_cost=card_data.get('Ultimate Cost', 1)  # Use the Ultimate Cost from CSV
        )
        
        # Now use the character instance to get the ultimate ability
        ultimate = character.get_ultimate_ability()  # Call the new method
        
        # Set the ultimate ability to the character
        character.ultimate = ultimate
        
        return character
