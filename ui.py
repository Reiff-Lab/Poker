"""Console input/output helpers.""" 


from __future__ import annotations

from cards import Card
from player import Player


class ConsoleUI: 
    def show_table(self, community_cards: list[Card], pot: int) -> None:
        board = self.format_cards(community_cards)

        if board == "":
            board = "(empty)"

        print(f"Board: {board}")
        print(f"Pot: {pot}")

    def show_player(self, player: Player) -> None: 
        cards = self.format_cards(player.hole_cards)
        print(f"Player: {player.name}")
        print(f"Cards: {cards}")
        print(f"Chips: {player.chips}")
    
    def ask_action(self, player: Player, call_amount: int) -> str: 
        while True:
            if call_amount == 0:
                prompt = f"{player.name}, please choose an action: check, raise, all-in, or fold: "
            else:
                prompt = f"{player.name}, please choose an action: call {call_amount}, raise, all-in, or fold: "
            
            action = input(prompt).strip().lower()

            if call_amount == 0 and action in {"c", "call", "check"}:
                return "call"

            if call_amount > 0 and action in {"c", "call"}:
                return "call"
            
            if action in {"r", "raise"}:
                return "raise"
            
            if action in {"a", "all-in","all in", "allin"}:
                return "all_in"
            
            if action in {"f", "fold"}:
                return "fold"
            
            print("Invalid action. Please try again.")

    def ask_raise_amount(self, minimum: int, maximum: int) -> int:
        while True:
            try:
                amount = int(input(f"Enter raise amount between {minimum} and {maximum}: "))
            except ValueError:
                print("Please enter a valid number.")
                continue

            if amount < minimum or amount > maximum:
                print(f"Invalid raise amount. Please enter a raise amount between {minimum} and {maximum}.")
                continue
            
            return amount

    def show_message(self, message: str) -> None:
        print(message)
    
    def format_cards(self, cards: list[Card]) -> str:
        return " ".join(str(card) for card in cards)
    
    def show_scoreboard(self, players: list[Player]) -> None:
        print("\n--- Scoreboard ---")
        for player in players:
            earnings = player.chips - player.starting_chips
            print(
                f"{player.name}: "
                f"Wins: {player.wins}, "
                f"Chips: {player.chips}, "
                f"Total earnings: {earnings}")