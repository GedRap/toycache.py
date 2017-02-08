from toycache.cache import ClientError, ServerError

class CacheInterface(object):
    """
    Interface between the cache and commands received.
    """
    def __init__(self, cache):
        """
        Initiate inteface
        :type cache toycache.cache.Cache
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

        try:
            result = getattr(self, method_name)(command)
        except ClientError as e:
            raise e
        except ServerError as e:
            raise e

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

    def exec_incr(self, cmd):
        try:
            new_value = self._cache.incr(cmd.parameters[0], cmd.parameters[1])
        except ClientError as e:
            return CacheProtocolResult("CLIENT_ERROR {msg}".format(msg=e.message))

        if new_value is not None:
            return CacheProtocolResult(new_value)

        return CacheProtocolResult("NOT_FOUND")

    def exec_decr(self, cmd):
        try:
            new_value = self._cache.decr(cmd.parameters[0], cmd.parameters[1])
        except ClientError as e:
            return CacheProtocolResult("CLIENT_ERROR {msg}".format(msg=e.message))

        if new_value is not None:
            return CacheProtocolResult(new_value)

        return CacheProtocolResult("NOT_FOUND")

    def exec_delete(self, cmd):
        deleted = self._cache.delete(cmd.parameters[0])

        if deleted:
            return CacheProtocolResult("DELETED")

        return CacheProtocolResult("NOT_FOUND")

    def exec_add(self, cmd):
        key, flags, ttl, size = cmd.parameters
        ttl = int(ttl)
        added = self._cache.add(key, cmd.data, ttl)

        if added:
            return CacheProtocolResult("STORED")

        return CacheProtocolResult("NOT_STORED")

    def exec_replace(self, cmd):
        key, flags, ttl, size = cmd.parameters
        ttl = int(ttl)
        replaced = self._cache.replace(key, cmd.data, ttl)

        if replaced:
            return CacheProtocolResult("STORED")

        return CacheProtocolResult("NOT_STORED")

    def exec_append(self, cmd):
        key, flags, ttl, size = cmd.parameters
        ttl = int(ttl)
        appended = self._cache.append(key, cmd.data, ttl)

        if appended:
            return CacheProtocolResult("STORED")

        return CacheProtocolResult("NOT_STORED")

    def exec_prepend(self, cmd):
        key, flags, ttl, size = cmd.parameters
        ttl = int(ttl)
        prepended = self._cache.prepend(key, cmd.data, ttl)

        if prepended:
            return CacheProtocolResult("STORED")

        return CacheProtocolResult("NOT_STORED")

    def exec_flush_all(self, cmd):
        self._cache.flush_all()

        return CacheProtocolResult("OK")

    def exec_stats(self, cmd):
        stats = self._cache.stats
        stats_output = "STAT cmd_get {cmd_get}\r\nSTAT cmd_set {cmd_set}\r\n" \
                       "STAT get_hits {get_hits}\r\nSTAT get_misses {get_misses}"
        stats_output = stats_output.format(
            cmd_get=stats.get_misses + stats.get_hits,
            cmd_set=stats.sets,
            get_hits=stats.get_hits,
            get_misses=stats.get_misses
        )

        return CacheProtocolResult("", stats_output)


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
            representation = str(self.data) + "\r\n"
        representation += str(self.state)

        return representation


class CacheProtocolCommand(object):
    """
    Parses cache commands from input (e.g. network) and hold relevant data.
    """

    # @todo [noreply] support
    supported_commands = [
        "get", "set", "stats", "incr", "decr", "delete", "add",
        "replace", "append", "prepend", "flush_all"
    ]
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