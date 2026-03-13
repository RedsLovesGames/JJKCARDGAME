import unittest

from engine import GameAPI


class TestGameAPI(unittest.TestCase):
    def setUp(self):
        self.api = GameAPI()
        self.state = self.api.start_game(seed=42, mode="test")

    def test_start_game_contract(self):
        self.assertIn("players", self.state)
        self.assertIn("current_player_id", self.state)
        self.assertEqual(self.state["mode"], "test")

    def test_play_card_and_end_turn(self):
        current = self.state["players"][0]
        playable_index = next(i for i, card in enumerate(current["hand"]) if card["cost"] <= current["energy"])
        updated = self.api.play_card(0, playable_index)
        self.assertEqual(updated["current_player_id"], 0)
        ended = self.api.end_turn()
        self.assertEqual(ended["current_player_id"], 1)


if __name__ == "__main__":
    unittest.main()
