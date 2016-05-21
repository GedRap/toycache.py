from twisted.internet.protocol import Factory
from twisted.protocols.basic import LineReceiver
from twisted.internet import reactor


def start_listening(port_number=11222):
    reactor.listenTCP(port_number, CacheProtocolFactory())
    reactor.run()


class CacheProtocol(LineReceiver):

    supported_commands = ["get", "set", "stats"]
    commands_which_send_data = ["set", "add", "replace", "append", "prepend"]

    def __init__(self):
        self.state = "command"
        self.command_waiting_for_data = None

    def lineReceived(self, line):
        if self.state != "command":
            return

        command = CacheProtocol.process_command(line)

        if command is None:
            return

        if command.command in CacheProtocol.commands_which_send_data:
            self.command_waiting_for_data = command
            self.state = "data"
            self.setRawMode()

        self.execute_command(command)

    def rawDataReceived(self, data):
        if self.state == "command":
            return

        if self.command_waiting_for_data is None:
            return

        self.command_waiting_for_data.data = data
        self.state = "command"
        self.setLineMode()

        command = self.command_waiting_for_data
        self.command_waiting_for_data = None

        self.execute_command(command)

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


class CacheProtocolFactory(Factory):

    def buildProtocol(self, addr):
        return CacheProtocol()
