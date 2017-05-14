import pytest
import time
import socket
import json
import threading

from server import Server, Command

@pytest.fixture
def server():
    return Server()

def send_msg(sock, msg, value=None):
    msg = msg.encode("utf-8")
    if value:
        msg += json.dumps(value).encode("utf-8") + "\n".encode("utf-8")
    sock.sendall(msg)

def read_response(sock):
    return json.loads(sock.recv(4096).decode())

def test_send(server):
    address = "localhost"
    port = 5000

    server_thread = threading.Thread(target=server.start, args=(address, port))
    server_thread.daemon = True
    server_thread.start()

    sock = socket.create_connection((address, port))

    msg = 'get\nfoo\n'
    send_msg(sock, msg)
    response = read_response(sock)
    assert response["status"] == "error" and response["value"] == "No such key"

    msg = 'put\nfoo\n'
    value = {
        "hello": "test"
    }
    send_msg(sock, msg, value)

    response = read_response(sock)
    assert response["status"] == "success" and "value" not in response

    msg = 'get\nfoo\n'
    send_msg(sock, msg)

    response = read_response(sock)
    assert response["status"] == "success" and response["value"] == {"hello": "test"}


