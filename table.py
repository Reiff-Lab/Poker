"""Shared table state for a Hold'em hand."""

from __future__ import annotations

from dataclasses import dataclass, field

from cards import Card


class Table:
    # Represents the shared state of the table during a hand, including community cards(visible to all players) and total pot value.
    community_cards: list[Card] = field(default_factory=list)
    pot: int = 0

    def reset(self):
        # Clears the community cards without replacing the list and resets the pot for a new hand.
        self.community_cards.clear()
        self.pot = 0

    def add_to_pot(self, amount:int):
        # No negative values allowed for pot contributions. Adds the specified amount to the total pot.
        if amount < 0:
            raise ValueError("Amount cannot be negative.")
        self.pot +=amount



