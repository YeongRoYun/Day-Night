from turtle import up, update
from venv import create


class Base:
    pass

class Cafe(Base):
    __tablename__ = 'cafes'
    def __init__(self, name, location, id=None, createdAt=None, updatedAt=None, deletedAt=None):
        self.isComplete = False
        self.name = name
        self.location = location

        if id != None:
            self.isComplete = True
            self.id = id
            self.createdAt = createdAt
            self.updatedAt = updatedAt
            self.deletedAt = deletedAt


class Site(Base):
    __tablename__ = 'sites'

    def __init__(self, name, id=None, createdAt=None, updatedAt=None, deletedAt=None):
        self.isComplete = False
        self.name = name

        if id != None:
            self.isComplete = True
            self.id = id
            self.createdAt = createdAt
            self.updatedAt = updatedAt
            self.deletedAt = deletedAt


class Type(Base):
    __tablename__ = 'types'

    def __init__(self, name, id=None, createdAt=None, updatedAt=None, deletedAt=None):
        self.isComplete = False
        self.name = name

        if id != None:
            self.isComplete = True
            self.id = id
            self.createdAt = createdAt
            self.updatedAt = updatedAt
            self.deletedAt = deletedAt


class CafesType(Base):
    __tablename__ = 'cafes_types'

    def __init__(self, cafeId, typeId, id=None):
        self.isComplete = False
        self.cafeId = cafeId
        self.typeId = typeId

        if id != None:
            self.isComplete = True
            self.id = id


class Review(Base):
    __tablename__ = 'reviews'

    def __init__(self, content, cafe, site, preference=5, id=None, createdAt=None, updatedAt=None, deletedAt=None):
        self.isComplete = False
        self.content = content
        self.cafe = cafe
        self.site = site
        self.preference = preference

        if id != None:
            self.isComplete = True
            self.id = id
            self.createdAt = createdAt
            self.updatedAt = updatedAt
            self.deletedAt = deletedAt