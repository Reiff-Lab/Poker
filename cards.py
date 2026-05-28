"""Card and deck primitives for Texas Hold'em."""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum
from random import shuffle


class Suit(IntEnum):
    CLUBS = 0
    # TODO: Task 1 - continue here 
    DIAMONDS = 1
    HEARTS = 2
    SPADES = 3

    @property
    def symbol(self) -> str:
        return {
            Suit.CLUBS: "C",
            Suit.DIAMONDS: "D",
            Suit.HEARTS: "H",
            Suit.SPADES: "S"
        }[self]


class Rank(IntEnum):
    TWO = 2
    # TODO: Task 2 - continue until ACE = 14 
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    EIGHT = 8
    NONE = 9
    TEN = 10
    JACK = 11
    QUEEN = 12
    KING = 13
    ACE = 14
    
    @property
    def label(self) -> str:
        return {
            Rank.TWO: "2",
            # TODO: Task 2 - continue the mapping 
            Rank.THREE: "3",
            Rank.FOUR: "4",
            Rank.FIVE: "5",
            Rank.SIX: "6",
            Rank.SEVEN: "7",
            Rank.EIGHT: "8",
            Rank.NONE: "9",
            Rank.TEN: "T",
            Rank.JACK: "J",
            Rank.QUEEN: "Q",
            Rank.KING: "K",
            Rank.ACE: "A"
        }[self]


@dataclass(frozen=True)
class Card:
    rank: Rank
    # TODO: Task 3 - continue here 
    suit: Suit
    
    def __str__(self) -> str:
        # TODO: Task 3 - return a string representation of the card, e.g. "AH" for Ace of Hearts
        return f"{self.rank.label}{self.suit.symbol}"
    

class Deck:
    def __init__(self) -> None:
        # TODO: Task 4 - initialize the deck with all 52 cards 
        self._cards = [Card(rank, suit) for suit in Suit for rank in Rank]
        shuffle(self._cards)

    def draw(self, count: int = 1) -> list[Card]:
        if count < 1:
            raise ValueError("count must be at least 1")
        # TODO: Task 4 - check if there are enough cards left in the deck, 
        # and if so, return the drawn cards and remove them from the deck
        if count > Len(self._cards):
            raise ValueError("Not enough cards left in the deck.")
    
        drawn_cards = []

        for _ in range(count):
            drawn_cards.append(self._cards.pop())

        return drawn_cards
        

    def remaining(self) -> int:
        return Len(self._cards)

    def reset(self):
        self._cards = [Card(rank, suit) for suit in suit for rank in Rank]
        shuffle(self._cards)


    deck = Deck()
    hand = deck.draw(2)
    print(hand)
    print(len(deck._cards))    #expected: 50

