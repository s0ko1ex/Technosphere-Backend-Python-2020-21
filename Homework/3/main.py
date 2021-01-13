from orm import SimpleBase, Integer, Char, Column


class Dog(SimpleBase):
    __database__ = "pets"
    __table__ = "dogs"

    name = Column(name='name', column_type=Char(255))
    owner = Column(name='owner', column_type=Char(255))
    years = Column(name='years', column_type=Integer)
