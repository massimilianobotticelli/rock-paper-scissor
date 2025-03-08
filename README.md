# Rock, Paper, Scissors

The documentation for this project is available at [GitHub Pages](https://massimilianobotticelli.github.io/rock-paper-scissor/).

## Description

Rock, Paper, Scissors is a popular game. Two players choose one of the symbols (scissors, rock or paper) and show it simultaneously when called. Each symbol is superior to another symbol. If both players choose the same symbol, there is a draw. In this case, the game is repeated.

The winner receives one point for each game won. After a predetermined condition, e.g. (best out of 3; first to 10; number of games; ...) a player wins the round.

1. The application is writte in Python and supports human players, computer-controlled players, and an LLM (Language Model) player.
2. The rule variants available should be the classic Scissors, Rock, Paper variant and an extended variant with the addition of Spock and Lizard.
3. The game should be easily expandable for further rule variants.

### Classic rules

- Scissors cut paper,
- Paper wraps rock,
- Rock beats scissors,

### Rules with Spock and lizard
- Scissors cut paper,
- Paper wraps around rock,
- Rock crushes lizard,
- Lizard poisons Spock,
- Spock smashes scissors,
- Scissors decapitate lizard,
- Lizard eats paper,
- Paper disproves Spock,
- Spock vaporizes rock,
- Rock crushes scissors

## Getting Started

### Prerequisites

* **Python 3.12 or higher**
* **Poetry** (for dependency management)

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/massimilianobotticelli/rock-paper-scissor
   ```

2. **Install dependencies using Poetry:**
   ```bash
   poetry install
   ```

## Configuration

The game configuration is specified in the `configs/game_config.yaml` file. You can set the rules, game mode, target score, and player types.

### Example Configuration

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
    type: "ComputerPlayer" # Options: "HumanPlayer", "ComputerPlayer"
    name: "Computer A"
```

## Running the Game

To run the game, execute the `game.py` script:

```bash
python src/rps_games/game.py
```

## Contributing

Contributions are welcome! Feel free to open issues or submit pull requests.

## License

This project is licensed under the [MIT License](LICENSE).

## About the Author

This repository was created by **Massimiliano Botticelli**. You can find more about me and my work here:

* [**Personal Website**](https://massimilianobotticelli.me/)
* [**Linkedin**](https://www.linkedin.com/in/massimilianobotticelli/)