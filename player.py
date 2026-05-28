"""Player model for the poker table."""
# Luisa
# Common Mistakes were checked
# Optional Extensions were not worked on yet :)

from __future__ import annotations

from dataclasses import dataclass, field

from cards import Card

# bc dataclass no __innit__ needed
@dataclass
class Player:
    name: str
    chips: int
    is_human: bool = False
    hole_cards: list[Card] = field(default_factory=list) # a list with objects of type Card and every time a new Player is created make a fresh empty list
    current_bet: int = 0
    folded: bool = False

    def reset_for_hand(self) -> None: #reset the player's state for a new hand
        self.hole_cards.clear()
        self.current_bet = 0
        self.folded = False
        pass

    def receive(self, cards: list[Card]) -> None: #add the received cards to the player's hole cards
        self.hole_cards.extend(cards) # hole_cards is a list of cards and with extend(cards) new cards are added one by one into the whole_cards list
        pass

    def bet(self, amount: int) -> int: # check if the player has enough chips to bet the specified amount
        if amount < 0: #checking for negative amount and raise Error
            raise ValueError(f"{self.name}, you cannot bet a negative amount: {amount}")
        wager = min(self.chips, amount) #calculate the wager that is possible
        self.chips -= wager #decrease chips
        self.current_bet += wager #increase the current bet
        return wager 
    
    @property
    def active(self) -> bool:
        return (not self.folded) and (self.chips > 0) # only return True if the Player has not Folded and if they still have chips
        


    

