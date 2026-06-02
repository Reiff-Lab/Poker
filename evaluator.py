"""Five-card hand evaluator used to rank Texas Hold'em showdowns."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from enum import IntEnum
from itertools import combinations

from cards import Card, Rank, Suit

# Hand categories ranked from weakest to strongest.
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
    

# Stores the result of a hand evaluation, including the category and tiebreaker information for comparing hands of the same category.
@dataclass(frozen=True, order=True)
class HandRank:
    category: HandCategory
    tiebreakers: tuple[int, ...] = ()

    # Convert enum name to a readable text (e.g., "Straight Flush" instead of "STRAIGHT_FLUSH").
    @property
    def label(self) -> str:
        return self.category.name.replace("_", " ").title()

# Evaluate poker hands.
class HandEvaluator:
    def best_rank(self, cards: list[Card]) -> HandRank:
        # At least 5 cards are needed to form a valid hand.
        if len(cards) < 5:
            raise ValueError("At least 5 cards are required to evaluate a hand")

        all_hands = combinations(cards, 5)

        # Generate all 5-card combinations and return the best hand rank among them.
        return max(self._rank_five(hand) for hand in all_hands)
     

    def _rank_five(self, cards: list[Card]) -> HandRank:
        # Extract ranks and sort them in descending order.
        ranks = sorted((card.rank for card in cards), reverse=True)
        unique_ranks = sorted(set(ranks), reverse=True)

        # Count the occurrences of each rank (e.g., pairs, three of a kind)
        counts = Counter(ranks)

        # Create groups of (count, rank), sorted by importance (e.g. [(3 ,10), (2, 5)] for a full house with three 10s and two 5s).
        groups = sorted(((count, rank) for rank, count in counts.items()), reverse=True)

        # Check if all suits are the same for a flush.
        suits = [card.suit for card in cards]
        is_flush = len(set(suits)) == 1

        if len(unique_ranks) == 5:
            if unique_ranks[0] - unique_ranks[-1] == 4:
                is_straight = True
                straight_high = unique_ranks[0]
            elif unique_ranks == [Rank.ACE, Rank.FIVE, Rank.FOUR, Rank.THREE, Rank.TWO]:
                is_straight = True
                straight_high = Rank.FIVE

        # check for straight and get the high card of the straight if it exists
        straight_high = self._straight_high(ranks)
        
        # --- Hand ranking logic based on poker rules ---

        # Straight Flush: A straight and a flush at the same time.
        if is_flush and straight_high:
            return HandRank(HandCategory.STRAIGHT_FLUSH, (straight_high,))
        
        # Four of a Kind: Four cards of the same rank.
        if groups[0][0] == 4:
            return HandRank(HandCategory.FOUR_OF_A_KIND, (groups[0][1], groups[1][1]))

        # Full House (3 + 2): Three cards of one rank and two cards of another rank.
        if groups[0][0] == 3 and groups[1][0] ==2:
            return HandRank(HandCategory.FULL_HOUSE, (groups[0][1], groups[1][1]))

        # Flush: All cards of the same suit, ranked by their high cards.
        if is_flush:
            return HandRank(HandCategory.FLUSH, tuple(ranks))

        # Straight: Five cards in sequence, ranked by the high card of the straight.
        if straight_high:
            return HandRank(HandCategory.STRAIGHT, (straight_high,))

        # Three of a Kind: Three cards of the same rank, ranked by the rank of the three and then the kickers.
        if groups[0][0] == 3:
            return HandRank(HandCategory.THREE_OF_A_KIND, (groups[0][1], groups[1][1], groups[2][1]))

        # Two Pair: Two different pairs, ranked by the higher pair, then the lower pair, and then the kicker.
        if groups[0][0] == 2 and groups[1][0] == 2:
            return HandRank(HandCategory.TWO_PAIR, (groups[0][1], groups[1][1], groups[2][1]))

        # One Pair: Two cards of the same rank, ranked by the rank of the pair and then the kickers.
        if groups[0][0] == 2:
            return HandRank(HandCategory.ONE_PAIR, (groups[0][1], groups[1][1], groups[2][1], groups[3][1]))

        # High Card: No combination, ranked by the highest cards in order.
        return HandRank(HandCategory.HIGH_CARD, tuple(ranks))


    def _straight_high(self, ranks: list[int]) -> int | None:
            # Remove duplicates and sort ranks in descending order.
            unique = sorted(set(ranks), reverse=True)

            # Special case for Ace-low straight (A-2-3-4-5), where Ace is treated as 1.
            if set([Rank.ACE, Rank.FIVE, Rank.FOUR, Rank.THREE, Rank.TWO]).issubset(unique):
                return Rank.FIVE

            # Check every group of 5 consecutive cards for a straight. If the difference between the highest and lowest in the group is 4, it's a straight.
            for i in range(len(unique) - 4):
                window = unique[i:i + 5]
                if window[0] - window[4] == 4:
                    return window [0]
            
            # No straight found, return None.
            return None




evaluator = HandEvaluator()

def c(rank, suit):
    return Card(rank, suit)


# EVALUATOR TESTS
# # Straight Flush Test
# cards = [
#     c(Rank.TEN, Suit.HEARTS),
#     c(Rank.JACK, Suit.HEARTS),
#     c(Rank.QUEEN, Suit.HEARTS),
#     c(Rank.KING, Suit.HEARTS),
#     c(Rank.ACE, Suit.HEARTS),
# ]
# print(evaluator.best_rank(cards).label)

# # Four of a Kind Test
# cards = [
#     c(Rank.NINE, Suit.CLUBS),
#     c(Rank.NINE, Suit.DIAMONDS),
#     c(Rank.NINE, Suit.CLUBS),
#     c(Rank.NINE, Suit.SPADES),
#     c(Rank.TWO, Suit.HEARTS),
# ]
# print(evaluator.best_rank(cards).label)

# # Full House Test
# cards = [
#     c(Rank.TEN, Suit.CLUBS),
#     c(Rank.TEN, Suit.HEARTS),
#     c(Rank.TEN, Suit.SPADES),
#     c(Rank.FIVE, Suit.CLUBS),
#     c(Rank.FIVE, Suit.HEARTS),
# ]
# print(evaluator.best_rank(cards).label)

# # Flush Test
# cards = [
#     c(Rank.TWO, Suit.SPADES),
#     c(Rank.FIVE, Suit.SPADES),
#     c(Rank.SEVEN, Suit.SPADES),
#     c(Rank.NINE, Suit.SPADES),
#     c(Rank.JACK, Suit.SPADES),
# ]
# print(evaluator.best_rank(cards).label)

# # Straight Test
# cards = [
#     c(Rank.SIX, Suit.CLUBS),
#     c(Rank.SEVEN, Suit.HEARTS),
#     c(Rank.EIGHT, Suit.DIAMONDS),
#     c(Rank.NINE, Suit.SPADES),
#     c(Rank.TEN, Suit.CLUBS),
# ]
# print(evaluator.best_rank(cards).label)

# # One Pair Test
# cards = [
#     c(Rank.ACE, Suit.HEARTS),
#     c(Rank.ACE, Suit.CLUBS),
#     c(Rank.THREE, Suit.SPADES),
#     c(Rank.SEVEN, Suit.DIAMONDS),
#     c(Rank.NINE, Suit.HEARTS),
# ]
# print(evaluator.best_rank(cards).label)

# # High Card Test
# cards = [
#     c(Rank.TWO, Suit.HEARTS),
#     c(Rank.FIVE, Suit.CLUBS),
#     c(Rank.NINE, Suit.DIAMONDS),
#     c(Rank.JACK, Suit.SPADES),
#     c(Rank.ACE, Suit.HEARTS),
# ]
# print(evaluator.best_rank(cards).label)

