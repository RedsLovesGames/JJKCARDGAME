"""
Player Class for JJK Card Game
Manages player state, hand, field, and card interactions during gameplay.
Handles resource management (life points, energy) and card placement rules.
"""

from typing import List
from base_types import BasePlayer, BaseDeck
from character import Character

class Player(BasePlayer):
    """
    Represents a player in the JJK Card Game.
    
    Manages the player's game state including:
    - Hand of cards
    - Field of played characters
    - Life points and energy resources
    - Card playing mechanics
    
    Each player has a deck of cards, can draw and play characters,
    and manages their resources during the game.
    """

    def __init__(self, name: str, deck: BaseDeck):
        """
        Initialize a new player with a deck.
        
        Args:
            name: Player's name identifier
            deck: Deck of cards for the player
            
        The player starts with:
        - Empty hand and field
        - 2000 life points
        - 0 energy (max 10)
        - 5 cards drawn from deck
        """
        super().__init__(name)
        self.deck = deck
        self.hand = []  # List of Character objects
        self.field = []  # List of Character objects
        self.life_points = 2000
        self.energy = 0
        self.max_energy = 10
        self.active_effects = {}  # Track active effects on player
        
        # Draw initial hand
        self.draw_cards(5)

    def is_alive(self) -> bool:
        """
        Check if player has life points remaining.
        
        Returns:
            bool: True if player has > 0 life points
        """
        return self.life_points > 0

    def can_play_to_field(self) -> bool:
        """
        Check if player can add more cards to field.
        
        Returns:
            bool: True if field has less than 5 cards
        """
        return len(self.field) < 5  # Maximum 5 cards on field

    def draw_cards(self, count: int = 1) -> bool:
        """
        Draw specified number of cards from deck to hand.
        
        Args:
            count: Number of cards to draw (default 1)
            
        Returns:
            bool: True if cards were successfully drawn
        """
        drawn = self.deck.draw(count)
        if drawn:
            self.hand.extend(drawn)  # Cards are already Character objects
            return True
        return False

    def can_play_card(self, character: Character) -> bool:
        """
        Check if a card can be played from hand.
        
        Verifies:
        - Player has enough energy for card's cost
        - Field has space for another card
        
        Args:
            character: Character card to check
            
        Returns:
            bool: True if card can be played
        """
        return (character.cost <= self.energy and 
                len(self.field) < 5)

    def play_card(self, character: Character) -> bool:
        """
        Attempt to play a character from hand to field.
        
        Verifies:
        - Card is in player's hand
        - Player has enough energy
        - Field has space
        
        Args:
            character: Character card to play
            
        Returns:
            bool: True if card was successfully played
        """
        if character in self.hand and character.cost <= self.energy and len(self.field) < 5:
            self.hand.remove(character)
            self.field.append(character)
            self.energy -= character.cost
            return True
        return False

    def take_damage(self, amount: int) -> None:
        """
        Apply damage to player's life points.
        
        Args:
            amount: Amount of damage to take
        """
        self.life_points = max(0, self.life_points - amount)

    def add_energy(self, amount: int = 1) -> None:
        """
        Add energy to player's pool, up to max_energy.
        
        Args:
            amount: Amount of energy to add (default 1)
        """
        self.energy = min(self.max_energy, self.energy + amount) 