from __future__ import annotations

from typing import Dict, Optional

from .game_engine import GameEngine


class GameAPI:
    """Serializable API layer for engine commands."""

    def __init__(self, cards_path: Optional[str] = None):
        self.engine = GameEngine(cards_path=cards_path)

    def start_game(self, seed: Optional[int], mode: str) -> Dict:
        return self.engine.start_game(seed=seed, mode=mode)

    def play_card(self, player_id: int, hand_index: int) -> Dict:
        return self.engine.play_card(player_id=player_id, hand_index=hand_index)

    def attack(self, attacker_id, target_id) -> Dict:
        return self.engine.attack(attacker_id=attacker_id, target_id=target_id)

    def end_turn(self) -> Dict:
        return self.engine.end_turn()

    def get_state(self) -> Dict:
        return self.engine.get_state()
