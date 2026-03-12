# JJKCARDGAME

## Engine/API Contract

Turn and battle logic now lives in `jjkcardgame/engine/` and exposes a serializable API contract:

- `start_game(seed, mode)`
- `play_card(player_id, hand_index)`
- `attack(attacker_id, target_id)`
- `end_turn()`

Both desktop (`jjkcardgame/src/gui.py`) and web (`jjkcardgame/src/web_client.py`) adapters consume this API layer.
