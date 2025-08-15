"""Base type definitions to prevent circular imports"""
from typing import List, Dict, Any, Optional

class BaseCharacter:
    def __init__(self, name: str, variant: str, cost: int, atk: int, def_: int, 
                 effect: str = '', ultimate: str = ''):
        self.name = name
        self.variant = variant
        self.cost = cost
        self.atk = atk
        self.def_val = def_
        self.max_health = def_
        self.current_health = def_
        self.effect = effect
        self.ultimate = ultimate

class BasePlayer:
    def __init__(self, name: str):
        self.name = name

class BaseDeck:
    def __init__(self):
        self.cards = [] 