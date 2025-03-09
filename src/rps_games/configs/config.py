"""This module contains the Pydantic models for the game configuration."""

from typing import Dict, Literal

from pydantic import BaseModel


class GameConfig(BaseModel):
    """Game configuration model.

    Attributes:
        rules: The ruleset to use for the game.
        mode: The game mode (first_to or best_of).
        target_score: The target score for the game.
        rounds: The number of rounds to play.
    """

    rules: Literal["BASIC_RULES", "SPOCK_LIZARD"]
    mode: Literal["first_to", "best_of"]
    target_score: int
    rounds: int


class PlayerConfig(BaseModel):
    """Player configuration model.

    Attributes:
        type: The type of player (HumanPlayer, ComputerPlayer, or LLMPlayer).
        name: The name of the player.
    """

    type: Literal["HumanPlayer", "ComputerPlayer", "LLMPlayer"]
    name: str


class RulesConfig(BaseModel):
    """Rules configuration model.

    Attributes:
        BASIC_RULES: The basic rules of the game.
        SPOCK_LIZARD: The extended rules of the game.
    """

    BASIC_RULES: Dict[str, Dict[str, str]]
    SPOCK_LIZARD: Dict[str, Dict[str, str]]
