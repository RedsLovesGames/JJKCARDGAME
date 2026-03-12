from __future__ import annotations

import random
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import pandas as pd

from deck import Deck
from player import Player


@dataclass(frozen=True)
class EntityRef:
    """Serializable identifier for cards on field."""

    player_id: int
    index: int

    def as_id(self) -> str:
        return f"p{self.player_id}:f{self.index}"


class GameEngine:
    """Pure game engine that is independent of any UI framework."""

    def __init__(self, cards_path: Optional[str] = None):
        self.cards_path = cards_path or str(Path(__file__).resolve().parents[1] / "characters.csv")
        self.mode: str = "pvp"
        self.turn: int = 1
        self.current_player_id: int = 0
        self.players: List[Player] = []
        self.winner_id: Optional[int] = None
        self.last_action: str = ""

    def start_game(self, seed: Optional[int] = None, mode: str = "pvp") -> Dict:
        if seed is not None:
            random.seed(seed)

        self.mode = mode
        self.turn = 1
        self.current_player_id = 0
        self.winner_id = None
        self.last_action = "Game started"

        characters_df = pd.read_csv(self.cards_path)
        deck1 = Deck(characters_df)
        deck2 = Deck(characters_df)
        p1 = Player("Player 1", deck1)
        p2 = Player("Player 2", deck2)
        p1.add_energy(1)
        self.players = [p1, p2]
        return self.get_state()

    def play_card(self, player_id: int, hand_index: int) -> Dict:
        self._ensure_started()
        self._ensure_turn_player(player_id)

        player = self.players[player_id]
        if hand_index < 0 or hand_index >= len(player.hand):
            raise ValueError("hand_index out of range")

        card = player.hand[hand_index]
        if not player.play_card(card):
            raise ValueError("Card cannot be played (insufficient energy or field full)")

        self.last_action = f"{player.name} played {card.name}"
        return self.get_state()

    def attack(self, attacker_id, target_id) -> Dict:
        self._ensure_started()
        attacker_ref = self._parse_ref(attacker_id)
        target_ref = self._parse_ref(target_id) if target_id is not None else None

        self._ensure_turn_player(attacker_ref.player_id)
        attacker_owner = self.players[attacker_ref.player_id]
        defender_owner = self.players[1 - attacker_ref.player_id]

        attacker = self._get_field_card(attacker_ref)
        if target_ref is None:
            defender_owner.take_damage(attacker.atk)
            self.last_action = f"{attacker.name} attacked {defender_owner.name} directly for {attacker.atk}"
        else:
            target = self._get_field_card(target_ref)
            damage = target.take_damage(attacker.atk)
            self.last_action = f"{attacker.name} attacked {target.name} for {damage}"
            if not target.is_alive():
                self.players[target_ref.player_id].field.pop(target_ref.index)

        self._update_winner()
        return self.get_state()

    def end_turn(self) -> Dict:
        self._ensure_started()
        self.current_player_id = 1 - self.current_player_id
        self.turn += 1

        current = self.players[self.current_player_id]
        current.add_energy(1)
        current.draw_cards(1)
        self.last_action = f"Turn ended. {current.name}'s turn."
        return self.get_state()

    def get_state(self) -> Dict:
        players_state = []
        for player_id, player in enumerate(self.players):
            hand = [
                {
                    "name": c.name,
                    "variant": c.variant,
                    "cost": c.cost,
                    "atk": c.atk,
                    "defense": c.def_val,
                    "current_health": c.current_health,
                }
                for c in player.hand
            ]
            field = [
                {
                    "id": EntityRef(player_id, idx).as_id(),
                    "name": c.name,
                    "variant": c.variant,
                    "cost": c.cost,
                    "atk": c.atk,
                    "defense": c.def_val,
                    "current_health": c.current_health,
                }
                for idx, c in enumerate(player.field)
            ]

            players_state.append(
                {
                    "player_id": player_id,
                    "name": player.name,
                    "life_points": player.life_points,
                    "energy": player.energy,
                    "deck_count": player.deck.cards_remaining(),
                    "hand": hand,
                    "field": field,
                }
            )

        return {
            "mode": self.mode,
            "turn": self.turn,
            "current_player_id": self.current_player_id,
            "winner_id": self.winner_id,
            "last_action": self.last_action,
            "players": players_state,
        }

    def _ensure_started(self) -> None:
        if not self.players:
            raise ValueError("Game not started. Call start_game first")

    def _ensure_turn_player(self, player_id: int) -> None:
        if player_id != self.current_player_id:
            raise ValueError("Not this player's turn")

    def _update_winner(self) -> None:
        if self.players[0].life_points <= 0:
            self.winner_id = 1
        elif self.players[1].life_points <= 0:
            self.winner_id = 0

    def _parse_ref(self, ref) -> EntityRef:
        if isinstance(ref, dict):
            return EntityRef(int(ref["player_id"]), int(ref["index"]))

        if isinstance(ref, (tuple, list)) and len(ref) == 2:
            return EntityRef(int(ref[0]), int(ref[1]))

        if isinstance(ref, str) and ref.startswith("p") and ":f" in ref:
            player_raw, index_raw = ref.split(":f", maxsplit=1)
            return EntityRef(int(player_raw[1:]), int(index_raw))

        raise ValueError("Invalid entity reference format")

    def _get_field_card(self, ref: EntityRef):
        player = self.players[ref.player_id]
        if ref.index < 0 or ref.index >= len(player.field):
            raise ValueError("Field index out of range")
        return player.field[ref.index]
