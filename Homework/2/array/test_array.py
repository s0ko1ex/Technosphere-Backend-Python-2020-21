from array import MyArray
import unittest


class MyArrayTest(unittest.TestCase):
    def setUp(self):
        pass

    def test_comparison(self):
        self.assertTrue(MyArray([1, 2, 3]) == MyArray([3, 2, 1]))
        self.assertTrue(MyArray([5, 6, 7]) >= MyArray([5, 4, 3]))
        self.assertFalse(MyArray([5, 6, 7]) <= MyArray([4, 3, 2]))
        self.assertTrue(MyArray([5, 6, 7]) > MyArray([5, 4, 3]))
        self.assertFalse(MyArray([5, 6, 7]) < MyArray([4, 3, 2]))

    def test_add(self):
        a, b = MyArray([1, 2, 3]), MyArray([2, 1])
        self.assertEqual(list(a + b), [3, 3, 3])
        self.assertEqual(list(a), [1, 2, 3])
        self.assertEqual(list(b), [2, 1])

        a, b = MyArray([3, 2, 1]), [0, 1, 2]
        self.assertEqual(list(a + b), [3, 3, 3])

    def test_sub(self):
        a, b = MyArray([3, 2, 1]), MyArray([2, 1])
        self.assertEqual(list(a - b), [1, 1, 1])
        self.assertEqual(list(a), [3, 2, 1])
        self.assertEqual(list(b), [2, 1])

        a, b = MyArray([5, 6, 7]), [1, 2]
        self.assertEqual(list(a - b), [4, 4, 7])


if __name__ == "__main__":
    unittest.main()
