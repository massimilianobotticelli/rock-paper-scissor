"""Rock, Paper, Scissors game with extended rules."""

import logging
import os
from typing import Optional

import emoji
import yaml
from dotenv import load_dotenv

from rps_games.players import (
    PLAYERS_TYPES,
    ComputerPlayer,
    HumanPlayer,
    LLMPlayer,
    Player,
)

load_dotenv()

# Configure logging to write to a file instead of the console
logging.basicConfig(
    filename="game.log",
    level=logging.INFO,
    filemode="w",
    format="%(asctime)s - %(levelname)s - %(message)s",
)

def validate_player(player_config: dict[str, str], rules: Optional[dict]) -> Player:
    """Validate the player configuration and return the player object.

    Args:
        player_config (dict[str, str]): Player configuration dictionary.
        rules (Optional[dict]): Rules dictionary for the game. Required for LLMPlayer.

    Returns:
        Player: Player object based on the configuration.

    Raises:
        ValueError: If the player type is invalid.
    """

    if player_config["type"] not in PLAYERS_TYPES:
        raise ValueError(f"Invalid player type for player one. Must be {PLAYERS_TYPES}")

    if player_config["type"] == "HumanPlayer":
        player = HumanPlayer(name=player_config["name"])
    elif player_config["type"] == "ComputerPlayer":
        player = ComputerPlayer(name=player_config["name"])
    elif player_config["type"] == "LLMPlayer":
        player = LLMPlayer(name=player_config["name"], rules=rules)
    else:
        raise ValueError(f"Invalid player type for player one. Must be {PLAYERS_TYPES}")
    return player

class RuleSet:
    """RuleSet class to store the rules of the game.

    Attributes:
        rules (dict[str, dict[str, str]]): Dictionary where keys are choices and values are
            dictionaries of choices they can defeat with reasons.

            Example:
                {
                    "Rock": {"Scissors": "crushes"},
                    "Scissors": {"Paper": "cuts"},
                    "Paper": {"Rock": "covers"},
                }
    """

    def __init__(self, rules: dict[str, dict[str, str]]):
        """Initializes the RuleSet with the given rules.

        Args:
            rules (dict[str, dict[str, str]]): The rules of the game.
        """
        self.rules = rules

    def get_choices(self) -> list[str]:
        """Gets the list of possible choices.

        Returns:
            list[str]: List of choices.
        """
        return list(self.rules.keys())

    def determine_winner(
        self, choice_a: str, choice_b: str
    ) -> Optional[tuple[str, str]]:
        """Determines the winner between two choices.

        Args:
            choice_a (str): First choice.
            choice_b (str): Second choice.

        Returns:
            Optional[tuple[str, str]]: Tuple containing the winning choice and the reason,
                or None if it's a draw.

        Example:
            >>> rules = RuleSet(BASIC_RULES)
            >>> rules.determine_winner("Rock", "Scissors")
                ("Rock", "crushes")
            >>> rules.determine_winner("Scissors", "Paper")
                ("Scissors", "cuts")
        """
        if choice_a == choice_b:
            return None
        if choice_a in self.rules[choice_b]:
            return choice_b, self.rules[choice_b][choice_a]
        return choice_a, self.rules[choice_a][choice_b]


class Game:
    """Game class to play the game.

    Attributes:
        player_a (Player): First player.
        player_b (Player): Second player.
        rule_set (RuleSet): RuleSet object containing the game rules.
        history (list[str]): List to store the history of the game.

    Methods:
        log_and_print: Logs and prints a message.
        play_best_of: Plays a game with the best of a specified number of rounds.
        play_first_to: Plays a game where the first player to reach a specified score wins.
        _play_round: Plays a single round of the game.
        _get_winner: Gets the winner of the game.
    """

    def __init__(self, player_a: Player, player_b: Player, rule_set: RuleSet):
        """Initializes the Game with the given players and rules.

        Args:
            player_a (Player): First player.
            player_b (Player): Second player.
            rule_set (RuleSet): RuleSet object containing the game rules.
        """
        self.player_a = player_a
        self.player_b = player_b
        self.rule_set = rule_set
        self.history = []

    def log_and_print(self, message: str):
        """Logs and prints a message.

        Args:
            message (str): Message to log and print.
        """
        self.history.append(message)
        logging.info(message)
        print(message)

    def play_best_of(self, rounds: int = 3) -> Optional[Player]:
        """Plays a game with the best of a specified number of rounds.

        Args:
            rounds (int): Number of rounds to play.

        Returns:
            Optional[Player]: The player who wins the most rounds, or None if it's a draw.
        """
        self.log_and_print(f"\nBest of {rounds} rounds")
        for round_num in range(rounds):
            self.log_and_print(f"\n---------\nRound {round_num+1}\n---------")
            self._play_round()

        if self.player_a.score == self.player_b.score:
            return None

        return self._get_winner()

    def play_first_to(self, score: int = 3) -> Player:
        """Plays a game where the first player to reach a specified score wins.

        Args:
            score (int): Score to reach to win the game.

        Returns:
            Player: The player who reaches the score first.
        """
        self.log_and_print(f"\nFirst to {score} wins")
        round_num = 0
        while self.player_a.score < score and self.player_b.score < score:
            self.log_and_print(f"\n--------\nRound {round_num+1}\n--------")
            self._play_round()
            round_num += 1

        return self._get_winner()

    def _play_round(self):
        """Plays a single round of the game."""
        choices = self.rule_set.get_choices()
        choice_a = self.player_a.choice(choices=choices, history=self.history)
        choice_b = self.player_b.choice(choices=choices, history=self.history)

        self.log_and_print(f"{self.player_a} chooses {choice_a}")
        self.log_and_print(f"{self.player_b} chooses {choice_b}")

        result = self.rule_set.determine_winner(choice_a, choice_b)

        if result is None:
            self.log_and_print("Draw")
            return

        winning_choice, reason = result

        winner = self.player_a if winning_choice == choice_a else self.player_b
        winner.score += 1

        self.log_and_print(
            f"{winning_choice} {reason} {choice_b if winning_choice == choice_a else choice_a}"
        )

        self.log_and_print(f"{winner} wins this round")

        self.log_and_print(
            f"Score: {self.player_a} {self.player_a.score} - {self.player_b} {self.player_b.score}"
        )

        return

    def _get_winner(self) -> Player:
        """Gets the winner of the game.

        Returns:
            Player: The player with the highest score.
        """
        return (
            self.player_a
            if self.player_a.score > self.player_b.score
            else self.player_b
        )


if __name__ == "__main__":

    # Get the directory of configuration and rules file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    config_file_path = os.path.join(current_dir, "configs/game_config.yaml")
    rules_file_path = os.path.join(current_dir, "configs/rules.yaml")

    # Load the game and rules configuration from the YAML file
    with open(config_file_path, "r", encoding="utf-8") as file:
        config = yaml.safe_load(file)

    with open(rules_file_path, "r", encoding="utf-8") as file:
        defined_rules = yaml.safe_load(file)

    # Get and validate the chosen rules from the configuration
    chosen_rules = config["game"]["rules"]

    if chosen_rules not in defined_rules:
        raise ValueError("Invalid rule set. Must be one of the keys in rules.yaml")

    game_rules = RuleSet(defined_rules[chosen_rules])

    # Get player configurations and init the players
    player_one = validate_player(
        config["players"]["player_one"], defined_rules[chosen_rules]
    )
    player_two = validate_player(
        config["players"]["player_two"], defined_rules[chosen_rules]
    )

    # Initialize the game with the players and rules
    game = Game(player_one, player_two, game_rules)

    # Play the game based on the mode specified in the configuration
    if config["game"]["mode"] == "first_to":
        game_winner = game.play_first_to(score=config["game"]["target_score"])
    if config["game"]["mode"] == "best_of":
        game_winner = game.play_best_of(rounds=config["game"]["rounds"])
    else:
        raise ValueError("Invalid game mode. Must be 'first_to' or 'best_of'")

    # Log and print the game over message
    print("\nGame Over")

    # Log and print the winner or draw message
    if game_winner is None:
        print("Draw")
    else:
        print(
            emoji.emojize(
                f":party_popper: {game_winner} wins with a score of "
                f"{game_winner.score} :party_popper:"
            )
        )
