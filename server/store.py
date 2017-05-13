import threading
import json

lock = threading._RLock()


class Store():
    """
    Store is a key-value service
    """
    def __init__(self):
        self.state = {}
        self.filename = "store.txt"

        # Initialize an empty file even if that file already exists
        with open(self.filename, "w"):
            pass

    def response(self, status, msg=None):
        """
        Build a response. Messages will be JSON encoded in Server send_msg.

        :param status:
        :param msg:
        :return:
        """
        data = {}
        data["status"] = "success" if status else "error"

        if msg:
            data["value"] = msg

        return data

    def get(self, key):
        """
        Returns a value for a key

        :param key:
        :return:
        """
        try:
            data = self.state[key]
        except KeyError:
            return self.response(False, "No such key")

        return self.response(True, data)

    def set(self, key, value):
        """
        Set JSON decoded value for key.
        Also writes the state to disk in JSON format

        :param key:
        :param value:
        :return:
        """
        try:
            data = json.loads(value)
        except ValueError:
            return self.response(False, "Value is not a valid JSON")

        with lock:
            self.state[key] = data
            try:
                with open(self.filename, "w") as f:
                    json.dump(self.state, f)
            except (OSError, IOError) as e:
                return self.response(False, "Couldn't save state: {}".format(e))

        return self.response(True)

    def save(self):
        """
        Save state to a file

        :return:
        """
        with lock:
            with open(self.filename, "w") as f:
                json.dump(self.state, f)

    def load(self):
        """
        Load state from a file

        :return:
        """
        with lock:
            with open(self.filename, "r") as f:
                self.state = json.load(f)
