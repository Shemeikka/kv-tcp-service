import pytest

from server import Command

@pytest.fixture
def command():
    return Command()

def test_valid_commands():
    for cmd in ["exit", "get", "put"]:
        assert Command.is_valid_command(cmd) is True

def test_is_set(command):
    assert command.is_set() is False

def test_is_exit(command):
    command.set_cmd("exit")

    assert command.is_exit() is True

def test_is_get(command):
    command.set_cmd("get")

    assert command.is_get() is True

def test_is_put(command):
    command.set_cmd("put")

    assert command.is_put() is True
    