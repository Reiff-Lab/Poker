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

    def show_player(self, player: Player) -> None: #display the player's name, hole cards, and chip count in a clear format.
        cards = self.format_cards(player.hand)
        print(f"Player: {player.name}")
        print(f"Cards: {cards}")
        print(f"Chips: {player.chips}")
    
    def ask_action(self, player: Player, call_amount: int) -> str: #prompt the player to choose an action (call/check, raise, or fold). match the player's input to the corresponding action, and return a string indicating the chosen action.
        if call_amount == 0:    #does the player have to give chips
            prompt = f"{player.name}, please choose an action: check, raise, or fold: "
        else:
            prompt = f"{player.name}, please choose an action: call {call_amount}, raise, or fold: "

        action = input(prompt).lower()

        if action == "check" and call_amount == 0:
            return "check"
        elif action == "call" and call_amount > 0:
            return "call"
        elif action == "raise":
            return "raise"
        elif action == "fold":
            return "fold"
        else:
            print("This is an Invalid action.")
            return self.ask_action(player, call_amount)

    def ask_raise_amount(self, minimum: int, maximum: int) -> int:
        try:
            amount = int(input(f"Enter raise amount between {minimum} and {maximum}: "))
        except ValueError:
            print("Please enter a valid number.")
            return self.ask_raise_amount(minimum, maximum)

        if amount < minimum or amount > maximum:
            print("Invalid raise amount.")
            return self.ask_raise_amount(minimum, maximum)
        
        return amount

    def show_message(self, message: str) -> None:
        print(message)
    
    def format_cards(self, cards: list[Card]) -> str:
        return " ".join(str(card) for card in cards)
    