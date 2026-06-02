"""Run the CLI Texas Hold'em starter game."""

from game import TexasHoldemGame
from player import Player
from simulation import run_simulation, print_results

MINIMUM_PLAYERS = 2
MAXIMUM_PLAYERS = 8

MINIMUM_CHIPS = 50
MAXIMUM_CHIPS = 5_000

def ask_numbers_players(prompt: str, minimum_players: int, maximum_players: int) -> int:
    while True:
        try:
            number = int(input(prompt))
        except ValueError:
            print("Please enter a valid number. ")
            continue

        if (number < minimum_players) or (number > maximum_players):
            print(f"Please enter a number between {minimum_players} and {maximum_players}. ")
            continue

        return number

def create_players() -> list[Player]:
    total_players = ask_numbers_players("\nHow many players should this game consist of in total? ", MINIMUM_PLAYERS, MAXIMUM_PLAYERS)
    human_players = ask_numbers_players("How many human players are playing this game? ", 1, total_players)

    players = []

    for i in range(human_players):
        name = input(f"Enter name for human player {i + 1}: ").strip()

        if name == "":
            name = f"Player {i + 1}"

        chips = ask_numbers_players(f"How many chips should {name} start with? ", MINIMUM_CHIPS, MAXIMUM_CHIPS)

        players.append(Player(name, chips=chips, is_human=True))
            
    number_of_bots = total_players - human_players

    for i in range(number_of_bots):
        bot_name = f"Bot {i+1}"
        chips = ask_numbers_players(f"How many chips should {bot_name} start with? ", MINIMUM_CHIPS, MAXIMUM_CHIPS)
        
        players.append(Player(bot_name, chips=chips))
    
    return players

def players_with_chips(players: list[Player]) -> list[Player]:
    return [player for player in players if player.chips > 0]

def reset_scoreboard(players: list[Player]) -> None:
    for player in players:
        player.wins = 0
        player.starting_chips = player.chips

def main() -> None:
    players = create_players()
    all_players = players.copy()
    hand_number = 1

    try:
        while len(players_with_chips(players)) > 1:
            players = players_with_chips(players)
            print(f"\n========== Hand {hand_number} ==========")
        
            game = TexasHoldemGame(players)
        
            game.play_hand()
        
            players = players_with_chips(players)

            if len(players) > 1:
                answer = input("\nPress Enter to play the next hand, or type q to quit: ").strip().lower()

                if answer == "q":
                    print("\nGame stopped by player.")
                    return
            
                players.append(players.pop(0)) # simplified version of dealer button rotation

            hand_number += 1
    
        winner = players_with_chips(players)[0]
        print(f"\nGame over! {winner.name} wins the game!")

    finally:
        reset_scoreboard(all_players)

# ================================================
# Monte Carlo Simulation for Poker Hand Probabilities
# ================================================  
print("\nRunning Monte Carlo simulation\n")
num_trials = 10000
results = run_simulation(num_trials)
print_results(results, num_trials)


if __name__ == "__main__":
    main()
