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
        
    def show_player(self, player: Player) -> None:
        # TODO: Task 2 - display the player's name, hole cards, and chip count in a clear format.
        pass
    
    def ask_action(self, player: Player, call_amount: int) -> str:
        # TODO: Task 3 - prompt the player to choose an action (call/check, raise, or fold).
        # TODO: Task 3 - match the player's input to the corresponding action, 
        # and return a string indicating the chosen action.
        pass 

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
