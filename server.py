import select
import socket
import datetime
import argparse
import store
import json

from command import Command

# Global key-value store
STORE = store.Store()


class Server(object):
    """
    TCP server for handling client connections
    """
    def __init__(self):
        # Line ending which is appended to the message when response to client
        self.le = "\n"
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setblocking(0)
        # Sockets from which we expect to read
        self.inputs = [self.server]

    def send_msg(self, connection, msg):
        """
        Send JSON encoded message to client connection

        :param connection: Client socket
        :param msg: Data to send
        :return:
        """

        try:
            data = json.dumps(msg)
        except ValueError:
            data = json.dumps("Couldn't encode response in Server")

        try:
            # Always add line ending to the message
            connection.send(data+self.le)
        except socket.error:
            # Maybe a broken socket connection,
            connection.close()

    def response(self, status, cmd=None, value=None):
        """
        Create response dict, which will be used as a response to client

        :param status: Success or not (boolean)
        :param cmd: Command (Command)
        :param value: Message (str)
        :return:
        """
        data = {}
        data["status"] = "success" if status else "error"

        if cmd:
            data["cmd"] = cmd

        if value:
            data["value"] = value

        return data

    def parse_data(self, data):
        """
        Parse data and try to find commands.

        :param data: Data to parse (str)
        :return:
        """

        # Replace line endings with "\n".
        data_list = data.replace("\r\n", "\n").replace("\r", "\n").replace("\\n", "\n").split("\n")

        # No line endings detected yet
        if len(data_list) == 1:
            return None

        # Command is always the first value
        cmd_value = data_list[0]
        value_count = len(data_list)

        if not Command.is_valid_command(cmd_value):
            return self.response(False, value="Invalid command {}".format(cmd_value))

        command = Command(cmd_value)

        # How many arguments command requires <=> How many line line endings should data have until we have enough data
        if value_count <= Command.get_le_count(command):
            return None

        try:
            if command.is_exit():
                command.set_end(0) # Index position in data_list
            elif command.is_get():
                command.set_key(data_list[1])
                command.set_end(1)
            elif command.is_put():
                command.set_key(data_list[1])
                command.set_value(data_list[2])
                command.set_end(2)
        except IndexError:
            return self.response(False, cmd=command, value="Couldn't parse data")

        return self.response(True, cmd=command)

    def start(self, address, port):
        """
        Start the server and enter into forever loop while using select to select between incoming connections

        :param address: Server address
        :param port: Server port
        :return:
        """
        server_address = (address, port)
        self.server.bind(server_address)

        print("[{}] Starting server on {}:{}".format(datetime.datetime.now(), address, port))
        self.server.listen(5)

        # Holds client data
        client_data = {}

        # Buffer size for reading data from socket
        recv_buffer = 4096

        def clean_all():
            """
            Close all input sockets
            :return:
            """
            for s in self.inputs:
                s.close()

        def clean_up(s):
            """
            Handle cleanup on socket errors or when client disconnects
            :param s: socket
            :return:
            """
            # Stop listening for input on the connection
            self.inputs.remove(s)
            # Remove client connection data from dict
            if s in client_data:
                del client_data[s]
            s.close()

        # Main loop - Uses select to select between incoming connections
        while True:
            try:
                readable, writable, exceptional = select.select(self.inputs, [], [], 0.01)
            except select.error, e:
                print("Error on select: {}".format(e))
                break
            except socket.error, e:
                print("Socket error on select: {}".format(e))
                break
            except KeyboardInterrupt:
                print("KeyboardInterrupt => Cleaning up and quitting")
                clean_all()
                break

            # Handle inputs
            for sock in readable:
                if sock is self.server:
                    # A "readable" self.server socket is ready to accept a connection
                    connection, client_address = sock.accept()
                    connection.setblocking(0)
                    self.inputs.append(connection)
                    client_data[connection] = []
                else:
                    # Receive data from client
                    try:
                        sock_data = sock.recv(recv_buffer)
                    except socket.error as e:
                        print("Closing {} after exception {}".format(sock.getpeername(), e))
                        clean_up(sock)
                        continue
                    except KeyboardInterrupt:
                        print("KeyboardInterrupt => Cleaning up and quitting")
                        clean_all()
                        break

                    if not sock_data:
                        # Interpret empty result as closed connection
                        print("Closing {} after reading no data".format(sock.getpeername()))
                        clean_up(sock)
                    else:
                        # Data can be either a single character (e.q. data from telnet) or multiple characters but we
                        # want to work with just one element so create a one big word and keep it at index 0
                        if not client_data[sock]:
                            client_data[sock].append(sock_data)
                        else:
                            client_data[sock] = [client_data[sock][0] + sock_data]

                        data = "".join(client_data[sock])
                        resp = self.parse_data(data)

                        # Not enough data to process command so continue
                        if resp is None:
                            continue

                        if resp["status"] == "error":
                            print("Error: {}".format(resp["value"]))
                            client_data[sock] = []
                            self.send_msg(sock, resp)
                            continue

                        command = resp["cmd"]

                        print("[{}] [{}] {}".format(datetime.datetime.now(), sock.getpeername(), command))
                        if command.is_exit():
                            print("Closing {} since exit command".format(sock.getpeername()))
                            clean_up(sock)
                        elif command.is_get():
                            store_data = STORE.get(command.key())
                            self.send_msg(sock, store_data)
                            # Client data has been parsed up to command.get_end() so remove the parsed data so that it will
                            # not be parsed again
                            client_data[sock] = client_data[sock][command.end_idx():]
                        elif command.is_put():
                            store_data = STORE.set(command.key(), command.value())
                            self.send_msg(sock, store_data)
                            # Client data has been parsed up to command.get_end() so remove the parsed data so that it will
                            # not be parsed again
                            client_data[sock] = client_data[sock][command.end_idx():]

            # Handle "exceptional conditions"
            for sock in exceptional:
                print("Exception for connection {}".format(sock.getpeername()))
                clean_up(sock)



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Key/Value TCP service.')
    parser.add_argument('-a', '--address', help='Address (e.q. localhost)', required=True)
    parser.add_argument('-p', '--port', help='Port number', type=int, required=True)

    args = parser.parse_args()

    server = Server()
    server.start(args.address, args.port)