class Command(object):
    """
    Command-class stores information of the current client send command
    """
    def __init__(self, cmd=None):
        self._cmd = cmd
        self._key = ""
        self._value = ""
        self._end_idx = 0

    @staticmethod
    def valid_commands():
        return ["get", "put", "exit"]

    @staticmethod
    def is_valid_command(cmd):
        return cmd in Command.valid_commands()

    @staticmethod
    def get_le_count(command):
        """
        How many line endings each command requires
        :param command: Command (Command)
        :return: Line ending count (int)
        """
        if command.cmd() == "exit":
            return 1
        elif command.cmd() == "get":
            return 2
        elif command.cmd() == "put":
            return 3
        else:
            return 0

    def is_set(self):
        return self.cmd() != None

    def is_get(self):
        return self.cmd() == "get"

    def is_put(self):
        return self.cmd() == "put"

    def is_exit(self):
        return self.cmd() == "exit"

    def cmd(self):
        return self._cmd

    def set_cmd(self, cmd):
        self._cmd = cmd.lower()

    def key(self):
        return self._key

    def set_key(self, key):
        self._key = key.lower()

    def value(self):
        return self._value

    def set_value(self, value):
        self._value = value

    def set_end(self, idx):
        self._end_idx = idx

    def end_idx(self):
        return self._end_idx

    def clear(self):
        self._cmd = None
        self._key = ""
        self._value = ""

    def __str__(self):
        return "{} => {} - {}".format(self.cmd(), self.key(), self.value())