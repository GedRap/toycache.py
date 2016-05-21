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

if __name__ == '__main__':
    unittest.main()
