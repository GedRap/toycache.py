import unittest

from toycache.cache import Cache
from toycache.cache_interface import CacheProtocolCommand, CacheInterface


class CacheInterfaceTestCase(unittest.TestCase):
    def setUp(self):
        self._cache = Cache()
        self._cache_interface = CacheInterface(self._cache)

    def test_exec_set(self):
        cmd = CacheProtocolCommand.process_command("set foobar 0 100 4")
        cmd.data = "Hello world"

        result = self._cache_interface.execute(cmd)

        self.assertIsNone(result.data)
        self.assertEqual(result.state, "STORED")

        item = self._cache.get("foobar")
        self.assertEqual(item, cmd.data)

    def test_exec_get(self):
        self._cache.set("foo", "Foobar123", 0)

        cmd = CacheProtocolCommand.process_command("get foo")
        result = self._cache_interface.execute(cmd)

        self.assertEqual(result.state, "END")
        self.assertEqual(result.data, "VALUE foo 0 9\r\nFoobar123")


class CacheProtocolCommandTestCase(unittest.TestCase):
    def test_process_command_invalid(self):
        command = CacheProtocolCommand.process_command("foobar")
        self.assertIsNone(command)

    def test_process_command_valid_no_args(self):
        command = CacheProtocolCommand.process_command("stats")

        self.assertIsNotNone(command)
        self.assertEqual(command.command, "stats")
        self.assertEqual(len(command.parameters), 0)

    def test_process_command_valid_with_args(self):
        command = CacheProtocolCommand.process_command("get foobar")

        self.assertIsNotNone(command)
        self.assertEqual(command.command, "get")
        self.assertEqual(len(command.parameters), 1)
        self.assertEqual(command.parameters[0], "foobar")

    def test_process_command_expecting_bytes_valid(self):
        command = CacheProtocolCommand.process_command("set a 0 60 5")

        self.assertIsNotNone(command)
        self.assertEqual(command.command, "set")
        self.assertEqual(len(command.parameters), 4)
        self.assertEqual(command.parameters[0], "a")
        self.assertEqual(command.expected_bytes, 5)

    def test_process_command_expecting_bytes_missing(self):

        self.assertRaises(AttributeError, lambda: CacheProtocolCommand.process_command("set a"))

    def test_process_command_expecting_bytes_not_int(self):
        self.assertRaises(ValueError, lambda: CacheProtocolCommand.process_command("set a 0 60 a"))

if __name__ == '__main__':
    unittest.main()
