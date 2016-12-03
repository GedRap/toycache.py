class CacheProtocolCommand(object):
    supported_commands = ["get", "set", "stats"]
    commands_which_send_data = ["set", "add", "replace", "append", "prepend"]

    def __init__(self, command, parameters, data=None):
        self.command = command
        self.parameters = parameters
        self.data = data
        self.expected_bytes = None

        if self.command in self.commands_which_send_data:
            if len(parameters) < 4:
                raise AttributeError("At least 4 arguments required")

            try:
                self.expected_bytes = int(parameters[3])
            except ValueError:
                raise ValueError("Number of bytes must be an integer")

    @staticmethod
    def process_command(command):
        tokens = command.split(" ")

        if tokens[0] not in CacheProtocolCommand.supported_commands:
            return None

        command = tokens[0]

        if len(tokens) > 1:
            parameters = tokens[1:]
        else:
            parameters = []

        return CacheProtocolCommand(command, parameters)