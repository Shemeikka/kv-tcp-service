import argparse
import socket
import datetime
import select
import json
import sys

def send_msg(sock, msg):
    """
    Send messages to socket connection

    :param sock: sock (socket)
    :param msg: message (str)
    :return:
    """
    try:
        sock.sendall(msg)
    except socket.error as e:
        raise socket.error("Couldn't send message: {}".format(e))

def parse_data(json_data):
    """
    Parse server send data. Can only handle one response message in data.

    :param json_data: str
    :return: json decoded object
    """
    try:
        return json.loads(json_data)
    except ValueError:
        raise ValueError("Received value is not valid JSON")

def handle_count(data):
    """
    Handle tick-count action.

    :param data: dict
    :return:
    """
    try:
        print("Data: {}".format(data))
        # Key was not found, so create new key
        if data["status"] == "error":
            return {"cmd": "put", "msg": 'put\ntick\n{"count": 0}\n'}

        # Handle only to messages which has value and count keys
        # If those keys are not found, then ask tick-key again
        if "value" in data and "count" in data["value"]:
            current_count = int(data["value"]["count"])
            # return {"cmd": "tick", "msg": 'put\ntick\n{"count": '+str(current_count+1)+'}\n'}
            return {"cmd": "tick", "msg": current_count}
        else:
            return {"cmd": "get", "msg": "get\ntick\n"}
    except KeyError:
        raise KeyError("Server sent unknown message")


def start(address, port):
    try:
        sock = socket.create_connection((address, port))
    except socket.error:
        print("Remote host is not responding")
        sys.exit(0)

    # Buffer size for reading data from socket
    recv_buffer = 4096

    inputs = [sock]

    # Timer for ticker
    ticker_timer = datetime.datetime.now()
    # Timer for get tick
    get_ticker_timer = datetime.datetime.now()

    try:
        get_tick = 'get\ntick\n'
        current_count = None

        send_msg(sock, get_tick)

        # Main loop - Uses select to select between incoming connections
        while True:
            try:
                readable, writable, exceptional = select.select(inputs, [], [], 0.01)
            except select.error, e:
                raise Exception("Error on select: {}".format(e))
            except socket.error, e:
                raise Exception("Socket error on select: {}".format(e))

            # Handle inputs
            for sock in readable:
                # Receive data from client
                try:
                    sock_data = sock.recv(recv_buffer)
                except socket.error as e:
                    raise Exception("Closing {} after exception {}".format(sock.getpeername(), e))

                if not sock_data:
                    continue

                parsed_data = parse_data(sock_data)
                resp = handle_count(parsed_data)
                # If response has a tick-key and contained new count value, then update the current count.
                # Otherwise send message to server
                if resp["cmd"] == "tick":
                    current_count = resp["msg"]
                else:
                    send_msg(sock, resp["msg"])

            # Handle "exceptional conditions"
            for sock in exceptional:
                raise Exception("Exception for connection {}".format(sock.getpeername()))

            # Send update ticker count message every 10 seconds
            if datetime.datetime.now() >= ticker_timer + datetime.timedelta(seconds=10):
                ticker_timer = datetime.datetime.now()
                send_msg(sock, 'put\ntick\n{"count": '+str(current_count+1)+'}\n')

            # Send query ticker count message every 5 seconds
            if datetime.datetime.now() >= get_ticker_timer + datetime.timedelta(seconds=5):
                get_ticker_timer = datetime.datetime.now()
                send_msg(sock, get_tick)

    except KeyboardInterrupt:
        print("KeyboardInterrupt => Cleaning up and quitting")
        sock.close()
    except Exception as e:
        print(e)
        sock.close()
        sys.exit(1)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Key/Value TCP client.')
    parser.add_argument('-a', '--address', help='Address (e.q. localhost)', required=True)
    parser.add_argument('-p', '--port', help='Port number', type=int,  required=True)

    args = parser.parse_args()
    start(args.address, args.port)