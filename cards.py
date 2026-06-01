"""Card and deck primitives for Texas Hold'em."""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum
from random import shuffle

# Suit represents the four card suits.
class Suit(IntEnum):
    CLUBS = 0
    DIAMONDS = 1
    HEARTS = 2
    SPADES = 3

# Returns a single-character symbol for each suit.
    @property
    def symbol(self) -> str:
        return {
            Suit.CLUBS: "C",
            Suit.DIAMONDS: "D",
            Suit.HEARTS: "H",
            Suit.SPADES: "S"
        }[self]

# Rank represents card values from 2 to Ace.
class Rank(IntEnum):
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    EIGHT = 8
    NINE = 9
    TEN = 10
    JACK = 11
    QUEEN = 12
    KING = 13
    ACE = 14
    
    # Returns a string label for each rank.
    @property
    def label(self) -> str:
        return {
            Rank.TWO: "2",
            Rank.THREE: "3",
            Rank.FOUR: "4",
            Rank.FIVE: "5",
            Rank.SIX: "6",
            Rank.SEVEN: "7",
            Rank.EIGHT: "8",
            Rank.NINE: "9",
            Rank.TEN: "T",
            Rank.JACK: "J",
            Rank.QUEEN: "Q",
            Rank.KING: "K",
            Rank.ACE: "A"
        }[self]


# Card represents a single playing card with a rank and suit.
@dataclass(frozen=True)
class Card:
    rank: Rank
    suit: Suit
    
    # Returns a string representation of the card, combining rank and suit symbols (e.g., "AH" for Ace of Hearts).
    def __str__(self) -> str:
        return f"{self.rank.label}{self.suit.symbol}"
    
# Deck represents a standard 52-card deck.
class Deck:
    def __init__(self) -> None:
        # Create all combinations of ranks and suits to form a standard deck, then shuffle it.
        self._cards = [Card(rank, suit) for suit in Suit for rank in Rank]
        shuffle(self._cards)

    def draw(self, count: int = 1) -> list[Card]:
        # Count must be at least 1.
        if count < 1:
            raise ValueError("count must be at least 1")

        # Cannot draw more cards than are left in the deck.
        if count > len(self._cards):
            raise ValueError("Not enough cards left in the deck.")
    
        # Remove cards from the deck and return them.
        drawn_cards = []
        for _ in range(count):
            drawn_cards.append(self._cards.pop())

        return drawn_cards
        
    # Returns the number of cards remaining in the deck.
    def remaining(self) -> int:
        return len(self._cards)

    # Resets the deck to a full 52-card set and shuffles it for a new game.
    def reset(self):
        self._cards = [Card(rank, suit) for suit in Suit for rank in Rank]
        shuffle(self._cards)


# deck = Deck()

# hand = deck.draw(2)
    
# print(hand)
# print(len(deck._cards))    #expected: 50

