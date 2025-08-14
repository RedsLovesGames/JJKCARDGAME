import random

class Deck:
    def build_initial_deck(self):
        """Build the initial deck from the provided cards DataFrame."""
        self.cards = []
        for cost in range(1, 7):  # Assuming costs range from 1 to 6
            cost_cards = self.cards_df[self.cards_df['Cost'] == cost].to_dict('records')
            
            # Check if cost_cards is empty
            if not cost_cards:
                print(f"No cards available for cost {cost}.")  # Debugging line
                continue  # Skip to the next cost
            
            # Randomly select a card from cost_cards
            card = random.choice(cost_cards)
            self.cards.append(card) 