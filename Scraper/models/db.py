import os
import sys
rootPath = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
sys.path.append(rootPath)

import time
import sqlalchemy as db
from sqlalchemy import select
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
from .model import *


class DB:
    def __init__(self, user='root', password='', host='localhost', port='3306', db=''):
        self.url = 'mysql+pymysql://{user}:{password}@{host}:{port}/{db}'
        self.url = self.url.format(user=user, password=password, host=host, port=port, db=db)
        self.__connect()

    def __connect(self):
        for _ in range(20):
            try:
                self.engine = db.create_engine(self.url, encoding='utf-8')
                self.connection = self.engine.connect()
                self.__Session = sessionmaker(self.engine)
                
                return
            except:
                time.sleep(1)
        raise Exception(message='DB Connection Fails')

    def addAll(self, *args):
            newInstances = []
            for arg in args:
                if not self.exist(arg):
                    newInstances.append(arg)
            if len(newInstances) != 0:
                try:
                    with self.__Session() as session:
                        session.add_all(newInstances)
                        session.commit()
                except:
                   session.rollback()
                   raise
    
    def exist(self, instance):
        if isinstance(instance, Cafe):
            query = select(Cafe.id).where(Cafe.name == instance.name)
        elif isinstance(instance, Type):
            query = select(Type.id).where(Type.name == instance.name)
        elif isinstance(instance, Site):
            query = select(Site.id).where(Site.name == instance.name)
        elif isinstance(instance, Review):
            query = select(Review.id).where(Review.cafe == instance.cafe and Review.site == instance.site)
        elif isinstance(instance, CafesType):
            query = select(CafesType.id).where(CafesType.cafeId == instance.cafeId and CafesType.siteId == instance.siteId)
        else:
            return False
        
        with self.__Session() as session:
            try:
                result = session.execute(query).all()

                if len(result) != 0:
                    return True
                else:
                    return False
            except:
                False
            
    def query(self, *args):
        with self.__Session() as session:
            results = []
            try:
                for query in args:
                    results.append(session.execute(query))
                return results
            except:
                raise