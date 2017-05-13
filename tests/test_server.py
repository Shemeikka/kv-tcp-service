import pytest

from server import Server, Command

@pytest.fixture
def server():
    return Server()

def test_parse_data_exit(server):
    data = "exit\n"
    response = server.parse_data(data)

    assert response["status"] == "success" and response["cmd"].is_exit()

def test_parse_data_exit_steps(server):
    data = "e"
    response = server.parse_data(data)
    assert response is None

    data += "x"
    response = server.parse_data(data)
    assert response is None

    data += "i"
    response = server.parse_data(data)
    assert response is None

    data += "t"
    response = server.parse_data(data)
    assert response is None

    data += "\\"
    response = server.parse_data(data)
    assert response is None

    data += "n"
    response = server.parse_data(data)
    assert response["status"] == "success" and response["cmd"].is_exit()

def test_parse_data_not_exit(server):
    data = "eexit\n"
    response = server.parse_data(data)

    assert response["status"] != "success"

def test_parse_data_not_exit_2(server):
    data = "exit"
    response = server.parse_data(data)

    assert response is None

def test_parse_data_get(server):
    data = "get\nfoo\n"
    response = server.parse_data(data)
    resp_cmd = response["cmd"]

    assert response["status"] == "success" and \
           resp_cmd.is_get() and \
           resp_cmd.key() == "foo"

def test_parse_data_get_steps(server):
    # Command
    data = "g"
    response = server.parse_data(data)
    assert response is None

    data += "e"
    response = server.parse_data(data)
    assert response is None

    data += "t"
    response = server.parse_data(data)
    assert response is None

    data += "\\"
    response = server.parse_data(data)
    assert response is None

    data += "n"
    response = server.parse_data(data)
    assert response is None

    # Key
    data += "f"
    response = server.parse_data(data)
    assert response is None

    data += "o"
    response = server.parse_data(data)
    assert response is None

    data += "o"
    response = server.parse_data(data)
    assert response is None

    data += "\\"
    response = server.parse_data(data)
    assert response is None

    data += "n"
    response = server.parse_data(data)
    resp_cmd = response["cmd"]

    assert response["status"] == "success" and \
           resp_cmd.is_get() and \
           resp_cmd.key() == "foo"

def test_parse_data_not_get(server):
    data = "gget\n"
    response = server.parse_data(data)

    assert response["status"] != "success"

def test_parse_data_put(server):
    data = "put\nfoo\nbar\n"
    response = server.parse_data(data)
    resp_cmd = response["cmd"]

    assert response["status"] == "success" and \
           resp_cmd.is_put() and \
           resp_cmd.key() == "foo" and \
           resp_cmd.value() == "bar"

def test_parse_data_put_steps(server):
    # Command
    data = "p"
    response = server.parse_data(data)
    assert response is None

    data += "u"
    response = server.parse_data(data)
    assert response is None

    data += "t"
    response = server.parse_data(data)
    assert response is None

    data += "\\"
    response = server.parse_data(data)
    assert response is None

    data += "n"
    response = server.parse_data(data)
    assert response is None

    # Key
    data += "f"
    response = server.parse_data(data)
    assert response is None

    data += "o"
    response = server.parse_data(data)
    assert response is None

    data += "o"
    response = server.parse_data(data)
    assert response is None

    data += "\\"
    response = server.parse_data(data)
    assert response is None

    data += "n"
    response = server.parse_data(data)
    assert response is None

    # Value
    data += "b"
    response = server.parse_data(data)
    assert response is None

    data += "a"
    response = server.parse_data(data)
    assert response is None

    data += "r"
    response = server.parse_data(data)
    assert response is None

    data += "\\"
    response = server.parse_data(data)
    assert response is None

    data += "n"
    response = server.parse_data(data)
    resp_cmd = response["cmd"]

    assert response["status"] == "success" and \
           resp_cmd.is_put() and \
           resp_cmd.key() == "foo" and \
           resp_cmd.value() == "bar"

def test_parse_data_not_put(server):
    data = "pput\n"
    response = server.parse_data(data)

    assert response["status"] != "success"
    