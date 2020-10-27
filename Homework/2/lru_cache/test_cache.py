import unittest
from main import LRUCache


class LRUCacheTest(unittest.TestCase):
    def setUp(self):
        self.cache = LRUCache(10)

    def test_get_set(self):
        for i in range(10):
            self.cache.set(str(i), str(i))

        self.assertIsNone(self.cache.get('10'))
        self.assertEqual(self.cache.get('2'), '2')

    def test_lru(self):
        self.cache.set('0', 0)
        self.assertEqual(self.cache.head.key, '0')
        self.assertEqual(self.cache.tail.key, '0')

        for i in range(1, 10):
            self.cache.set(str(i), str(i))
            self.assertEqual(self.cache.head.key, str(i))
            self.assertEqual(self.cache.tail.key, '0')

        self.cache.get('0')
        self.assertEqual(self.cache.head.key, '0')
        self.assertEqual(self.cache.tail.key, '1')

    def test_delete(self):
        for i in range(10):
            self.cache.set(str(i), i)

        self.cache.delete('1')
        self.assertIsNone(self.cache.get('1'))
        self.assertRaises(KeyError, lambda: self.cache.table['1'])
        self.assertRaises(KeyError, lambda: self.cache.delete('1'))

        self.cache.delete('0')
        self.assertEqual(self.cache.tail.key, '2')

        self.cache.delete('9')
        self.assertEqual(self.cache.head.key, '8')


if __name__ == "__main__":
    unittest.main()
