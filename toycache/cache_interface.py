class CacheInterface(object):
    """
    Interface between the cache and commands received.
    """
    def __init__(self, cache):
        """
        Initiate inteface
        :param cache: Cache to bind the interface to
        """
        self._cache = cache

    def execute(self, command):
        """
        Execute command on the bound cache.
        :param command: CacheProtocolCommand instance
        :return: Result of command
        :rtype: CacheProtocolResult
        """
        method_name = "exec_{cmd}".format(cmd=command.command)

        if not(hasattr(self, method_name) and callable(getattr(self, method_name))):
            # @todo network interface should write back "ERROR\r\n"
            raise AttributeError("Command {cmd} is not implemented".format(cmd=command.command))

        result = getattr(self, method_name)(command)

        return result

    def exec_set(self, cmd):
        key, flags, ttl, size = cmd.parameters

        ttl = int(ttl)

        self._cache.set(key, cmd.data, ttl)

        return CacheProtocolResult("STORED")

    def exec_get(self, cmd):
        key = cmd.parameters[0]

        item = self._cache.get(key)

        if item is None:
            return CacheProtocolResult("END")

        result_data = "VALUE {key} {flags} {size}\r\n".format(key=key, flags=0, size=len(item))
        result_data += item # terminating \r\n will be appended automatically

        return CacheProtocolResult("END", result_data)

class CacheProtocolResult(object):
    """
    Result of command execution
    """
    def __init__(self, state, data=None):
        """
        Initialize object
        :param state: State of result, e.g. STORED, END, ERROR.
        :param data: Optional data associated with the result, e.g. value stored at key for get
                     command.
        :return:
        """
        self.state = state
        self.data = data

    def __str__(self):
        representation = ""
        if self.data is not None:
            representation = self.data + "\r\n"
        representation += self.state

        return representation


class CacheProtocolCommand(object):
    """
    Parses cache commands from input (e.g. network) and hold relevant data.
    """

    # @todo [noreply] support
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