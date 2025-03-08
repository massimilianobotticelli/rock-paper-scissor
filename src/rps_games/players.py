"""Players module."""
import getpass
import random
import sys
from abc import ABC, abstractmethod
from typing import Optional

from langchain_core.prompts import PromptTemplate
from google.api_core.exceptions import ResourceExhausted
from langchain_google_genai import ChatGoogleGenerativeAI

PLAYERS_TYPES = ["HumanPlayer", "ComputerPlayer", "LLMPlayer"]


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
        """Initializes the player with a name and a score of 0.

        Args:
            name (str): Name of the player.
        """
        self.name = name
        self.score = 0

    @abstractmethod
    def choice(self, choices: list[str], history: Optional[list] = None) -> str:
        """Abstract method to get the player's choice.

        Args:
            choices (list[str]): List of possible choices.
            history (Optional[list]): List of previous choices made in the game.

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
        choice: Gets the human player's choice using a secure input method.
        __str__: String representation of the player.
    """

    def choice(self, choices: list[str], history: Optional[list] = None) -> str:
        """Gets the human player's choice using a secure input method. This avoids
        that if two humans are playing, they know what the other player has chosen.

        Args:
            choices (list[str]): List of possible choices.
            history (Optional[list]): List of previous choices made in the game.

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

    def choice(self, choices: list[str], history: Optional[list] = None) -> str:
        """Gets the computer player's choice randomly.

        Args:
            choices (list[str]): List of possible choices.
            history (Optional[list]): List of previous choices made in the game.

        Returns:
            str: Chosen option.
        """
        return random.choice(choices)


class LLMPlayer(Player):
    """LLM Player class.

    Attributes:
        name (str): Name of the player.
        score (int): Score of the player.
        model (ChatGoogleGenerativeAI): Language model for generating choices.
        rules (dict[str, dict[str, str]]): Rules of the game.

    Methods:
        choice: Gets the LLM player's choice based on a generated prompt.
        _generate_prompt: Generates a prompt for the LLM with the current choices and game history.
        __str__: String representation of the player.
    """

    def __init__(self, name: str, rules: dict[str, dict[str, str]]):
        """Initializes the LLM player with a name, rules, and a language model.

        Args:
            name (str): Name of the player.
            rules (dict[str, dict[str, str]]): Rules of the game.
        """
        super().__init__(name)
        self.model = ChatGoogleGenerativeAI(model="gemini-1.5-flash")
        self.rules = rules

    def _generate_prompt(self, choices: list[str], history: list) -> str:
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

        Develop a strategy based on the game history. Game history between you
        and your opponent (your name is {name}):
        {history}

        What is your next move? Answer providing only the choice (e.g., 'Rock').
        """
        prompt = PromptTemplate(
            input_variables=["choices", "history"], template=template
        )
        choices_str = "\n".join(f"- {choice}" for choice in choices)
        history_str = "\n".join(history)
        rules_str = "\n".join(
            f"{choice} {reason} {defeated_choice}"
            for choice in self.rules
            for defeated_choice, reason in self.rules[choice].items()
        )
        return prompt.format(
            choices=choices_str, history=history_str, rules=rules_str, name=self.name
        )

    def choice(self, choices: list[str], history: list) -> str:
        """Gets the LLM player's choice based on a generated prompt.

        Args:
            choices (list[str]): List of possible choices.
            history (list[str]): List of previous choices made in the game.

        Returns:
            str: Chosen option.
        """
        prompt = self._generate_prompt(choices, history)
        try:
            res = self.model.invoke(prompt)
        except ResourceExhausted:
            print("LLM resource exhausted. Please try again.")
            sys.exit()
        return res.content
