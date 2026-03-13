"""Web-facing adapter that consumes the serializable GameAPI contract."""

from engine import GameAPI


class WebGameClient:
    """Thin adapter for web clients to call engine commands."""

    def __init__(self):
        self.api = GameAPI()

    def dispatch(self, command: str, payload: dict):
        if command == "start_game":
            return self.api.start_game(seed=payload.get("seed"), mode=payload.get("mode", "web"))
        if command == "play_card":
            return self.api.play_card(
                player_id=payload["player_id"],
                hand_index=payload["hand_index"],
            )
        if command == "attack":
            return self.api.attack(
                attacker_id=payload["attacker_id"],
                target_id=payload.get("target_id"),
            )
        if command == "end_turn":
            return self.api.end_turn()
        raise ValueError(f"Unsupported command: {command}")
