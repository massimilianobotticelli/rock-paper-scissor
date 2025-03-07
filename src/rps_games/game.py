"""Rock, Paper, Scissors game with extended rules."""

import getpass
import random
import sys
from abc import ABC, abstractmethod
from typing import Optional

import emoji

BASIC_RULES = {
    "Rock": {"Scissors": "crushes"},
    "Scissors": {"Paper": "cuts"},
    "Paper": {"Rock": "covers"},
}

EXTENDED_RULES = {
    "Lizard": {"Spock": "poisons", "Paper": "eats"},
    "Spock": {"Scissors": "smashes", "Rock": "vaporizes"},
    "Rock": {"Scissors": "crushes", "Lizard": "crushes"},
    "Scissors": {"Paper": "cuts", "Lizard": "decapitates"},
    "Paper": {"Rock": "covers", "Spock": "disproves"},
}


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


class Game:
    """Game class to play the game.

    Attributes:
        player_a (Player): First player.
        player_b (Player): Second player.
        rule_set (RuleSet): RuleSet object containing the game rules.

        Methods:
            round_eval: Evaluates the round and updates the score.
            play_best_of: Plays a game with the best of a specified number of rounds.
            play_first_to: Plays a game where the first player to reach a specified score wins.
            play_round: Plays a single round of the game.
    """

    def __init__(self, player_a: Player, player_b: Player, rule_set: RuleSet):
        self.player_a = player_a
        self.player_b = player_b
        self.rule_set = rule_set

    def round_eval(self, winner: Optional[Player]):
        """Evaluates the round and updates the score.

        Args:
            winner (Optional[Player]): The player who won the round, or None if it's a draw.
        """
        if winner is None:
            print("Draw")
        else:
            winner.score += 1
            print(f"{winner} wins this round")

        print(
            f"Score: {self.player_a} {self.player_a.score} - {self.player_b} {self.player_b.score}"
        )

    def get_winner(self) -> Player:
        """Gets the winner of the game.

        Returns:
            Player: The player with the highest score.
        """
        return (
            self.player_a
            if self.player_a.score > self.player_b.score
            else self.player_b
        )

    def play_best_of(self, rounds: int = 3) -> Optional[Player]:
        """Plays a game with the best of a specified number of rounds.

        Args:
            rounds (int): Number of rounds to play.

        Returns:
            Optional[Player]: The player who wins the most rounds, or None if it's a draw.
        """
        print(f"\nBest of {rounds} rounds")
        for round_num in range(rounds):
            print("\n---------")
            print(f"Round {round_num+1}")
            print("---------")
            self.play_round()

        if self.player_a.score == self.player_b.score:
            return None

        return self.get_winner()

    def play_first_to(self, score: int = 3) -> Player:
        """Plays a game where the first player to reach a specified score wins.

        Args:
            score (int): Score to reach to win the game.

        Returns:
            Player: The player who reaches the score first.
        """
        print(f"\nFirst to {score} wins")
        round_num = 0
        while self.player_a.score < score and self.player_b.score < score:
            print("\n--------")
            print(f"Round {round_num+1}")
            print("--------")
            self.play_round()
            round_num += 1

        return self.get_winner()

    def play_round(self):
        """Plays a single round of the game."""
        choices = self.rule_set.get_choices()
        choice_a = self.player_a.choice(choices=choices)
        choice_b = self.player_b.choice(choices=choices)

        print(f"{self.player_a} chooses {choice_a}")
        print(f"{self.player_b} chooses {choice_b}")

        result = self.rule_set.determine_winner(choice_a, choice_b)

        if result is None:
            print("Draw")
            return

        winning_choice, reason = result
        winner = self.player_a if winning_choice == choice_a else self.player_b

        print(
            f"{winning_choice} {reason} {choice_b if winning_choice == choice_a else choice_a}"
        )
        self.round_eval(winner)

        return


if __name__ == "__main__":

    game_rules = RuleSet(EXTENDED_RULES)

    player_one = ComputerPlayer(name="Computer A")
    player_two = ComputerPlayer(name="Computer B")

    # player_one = HumanPlayer(name="Massimiliano")
    # player_two = HumanPlayer(name="Peter")

    game = Game(player_one, player_two, game_rules)

    game_winner = game.play_first_to(score=3)
    # game_winner = game.play_best_of(rounds=5)

    print("\nGame Over")

    if game_winner is None:
        print("Draw")
    else:
        print(
            emoji.emojize(
                f":party_popper: {game_winner} wins with a score of "
                f"{game_winner.score} :party_popper:"
            )
        )
