import unittest
import unittest.mock
import logging
from random import randint
from orm import Integer, Char, DBConnector, MetaBase, SimpleBase, Column


class DBConnectorCase(unittest.TestCase):
    @unittest.mock.patch("mysql.connector.connect")
    def test_signletone(self, connect_func: unittest.mock.MagicMock):
        DBConnector._instance = None
        connector1 = DBConnector("host1", "user1", "password1")

        self.assertTrue(connect_func.called)
        connect_func.called = False

        connect_func.assert_called_with(
            host="host1",
            user="user1",
            password="password1"
        )

        connector2 = DBConnector()

        self.assertFalse(connect_func.called)
        self.assertEqual(connector1, connector2)

        DBConnector._instance = None

    @unittest.mock.patch("mysql.connector.connect")
    def test_check_db(self, connect_func):
        DBConnector._instance = None
        connector = DBConnector("host1", "user1", "password1")
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

        DBConnector._instance = None

    @unittest.mock.patch("mysql.connector.connect")
    def test_check_table(self, connect_func):
        DBConnector._instance = None
        connector = DBConnector("host1", "user1", "password1")
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
    def setUp(self):
        Dogs = MetaBase('Dogs', (SimpleBase,), {
            '__table__': 'dogs',
            '__database__': 'pets',
            'name': Column('name', Char(255)),
            'owner': Column('owner', Char(255)),
            'years': Column('years', Integer)
        })
        Dogs.__class__.check_table = unittest.mock.Mock(
            return_value=iter([1, 2, 3])
        )
        Dogs.connector = unittest.mock.Mock()

        self.dog = Dogs(id=1, name='Jack', owner='Sam', years=3)

    def test_get_attribute(self):
        self.assertNotEqual(self.dog.name,
                            self.dog.__class__.__dict__['name'])
        self.assertNotEqual(self.dog.years,
                            self.dog.__class__.__dict__['years'])
        self.assertEqual(self.dog.__table__,
                         self.dog.__class__.__dict__['__table__'])

    def test_create(self):
        self.dog.__class__.connector = unittest.mock.Mock()
        self.dog.__class__.create(id=1, name='Jack', owner='Sam', years=3)
        self.dog.connector.execute.assert_called_with(
            "INSERT INTO dogs (id, name, owner, years) " +
            "VALUES (1, 'Jack', 'Sam', 3)"
        )

    def test_update(self):
        self.dog.connector = unittest.mock.Mock()
        self.dog.update()
        self.dog.connector.execute.assert_called_with(
            "UPDATE dogs SET name='Jack', owner='Sam', years=3 " +
            "WHERE id=1"
        )

    def test_delete(self):
        self.dog.connector = unittest.mock.Mock()
        self.dog.delete()
        self.dog.connector.execute.assert_called_with(
            "DELETE FROM dogs WHERE id=1"
        )


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
    logging.disable(logging.CRITICAL)
    unittest.main()
