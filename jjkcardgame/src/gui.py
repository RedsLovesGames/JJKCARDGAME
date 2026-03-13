import tkinter as tk
from tkinter import messagebox, simpledialog

from engine import GameAPI


class JJKCardGameGUI:
    """Desktop adapter for the serializable game API."""

    def __init__(self, master):
        self.master = master
        self.master.title("JJK Card Game")
        self.api = GameAPI()
        self.state = None
        self.setup_ui()

    def setup_ui(self):
        self.frame = tk.Frame(self.master)
        self.frame.pack(pady=20)

        self.label = tk.Label(self.frame, text="Enter Player Names:")
        self.label.grid(row=0, columnspan=2)

        self.player1_name_entry = tk.Entry(self.frame)
        self.player1_name_entry.grid(row=1, column=0, padx=5)
        self.player1_name_entry.insert(0, "Player 1")

        self.player2_name_entry = tk.Entry(self.frame)
        self.player2_name_entry.grid(row=1, column=1, padx=5)
        self.player2_name_entry.insert(0, "Player 2")

        self.start_button = tk.Button(self.frame, text="Start Game", command=self.start_game)
        self.start_button.grid(row=2, columnspan=2, pady=10)

        self.game_frame = None

    def start_game(self):
        self.state = self.api.start_game(seed=None, mode="desktop")
        self.setup_game_ui()
        self.refresh_labels()

    def setup_game_ui(self):
        if self.game_frame:
            self.game_frame.destroy()

        self.game_frame = tk.Frame(self.master)
        self.game_frame.pack(pady=20)

        self.turn_label = tk.Label(self.game_frame, text="")
        self.turn_label.grid(row=0, columnspan=3)

        self.play_button = tk.Button(self.game_frame, text="Play Card", command=self.choose_card)
        self.play_button.grid(row=1, column=0, padx=5)

        self.attack_button = tk.Button(self.game_frame, text="Attack", command=self.attack)
        self.attack_button.grid(row=1, column=1, padx=5)

        self.end_turn_button = tk.Button(self.game_frame, text="End Turn", command=self.end_turn)
        self.end_turn_button.grid(row=1, column=2, padx=5)

        self.status_label = tk.Label(self.game_frame, text="")
        self.status_label.grid(row=2, columnspan=3)

        self.stats_button = tk.Button(self.game_frame, text="Show Stats", command=self.show_stats)
        self.stats_button.grid(row=3, columnspan=3, pady=10)

    def refresh_labels(self):
        player = self.state["players"][self.state["current_player_id"]]
        self.turn_label.config(text=f"{player['name']}'s Turn")
        self.status_label.config(text=self.state.get("last_action", ""))

    def show_stats(self):
        p1 = self.state["players"][0]
        p2 = self.state["players"][1]
        stats_message = (
            f"{p1['name']} - Life Points: {p1['life_points']}, Energy: {p1['energy']}\n"
            f"{p2['name']} - Life Points: {p2['life_points']}, Energy: {p2['energy']}\n\n"
            f"{p1['name']}'s Field: {[char['name'] for char in p1['field']]}\n"
            f"{p2['name']}'s Field: {[char['name'] for char in p2['field']]}"
        )
        messagebox.showinfo("Player Stats", stats_message)

    def choose_card(self):
        current_player_id = self.state["current_player_id"]
        current_player = self.state["players"][current_player_id]

        if not current_player["hand"]:
            self.status_label.config(text=f"{current_player['name']} has no cards to play.")
            return

        card_details = []
        for index, card in enumerate(current_player["hand"]):
            details = f"{index + 1}. {card['name']} (Cost: {card['cost']}, ATK: {card['atk']}, DEF: {card['defense']})"
            card_details.append(details)

        card_selection_message = "\n".join(card_details) + "\n\nType the number of the card to play:"
        selected_index = simpledialog.askinteger("Choose Card", card_selection_message)

        if selected_index is not None and 1 <= selected_index <= len(current_player["hand"]):
            try:
                self.state = self.api.play_card(current_player_id, selected_index - 1)
                self.refresh_labels()
            except ValueError as error:
                self.status_label.config(text=str(error))
        else:
            self.status_label.config(text="Invalid card selection.")

    def attack(self):
        current_player_id = self.state["current_player_id"]
        current_player = self.state["players"][current_player_id]
        opponent_id = 1 - current_player_id
        opponent = self.state["players"][opponent_id]

        if not current_player["field"]:
            self.status_label.config(text="No attackers on field.")
            return

        attacker_prompt = "\n".join(
            [f"{idx + 1}. {card['name']}" for idx, card in enumerate(current_player["field"])]
        )
        attacker_index = simpledialog.askinteger("Choose Attacker", attacker_prompt)
        if attacker_index is None or not (1 <= attacker_index <= len(current_player["field"])):
            self.status_label.config(text="Invalid attacker selection.")
            return

        target_id = None
        if opponent["field"]:
            target_prompt = "0. Attack player directly\n" + "\n".join(
                [f"{idx + 1}. {card['name']}" for idx, card in enumerate(opponent["field"])]
            )
            target_index = simpledialog.askinteger("Choose Target", target_prompt)
            if target_index is None:
                self.status_label.config(text="Attack cancelled.")
                return
            if target_index != 0:
                if not (1 <= target_index <= len(opponent["field"])):
                    self.status_label.config(text="Invalid target selection.")
                    return
                target_id = opponent["field"][target_index - 1]["id"]

        attacker_id = current_player["field"][attacker_index - 1]["id"]
        try:
            self.state = self.api.attack(attacker_id=attacker_id, target_id=target_id)
            self.refresh_labels()
            self._check_winner()
        except ValueError as error:
            self.status_label.config(text=str(error))

    def end_turn(self):
        self.state = self.api.end_turn()
        self.refresh_labels()
        self._check_winner()

    def _check_winner(self):
        winner_id = self.state.get("winner_id")
        if winner_id is None:
            return
        winner_name = self.state["players"][winner_id]["name"]
        messagebox.showinfo("Game Over", f"{winner_name} wins!")
        self.master.quit()


if __name__ == "__main__":
    root = tk.Tk()
    app = JJKCardGameGUI(root)
    root.mainloop()
