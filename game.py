"""Main Texas Hold'em game loop."""


from __future__ import annotations

from cards import Deck
from evaluator import HandEvaluator
from player import Player
from table import Table
from ui import ConsoleUI


class TexasHoldemGame:
    def __init__(self, players: list[Player], small_blind: int = 5, big_blind: int = 10) -> None:
        if len(players) < 2:
            raise ValueError("At least 2 players are required to play.")
        
        self.players = players
        self.small_blind = small_blind
        self.big_blind = big_blind
        self.table = Table()
        self.evaluator = HandEvaluator()
        self.ui = ConsoleUI()
        

    def play_hand(self) -> None:
        deck = Deck()
        self.table.reset()

        for player in self.players:
            player.reset_for_hand()
            player.receive(deck.draw(2))

        self._post_blinds()
        self._show_human_cards()

        self._betting_round("Pre-flop")

        self._deal_community(deck, 3, "Flop")
        self._betting_round("Flop")

        self._deal_community(deck, 1, "Turn")
        self._betting_round("Turn")

        self._deal_community(deck, 1, "River")
        self._betting_round("River")

        self._showdown()

    def _post_blinds(self) -> None:
        small_blind_player = self.players[0]
        big_blind_player = self.players[1]

        small_amount = small_blind_player.bet(self.small_blind)
        big_amount = big_blind_player.bet(self.big_blind)

        self.table.add_to_pot(small_amount)
        self.table.add_to_pot(big_amount)

        self.ui.show_message(f"{small_blind_player.name} posts {small_amount}; {big_blind_player.name} posts {big_amount}")

    def _show_human_cards(self) -> None:
        for player in self.players:
            if player.is_human:
                cards = self.ui.format_cards(player.hole_cards)
                self.ui.show_message(f"{player.name}: {cards}")

    def _deal_community(self, deck: Deck, count: int, street: str) -> None:
        if self._only_one_player_left():
            return

        self.table.community_cards.extend(deck.draw(count))
        self.ui.show_message(f"\n-- {street} --")

    def _betting_round(self, street: str) -> None:
        if self._only_one_player_left():
            return
        
        self.ui.show_message(f"\nBetting round: {street}")
        self.ui.show_table(self.table.community_cards, self.table.pot)
        
        highest_bet = max(player.current_bet for player in self.players)
        players_to_act = [player for player in self.players if player.active]

        while players_to_act and not self._only_one_player_left():
            player = players_to_act.pop(0)

            if not player.active:
                continue

            call_amount = max(0, highest_bet - player.current_bet)

            if player.is_human:
                self.ui.show_player(player)
                action = self.ui.ask_action(player, call_amount)
            else:
                action = self._bot_action(player, call_amount)
                self.ui.show_message(f"{player.name} chooses to {action}")

            if action == "fold":
                player.folded = True
                player.active = False
                self.ui.show_message(f"{player.name} folds.")

            elif action == "call":
                paid = player.bet(call_amount)
                self.table.add_to_pot(paid)

                if call_amount == 0:
                    self.ui.show_message(f"{player.name} checks.")
                else:
                    self.ui.show_message(f"{player.name} calls {paid}.")

            elif action == "raise":
                max_raise = player.chips - call_amount

                if max_raise < self.big_blind:
                    paid = player.bet(call_amount)
                    self.table.add_to_pot(paid)
                else:
                    raise_amount = self.ui.ask_raise_amount(self.big_blind, max_raise)
                    total_payment = call_amount + raise_amount
                    paid = player.bet(total_payment)
                    self.table.add_to_pot(paid)
                    highest_bet = player.current_bet
                    self.ui.show_message(f"{player.name} raises by {raise_amount}.")
                    players_to_act = [
                        other_player
                        for other_player in self.players
                        if other_player.active and other_player != player
                    
                    ]




        for player in self.players:
            player.current_bet = 0


    def _bot_action(self, player: Player, call_amount: int) -> str:
        if call_amount > player.chips / 2:
            return "fold"
        return "call"

    def _showdown(self) -> None: #I cant do this anymore :(
        active_players = [player for player in self.players if player.active]
        
        if len(active_players) == 1:
            winner = active_players[0]
            winner.chips += self.table.pot
            self.ui.show_message(f"{winner.name} wins {self.table.pot} chips.")
            self.table.pot = 0
            return
        
        player_ranks = []
        for player in active_players:
            cards = player.hole_cards + self.table.community_cards
            rank = self.evaluator.best_rank(cards)
            player_ranks.append((player, rank))
            self.ui.show_message(f"{player.name}: {rank.label}")

        best_rank = max(rank for player, rank in player_ranks)
        winners = [
            player
            for player, rank in player_ranks
            if rank == best_rank]
        
        winnings = self.table.pot // len(winners)
        for winner in winners:
            winner.chips += winnings
        winner_names = ", ".join(winner.name for winner in winners)

        self.ui.show_message(
            f"{winner_names} win {winnings} chips each with {best_rank.label}."
        )

        self.table.pot = 0

    def _only_one_player_left(self) -> bool:
        active_players = [player for player in self.players if player.active]
        return len(active_players) == 1        
