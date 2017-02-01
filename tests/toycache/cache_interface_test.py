import unittest

from toycache.cache import Cache
from toycache.cache_interface import CacheProtocolCommand, CacheInterface


class CacheInterfaceTestCase(unittest.TestCase):
    def setUp(self):
        self._cache = Cache()
        self._cache_interface = CacheInterface(self._cache)

    def test_exec_set(self):
        cmd = CacheProtocolCommand.process_command("set foobar 0 100 11")
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

    def test_exec_incr_not_exists(self):
        result = self._cache_interface.execute(CacheProtocolCommand.process_command("incr foo 2"))
        self.assertEqual(result.state, "NOT_FOUND")
        self.assertIsNone(result.data)

    def test_exec_incr_exists(self):
        self._cache.set("foo", "12", 0)

        result = self._cache_interface.execute(CacheProtocolCommand.process_command("incr foo 10"))
        self.assertEqual(result.state, 22)
        self.assertIsNone(result.data)

    def test_exec_decr_not_exists(self):
        result = self._cache_interface.execute(CacheProtocolCommand.process_command("decr foo 2"))
        self.assertEqual(result.state, "NOT_FOUND")
        self.assertIsNone(result.data)

    def test_exec_decr_exists(self):
        self._cache.set("foo", "12", 0)

        result = self._cache_interface.execute(CacheProtocolCommand.process_command("decr foo 10"))
        self.assertEqual(result.state, 2)
        self.assertIsNone(result.data)

    def test_exec_delete_exists(self):
        self._cache.set("foo", 12, 0)

        result = self._cache_interface.execute(CacheProtocolCommand.process_command("delete foo"))
        self.assertEqual(result.state, "DELETED")
        self.assertIsNone(result.data)

    def test_exec_delete_not_exists(self):
        result = self._cache_interface.execute(CacheProtocolCommand.process_command("delete foo"))
        self.assertEqual(result.state, "NOT_FOUND")
        self.assertIsNone(result.data)

    def test_exec_add_exists(self):
        self._cache.set("foo", "bar", 0)

        cmd = CacheProtocolCommand.process_command("add foo 0 100 4")
        cmd.data = "barz"

        result = self._cache_interface.execute(cmd)

        self.assertEqual(result.state, "NOT_STORED")
        self.assertIsNone(result.data)

    def test_exec_add_not_exists(self):
        cmd = CacheProtocolCommand.process_command("add foo 0 100 4")
        cmd.data = "barz"

        result = self._cache_interface.execute(cmd)

        self.assertEqual(result.state, "STORED")
        self.assertIsNone(result.data)

    def test_exec_replace_exists(self):
        self._cache.set("foo", "bar", 0)

        cmd = CacheProtocolCommand.process_command("replace foo 0 100 4")
        cmd.data = "barz"

        result = self._cache_interface.execute(cmd)

        self.assertEqual(result.state, "STORED")
        self.assertIsNone(result.data)

    def test_exec_replace_not_exists(self):
        cmd = CacheProtocolCommand.process_command("replace foo 0 100 4")
        cmd.data = "barz"

        result = self._cache_interface.execute(cmd)

        self.assertEqual(result.state, "NOT_STORED")
        self.assertIsNone(result.data)

    def test_exec_append_exists(self):
        self._cache.set("foo", "bar", 0)

        cmd = CacheProtocolCommand.process_command("append foo 0 100 4")
        cmd.data = "barz"

        result = self._cache_interface.execute(cmd)

        self.assertEqual(result.state, "STORED")
        self.assertIsNone(result.data)

    def test_exec_append_not_exists(self):
        cmd = CacheProtocolCommand.process_command("append foo 0 100 4")
        cmd.data = "barz"

        result = self._cache_interface.execute(cmd)

        self.assertEqual(result.state, "NOT_STORED")
        self.assertIsNone(result.data)

    def test_exec_prepend_exists(self):
        self._cache.set("foo", "bar", 0)

        cmd = CacheProtocolCommand.process_command("prepend foo 0 100 4")
        cmd.data = "barz"

        result = self._cache_interface.execute(cmd)

        self.assertEqual(result.state, "STORED")
        self.assertIsNone(result.data)

    def test_exec_prepend_not_exists(self):
        cmd = CacheProtocolCommand.process_command("prepend foo 0 100 4")
        cmd.data = "barz"

        result = self._cache_interface.execute(cmd)

        self.assertEqual(result.state, "NOT_STORED")
        self.assertIsNone(result.data)

    def test_exec_flush_all(self):
        cmd = CacheProtocolCommand.process_command("flush_all")

        result = self._cache_interface.execute(cmd)

        self.assertEqual(result.state, "OK")
        self.assertIsNone(result.data)

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
