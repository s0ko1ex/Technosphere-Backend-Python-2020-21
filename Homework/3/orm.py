import mysql.connector
from abc import ABCMeta
from mysql.connector.cursor import MySQLCursor
from mysql.connector import ProgrammingError, DatabaseError
from typing import List, Union
import logging

logging.basicConfig(
    filename="orm.log",
    format='[%(levelname)s] %(asctime)s - %(message)s',
    level=logging.DEBUG
)

host = "localhost"
user = "root"
password = "nRZ3AfHZcmhdXrRp"


class Column:
    def __init__(self, name=None, column_type=None,
                 is_none=False, default=None):
        self.name = name
        self.column_type = column_type
        self.is_none = is_none
        self.default = default


class ORMConnector:
    _instance = None
    cursor = None

    def __init__(self, host: str = None, user: str = None,
                 password: str = None):
        if self._instance is None:
            self.mydb = mysql.connector.connect(
                host=host,
                user=user,
                password=password
            )
            logging.info("Connected to database")
            self.cur_db: str = None

            self.cursor: MySQLCursor = self.mydb.cursor()

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            obj = super(ORMConnector, cls).__new__(cls)

            try:
                obj.__init__(*args, **kwargs)
            except DatabaseError:
                logging.exception("Error in database initialization!")

            cls._instance = obj

        return cls._instance

    def execute(self, string: str) -> list:
        try:
            self.cursor.execute(string)
            logging.info(f"Made call '{string}' to MySQL")
            return list(self.cursor)
        except ProgrammingError:
            logging.exception(
                f"Call '{string}' to MySQL resulted in a failure!"
            )

    def commit(self) -> None:
        self.mydb.commit()

    def check_db(self, new_db: str) -> None:
        self.cursor.execute("SHOW DATABASES")
        databases = [i[0] for i in self.cursor]

        if new_db not in databases:
            self.cursor.execute(f"CREATE DATABASE {new_db}")
            self.cursor.execute(f"USE {new_db}")
            logging.info(f"Created new database '{new_db}'")
            self.cur_db = new_db
        elif new_db != self.cur_db:
            self.cursor.execute(f"USE {new_db}")
            logging.info(f"Switched to database '{new_db}'")
            self.cur_db = new_db

    def check_table(self, table: str, cls: type) -> int:
        self.cursor.execute("SHOW TABLES")
        tables = [i[0] for i in list(self.cursor)]

        if table in tables:
            self.cursor.execute(f"SELECT (id) from {table}")
            ids = list(self.cursor)
            if len(ids) > 0:
                return ids[-1][0] + 1
            else:
                return 1

        names = ["id"]
        types = ["INT NOT NULL AUTO_INCREMENT PRIMARY KEY"]

        for (name, value) in cls.__dict__.items():
            if isinstance(value, Column):
                names.append(value.name)
                types.append(value.column_type.sql_type)

        querry = f"CREATE TABLE {table}" +\
            f"({', '.join(i + ' ' + j for (i, j) in zip(names, types))})"
        self.cursor.execute(querry)
        logging.info(f"Created new table '{table}'")

        return 1


class ColumnType(metaclass=ABCMeta):
    pass


class MetaBase(type):
    def __init__(cls, name, bases, dct):
        cls.__columns__ = []

        for (name, value) in cls.__dict__.items():
            if isinstance(value, Column):
                cls.__columns__.append(name)

    def check_table(cls):
        if cls.connector is None:
            cls.connector = ORMConnector(host, user, password)

        new_id = None
        if cls.__database__ is not None:
            cls.connector.check_db(cls.__database__)
        if cls.__table__ is not None:
            new_id = cls.connector.check_table(cls.__table__, cls)

        return new_id


class SimpleBase(metaclass=MetaBase):
    __database__ = None
    __table__ = None
    __created__: bool = False
    connector: ORMConnector = None

    def __init__(self, *args, **kwargs):
        new_id = self.__class__.check_table()

        if "id" not in kwargs:
            self.id: int = new_id
        else:
            self.id: int = kwargs["id"]

        for name in self.__class__.__columns__:
            value = super().__getattribute__(name)

            if name not in kwargs:
                self.__setattr__(name, value.column_type(value.default))
            else:
                self.__setattr__(name, value.column_type(kwargs[name]))

    def __getattribute__(self, key):
        if key in super().__getattribute__("__columns__"):
            return super().__getattribute__(f"_{key}")
        else:
            return super().__getattribute__(key)

    def __setattr__(self, key, value):
        if key in self.__class__.__columns__:
            return super().__setattr__(f"_{key}", value)
        else:
            return super().__setattr__(key, value)

    def create(self):
        logging.info(f"Created new object with id={self.id} " +
                     "in table='{self.__table__}'")
        self.connector.check_db(self.__database__)

        columns: List[str] = ["id"]
        values: List[str] = [str(self.id)]

        for name in self.__class__.__columns__:
            value = super().__getattribute__(name)
            columns.append(value.name)
            values.append(str(self.__getattribute__(name)))

        querry = f"INSERT INTO {self.__table__} " +\
            f"({', '.join(columns)}) VALUES ({', '.join(values)})"

        self.connector.execute(querry)
        self.connector.commit()

    def update(self):
        logging.info(f"Updated object with id={self.id} " +
                     "in table='{self.__table__}'")
        self.connector.check_db(self.__database__)

        columns: List[str] = []
        values: List[str] = []

        for name in self.__class__.__columns__:
            value = super().__getattribute__(name)
            columns.append(value.name)
            values.append(str(self.__getattribute__(name)))

        querry = f"UPDATE {self.__table__} SET " +\
            f"{', '.join(i+'='+j for (i,j) in zip(columns, values))} " +\
            f"WHERE id={self.id}"

        self.connector.execute(querry)

    def delete(self):
        logging.info(f"Deleted object with id={self.id} " +
                     "from table='{self.__table__}'")
        querry = f" DELETE FROM {self.__table__} WHERE id={self.id}"
        self.connector.execute(querry)
        self.connector.commit()

    @classmethod
    def all(cls):
        cls.check_table()

        columns: List[str] = ["id"] + cls.__columns__
        res: List[str] = []

        for i in cls.connector.execute(f"SELECT * FROM {cls.__table__}"):
            base = cls(**dict(zip(columns, i)))
            res.append(base)

        return res

    @classmethod
    def get(cls, **kwargs):
        cls.check_table()

        kwargs = [[str(el) for el in row] for row in kwargs.items()]
        querry = f"SELECT * FROM {cls.__table__} WHERE " +\
            f"{' AND '.join(map(lambda a: '='.join(a), kwargs))}"
        querry_res = cls.connector.execute(querry)

        columns: List[str] = ["id"] + cls.__columns__
        res: List[cls] = []

        for i in querry_res:
            base = cls(**dict(zip(columns, i)))
            res.append(base)

        return res


class Integer(ColumnType):
    sql_type = "INT"

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Char(ColumnType):
    sql_type = "CHAR"
    str_len = 1

    def __init__(self, value):
        self.value = value[:self.str_len]

    def __new__(cls, value: Union[str, int]):
        if isinstance(value, str):
            return super(Char, cls).__new__(cls)
        elif isinstance(value, int):
            class CharMul(Char):
                sql_type = f"CHAR({value})"
                str_len = value

            return CharMul
        else:
            raise ValueError("Char argument type is only str or int")

    def __str__(self):
        return f"'{self.value}'"
