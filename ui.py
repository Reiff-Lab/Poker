"""Console input/output helpers.""" 

from __future__ import annotations
from cards import Card
from player import Player

class ConsoleUI: 
    def show_table(self, community_cards: list[Card], pot: int) -> None:
        board = self.format_cards(community_cards)

        # Before Flop there are no community cards yet.
        if board == "":
            board = "(empty)"

        # Show current board and current pot
        print(f"Board: {board}")
        print(f"Pot: {pot}")

    def show_player(self, player: Player) -> None:
        # Show one players hole cards and chip count.
        # Mainly used when a human player needs to see their hand.
        cards = self.format_cards(player.hole_cards)
        print(f"Player: {player.name}")
        print(f"Cards: {cards}")
        print(f"Chips: {player.chips}")
    
    def ask_action(self, player: Player, call_amount: int) -> str: 
        # Asks Human Player which action they want to take and returns it.
        # Keeps asking till valid action
        while True:
            if call_amount == 0: # to differentiate between check and call
                prompt = f"{player.name}, please choose an action: check, raise, all-in, or fold: "
            else:
                prompt = f"{player.name}, please choose an action: call {call_amount}, raise, all-in, or fold: "
            
            action = input(prompt).strip().lower() # Player Input here

            if call_amount == 0 and action in {"c", "call", "check"}: # accepts check and call
                return "call"

            if call_amount > 0 and action in {"c", "call"}:
                return "call"
            
            if action in {"r", "raise"}:
                return "raise"
            
            if action in {"a", "all-in","all in", "allin"}:
                return "all_in"
            
            if action in {"f", "fold"}:
                return "fold"
            
            print("Invalid action. Please try again.") # If the input was not valid, the loop will continue and the Player will be asked again. 

    def ask_raise_amount(self, minimum: int, maximum: int) -> int:
        # Ask the Player how many chips they want to raise and returns the number/amount.
        while True:
            try:
                amount = int(input(f"Enter raise amount between {minimum} and {maximum}: "))
            except ValueError:
                print("Please enter a valid number.")
                continue

            if amount < minimum or amount > maximum: # Checking that number is not outside of allowed range
                print(f"Invalid raise amount. Please enter a raise amount between {minimum} and {maximum}.")
                continue
            
            return amount 

    def show_message(self, message: str) -> None: # simply print()
        print(message)
    
    def format_cards(self, cards: list[Card]) -> str:
        # Convert list of Card Objects into one string that is readable
        return " ".join(str(card) for card in cards)
    
    def show_scoreboard(self, players: list[Player]) -> None:
        print("\n--- Scoreboard ---")
        for player in players:
            earnings = player.chips - player.starting_chips
           
            if player.hands_played > 0:
                win_ratio = (player.wins / player.hands_played) * 100 # in %
            else:
                win_ratio = 0 # divide by 0 Error
           
            print(
                f"{player.name}: "
                f"Wins: {player.wins}, "
                f"Chips: {player.chips}, "
                f"Total earnings: {earnings}, "
                f"Win ratio: {win_ratio:.1f}%")