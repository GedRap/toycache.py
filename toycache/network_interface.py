from twisted.internet import reactor
from twisted.internet.protocol import Factory
from twisted.protocols.basic import LineReceiver

from toycache.cache import Cache
from toycache.cache_interface import CacheProtocolCommand, CacheInterface


def start_listening(port_number=11222):
    reactor.listenTCP(port_number, CacheProtocolFactory())
    reactor.run()

# @todo support getting multiple keys in one request

class CacheProtocol(LineReceiver):
    """
    Implementation of the protocol. Receives data, makes sure that expect number of bytes received
    (if specified, e.g. set command).

    Works as a state machine with 2 states.
    command state: expects to receive a command (e.g. "get key");
    data state: expect to receive raw data (e.g. after receiving set command).

    Memcached protocol docs say "There are two kinds of data sent in the memcache protocol:
    text lines and unstructured data." thus making LineReceiver a perfect choice as a helper
    parent class.
    """

    def __init__(self, cache_interface):
        self.cache_interface = cache_interface
        self.state = "command"
        self.command_waiting_for_data = None

        self.data_bytes_remaining = 0

        self._processed_commands = list()

    def lineReceived(self, line):
        if len(line) == 0:
            return

        if self.state != "command":
            return

        command = CacheProtocolCommand.process_command(line)

        if command is None:
            return

        if command.command in CacheProtocolCommand.commands_which_send_data:
            self.data_bytes_remaining = command.expected_bytes
            self.command_waiting_for_data = command
            self.state = "data"
            self.setRawMode()
        else:
            self._processed_commands.append(command)

        if self.state != "data":
            result = self.cache_interface.execute(command)
            self.write_result(result)

    def rawDataReceived(self, data):
        if self.data_bytes_remaining == 0:
            raise ValueError("No data expected")

        bytes_received = len(data)

        if (bytes_received == (self.data_bytes_remaining + 2)) and data[-2:] == "\r\n":
            # remove terminating \r\n sequence
            data = data.rstrip()
            bytes_received -= 2

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

            result = self.cache_interface.execute(command)
            self.write_result(result)

    def write_result(self, result):
        printable_result = str(result)
        self.sendLine(printable_result)


class CacheProtocolFactory(Factory):
    def __init__(self):
        self.cache_interface = CacheInterface(Cache())

    def buildProtocol(self, addr):
        return CacheProtocol(self.cache_interface)
