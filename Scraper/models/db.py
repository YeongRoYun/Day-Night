import os
import sys
rootPath = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
sys.path.append(rootPath)

import time
import sqlalchemy as db
from sqlalchemy import select
from sqlalchemy.orm import sessionmaker
from . import dbModel, userModel
from .middlewares import ModelChanger, Mode

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
                self.Session = sessionmaker(self.engine)
                
                return
            except:
                time.sleep(1)
        raise NameError('connect(): Error')

    def addAll(self, *args, mode=Mode.User):
            newInstances = []
            for arg in args:
                if mode is Mode.DB:
                    model = arg
                else:
                    model = ModelChanger.userToDb(arg)

                if not self.exist(model, Mode.DB):
                    newInstances.append(model)

            if len(newInstances) != 0:
                try:
                    with self.Session() as session:
                        session.add_all(newInstances)
                        session.commit()
                except:
                   session.rollback()
                   raise NameError('addAll(): Error')
    
    def exist(self, instance, mode=Mode.User):
        if mode is Mode.User:
            model = ModelChanger.userToDb(instance)
        else:
            model = instance

        if isinstance(model, dbModel.Cafe):
            query = select(dbModel.Cafe.id).where(dbModel.Cafe.name == model.name)
        elif isinstance(model, dbModel.Type):
            query = select(dbModel.Type.id).where(dbModel.Type.name == model.name)
        elif isinstance(model, dbModel.Site):
            query = select(dbModel.Site.id).where(dbModel.Site.name == model.name)
        elif isinstance(model, dbModel.Review):
            query = select(dbModel.Review.id).where(dbModel.Review.cafe == model.cafe and dbModel.Review.site == model.site)
        elif isinstance(model, dbModel.CafesType):
            query = select(dbModel.CafesType.id).where(dbModel.CafesType.cafeId == model.cafeId and dbModel.CafesType.siteId == model.siteId)
        else:
            return False
        
        with self.Session() as session:
            try:
                result = session.execute(query).all()

                if len(result) != 0:
                    return True
                else:
                    return False
            except:
                False
            
    def query(self, *args, mode=Mode.User):
        results = []
        with self.Session() as session:
            try:
                if mode is Mode.User:
                    for arg in args:
                        results.append(session.execute(arg).all())
                else:
                    for arg in args:
                        results.append(session.execute(arg))
            except:
                raise NameError('query(): Error')
        return results

    def getIDs(self, *args, mode=Mode.User):
        queries = []

        for arg in args:
            if mode is Mode.User:
                model = ModelChanger.userToDb(arg)
            else:
                model = arg
            queries.append(select(type(model).id).where(type(model).name == model.name))
        ids = self.query(*queries)

        try:
            strCafeAndTypeAndSiteIds = [rawId[0][0] for rawId in ids]
            return strCafeAndTypeAndSiteIds
        except:
            raise NameError('getIDs(): Error')
        