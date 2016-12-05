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

    def get(self, key):
        """
        Get value of cached item stored under the given key.
        :param key: Key
        :return: Value of the cached item if found, None if not found or expired.
        """
        try:
            item = self._cache[key]
        except KeyError:
            return None

        if (item.expires_at is not None) and (item.expires_at <= self._timer()):
            return None

        return item.value

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