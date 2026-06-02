"""Main Texas Hold'em game loop."""


from __future__ import annotations

import random

from cards import Deck
from evaluator import HandEvaluator
from player import Player
from table import Table
from ui import ConsoleUI


class TexasHoldemGame:
    def __init__(self, players: list[Player], small_blind: int = 5, big_blind: int = 10) -> None:
        if len(players) < 2:
            raise ValueError("At least 2 players are required to play.")
        
        self.players = players  # self.players = list of all players in a game
        self.small_blind = small_blind
        self.big_blind = big_blind
        self.table = Table()
        self.evaluator = HandEvaluator()
        self.ui = ConsoleUI()
        
    def play_hand(self) -> None: # start and sequence of every mini-game / every hand 
        deck = Deck()
        
        self.table.reset()

        for player in self.players: # for every player in the game do the following
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

        self.ui.show_scoreboard(self.players)

    def _post_blinds(self) -> None:
        small_blind_player = self.players[0]  
        big_blind_player = self.players[1]

        small_amount = small_blind_player.bet(self.small_blind)
        big_amount = big_blind_player.bet(self.big_blind)

        self.table.add_to_pot(small_amount)
        self.table.add_to_pot(big_amount)

        self.ui.show_message(
            f"{small_blind_player.name} posts {small_amount}; {big_blind_player.name} posts {big_amount}"
            )

    def _show_human_cards(self) -> None: # this I changed to allow multiple human players to see their cards one after the other
        for player in self.players:
            if player.is_human:
                input(f"\n{player.name}, press Enter to see your cards and choose your action.")
                cards = self.ui.format_cards(player.hole_cards)
                self.ui.show_message(f"{player.name}: {cards}")
                input(f"{player.name}, press Enter when you are done.")
                print("\n" * 15)

    def _deal_community(self, deck: Deck, count: int, street: str) -> None:
        if self._only_one_player_left():
            return

        self.table.community_cards.extend(deck.draw(count)) # drawing new cars and adding them to the table cards in the middle
        self.ui.show_message(f"\n-- {street} --")   # -- current betting stage --

    def _betting_round(self, street: str) -> None:
        if self._only_one_player_left():    # is betting needed?
            return
        
        self.ui.show_message(f"\nBetting round: {street}") 
        self.ui.show_table(self.table.community_cards, self.table.pot)
        
        highest_bet = max(player.current_bet for player in self.players)

        players_to_act = [player for player in self.players if player.can_act] # list of players that have not folded and thus need to act

        while players_to_act and not self._only_one_player_left(): # loop stop if everyone has acted or everyone but one has folded
            player = players_to_act.pop(0)

            if not player.can_act:   # safety guard (redundant in theory)
                continue

            call_amount = max(0, (highest_bet - player.current_bet))

            if player.is_human:
                input(f"\n{player.name}, press Enter and proceed with your turn.")
                self.ui.show_table(self.table.community_cards, self.table.pot)

                cards = self.ui.format_cards(player.hole_cards)
                self.ui.show_message(f"Your cards: {cards}")
                self.ui.show_message(f"Your chips: {player.chips}")

                action = self.ui.ask_action(player, call_amount)
                print("\n" * 15)
            else:
                action = self._bot_action(player, call_amount)
                self.ui.show_message(f"{player.name} chooses to {action}")


            if action == "fold":
                player.folded = True
                self.ui.show_message(f"{player.name} folds.")

            elif action == "call":
                paid = player.bet(call_amount)
                self.table.add_to_pot(paid)

                if call_amount == 0:
                    self.ui.show_message(f"{player.name} checks.")
                elif paid < call_amount:
                    self.ui.show_message(f"{player.name} cannot fully call and goes all-in with {paid}.")
                else:
                    self.ui.show_message(f"{player.name} calls {paid}.")
            
            elif action == "all_in":
                paid = player.all_in()
                self.table.add_to_pot(paid)

                if player.current_bet > highest_bet:
                    highest_bet = player.current_bet
                    self.ui.show_message(f"{player.name} goes all-in with {paid} chips.")
                    players_to_act= [
                        other_player 
                        for other_player in self.players if other_player.can_act and other_player != player]
                else:
                    self.ui.show_message(f"{player.name} goes all-in with {paid} chips.")            

            elif action == "raise": 
                # Raise must be more than the previous bet
                min_raise = 1
                max_raise = player.chips - call_amount

                if player.chips < call_amount:
                    player.folded = True
                    self.ui.show_message(f"{player.name} cannot call and folds")
                    continue

                if max_raise < min_raise: # Player does not have enough chips to call AND also raise, thus we treat it as a call
                    paid = player.bet(call_amount)
                    self.table.add_to_pot(paid)
                    if call_amount == 0:
                        self.ui.show_message(f"{player.name} checks.")
                    else:
                        self.ui.show_message(f"{player.name} cannot raise, so they call {paid}.")


                else:
                    if player.is_human:
                        raise_amount = self.ui.ask_raise_amount(min_raise, max_raise)
                    else:
                        raise_amount = self._bot_raise_amount(player, call_amount, min_raise, max_raise)

                    total_payment = call_amount + raise_amount

                    paid = player.bet(total_payment)

                    self.table.add_to_pot(paid)

                    highest_bet = player.current_bet

                    self.ui.show_message(f"{player.name} raises by {raise_amount}.")
                    
                    players_to_act = [
                        other_player
                        for other_player in self.players
                        if other_player.can_act and other_player != player 
                    ]

        for player in self.players: # resetting the current bet at the end of a betting round
            player.current_bet = 0



    def _bot_action(self, player: Player, call_amount: int) -> str:
        strength = self._bot_hand_strength(player)

        if player.chips <= 0:
            return "call"
        
        call_ratio = call_amount / player.chips

        if call_amount >= player.chips:
            if strength >= 6 or random.random() < 0.10:
                return "all_in"
            return "fold"
        
        if call_amount == 0:
            if strength >= 5 and player.chips > self.big_blind and random.random() < 0.50:
                return "raise"
            if strength >= 3 and player.chips > self.big_blind and random.random() < 0.15:
                return "raise"
            if player.chips > self.big_blind and random.random() < 0.05:
                return "raise"
            return "call"
        
        if call_ratio > 0.5 and strength < 6:
            return "fold"
        if call_ratio > 0.25 and strength < 4 and random.random() < 0.75:
            return "fold"
        if strength >= 6 and player.chips > call_amount + self.big_blind and random.random() < 0.45:
            return "raise"
        if strength >= 4 and player.chips > call_amount + self.big_blind and random.random() < 0.20:
            return "raise"
        if player.chips > call_amount + self.big_blind and random.random() < 0.05:
            return "raise"
        return "call"
    
    def _bot_hand_strength(self, player: Player) -> int:
        cards = player.hole_cards + self.table.community_cards

        if len(cards) >= 5:
            rank = self.evaluator.best_rank(cards)
            return int(rank.category) * 2
        return self._bot_preflop_strength(player)

    def _bot_preflop_strength(self, player: Player) -> int:
        if len(player.hole_cards) < 2:
            return 0
        
        first_card = player.hole_cards[0]
        second_card = player.hole_cards[1]
        ranks = sorted([first_card.rank, second_card.rank], reverse=True)

        strength = 0

        if ranks[0] == ranks[1]:
            strength += 5
            if ranks[0] >= 10:
                strength += 2

        if ranks[0] >= 14:
            strength += 2
        elif ranks[0] >= 11:
            strength += 1

        if ranks[1] > 10:
            strength += 1
        
        if first_card.suit == second_card.suit:
            strength += 1

        return strength
    
    def _bot_raise_amount(self, player: Player, call_amount: int, minimum: int, maximum: int) -> int:
        safe_maximum = min(maximum, self.big_blind * 3)
        safe_maximum = max(minimum, safe_maximum)
        return random.randint(minimum, safe_maximum)
    

    def _showdown(self) -> None:
        active_players = [player for player in self.players if not player.folded]
        
        if len(active_players) == 1:
            active_players[0].chips += self.table.pot
            active_players[0].wins += 1
            self.ui.show_message(f"{active_players[0].name} wins {self.table.pot} chips.")
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
            winner.wins += 1

        winner_names = ", ".join(winner.name for winner in winners)

        if len(winners) == 1:
            self.ui.show_message(
                f"Winner: {winner_names} won {winnings} chips with {best_rank.label}.")
        else:
            self.ui.show_message(
                f"Winners: {winner_names} won {winnings} chips each with {best_rank.label}.")

        self.table.pot = 0

    def _only_one_player_left(self) -> bool:
        active_players = [player for player in self.players if player.active]
        return len(active_players) == 1        
