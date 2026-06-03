"""Player model for the poker table."""

from __future__ import annotations
from dataclasses import dataclass, field
from cards import Card

@dataclass
class Player:
    name: str
    chips: int
    is_human: bool = False
    hole_cards: list[Card] = field(default_factory=list) # 
    current_bet: int = 0
    folded: bool = False
    starting_chips: int = 0
    wins: int = 0
    hands_played: int = 0

    def __post_init__(self) -> None:
        # Runs after Player object is created to save original chip amount for scoreboard.
        self.starting_chips = self.chips

    def reset_for_hand(self) -> None: #reset the player's state for a new hand/round
        self.hole_cards.clear()
        self.current_bet = 0
        self.folded = False  

    def receive(self, cards: list[Card]) -> None: #add the received cards to the player's hole cards
        self.hole_cards.extend(cards) # hole_cards is a list of cards and with extend(cards) new cards are added one by one into the whole_cards list

    def bet(self, amount: int) -> int: # check if the player has enough chips to bet the specified amount
        if amount < 0: #checking for negative amount and raise Error
            raise ValueError(f"{self.name} cannot bet a negative amount: {amount}")
        
        wager = min(self.chips, amount) #calculate the wager that is possible also allowing all_in
        
        self.chips -= wager # remove wagered chips from the players chips
        self.current_bet += wager # add the wagered chips to the amount the player has bet in this betting round
        
        return wager # return the real amount that was paid (matters because the player may have had fewer chips than the requested amount.)
    
    def all_in(self) -> int:
        return self.bet(self.chips)
    
    @property
    def active(self) -> bool: #is this player still in current hand? 
        return (not self.folded)
    
    @property
    def can_act(self) -> bool: # Should this Player still be asked to c,r,f?
        return (not self.folded) and (self.chips > 0) 
    
    # All-in player is active = True and can_act = False

        


    

