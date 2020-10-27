import unittest
import unittest.mock
from random import randint
from orm import Integer, Char


class ORMConnectorCase(unittest.TestCase):
    pass


class SimpleBaseCase(unittest.TestCase):
    @unittest.mock.patch("mysql.connector.connect")
    @unittest.mock.patch("mysql.connector.MySQLConnection.cursor")
    def test_signletone(self, cursor_func, connect_func):
        pass


class IntegerCase(unittest.TestCase):
    def setUp(self):
        self.value = randint(1, 10)
        self.integer = Integer(self.value)

    def test_value(self):
        self.assertEqual(self.integer.value, self.value)

    def test_str(self):
        self.assertEqual(str(self.integer), str(self.value))


class CharCase(unittest.TestCase):
    def setUp(self):
        self.value = randint(1, 10)
        self.char_mul = Char(self.value)

    def test_new_char_class(self):
        self.assertEqual(self.char_mul.str_len, self.value)
        self.assertEqual(self.char_mul.sql_type, f"CHAR({self.value})")

    def test_value(self):
        string = "qwertyuiopasdfghjkl"
        char = self.char_mul(string)
        self.assertEqual(str(char), string[:self.value])
        self.assertRaises(ValueError, lambda: self.char_mul(True))
