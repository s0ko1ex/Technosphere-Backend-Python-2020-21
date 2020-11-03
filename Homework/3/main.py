from orm import SimpleBase, Integer, Char, Column


class Dogs(SimpleBase):
    __database__ = "pets"
    __table__ = "dogs"

    name = Column('name', Char(255), True)
    owner = Column('owner', Char(255), True)
    years = Column('years', Integer, True)


print(*(i.name for i in Dogs.all()))
print(Dogs.connector.execute("la"))
