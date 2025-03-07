"""Rock, Paper, Scissors game with extended rules."""

import getpass
import random
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
    """RuleSet class to store the rules of the game."""

    def __init__(self, rules: dict):
        """
        Initializes the RuleSet with a dictionary of rules.

        Args:
            rules (dict): Dictionary where keys are choices and values are
                dictionaries of choices they can defeat with reasons.
        """
        self.rules = rules

    def get_choices(self):
        """
        Gets the list of possible choices.

        Returns:
            list: List of choices.
        """
        return list(self.rules.keys())

    def determine_winner(self, choice_a: str, choice_b: str) -> Optional[tuple]:
        """
        Determines the winner between two choices.

        Args:
            choice_a (str): First choice.
            choice_b (str): Second choice.

        Returns:
            Optional[tuple]: Tuple containing the winning choice and the reason,
                or None if it's a draw.
        """
        if choice_a == choice_b:
            return None
        if choice_a in self.rules[choice_b]:
            return choice_b, self.rules[choice_b][choice_a]
        return choice_a, self.rules[choice_a][choice_b]


class Player(ABC):
    """Abstract Player class."""

    def __init__(self, name: str):
        """
        Initializes a Player with a name and score.

        Args:
            name (str): Name of the player.
        """
        self.name = name
        self.score = 0

    @abstractmethod
    def choice(self, choices: list):
        """
        Abstract method to get the player's choice.

        Args:
            choices (list): List of possible choices.
        """
        pass

    def __str__(self):
        """
        String representation of the player.

        Returns:
            str: Name of the player.
        """
        return self.name


class HumanPlayer(Player):
    """HumanPlayer class to get the choice from the user."""

    def choice(self, choices: list):
        """
        Gets the human player's choice using a secure input method.

        Args:
            choices (list): List of possible choices.

        Returns:
            str: Chosen option.
        """
        return getpass.getpass(f"{self.name}, enter your choice {choices}: ")


class ComputerPlayer(Player):
    """ComputerPlayer class to get the choice randomly."""

    def choice(self, choices: list):
        """
        Gets the computer player's choice randomly.

        Args:
            choices (list): List of possible choices.

        Returns:
            str: Chosen option.
        """
        return random.choice(choices)


class Game:
    """Game class to play the game."""

    def __init__(self, player_a: Player, player_b: Player, rule_set: RuleSet):
        """
        Initializes the Game with two players and a rule set.

        Args:
            player_a (Player): First player.
            player_b (Player): Second player.
            rule_set (RuleSet): RuleSet object containing the game rules.
        """
        self.player_a = player_a
        self.player_b = player_b
        self.rule_set = rule_set

    def round_eval(self, winner: Player):
        """
        Evaluates the round and updates the score.

        Args:
            winner (Player): The player who won the round, or None if it's a draw.
        """
        if winner is None:
            print("Draw")
        else:
            winner.score += 1
            print(f"{winner} wins this round")

        print(
            f"Score: {self.player_a}: {self.player_a.score} - {self.player_b}: \
                {self.player_b.score}"
        )

    def play_best_of(self, rounds: int = 3) -> Player:
        """
        Plays a game with the best of a specified number of rounds.

        Args:
            rounds (int): Number of rounds to play.

        Returns:
            Player: The player who wins the most rounds, or None if it's a draw.
        """
        print(f"Best of {rounds} rounds")
        for round_num in range(rounds):
            print("\n---------")
            print(f"Round {round_num+1}")
            print("---------")
            self.play_round()

        if self.player_a.score == self.player_b.score:
            return None
        return (
            self.player_a
            if self.player_a.score > self.player_b.score
            else self.player_b
        )

    def play_first_to(self, score: int = 3) -> Player:
        """
        Plays a game where the first player to reach a specified score wins.

        Args:
            score (int): Score to reach to win the game.

        Returns:
            Player: The player who reaches the score first.
        """
        print(f"First to {score} wins")
        round_num = 0
        while self.player_a.score < score and self.player_b.score < score:
            print(f"\nRound {round_num+1}")
            self.play_round()
            round_num += 1

        return (
            self.player_a
            if self.player_a.score > self.player_b.score
            else self.player_b
        )

    def play_round(self):
        """
        Plays a single round of the game.
        """
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

    computer_a = ComputerPlayer(name="Computer A")
    computer_b = ComputerPlayer(name="Computer B")
    # player_a = HumanPlayer(name="Massimiliano")
    # player_b = HumanPlayer(name="Sarah")

    game_rules = RuleSet(EXTENDED_RULES)

    game = Game(computer_a, computer_b, game_rules)
    # winner = game.play_first_to(score=3)
    game_winner = game.play_best_of(rounds=5)

    print("\nGame Over")

    if game_winner is None:
        print("Draw")
    else:
        print(
            emoji.emojize(
                f":party_popper: {game_winner} wins with a score of \
                    {game_winner.score} :party_popper:"
            )
        )
