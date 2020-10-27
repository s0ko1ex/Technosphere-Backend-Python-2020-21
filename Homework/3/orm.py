import mysql.connector
from abc import ABCMeta
from mysql.connector.cursor import MySQLCursor
from typing import List, Union

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

    def __init__(self, host: str, user: str, password: str):
        self.mydb = mysql.connector.connect(
            host=host,
            user=user,
            password=password
        )
        self.cur_db: str = None

        self.cursor: MySQLCursor = self.mydb.cursor()

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(ORMConnector, cls).__new__(cls)

        return cls._instance

    def execute(self, string: str) -> list:
        self.cursor.execute(string)
        return list(self.cursor)

    def commit(self) -> None:
        self.mydb.commit()

    def change_db(self, new_db: str) -> None:
        self.cursor.execute("SHOW DATABASES")
        databases = (i[0] for i in list(self.cursor))

        if new_db not in databases:
            self.cursor.execute(f"CREATE DATABASE {new_db}")
        elif new_db != self.cur_db:
            self.cursor.execute(f"USE {new_db}")
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

        return 1


class ColumnType(metaclass=ABCMeta):
    pass


class SimpleBase:
    __database__ = None
    __table__ = None
    __created__: bool = False
    connector: ORMConnector = ORMConnector(host, user, password)

    def __init__(self, *args, **kwargs):
        new_id = self.__class__.init_table()

        if "id" not in kwargs:
            self.id: int = new_id
        else:
            self.id: int = kwargs["id"]

        for (name, value) in self.__class__.__dict__.items():
            if isinstance(value, Column):
                if name not in kwargs:
                    self.__setattr__(name, value.column_type(value.default))
                else:
                    self.__setattr__(name, value.column_type(kwargs[name]))

    @classmethod
    def init_table(cls):
        cls.connector.change_db(cls.__database__)
        new_id = cls.connector.check_table(cls.__table__, cls)

        if not cls.__created__:
            cls.__columns__ = []
            cls.created = True

            for (name, value) in cls.__dict__.items():
                if isinstance(value, Column):
                    cls.__columns__.append(name)

            cls.__created__ = True

        return new_id

    def __getattribute__(self, key):
        if (key in super().__getattribute__("__columns__")):
            return super().__getattribute__(f"_{key}")
        else:
            return super().__getattribute__(key)

    def __setattr__(self, key, value):
        if (key in self.__class__.__columns__):
            return super().__setattr__(f"_{key}", value)
        else:
            return super().__setattr__(key, value)

    def create(self):
        self.connector.change_db(self.__database__)

        columns: List[str] = ["id"]
        values: List[str] = [str(self.id)]

        for (name, value) in self.__class__.__dict__.items():
            if isinstance(value, Column):
                columns.append(value.name)
                values.append(str(self.__getattr__(name)))

        querry = f"INSERT INTO {self.__table__} " +\
            f"({', '.join(columns)}) VALUES ({', '.join(values)})"

        self.connector.execute(querry)
        self.connector.commit()

    def update(self):
        self.connector.change_db(self.__database__)

        columns: List[str] = []
        values: List[str] = []

        for (name, value) in self.__class__.__dict__.items():
            if isinstance(value, Column):
                columns.append(value.name)
                values.append(str(self.__getattr__(name)))

        self.connector.change_db(self.__database__)

        querry = f"UPDATE {self.__table__} SET " +\
            f"{', '.join(i+'='+j for (i,j) in zip(columns, values))} " +\
            f"WHERE id={self.id}"

        self.connector.execute(querry)

    def delete(self):
        self.connector.change_db(self.__database__)

        querry = f" DELETE FROM {self.__table__} WHERE id={self.id}"
        self.connector.execute(querry)
        self.connector.commit()

    @classmethod
    def all(cls):
        cls.init_table()

        columns: List[str] = ["id"] + cls.__columns__
        res: List[str] = []

        for i in cls.connector.execute(f"SELECT * FROM {cls.__table__}"):
            base = cls.__new__(cls.__class__)
            base.__init__(**dict(zip(columns, i)))
            res.append(base)

        return res

    @classmethod
    def get(cls, **kwargs):
        cls.init_table()

        kwargs = [[str(el) for el in row] for row in kwargs.items()]
        querry = f"SELECT * FROM {cls.__table__} WHERE " +\
            f"{' AND '.join(map(lambda a: '='.join(a), kwargs))}"
        querry_res = cls.connector.execute(querry)

        columns: List[str] = ["id"] + cls.__columns__
        res: List[cls] = []

        for i in querry_res:
            base = cls.__new__(cls)
            base.__init__(**dict(zip(columns, i)))
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
