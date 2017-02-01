from twisted.trial import unittest
from twisted.test import proto_helpers

from toycache.network_interface import CacheProtocolFactory

class NetworkInterfaceTestCase(unittest.TestCase):
    """
    Test case covers handling network communication (state machine switching between line and data
    mode) and feeding received data into commands parser.
    It does not cover executing the commands on the cache since it's covered in unit tests.
    """
    def setUp(self):
        factory = CacheProtocolFactory()
        self.protocol = factory.buildProtocol(('127.0.0.1', 0))
        self.transport = proto_helpers.StringTransport()
        self.protocol.makeConnection(self.transport)

    def test_get(self):
        # simple one line command
        self.protocol.dataReceived("get foo\r\n")
        self.assertEqual(self.protocol.processed_commands[0].command, "get")
        self.assertEqual(self.protocol.processed_commands[0].parameters, ["foo"])

    def test_set(self):
        # more complex command consisting of command itself and data attached
        self.protocol.dataReceived("set foobar 0 100 11\r\n")
        self.protocol.dataReceived("Hello world\r\n")
        self.assertEqual(self.protocol.processed_commands[0].command, "set")
        self.assertEqual(self.protocol.processed_commands[0].data, "Hello world")
        self.assertEqual(self.protocol.processed_commands[0].parameters, ['foobar', '0', '100', '11'])

    def test_set_too_much_data(self):
        self.protocol.dataReceived("set foobar 0 100 11\r\n")
        self.protocol.dataReceived("Hello world 123\r\n")
        self.assertEqual(self.protocol.processed_commands, [])