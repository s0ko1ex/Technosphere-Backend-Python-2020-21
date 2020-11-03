import unittest
import unittest.mock
from random import randint
from orm import Integer, Char, ORMConnector, MetaBase, SimpleBase, Column


class ORMConnectorCase(unittest.TestCase):
    @unittest.mock.patch("mysql.connector.connect")
    def test_signletone(self, connect_func: unittest.mock.MagicMock):
        ORMConnector._instance = None
        connector1 = ORMConnector("host1", "user1", "password1")

        self.assertTrue(connect_func.called)
        connect_func.called = False

        connect_func.assert_called_with(
            host="host1",
            user="user1",
            password="password1"
        )

        connector2 = ORMConnector()

        self.assertFalse(connect_func.called)
        self.assertEqual(connector1, connector2)

        ORMConnector._instance = None

    @unittest.mock.patch("mysql.connector.connect")
    def test_check_db(self, connect_func):
        ORMConnector._instance = None
        connector = ORMConnector("host1", "user1", "password1")
        connector.cursor = unittest.mock.MagicMock()

        connector.cursor.__iter__ = unittest.mock.Mock(
            return_value=iter([('dogs',), ('cats',)])
        )
        connector.cursor.execute.return_value = None
        connector.check_db('mice')
        connector.cursor.execute.assert_any_call("CREATE DATABASE mice")
        connector.cursor.execute.assert_any_call("USE mice")
        self.assertEqual(connector.cur_db, 'mice')

        connector.check_db('dogs')
        connector.cursor.execute.assert_called_with("USE dogs")

        ORMConnector._instance = None

    @unittest.mock.patch("mysql.connector.connect")
    def test_check_table(self, connect_func):
        ORMConnector._instance = None
        connector = ORMConnector("host1", "user1", "password1")
        connector.cursor = unittest.mock.MagicMock()
        connector.cursor.__iter__ = unittest.mock.Mock(
            side_effect=[iter([('dogs',), ('cats',)]),
                         iter([(1,), (2,), (3,)])]
        )

        self.assertEqual(connector.check_table('dogs', None), 4)

        Dogs = MetaBase('Dogs', (SimpleBase,), {
            'name': Column('name', Char(255)),
            'owner': Column('owner', Char(255)),
            'years': Column('years', Integer)
        })

        connector.cursor.__iter__ = unittest.mock.Mock(
            return_value=iter([('mice',), ('cats',)])
        )
        connector.check_table('dogs', Dogs)
        connector.cursor.execute.assert_called_with(
            "CREATE TABLE dogs" +
            "(id INT NOT NULL AUTO_INCREMENT PRIMARY KEY, " +
            "name CHAR(255), " +
            "owner CHAR(255), " +
            "years INT)"
        )


class MetaBaseCase(unittest.TestCase):
    def setUp(self):
        self.Dogs = MetaBase('Dogs', (SimpleBase,), {
            '__table__': 'dogs',
            '__database__': 'pets',
            'name': Column('name', Char(255)),
            'owner': Column('owner', Char(255)),
            'years': Column('years', Integer)
        })

    def test_columns(self):
        self.assertIn('__columns__', self.Dogs.__dict__)
        self.assertIn('name', self.Dogs.__columns__)
        self.assertIn('owner', self.Dogs.__columns__)
        self.assertIn('years', self.Dogs.__columns__)

    def test_check_table(self):
        self.Dogs.connector = unittest.mock.Mock()
        self.Dogs.connector.check_db = unittest.mock.Mock()
        self.Dogs.connector.check_table = unittest.mock.Mock()

        self.Dogs.check_table()
        self.Dogs.connector.check_db.assert_called_with('pets')
        self.Dogs.connector.check_table.assert_called_with('dogs', self.Dogs)


class SimpleBaseCase(unittest.TestCase):
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
        self.assertEqual(str(char), f"'{string[:self.value]}'")
        self.assertRaises(ValueError, lambda: self.char_mul(1.1))


if __name__ == "__main__":
    unittest.main()
