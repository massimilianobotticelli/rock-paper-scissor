"""Rock, Paper, Scissors game with extended rules."""

import getpass
import random
import sys
import os
import logging
from abc import ABC, abstractmethod
from typing import Optional

from icecream import ic

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
import emoji
import yaml

from dotenv import load_dotenv

load_dotenv()

# Configure logging to write to a file instead of the console
logging.basicConfig(filename='game.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s', filemode='w')

PLAYERS_TYPES = ["HumanPlayer", "ComputerPlayer", "LLMPlayer"]
GAME_TYPES = ["first_to", "best_of"]

def log_and_print(message: str):
    """Logs and prints a message."""
    
    logging.info(message)
    print(message)


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


class Player(ABC):
    """Abstract Player class.

    Attributes:
        name (str): Name of the player.
        score (int): Score of the player.

    Methods:
        choice: Abstract method to get the player's choice.
        __str__: String representation of the player.
    """

    def __init__(self, name: str):
        self.name = name
        self.score = 0

    @abstractmethod
    def choice(self, choices: list[str]) -> str:
        """Abstract method to get the player's choice.

        Args:
            choices (list[str]): List of possible choices.

        Returns:
            str: Chosen option.
        """

    def __str__(self) -> str:
        """String representation of the player.

        Returns:
            str: Name of the player.
        """
        return self.name


class HumanPlayer(Player):
    """Human Player class.

    Attributes:
        name (str): Name of the player.
        score (int): Score of the player.

    Methods:
        choice: Gets the human player's choice using a secure
            input method.
        __str__: String representation of the player.
    """

    def choice(self, choices: list[str]) -> str:
        """Gets the human player's choice using a secure input method. This avoids
        that if two humans are playing, they know what the other player has chosen.

        Args:
            choices (list[str]): List of possible choices.

        Returns:
            str: Chosen option.
        """
        while True:
            choice = getpass.getpass(
                f"{self.name}, enter your choice {choices} " f"(or 'q' to quit): "
            )
            if choice.upper() == "Q":
                sys.exit()
            if choice in choices:
                return choice
            print(f"Invalid choice. Please choose from {choices}.")


class ComputerPlayer(Player):
    """Computer Player class.

    Attributes:
        name (str): Name of the player.
        score (int): Score of the player.

    Methods:
        choice: Gets the computer player's choice randomly.
        __str__: String representation of the player.
    """

    def choice(self, choices: list[str]) -> str:
        """Gets the computer player's choice randomly.

        Args:
            choices (list[str]): List of possible choices.

        Returns:
            str: Chosen option.
        """
        return random.choice(choices)
    

class LLMPlayer(Player):

    def __init__(self, name: str, rules: dict[str, dict[str, str]]):
        super().__init__(name)
        self.model  = ChatGoogleGenerativeAI(model="gemini-1.5-flash")
        self.rules = rules

    def _generate_prompt(self, choices: list[str]) -> str:
        """Generates a prompt for the LLM with the current choices and game history.

        Args:
            choices (list[str]): List of possible choices.
            history (list[str]): List of previous choices made in the game.

        Returns:
            str: Generated prompt.
        """
        template = """
        You are playing Rock, Paper, Scissors or an extended version of it.
        
        Here are your options:
        {choices}

        Here are the rules:
        {rules}

        Game history between you and your opponent (your name is {name}):
        {history}

        What is your next move? Develop a strategy based on the game history.
        
        Answer providing only the choice (e.g., 'Rock').
        """
        prompt = PromptTemplate(
            input_variables=["choices", "history"],
            template=template
        )
        choices_str = "\n".join(f"- {choice}" for choice in choices)
        with open('game.log', 'r', encoding="utf-8") as log_file:
            history_str = log_file.read()
        rules_str = "\n".join(
            f"{choice} {reason} {defeated_choice}" for choice in self.rules for defeated_choice, reason in self.rules[choice].items()
        )
        return prompt.format(choices=choices_str, history=history_str, rules=rules_str,
                             name=self.name)

    def choice(self, choices: list[str]) -> str:
        prompt = self._generate_prompt(choices)
        ic(prompt)
        res = self.model.invoke(prompt)
        return res.content

class Game:
    """Game class to play the game.

    Attributes:
        player_a (Player): First player.
        player_b (Player): Second player.
        rule_set (RuleSet): RuleSet object containing the game rules.

        Methods:
            play_best_of: Plays a game with the best of a specified number of rounds.
            play_first_to: Plays a game where the first player to reach a specified score wins.
            _play_round: Plays a single round of the game.
            _round_eval: Evaluates the round and updates the score.
            _get_winner: Gets the winner of the game.
    """

    def __init__(self, player_a: Player, player_b: Player, rule_set: RuleSet):
        self.player_a = player_a
        self.player_b = player_b
        self.rule_set = rule_set

    def play_best_of(self, rounds: int = 3) -> Optional[Player]:
        """Plays a game with the best of a specified number of rounds.

        Args:
            rounds (int): Number of rounds to play.

        Returns:
            Optional[Player]: The player who wins the most rounds, or None if it's a draw.
        """
        log_and_print(f"\nBest of {rounds} rounds")
        for round_num in range(rounds):
            log_and_print(f"\n---------\nRound {round_num+1}\n---------")
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
        log_and_print(f"\nFirst to {score} wins")
        round_num = 0
        while self.player_a.score < score and self.player_b.score < score:
            log_and_print(f"\n--------\nRound {round_num+1}\n--------")
            self._play_round()
            round_num += 1

        return self._get_winner()

    def _play_round(self):
        """Plays a single round of the game."""
        choices = self.rule_set.get_choices()
        choice_a = self.player_a.choice(choices=choices)
        choice_b = self.player_b.choice(choices=choices)

        log_and_print(f"{self.player_a} chooses {choice_a}")
        log_and_print(f"{self.player_b} chooses {choice_b}")

        result = self.rule_set.determine_winner(choice_a, choice_b)

        if result is None:
            log_and_print("Draw")
            return

        winning_choice, reason = result
        winner = self.player_a if winning_choice == choice_a else self.player_b

        log_and_print(
            f"{winning_choice} {reason} {choice_b if winning_choice == choice_a else choice_a}"
        )
        self._round_eval(winner)

        return

    def _round_eval(self, winner: Optional[Player]):
        """Evaluates the round and updates the score.

        Args:
            winner (Optional[Player]): The player who won the round, or None if it's a draw.
        """
        if winner is None:
            log_and_print("Draw")
        else:
            winner.score += 1
            log_and_print(f"{winner} wins this round")

        log_and_print(
            f"Score: {self.player_a} {self.player_a.score} - {self.player_b} {self.player_b.score}"
        )

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

    # Get player configurations
    player_one_config = config["players"]["player_one"]
    player_two_config = config["players"]["player_two"]

    if (
        player_one_config["type"] not in PLAYERS_TYPES
        or player_two_config["type"] not in PLAYERS_TYPES
    ):
        raise ValueError(f"Invalid player type for player one. Must be {PLAYERS_TYPES}")

    # Initialize player one based on the configuration
    if player_one_config["type"] == "HumanPlayer":
        player_one = HumanPlayer(name=player_one_config["name"])
    elif player_one_config["type"] == "ComputerPlayer":
        player_one = ComputerPlayer(name=player_one_config["name"])
    elif player_one_config["type"] == "LLMPlayer":
        player_one = LLMPlayer(name=player_one_config["name"], rules=defined_rules[chosen_rules])
    else:
        raise ValueError(f"Invalid player type for player one. Must be {PLAYERS_TYPES}")

    # Initialize player two based on the configuration
    if player_two_config["type"] == "HumanPlayer":
        player_two = HumanPlayer(name=player_two_config["name"])
    elif player_two_config["type"] == "ComputerPlayer":
        player_two = ComputerPlayer(name=player_two_config["name"])
    elif player_two_config["type"] == "LLMPlayer":
        player_two = LLMPlayer(name=player_two_config["name"], rules=defined_rules[chosen_rules])
    else:
        raise ValueError(f"Invalid player type for player two. Must be {PLAYERS_TYPES}")

    # Initialize the game with the players and rules
    game = Game(player_one, player_two, game_rules)

    # Validate the game mode
    if config["game"]["mode"] not in GAME_TYPES:
        raise ValueError(f"Invalid game mode. Must be one of {GAME_TYPES}")

    # Play the game based on the mode specified in the configuration
    if config["game"]["mode"] == "first_to":
        game_winner = game.play_first_to(score=config["game"]["target_score"])
    else:
        game_winner = game.play_best_of(rounds=config["game"]["rounds"])

    # Log and print the game over message
    log_and_print("\nGame Over")

    # Log and print the winner or draw message
    if game_winner is None:
        log_and_print("Draw")
    else:
        log_and_print(
            emoji.emojize(
                f":party_popper: {game_winner} wins with a score of "
                f"{game_winner.score} :party_popper:"
            )
        )
