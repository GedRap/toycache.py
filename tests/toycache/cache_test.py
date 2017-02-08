import unittest

from toycache.cache import Cache, ClientError
from .helper import Timer


class CacheTestCase(unittest.TestCase):
    def setUp(self):
        self._timer = Timer()
        self._cache = Cache(timer=self._timer)

    def test_get_not_existing(self):
        item = self._cache.get("foobar")

        self.assertIsNone(item)
        self.assertEqual(self._cache.stats.get_misses, 1)
        self.assertEqual(self._cache.stats.get_hits, 0)
        self.assertEqual(self._cache.stats.sets, 0)

    def test_set(self):
        item = self._cache.set("foobar", "cached", 3)

        self.assertEqual(item.key, "foobar")
        self.assertEqual(item.value, "cached")
        self.assertEqual(item.expires_at, 3)

        self.assertEqual(self._cache.stats.get_misses, 0)
        self.assertEqual(self._cache.stats.get_hits, 0)
        self.assertEqual(self._cache.stats.sets, 1)

    def test_get_expired(self):
        self._cache.set("foobar", "cache", 2)

        for _ in range(3):
            self._timer.tick()

        item = self._cache.get("foobar")
        self.assertIsNone(item)

    def test_get_valid(self):
        self._cache.set_cached_item("foo", "hello", 2)
        self._timer.tick()

        item = self._cache.get("foo")

        self.assertEqual(item, "hello")

        self.assertEqual(self._cache.stats.get_misses, 0)
        self.assertEqual(self._cache.stats.get_hits, 1)
        self.assertEqual(self._cache.stats.sets, 0)

    def test_incr_not_exists(self):
        self.assertIsNone(self._cache.incr("foobar", 1))

    def test_incr_not_number(self):
        self._cache.set("foo", "bar", 0)

        self.assertRaises(ClientError, lambda: self._cache.incr("foo", 10))

    def test_incr_valid(self):
        self._cache.set_cached_item("foo", 10, 0)

        self.assertEqual(self._cache.incr("foo", 4), 14)

        self.assertEqual(self._cache.stats.get_misses, 0)
        self.assertEqual(self._cache.stats.get_hits, 0)
        self.assertEqual(self._cache.stats.sets, 0)

    def test_decr_not_exists(self):
        self.assertIsNone(self._cache.decr("foobar", 1))

    def test_decr_not_number(self):
        self._cache.set("foo", "bar", 0)

        self.assertRaises(ClientError, lambda: self._cache.decr("foo", 10))

    def test_decr_valid(self):
        self._cache.set("foo", 10, 0)

        self.assertEqual(self._cache.decr("foo", 4), 6)

    def test_delete_not_exists(self):
        self.assertFalse(self._cache.delete("foobar"))

    def test_delete_exists(self):
        self._cache.set("foo", "bar", 0)

        self.assertTrue(self._cache.delete("foo"))

    def test_add_not_exists(self):
        self.assertTrue(self._cache.add("foo", "bar", 10))

    def test_add_exists(self):
        self._cache.set("foo", "bar", 10)

        self.assertFalse(self._cache.add("foo", "barz", 10))

    def test_replace_not_exists(self):
        self.assertFalse(self._cache.replace("foo123", "bar", 0))

    def test_replace_exists(self):
        self._cache.set("foo", "111", 0)

        self.assertTrue(self._cache.replace("foo", "bar", 0))
        self.assertEqual(self._cache.get("foo"), "bar")

    def test_append_not_exists(self):
        self.assertFalse(self._cache.append("foo", "bar", 0))

    def test_append_exists(self):
        self._cache.set("foo", "bar", 0)

        self.assertTrue(self._cache.append("foo", "123", 0))

        self.assertEqual(self._cache.get("foo"), "bar123")

    def test_prepend_not_exists(self):
        self.assertFalse(self._cache.prepend("foo", "bar", 0))

    def test_prepend_exists(self):
        self._cache.set("foo", "bar", 0)

        self.assertTrue(self._cache.prepend("foo", "123", 0))

        self.assertEqual(self._cache.get("foo"), "123bar")

    def test_flush_all(self):
        self._cache.set("foo", "bar", 0)

        self.assertEqual(len(self._cache.keys()), 1)

        self.assertTrue(self._cache.flush_all())

        self.assertEqual(len(self._cache.keys()), 0)
        self.assertIsNone(self._cache.get("foo"))

if __name__ == '__main__':
    unittest.main()
