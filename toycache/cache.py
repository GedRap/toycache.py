import time
import sys

from cachetools import LRUCache

class Cache(object):
    """
    The cache itself.

    Uses cachetools implementation via composition to reduce the complexity of the project
    and avoid reimplementing and testing common things.
    """
    def __init__(self, max_items=10000, timer=time.time):
        """
        Initialize the cache
        :param max_items: Maximum number of *items* that can be cached. Does not limit the size
                          of the itmes
        :param timer:     Callable that returns current time (int/float). Defaults to time.time
                          which returns local Unix time, however can be overriden with custom
                          function which is very useful when testing as it gives more control.
        """
        # we use LRUCache instead of TTLCache because TTLCache implementation of expiration is not
        # flexible enough and doesn't match our needs (TTLCache uses cache-wide standard TTL period
        # and we want to use different TTL periods for different items).
        self._cache = LRUCache(max_items)
        self._timer = timer

    def set(self, key, value, ttl):
        """
        Set value for cache item
        :param key: Item key
        :param value: Item value
        :param ttl: Time to live in units of the timer set (default: seconds).
        :return: Created cached item
        :rtype: CachedItem
        """

        # @todo handle "Can be up to 30 days. After 30 days, is treated as a unix timestamp of an exact date."
        if ttl == 0:
            expires_at = None
        else:
            expires_at = self._timer() + ttl
        cached_item = CachedItem(key, value, expires_at)
        self._cache[key] = cached_item

        return cached_item

    def get(self, key, return_value=True):
        """
        Get value of cached item stored under the given key.
        :param key: Key
        :return: Value of the cached item if found, None if not found or expired.
        """

        # @todo differentiate stored null value and not found
        try:
            item = self._cache[key]
        except KeyError:
            return None

        if (item is None) or ((item.expires_at is not None) and (item.expires_at <= self._timer())):
            return None

        if return_value:
            return item.value

        return item

    def incr(self, key, increment):
        """
        Increment integer value stored under given key by a given number
        :param key: Cache key
        :param increment: Increase stored value by this number
        :return: New value
        """
        item = self.get(key, return_value=False)

        if item is None:
            return None

        try:
            item_int = int(item.value)
        except ValueError:
            raise ClientError("cannot increment or decrement non-numeric value")

        self._cache[key].value = item_int + int(increment)

        return self._cache[key].value

    def decr(self, key, decremet):
        """
        Decrease integer value stored under given key by a given number
        :param key: Cache key
        :param decremet: Decrease stored vaue by this number
        :return: New value
        """
        item = self.get(key, return_value=False)

        if item is None:
            return None

        try:
            item_int = int(item.value)
        except ValueError:
            raise ClientError("cannot increment or decrement non-numeric value")

        self._cache[key].value = item_int - int(decremet)

        return self._cache[key].value

    def delete(self, key):
        """
        Delete key from the cache
        :param key: Cache key
        :return: True if deleted, False if not found
        """
        exists = self.get(key) is not None

        if not exists:
            return False

        self._cache[key] = None

        return True

    def add(self, key, value, ttl):
        """
        Add value to the cache if the key is not used
        :param key: Cache key
        :param value: Value to cache
        :param ttl: Time to live
        :return: True if value has been added
        """
        exists = self.get(key) is not None

        if exists:
            return False

        self.set(key, value, ttl)

        return True

    def replace(self, key, value, ttl):
        """
        Replace value stored under the key
        :param key: Cache key
        :param value: Value to store
        :param ttl: New TTL
        :return: True if replaced, False if not found
        """
        exists = self.get(key) is not None

        if not exists:
            return False

        self.set(key, value, ttl)

        return True

    def append(self, key, value, ttl):
        """
        Append given value to the already stored one under the given cache key
        :param key: Cache key
        :param value: Value to append
        :param ttl: New TTL
        :return: True if stored successfully, False if not found
        """
        current_data = self.get(key)

        # @todo ignore ttl

        if current_data is None:
            return False

        self.set(key, current_data + value, ttl)

        return True

    def prepend(self, key, value, ttl):
        """
        Prepend given vaue to the already stored one under the given cache key
        :param key: Cache key
        :param value: Value to prepend
        :param ttl: New TTL
        :return: True if prepended successfully, False if not found
        """
        current_data = self.get(key)

        if current_data is None:
            return False

        # @todo ignore ttl

        self.set(key, value + current_data, ttl)

        return True

    def flush_all(self):
        """
        Remove all items from the cache.
        :return: Always True
        """
        self._cache.clear()
        return True

    def keys(self):
        """
        List of keys available in Cache
        :return:
        """
        return self._cache.keys()

class ClientError(Exception):
    pass


class ServerError(Exception):
    pass

class CachedItem(object):
    """
    Object used to hold some data around cached item.
    """

    def __init__(self, key, value, expires_at):
        """
        Initiate item
        :param key: Key
        :param value: Value
        :param expires_at: Expiration time. Expressed in timer units and is absolute (i.e. not the
                           same as TTL). Usually equals to current_time + ttl.
        :return:
        """
        self.key = key
        self.value = value
        self.expires_at = expires_at