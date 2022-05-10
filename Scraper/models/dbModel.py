# coding: utf-8
from sqlalchemy import Column, ForeignKey, String, TIMESTAMP, Text, text
from sqlalchemy.dialects.mysql import INTEGER
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata

class Cafe(Base):
    __tablename__ = 'cafes'

    id = Column(INTEGER, primary_key=True, unique=True)
    name = Column(String(100, 'utf8mb4_unicode_ci'), nullable=False, unique=True)
    location = Column(String(200, 'utf8mb4_unicode_ci'), nullable=False)
    createdAt = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    updatedAt = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))
    deletedAt = Column(TIMESTAMP)


class Site(Base):
    __tablename__ = 'sites'

    id = Column(INTEGER, primary_key=True, unique=True)
    name = Column(String(500, 'utf8mb4_unicode_ci'), nullable=False, unique=True)
    createdAt = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    updatedAt = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))
    deletedAt = Column(TIMESTAMP)


class Type(Base):
    __tablename__ = 'types'

    id = Column(INTEGER, primary_key=True, unique=True)
    name = Column(String(30, 'utf8mb4_unicode_ci'), nullable=False, unique=True)
    createdAt = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    updatedAt = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))
    deletedAt = Column(TIMESTAMP)


class CafesType(Base):
    __tablename__ = 'cafes_types'

    id = Column(INTEGER, primary_key=True, unique=True)
    cafeId = Column(ForeignKey('cafes.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False, index=True)
    typeId = Column(ForeignKey('types.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False, index=True)

    cafe = relationship('Cafe')
    type = relationship('Type')


class Review(Base):
    __tablename__ = 'reviews'

    id = Column(INTEGER, primary_key=True, unique=True)
    content = Column(Text(collation='utf8mb4_unicode_ci'), nullable=False)
    preference = Column(INTEGER, nullable=False, server_default=text("'5'"))
    cafe = Column(ForeignKey('cafes.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False, index=True)
    site = Column(ForeignKey('sites.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False, index=True)
    createdAt = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    updatedAt = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))
    deletedAt = Column(TIMESTAMP)

    cafe1 = relationship('Cafe')
    site1 = relationship('Site')
