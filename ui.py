"""Console input/output helpers."""
# Luisa


from __future__ import annotations

from cards import Card
from player import Player


class ConsoleUI: 
    def show_table(self, community_cards: list[Card], pot: int) -> None:
        board = self.format_cards(community_cards)
        if board == "":
            board = "empty"
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
        # TODO: Task 4 - prompt the player to enter a raise amount, 
        # ensuring that it is a valid integer within the specified range.
        pass

    def show_message(self, message: str) -> None:
        # TODO: Task 5 - display a message to the player
        pass
    
    def format_cards(self, cards: list[Card]) -> str:
        # TODO: Task 6 - convert a list of Card objects into a string representation
        pass
