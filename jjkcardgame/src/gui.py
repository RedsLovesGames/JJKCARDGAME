import tkinter as tk
from tkinter import messagebox, simpledialog
from player import Player
from deck import Deck
from battle import Battle
from character import Character
import pandas as pd

class JJKCardGameGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("JJK Card Game")
        
        self.player1 = None
        self.player2 = None
        self.battle = None
        
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
        player1_name = self.player1_name_entry.get()
        player2_name = self.player2_name_entry.get()

        # Load characters from CSV
        characters_df = pd.read_csv("characters.csv")
        deck1 = Deck(characters_df)
        deck2 = Deck(characters_df)

        self.player1 = Player(player1_name, deck1)
        self.player2 = Player(player2_name, deck2)
        self.battle = Battle(self.player1, self.player2)

        self.setup_game_ui()

    def setup_game_ui(self):
        if self.game_frame:
            self.game_frame.destroy()

        self.game_frame = tk.Frame(self.master)
        self.game_frame.pack(pady=20)

        self.turn_label = tk.Label(self.game_frame, text=f"{self.player1.name}'s Turn")
        self.turn_label.grid(row=0, columnspan=2)

        self.play_button = tk.Button(self.game_frame, text="Play Card", command=self.choose_card)
        self.play_button.grid(row=1, column=0, padx=5)

        self.end_turn_button = tk.Button(self.game_frame, text="End Turn", command=self.end_turn)
        self.end_turn_button.grid(row=1, column=1, padx=5)

        self.status_label = tk.Label(self.game_frame, text="")
        self.status_label.grid(row=2, columnspan=2)

        self.stats_button = tk.Button(self.game_frame, text="Show Stats", command=self.show_stats)
        self.stats_button.grid(row=3, columnspan=2, pady=10)

    def show_stats(self):
        stats_message = (
            f"{self.player1.name} - Life Points: {self.player1.life_points}, Energy: {self.player1.energy}\n"
            f"{self.player2.name} - Life Points: {self.player2.life_points}, Energy: {self.player2.energy}\n\n"
            f"{self.player1.name}'s Field: {[char.name for char in self.player1.field]}\n"
            f"{self.player2.name}'s Field: {[char.name for char in self.player2.field]}"
        )
        messagebox.showinfo("Player Stats", stats_message)

    def choose_card(self):
        current_player = self.battle.player1 if self.battle.current_turn % 2 != 0 else self.battle.player2
        if not current_player.hand:
            self.status_label.config(text=f"{current_player.name} has no cards to play.")
            return

        card_details = []
        for index, card in enumerate(current_player.hand):
            details = f"{index + 1}. {card.name} (Cost: {card.cost}, ATK: {card.atk}, DEF: {card.defense})"
            card_details.append(details)

        card_selection_message = "\n".join(card_details) + "\n\nType the number of the card to play:"
        selected_index = simpledialog.askinteger("Choose Card", card_selection_message)

        if selected_index is not None and 1 <= selected_index <= len(current_player.hand):
            card = current_player.hand[selected_index - 1]
            if current_player.play_card(card):
                self.status_label.config(text=f"{current_player.name} played {card.name}.")
            else:
                self.status_label.config(text=f"{current_player.name} cannot play {card.name}.")
        else:
            self.status_label.config(text="Invalid card selection.")

    def end_turn(self):
        self.battle.current_turn += 1
        self.turn_label.config(text=f"{self.battle.player1.name if self.battle.current_turn % 2 != 0 else self.battle.player2.name}'s Turn")
        self.status_label.config(text="")

        # Check for game end condition
        if self.battle.player1.life_points <= 0 or self.battle.player2.life_points <= 0:
            winner = self.battle.player1 if self.battle.player1.is_alive() else self.battle.player2
            messagebox.showinfo("Game Over", f"{winner.name} wins!")
            self.master.quit()

if __name__ == "__main__":
    root = tk.Tk()
    app = JJKCardGameGUI(root)
    root.mainloop() 