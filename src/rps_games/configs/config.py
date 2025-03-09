from pydantic import BaseModel
from typing import Literal, Dict

class GameConfig(BaseModel):
    rules: Literal["BASIC_RULES", "SPOCK_LIZARD"]
    mode: Literal["first_to", "best_of"]
    target_score: int
    rounds: int

class PlayerConfig(BaseModel):
    type: Literal["HumanPlayer", "ComputerPlayer", "LLMPlayer"]
    name: str

class RulesConfig(BaseModel):
    BASIC_RULES: Dict[str, Dict[str, str]]
    SPOCK_LIZARD: Dict[str, Dict[str, str]]
