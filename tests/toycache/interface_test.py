import unittest

from toycache.interface import CacheProtocol


class CacheProtocolTestCase(unittest.TestCase):
    def test_process_command_invalid(self):
        command = CacheProtocol.process_command("foobar")
        self.assertIsNone(command)

    def test_process_command_valid_no_args(self):
        command = CacheProtocol.process_command("stats")

        self.assertIsNotNone(command)
        self.assertEqual(command.command, "stats")
        self.assertEqual(len(command.parameters), 0)

    def test_process_command_valid_with_args(self):
        command = CacheProtocol.process_command("get foobar")

        self.assertIsNotNone(command)
        self.assertEqual(command.command, "get")
        self.assertEqual(len(command.parameters), 1)
        self.assertEqual(command.parameters[0], "foobar")

    def test_process_command_expecting_bytes_valid(self):
        command = CacheProtocol.process_command("set a 0 60 5")

        self.assertIsNotNone(command)
        self.assertEqual(command.command, "set")
        self.assertEqual(len(command.parameters), 4)
        self.assertEqual(command.parameters[0], "a")
        self.assertEqual(command.expected_bytes, 5)

    def test_process_command_expecting_bytes_missing(self):

        self.assertRaises(AttributeError, lambda: CacheProtocol.process_command("set a"))

    def test_process_command_expecting_bytes_not_int(self):
        self.assertRaises(ValueError, lambda: CacheProtocol.process_command("set a 0 60 a"))

if __name__ == '__main__':
    unittest.main()
