"""Main Texas Hold'em game loop."""

from __future__ import annotations
import random
import os
from cards import Deck, show_cards
from evaluator import HandEvaluator
from player import Player
from table import Table
from ui import ConsoleUI


# Controls the main game logic of dealing cards, betting rounds, showdown and scoreboard.
class TexasHoldemGame:
    def __init__(self, players: list[Player], small_blind: int = 5, big_blind: int = 10) -> None:
        # A poker game needs at least two players.
        if len(players) < 2:
            raise ValueError("At least 2 players are required to play.")
        
        self.players = players
        self.small_blind = small_blind 
        self.big_blind = big_blind 
        
        self.table = Table()
        self.evaluator = HandEvaluator() 
        self.ui = ConsoleUI()
        
    def play_hand(self) -> None: 
        # Runs one complete hand from setup to scoreboard. Sequence of every round.
        deck = Deck()
        self.table.reset()

        for player in self.players: 
            player.reset_for_hand() # reset Players
            player.hands_played += 1
            player.receive(deck.draw(2)) # Deal 2 hole cards to each Player privatly

        # The first 2 Players post the small/big blind.
        self._post_blinds() 
        
        # The Human Players privately look at their cards befre betting starts.
        self._show_human_cards()
        
        # Betting before the Flop
        self._betting_round("Pre-flop")
        
        # Deal the Flop: 3 community cards.
        self._deal_community(deck, 3, "Flop")

        # Betting after the Flop.        
        self._betting_round("Flop")

        # Deal the Turn: 1 community card.
        self._deal_community(deck, 1, "Turn")
        
        # Betting after the Turn.
        self._betting_round("Turn")

        # Deal the River: 1 (final) community card.
        self._deal_community(deck, 1, "River")
        
        # Final betting round.
        self._betting_round("River")

        # Compare all reamining hands and give pot to the winner(s).
        self._showdown()

        # Show Scoreboard
        self.ui.show_scoreboard(self.players)

    def _post_blinds(self) -> None:
        # The first 2 players in the list pay the set blind bets.
        # The player order is rotated in main.py after each round is played.
        small_blind_player = self.players[0]  
        big_blind_player = self.players[1]

        # bet() removes chips from Player and returns the amount they paid
        small_amount = small_blind_player.bet(self.small_blind)
        big_amount = big_blind_player.bet(self.big_blind)

        # Adding both blind payments to the pot.
        self.table.add_to_pot(small_amount)
        self.table.add_to_pot(big_amount)

        self.ui.show_message(f"{small_blind_player.name} posts small blind: {small_amount}")
        self.ui.show_message(f"{big_blind_player.name} posts big blind: {big_amount}")

    def _show_human_cards(self) -> None:
        # Shows each human players their hole cards privately before the first betting round.
        for player in self.players:
            if player.is_human:
                input(f"\n{player.name}, press Enter to see your cards.")
                
                print ("\n" + "-" * 20)
                print(f"\n{player.name.upper()}'s hole cards:")
                print ("-" * 20)

                show_cards(player.hole_cards)
                
                input(f"{player.name}, press Enter when you are done.")
                self._hide_private_info() # hide previous players cards

    def _deal_community(self, deck: Deck, count: int, street: str) -> None:
        # If only 1 Player has not folded, no more cards need to be dealt.
        if self._only_one_player_left():
            return
        
        # Otherwise: Drawing new community cards and adding them to table.
        self.table.community_cards.extend(deck.draw(count)) 

        print("\n" + "-" * 30)
        print (f"{street.upper()} CARDS")
        print ("-" * 30)

        show_cards(self.table.community_cards)


    def _betting_round(self, street: str) -> None:
        # Handles a betting round
        if self._only_one_player_left():    
            return
        
        # Show currrent betting round, community cards and pot.
        print("\n" + "-" * 40)
        print(f" {street.upper()} BETTING ROUND")
        print("=" * 40)

        print(f"Pot: {self.table.pot}")

        print("\nCommunity Cards:")
        show_cards(self.table.community_cards)

        # Find the Highest bet, so what players must call. 
        highest_bet = max(player.current_bet for player in self.players)

        # Only Players who have not folded and still have chips need to act.
        players_to_act = [player for player in self.players if player.can_act] # list of players that have not folded and thus need to act

        while players_to_act and not self._only_one_player_left(): # loop stop if everyone has acted or everyone but one has folded
            # Takes the next Player whose turn it is
            player = players_to_act.pop(0)

            if not player.can_act:   # safety check
                continue
            
            # Amount needed to match the current highest bet
            call_amount = max(0, (highest_bet - player.current_bet))

            if player.is_human:
                # Give human Player a private moment to see their cards and choose an action.
                input(f"\n{player.name}, press Enter and proceed with your turn.")
            
                self.ui.show_message(f"\n{player.name}'s turn - {street}")

                if self.table.community_cards:
                    self.ui.show_message("Community Cards:")
                    show_cards(self.table.community_cards)
                else:
                    self.ui.show_message("Community Cards: (empty)")
                
                self.ui.show_message(f"Pot: {self.table.pot}")

                self.ui.show_message("Your cards:")
                show_cards(player.hole_cards)
                self.ui.show_message(f"Your chips: {player.chips}")

                action = self.ui.ask_action(player, call_amount) # Ask Human to choose call/check, raise, fold or all-in
            
            else:
                # Bots will choose an action automatically.
                action = self._bot_action(player, call_amount)

            if action == "fold":
                # Folding removes the player from the current round. 
                player.folded = True

                if player.is_human:
                    self._hide_private_info() # Hide private info

                self.ui.show_message(f"{player.name} folds.")

            elif action == "call":
                # Player pays chips to match highest bet
                paid = player.bet(call_amount)
                self.table.add_to_pot(paid)

                if player.is_human:
                    self._hide_private_info()

                if call_amount == 0: # special case: distinguish between call and check
                    self.ui.show_message(f"{player.name} checks.")  
                elif paid < call_amount: # special case: if player cannot fully call, they go all in
                    self.ui.show_message(f"{player.name} cannot fully call and goes all-in with {paid}.")
                else:
                    self.ui.show_message(f"{player.name} calls {paid}.")
            
            elif action == "all_in":
                paid = player.all_in()
                self.table.add_to_pot(paid)

                if player.is_human:
                    self._hide_private_info() # hide private info

                if player.current_bet > highest_bet:
                    # If the all-in raises the highest bet, the other players must act again
                    highest_bet = player.current_bet
                    self.ui.show_message(f"{player.name} goes all-in with {paid} chips.")
                    players_to_act = [
                        other_player 
                        for other_player in self.players if other_player.can_act and other_player != player]
                else:
                    self.ui.show_message(f"{player.name} goes all-in with {paid} chips.")            

            elif action == "raise": 
                # Simplified raise rule: the raise only has to increase the current bet by at least 1 chip.
                min_raise = 1

                # Maximum extra raise the player can afford after calling.
                max_raise = player.chips - call_amount

                # If the player cannot call (and thus not raise), they fold.
                if player.chips < call_amount:
                    player.folded = True

                    if player.is_human:
                        self._hide_private_info()

                    self.ui.show_message(f"{player.name} cannot call and folds")
                    continue

                # If the player can call but not raise, it will be treated as a call.
                if max_raise < min_raise:
                    paid = player.bet(call_amount)
                    self.table.add_to_pot(paid)

                    if player.is_human:
                        self._hide_private_info()

                    if call_amount == 0:
                        self.ui.show_message(f"{player.name} checks.")
                    else:
                        self.ui.show_message(f"{player.name} cannot raise, so they call {paid}.")

                else: # only happens if Player can actually raise
                    if player.is_human:
                        # Human Players choose the raise amount
                        raise_amount = self.ui.ask_raise_amount(min_raise, max_raise)
                    else:
                        # Bots calculate the raise automatically
                        raise_amount = self._bot_raise_amount(player, call_amount, min_raise, max_raise)

                    total_payment = call_amount + raise_amount
                    paid = player.bet(total_payment)
                    self.table.add_to_pot(paid)

                    # The raisers current bet becomes the new highest bet
                    highest_bet = player.current_bet

                    if player.is_human:
                        self._hide_private_info() # hide private info

                    self.ui.show_message(f"{player.name} raises by {raise_amount}.")
                    
                    # Adter a raise all other players must respond to the new highest bet. Thus, we update players_to_act
                    players_to_act = [
                        other_player
                        for other_player in self.players
                        if other_player.can_act and other_player != player ]

        # At end of the bettiing round the current_bet is reset.
        # The pot stays
        for player in self.players:
            player.current_bet = 0


    def _bot_action(self, player: Player, call_amount: int) -> str:
        # The bot makes a simple decision using hand strength, chip cost, and some randomness.
        strength = self._bot_hand_strength(player)

        # If the bot has no chips left, it cannot act anymore (it returns call and only if necessary the game will force a fold)
        if player.chips <= 0:
            return "call"
        
        call_ratio = call_amount / player.chips # shows how expensive the call is compared to the bots chips

        # If calling costs all remaining chips of the bot it will either go all in or fold
        if call_amount >= player.chips:
            if strength >= 6 or random.random() < 0.10:
                return "all_in"
            return "fold"
        
        # Decision between check or raise.
        if call_amount == 0:
            if strength >= 5 and (player.chips > self.big_blind) and random.random() < 0.50: # strong hands raise quite often.
                return "raise"
            if strength >= 3 and (player.chips > self.big_blind) and random.random() < 0.15: # medum hands sometimes raise.
                return "raise"
            if player.chips > self.big_blind and random.random() < 0.05: # weak hands rarly - bots can bluff.
                return "raise"
            return "call" # bot checks (represented as call with call_amount 0).
        
        # If calling costs more than almost half of the bots chips and the hand is weak it will fold
        if call_ratio > 0.45 and strength < 6: 
            return "fold"
        # if calling costs more than a quarter of the bots chips and the hand is weak is will usually fold (randomness)
        if call_ratio > 0.25 and strength < 4 and random.random() < 0.75:
            return "fold"
        
        # Strong hands might raise after another player has already bet.
        if strength >= 6 and player.chips > call_amount + self.big_blind and random.random() < 0.45:
            return "raise"
        # For Medium hands sometimes 
        if strength >= 4 and player.chips > call_amount + self.big_blind and random.random() < 0.20:
            return "raise"
        
        # Rare random raise so the bot does not always act the same way.
        if player.chips > call_amount + self.big_blind and random.random() < 0.05:
            return "raise"
        
        # Default action is call the current bet.
        return "call" 
    
    def _bot_hand_strength(self, player: Player) -> int:
        # Estimate how strong the bots hand is AFTER THE FLOP
        cards = player.hole_cards + self.table.community_cards

        if len(cards) >= 5:
            rank = self.evaluator.best_rank(cards)
            return int(rank.category) * 2
        return self._bot_preflop_strength(player)

    def _bot_preflop_strength(self, player: Player) -> int:
        # Estimate starting hand strength before community cards are dealt
        if len(player.hole_cards) < 2: # safety check
            return 0
        
        first_card = player.hole_cards[0]
        second_card = player.hole_cards[1]
        ranks = sorted([first_card.rank, second_card.rank], reverse=True) # 

        strength = 0

        if ranks[0] == ranks[1]: # A pair is a strong starting hand, so it gets many points.
            strength += 5
            if ranks[0] >= 10:  # High pairs like 10s, Jacks, Queens, Kings, or Aces are even stronger.
                strength += 2

        if ranks[0] >= 14: # highest card Ace
            strength += 2
        elif ranks[0] >= 11: # highest card Jack, Queem, King
            strength += 1

        if ranks[1] > 10: # if the second card is also high
            strength += 1 
        
        if first_card.suit == second_card.suit: # two cards of the same suit
            strength += 1

        return strength
    
    def _bot_raise_amount(self, player: Player, call_amount: int, minimum: int, maximum: int) -> int:
        # Bots will choose a random raise amount that is not too high.
        safe_maximum = min(maximum, self.big_blind * 3)
        safe_maximum = max(minimum, safe_maximum)
        return random.randint(minimum, safe_maximum)
    

    def _showdown(self) -> None:
        # Only players who have not folded can wind the hand.
        active_players = [player for player in self.players if not player.folded]
        
        if len(active_players) == 1:
            # If everyone but 1 player has folded, that player wins the whole pot.
            active_players[0].chips += self.table.pot
            active_players[0].wins += 1
            self.ui.show_message(f"{active_players[0].name} wins {self.table.pot} chips.")
            self.table.pot = 0
            return
        
        # Evaluate the best possible poker hand for each player that has not folded
        player_ranks = []
        for player in active_players:
            cards = player.hole_cards + self.table.community_cards
            rank = self.evaluator.best_rank(cards)
            player_ranks.append((player, rank))
            
            self.ui.show_message(f"{player.name}: {rank.label}")
            
            print("\n" + "-" * 30)
            print(f"{player.name.upper()}: {rank.label}")
            print("Hole cards:")
            show_cards(player.hole_cards)
            print("Community cards:")
            show_cards(self.table.community_cards)
            print("-" * 30)

        # Find best hand rank
        best_rank = max(rank for player, rank in player_ranks)
        
        # All players with the best hand rank are winners. 
        winners = [
            player
            for player, rank in player_ranks
            if rank == best_rank]
        
        winnings = self.table.pot // len(winners)
        odd_chips = self.table.pot % len(winners)

        for index, winner in enumerate(winners):
            # Split the pot evenly between the winners. The first winner gets the leftover chip(s).
            winner.chips += winnings

            if index == 0:
                winner.chips += odd_chips
            
            winner.wins += 1
    

        winner_names = ", ".join(winner.name for winner in winners)

        if len(winners) == 1:
            # 1 Winner
            self.ui.show_message(
                f"Winner: {winner_names} won {self.table.pot} chips with {best_rank.label}.")
        else:
            # Multiple Winners
            if odd_chips == 0:
                self.ui.show_message(
                    f"Winners: {winner_names} won {winnings} chips each with {best_rank.label}.")
            else:
                self.ui.show_message(
                    f"Winners: {winner_names} split the pot with {best_rank.label}. "
                    f"{winners[0].name} got {winnings + odd_chips} chips, "
                    f"the others got {winnings} chips each.")
            
        # Reset the pot after the chips have been distributed.
        self.table.pot = 0

    def _only_one_player_left(self) -> bool:
        # active means not folded, so all-in Players with 0 chips are still active and can wini at showdown
        active_players = [player for player in self.players if player.active]
        return len(active_players) == 1

    def _hide_private_info(self) -> None:
        if os.name == "nt":
            os.system("cls")
        elif os.environ.get("TERM") and os.environ.get("TERM") != "dumb":
            os.system("clear")
        else:
            print("\n" * 30)
        print("Previouly shown cards are hidden.")       
