"""Tests for the players module."""

import pytest

from rps_games.players import ComputerPlayer, HumanPlayer


def test_human_player_choice(monkeypatch):
    """Test that HumanPlayer returns a valid choice when given valid input."""
    player = HumanPlayer("Alice")
    choices = ["Rock", "Paper", "Scissors"]

    monkeypatch.setattr("getpass.getpass", lambda _: "Rock")
    assert player.choice(choices) == "Rock"

    monkeypatch.setattr("getpass.getpass", lambda _: "Q")
    with pytest.raises(SystemExit):
        player.choice(choices)


def test_computer_player_choice():
    """Test that ComputerPlayer returns a valid choice from the given options."""
    player = ComputerPlayer("Bot")
    choices = ["Rock", "Paper", "Scissors"]
    assert player.choice(choices) in choices
