import unittest

from toycache.cache import Cache
from .helper import Timer


class CacheTestCase(unittest.TestCase):
    def setUp(self):
        self._timer = Timer()
        self._cache = Cache(timer=self._timer)

    def test_get_not_existing(self):
        item = self._cache.get("foobar")

        self.assertIsNone(item)

    def test_set(self):
        item = self._cache.set("foobar", "cached", 3)

        self.assertEqual(item.key, "foobar")
        self.assertEqual(item.value, "cached")
        self.assertEqual(item.expires_at, 3)

    def test_get_expired(self):
        self._cache.set("foobar", "cache", 2)

        for _ in range(3):
            self._timer.tick()

        item = self._cache.get("foobar")
        self.assertIsNone(item)

    def test_get_valid(self):
        self._cache.set("foo", "hello", 2)
        self._timer.tick()

        item = self._cache.get("foo")

        self.assertEqual(item, "hello")

if __name__ == '__main__':
    unittest.main()
