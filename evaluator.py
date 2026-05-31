"""Five-card hand evaluator used to rank Texas Hold'em showdowns."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from enum import IntEnum
from itertools import combinations

from cards import Card, Rank, Suit


class HandCategory(IntEnum):
    HIGH_CARD = 0
    ONE_PAIR = 1
    TWO_PAIR = 2
    THREE_OF_A_KIND = 3
    STRAIGHT = 4
    FLUSH = 5
    FULL_HOUSE = 6
    FOUR_OF_A_KIND = 7
    STRAIGHT_FLUSH = 8
    


@dataclass(frozen=True, order=True)
class HandRank:
    category: HandCategory
    tiebreakers: tuple[int, ...] = ()

    @property
    def label(self) -> str:
        return self.category.name.replace("_", " ").title()


class HandEvaluator:
    def best_rank(self, cards: list[Card]) -> HandRank:
        if len(cards) < 5:
            raise ValueError("At least 5 cards are required to evaluate a hand")

        all_hands = combinations(cards, 5)

        return max(self._rank_five(hand) for hand in all_hands)
     

    def _rank_five(self, cards: list[Card]) -> HandRank:
        ranks = sorted((card.rank for card in cards), reverse=True)
        unique_ranks = sorted(set(ranks), reverse=True)
        counts = Counter(ranks)
        groups = sorted(((count, rank) for rank, count in counts.items()), reverse=True)
        suits = [card.suit for card in cards]
        is_flush = len(set(suits)) == 1

        if len(unique_ranks) == 5:
            if unique_ranks[0] - unique_ranks[-1] == 4:
                is_straight = True
                straight_high = unique_ranks[0]
            elif unique_ranks == [Rank.ACE, Rank.FIVE, Rank.FOUR, Rank.THREE, Rank.TWO]:
                is_straight = True
                straight_high = Rank.FIVE


        straight_high = self._straight_high(ranks)
        
        if is_flush and straight_high:
            return HandRank(HandCategory.STRAIGHT_FLUSH, (straight_high,))
        
        if groups[0][0] == 4:
            return HandRank(HandCategory.FOUR_OF_A_KIND, (groups[0][1], groups[1][1]))

        if groups[0][0] == 3 and groups[1][0] ==2:
            return HandRank(HandCategory.FULL_HOUSE, (groups[0][1], groups[1][1]))

        if is_flush:
            return HandRank(HandCategory.FLUSH, tuple(ranks))

        if straight_high:
            return HandRank(HandCategory.STRAIGHT, (straight_high,))

        if groups[0][0] == 3:
            return HandRank(HandCategory.THREE_OF_A_KIND, (groups[0][1], groups[1][1], groups[2][1]))

        if groups[0][0] == 2 and groups[1][0] == 2:
            return HandRank(HandCategory.TWO_PAIR, (groups[0][1], groups[1][1], groups[2][1]))

        if groups[0][0] == 2:
            return HandRank(HandCategory.ONE_PAIR, (groups[0][1], groups[1][1], groups[2][1], groups[3][1]))

        return HandRank(HandCategory.HIGH_CARD, tuple(ranks))


    def _straight_high(self, ranks: list[int]) -> int | None:
            unique = sorted(set(ranks), reverse=True)

            if set([Rank.ACE, Rank.FIVE, Rank.FOUR, Rank.THREE, Rank.TWO]).issubset(unique):
                return Rank.FIVE

            for i in range(len(unique) - 4):
                window = unique[i:i + 5]
                if window[0] - window[4] == 4:
                    return window [0]
            
            return None




evaluator = HandEvaluator()

def c(rank, suit):
    return Card(rank, suit)

# Straight Flush Test
cards = [
    c(Rank.TEN, Suit.HEARTS),
    c(Rank.JACK, Suit.HEARTS),
    c(Rank.QUEEN, Suit.HEARTS),
    c(Rank.KING, Suit.HEARTS),
    c(Rank.ACE, Suit.HEARTS),
]
print(evaluator.best_rank(cards).label)

# Four of a Kind Test
cards = [
    c(Rank.NINE, Suit.CLUBS),
    c(Rank.NINE, Suit.DIAMONDS),
    c(Rank.NINE, Suit.CLUBS),
    c(Rank.NINE, Suit.SPADES),
    c(Rank.TWO, Suit.HEARTS),
]
print(evaluator.best_rank(cards).label)

# Full House Test
cards = [
    c(Rank.TEN, Suit.CLUBS),
    c(Rank.TEN, Suit.HEARTS),
    c(Rank.TEN, Suit.SPADES),
    c(Rank.FIVE, Suit.CLUBS),
    c(Rank.FIVE, Suit.HEARTS),
]
print(evaluator.best_rank(cards).label)

# Flush Test
cards = [
    c(Rank.TWO, Suit.SPADES),
    c(Rank.FIVE, Suit.SPADES),
    c(Rank.SEVEN, Suit.SPADES),
    c(Rank.NINE, Suit.SPADES),
    c(Rank.JACK, Suit.SPADES),
]
print(evaluator.best_rank(cards).label)

# Straight Test
cards = [
    c(Rank.SIX, Suit.CLUBS),
    c(Rank.SEVEN, Suit.HEARTS),
    c(Rank.EIGHT, Suit.DIAMONDS),
    c(Rank.NINE, Suit.SPADES),
    c(Rank.TEN, Suit.CLUBS),
]
print(evaluator.best_rank(cards).label)

# One Pair Test
cards = [
    c(Rank.ACE, Suit.HEARTS),
    c(Rank.ACE, Suit.CLUBS),
    c(Rank.THREE, Suit.SPADES),
    c(Rank.SEVEN, Suit.DIAMONDS),
    c(Rank.NINE, Suit.HEARTS),
]
print(evaluator.best_rank(cards).label)

# High Card Test
cards = [
    c(Rank.TWO, Suit.HEARTS),
    c(Rank.FIVE, Suit.CLUBS),
    c(Rank.NINE, Suit.DIAMONDS),
    c(Rank.JACK, Suit.SPADES),
    c(Rank.ACE, Suit.HEARTS),
]
print(evaluator.best_rank(cards).label)

