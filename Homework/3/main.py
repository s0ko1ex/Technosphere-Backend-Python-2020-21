from orm import SimpleBase, Integer, Char, Column


class Dogs(SimpleBase):
    __database__ = "pets"
    __table__ = "dogs"

    name = Column('name', Char(255), True)
    owner = Column('owner', Char(255), True)
    years = Column('years', Integer, True)


a = Dogs.get(id=1)
print(a[0].years)
