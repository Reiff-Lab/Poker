"""Run the CLI Texas Hold'em starter game."""

from game import TexasHoldemGame
from player import Player
from simulation import run_simulation, print_results

# Min and Max allowed number of players in a game
MINIMUM_PLAYERS = 2
MAXIMUM_PLAYERS = 8

# Min and Max starting chips allowed for each player
MINIMUM_CHIPS = 50
MAXIMUM_CHIPS = 5_000

def ask_numbers_players(prompt: str, minimum_players: int, maximum_players: int) -> int:
    # Asks for number only returns if valid
    while True:
        try:
            number = int(input(prompt))
        except ValueError: # for invalid input
            print("Please enter a valid number. ")
            continue

        if (number < minimum_players) or (number > maximum_players): # check that number is within allowed range
            print(f"Please enter a number between {minimum_players} and {maximum_players}. ")
            continue

        return number # if numbe valid, it is returned

def create_players() -> list[Player]:
    # Ask how many players in total should play.
    total_players = ask_numbers_players("\nHow many players should this game consist of in total? ", MINIMUM_PLAYERS, MAXIMUM_PLAYERS)
    
    # Aks how many of those are humans.
    human_players = ask_numbers_players("How many human players are playing this game? ", 1, total_players)

    players = []

    # Create the human players.
    for i in range(human_players):
        name = input(f"Enter name for human player {i + 1}: ").strip()

        if name == "": # Default name, if the player does not enter a name
            name = f"Player {i + 1}"

        # Aks how many chips human player starts with
        chips = ask_numbers_players(f"How many chips should {name} start with? ", MINIMUM_CHIPS, MAXIMUM_CHIPS)

        # Create the player object and mark it as human Player
        players.append(Player(name, chips=chips, is_human=True))
            
    # Remaining Players are bots
    number_of_bots = total_players - human_players

    # Create all bots.
    for i in range(number_of_bots):
        bot_name = f"Bot {i+1}"
        # Asks how many chips this bots starts with.
        chips = ask_numbers_players(f"How many chips should {bot_name} start with? ", MINIMUM_CHIPS, MAXIMUM_CHIPS)
        
        players.append(Player(bot_name, chips=chips)) # Bots use is_human by default, so its not added here
    
    return players # return finished list of all players.

def players_with_chips(players: list[Player]) -> list[Player]:
    # retuns only players who still have chips. Players with 0 chips are removed from the next rounds/hand.
    return [player for player in players if player.chips > 0]

def reset_scoreboard(players: list[Player]) -> None:
    # Reset scoreboard values.
    for player in players:
        player.wins = 0
        player.starting_chips = player.chips

def main() -> None:
    # Create the player before the first hand starts
    players = create_players()
    all_players = players.copy() # we save a copy of all players for the scoreboard.
    
    # Count which round/hand is being played.
    hand_number = 1

    try:
        # Keep playing as long as at least two players still have chips.
        while len(players_with_chips(players)) > 1:
            # Removing players with 0 chips before starting the next hand.
            players = players_with_chips(players)
            print(f"\n========== Hand {hand_number} ==========")
        
            # Create a new THG object for this round/hand.
            # the same player objects get reused and their chip counts continue.
            game = TexasHoldemGame(players)
        
            # Play one complete hand. 
            game.play_hand()
        
            # Remove players who lost all their chips during this hand.
            players = players_with_chips(players)

            # if more than one player still has chips, ask if continue.
            # Allows quit (to stop the whole game)
            if len(players) > 1:
                answer = input("\nPress Enter to play the next hand, or type q to quit: ").strip().lower()

                if answer == "q":
                    print("\nGame stopped by player.")
                    return
            
                # Move the first player to the end of the lsit
                players.append(players.pop(0)) # simplified version of dealer button rotation

            # Increase the hand number for the next round/hand.
            hand_number += 1
    
        # If only one player still has chips, that player wins the whole game.
        winner = players_with_chips(players)[0]
        print(f"\nGame over! {winner.name} wins!")

    finally:
        # Always runs when main() ends
        # Reset scoreboard also runs if player quits
        reset_scoreboard(all_players)

# ================================================
# Monte Carlo Simulation for Poker Hand Probabilities
# ================================================  
def run_monte_carlo():
    print("\nRunning Monte Carlo simulation\n")
    num_trials = 10000
    results = run_simulation(num_trials)
    print_results(results, num_trials)



if __name__ == "__main__":
    run_monte_carlo()
    main()
