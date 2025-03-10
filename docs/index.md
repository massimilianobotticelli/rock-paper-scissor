# Rock, Paper, Scissors Game Documentation

## Overview

This project implements a Rock, Paper, Scissors game with extended rules. The game can be played between two human players, two computer players, or one human and one computer player. Additionally, it supports a player powered by a large language model (LLM).

## Game Rules

### Basic Rules

- Rock crushes Scissors
- Scissors cuts Paper
- Paper covers Rock

### Spock-Lizard Rules

- Lizard poisons Spock and eats Paper
- Spock smashes Scissors and vaporizes Rock
- Rock crushes Scissors and Lizard
- Scissors cuts Paper and decapitates Lizard
- Paper covers Rock and disproves Spock

## How to Start

### Prerequisites

- Python 3.12
- Poetry

### Setup

1. Clone the repository to your local machine.
2. Navigate to the project directory.
3. Set up the environment variables by creating a `.env` file in the project directory.
4. Install the required Python packages:
   ```sh
   pip install poetry
   poetry install
   ```

### Configuration

The game configuration and rules are defined in YAML files located in the `configs` directory.

#### Game Configuration

The game configuration is located in `configs/game_config.yaml`. This file contains the configuration for the game, including the ruleset, game mode, target score, and player details.

```yaml
game:
  rules: "SPOCK_LIZARD"    # Options: "BASIC_RULES", "SPOCK_LIZARD"
  mode: "best_of"          # Options: "first_to", "best_of"
  target_score: 10         # Used if mode is "first_to"
  rounds: 10               # Used if mode is "best_of"

players:
  player_one:
    type: "LLMPlayer"      # Options: "HumanPlayer", "ComputerPlayer", "LLMPlayer"
    name: "Gemini"
  player_two:
    type: "ComputerPlayer" # Options: "HumanPlayer", "ComputerPlayer", "LLMPlayer"
    name: "Computer A"
```

#### Rules Configuration

The tules configuration is located in `configs/rules.yaml`. This file contains the rules for the game. You can define multiple rulesets and choose one in the game configuration.

```yaml
BASIC_RULES:
  Rock:
    Scissors: "crushes"
  Paper:
    Rock: "covers"
  Scissors:
    Paper: "cuts"

SPOCK_LIZARD:
  Rock:
    Scissors: "crushes"
    Lizard: "crushes"
  Paper:
    Rock: "covers"
    Spock: "disproves"
  Scissors:
    Paper: "cuts"
    Lizard: "decapitates"
  Lizard:
    Spock: "poisons"
    Paper: "eats"
  Spock:
    Scissors: "smashes"
    Rock: "vaporizes"
```

### Running the Game

To start the game, run the `game.py` script:

```sh
python src/rps_games/game.py
```

The game will use the configuration specified in the `game_config.yaml` file and the rules defined in the `rules.yaml` file.

