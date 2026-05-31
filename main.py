"""Run the CLI Texas Hold'em starter game."""

from game import TexasHoldemGame
from player import Player

MINIMUM_PLAYERS = 2
MAXIMUM_PLAYERS = 8

MINIMUM_CHIPS = 50
MAXIMUM_CHIPS = 5_000

def ask_numbers_players(prompt: str, minimum_players: int, maximum_players: int) -> int:
    while True:
        try:
            number = int(input(prompt))
        except ValueError:
            print("Please enter a valid number.")
            continue

        if (number < minimum_players) or (number > maximum_players):
            print(f"Please enter a number between {minimum_players} and {maximum_players}.")
            continue

        return number

def create_players() -> list[Player]:
    total_players = ask_numbers_players("How many players should this game consist of in total?", MINIMUM_PLAYERS, MAXIMUM_PLAYERS)
    human_players = ask_numbers_players("How many human players are playing this game?", 1, total_players)

    players = []

    for i in range(human_players):
        name = input(f"Enter name for human player {i + 1}: ").strip()

        if name == "":
            name = f"Player {i + 1}"

        chips = ask_numbers_players(f"How many chips should {name} start with? " MINIMUM_CHIPS, MAXIMUM_CHIPS)

        players.append(Player(name, chips=chips, is_human=True))
            
    number_of_bots = total_players - human_players

    for i in range(number_of_bots):
        bot_name = f"Bot {i+1}"
        chips = ask_numbers_players(f"How many chips should {bot_name} start with? ", MINIMUM_CHIPS, MAXIMUM_CHIPS)
        
        players.append(Player(bot_name, chips=chips))
    
    return players


def main() -> None:
    players = create_players()

    game = TexasHoldemGame(players)

    game.play_hand()


if __name__ == "__main__":
    main()

