import pytest

from server import Server

@pytest.fixture
def server():
    return Server()

def test_parse_data(server):
    data = "get"
    response = server.parse_data(data)

    assert response["status"] == "success"
    