from twisted.internet.protocol import Factory
from twisted.protocols.basic import LineReceiver
from twisted.internet import reactor


def start_listening(port_number=11222):
    reactor.listenTCP(port_number, CacheProtocolFactory())
    reactor.run()


class CacheProtocol(LineReceiver):
    """
    Implementation of the protocol. Receives data, makes sure that expect number of bytes received
    (if specified, e.g. set command).

    Works as a state machine with 2 states.
    command state: expects to receive a command (e.g. "get key");
    data state: expect to receive raw data (e.g. after receiving set command).
    """
    supported_commands = ["get", "set", "stats"]
    commands_which_send_data = ["set", "add", "replace", "append", "prepend"]

    def __init__(self):
        self.state = "command"
        self.command_waiting_for_data = None

        self.data_bytes_remaining = 0

        self._processed_commands = list()

    def lineReceived(self, line):
        if len(line) == 0:
            return

        if self.state != "command":
            return

        command = CacheProtocol.process_command(line)

        if command is None:
            return

        if command.command in CacheProtocol.commands_which_send_data:
            self.data_bytes_remaining = command.expected_bytes
            self.command_waiting_for_data = command
            self.state = "data"
            self.setRawMode()
        else:
            self._processed_commands.append(command)

        # don't execute if data is pendig @todo
        # self.execute_command(command)

    def rawDataReceived(self, data):
        if self.data_bytes_remaining == 0:
            raise ValueError("No data expected")

        bytes_received = len(data)

        if bytes_received > self.data_bytes_remaining:
            raise ValueError("Received more data than expected")

        if self.state == "command":
            return

        if self.command_waiting_for_data is None:
            return

        if self.command_waiting_for_data.data is None:
            self.command_waiting_for_data.data = ""

        self.command_waiting_for_data.data += data
        self.data_bytes_remaining -= bytes_received

        if self.data_bytes_remaining == 0:
            self.state = "command"
            self.setLineMode()

            command = self.command_waiting_for_data
            self.command_waiting_for_data = None

            self._processed_commands.append(command)

            # self.execute_command(command)

    def execute_command(self, command):
        pass

    @staticmethod
    def process_command(command):
        tokens = command.split(" ")

        if tokens[0] not in CacheProtocol.supported_commands:
            return None

        command = tokens[0]

        if len(tokens) > 1:
            parameters = tokens[1:]
        else:
            parameters = []

        return CacheProtocolCommand(command, parameters)


class CacheProtocolCommand(object):

    def __init__(self, command, parameters, data=None):
        self.command = command
        self.parameters = parameters
        self.data = data
        self.expected_bytes = None

        if self.command in CacheProtocol.commands_which_send_data:
            if len(parameters) < 4:
                raise AttributeError("At least 4 arguments required")

            try:
                self.expected_bytes = int(parameters[3])
            except ValueError:
                raise ValueError("Number of bytes must be an integer")


class CacheProtocolFactory(Factory):

    def buildProtocol(self, addr):
        return CacheProtocol()
