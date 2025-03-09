"""Tests for the Game class."""

import pytest

from rps_games.game import Game, RuleSet, init_player
from rps_games.players import ComputerPlayer, HumanPlayer


@pytest.fixture
def basic_rules():
    """Fixture for basic rules of the game."""
    return {
        "Rock": {"Scissors": "crushes"},
        "Scissors": {"Paper": "cuts"},
        "Paper": {"Rock": "covers"},
    }


@pytest.fixture
def rule_set(basic_rules):
    """Fixture for creating a RuleSet instance."""
    return RuleSet(basic_rules)


@pytest.fixture
def player_a():
    """Fixture for creating a HumanPlayer instance."""
    return HumanPlayer(name="Alice")


@pytest.fixture
def player_b():
    """Fixture for creating a ComputerPlayer instance."""
    return ComputerPlayer(name="Bob")


@pytest.fixture
def game(player_a, player_b, rule_set):
    """Fixture for creating a Game instance."""
    return Game(player_a, player_b, rule_set)


def test_init_player_human(basic_rules):
    """Test initializing a HumanPlayer."""
    player_config = {"type": "HumanPlayer", "name": "Alice"}
    player = init_player(player_config, basic_rules)
    assert isinstance(player, HumanPlayer)
    assert player.name == "Alice"


def test_init_player_computer(basic_rules):
    """Test initializing a ComputerPlayer."""
    player_config = {"type": "ComputerPlayer", "name": "Bob"}
    player = init_player(player_config, basic_rules)
    assert isinstance(player, ComputerPlayer)
    assert player.name == "Bob"


def test_rule_set_get_choices(rule_set):
    """Test getting choices from the RuleSet."""
    choices = rule_set.get_choices()
    assert set(choices) == {"Rock", "Scissors", "Paper"}


def test_rule_set_determine_winner(rule_set):
    """Test determining the winner based on the rules."""
    assert rule_set.determine_winner("Rock", "Scissors") == ("Rock", "crushes")
    assert rule_set.determine_winner("Scissors", "Paper") == ("Scissors", "cuts")
    assert rule_set.determine_winner("Paper", "Rock") == ("Paper", "covers")
    assert rule_set.determine_winner("Rock", "Rock") is None


def test_play_best_of(game):
    """Test playing a 'best of' series."""
    game.player_a.choice = lambda choices, history: "Rock"
    game.player_b.choice = lambda choices, history: "Scissors"
    winner = game.play_best_of(rounds=3)
    assert winner == game.player_a
    assert game.player_a.score == 3
    assert game.player_b.score == 0


def test_play_first_to(game):
    """Test playing a 'first to' series."""
    game.player_a.choice = lambda choices, history: "Rock"
    game.player_b.choice = lambda choices, history: "Scissors"
    winner = game.play_first_to(score=3)
    assert winner == game.player_a
    assert game.player_a.score == 3
    assert game.player_b.score == 0


def test_play_round(game):
    """Test playing a single round."""
    game.player_a.choice = lambda choices, history: "Rock"
    game.player_b.choice = lambda choices, history: "Scissors"
    game._play_round()
    assert game.player_a.score == 1
    assert game.player_b.score == 0


def test_get_winner(game):
    """Test getting the winner of the game."""
    game.player_a.score = 3
    game.player_b.score = 1
    winner = game._get_winner()
    assert winner == game.player_a


def test_game_draw(game):
    """Test a game resulting in a draw."""
    game.player_a.choice = lambda choices, history: "Rock"
    game.player_b.choice = lambda choices, history: "Rock"
    winner = game.play_best_of(rounds=3)
    assert winner is None
    assert game.player_a.score == 0
    assert game.player_b.score == 0
