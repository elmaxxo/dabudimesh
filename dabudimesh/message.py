import json


class Message:
    def __init__(self, command, source, destination, params=None):
        self.fields = {"source": source, "command": command, "destination": destination}
        if params is not None:
            self.fields["params"] = params

    def get_command(self):
        return self.fields["command"]

    def get_source(self):
        return self.fields["source"]

    def get_destination(self):
        return self.fields["destination"]

    def get_params(self):
        return self.fields["params"]

    @staticmethod
    def decode(line):
        return json.loads(line)

    def encode(self):
        return bytes(json.dumps(self.fields), "utf-8")
