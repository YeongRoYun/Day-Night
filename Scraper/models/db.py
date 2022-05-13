import time
import logging
from .dbModel import *
import sqlalchemy as db
from .errors import DBError
from sqlalchemy import select
from sqlalchemy.orm import sessionmaker, scoped_session


class DB:
    def __init__(self, user='root', password='', host='localhost', port='3306', db=''):
        self.url = 'mysql+pymysql://{user}:{password}@{host}:{port}/{db}'
        self.url = self.url.format(user=user, password=password, host=host, port=port, db=db)
        self.__connect()

    def __connect(self):
        for _ in range(20):
            try:
                self.engine = db.create_engine(self.url, convert_unicode=True, pool_size=2, pool_recycle=1800, max_overflow=0) #pool_size: 세션 호출 가능 자원 수
                self.connection = self.engine.connect()
                self.__Session = scoped_session(sessionmaker(bind=self.engine, autocommit=False, autoflush=True))
                
                return
            except:
                time.sleep(1)
        raise DBError()

    def saveInfo(self, info):
        if info != None:
            with self.__Session() as session:
                try:
                    cafe = Cafe(name=info.cafeName, location=info.cafeLocation, preference=info.cafePreference, keywords=' '.join(info.cafeKeywords))
                    types = [Type(name=type) for type in info.cafeTypes]
                    site = Site(name=info.siteName)
                    
                    self.__addAll(cafe, *types, site)
                    
                    cafeId, siteId = self.__getIDs(cafe, site)
                    typeIds = self.__getIDs(*types)

                    reviews = []
                    for review in info.cafeReviews:
                        reviews.append(Review(content=review.content, cafe=cafeId, site=siteId, preference=review.preference, keywords=' '.join(review.keywords)))
                    
                    cafeAndTypes = []
                    for typeId in typeIds:
                        cafeAndTypes.append(CafesType(cafeId=cafeId, typeId=typeId))
                    
                    self.__addAll(*reviews, *cafeAndTypes)

                    session.commit()
                    logging.info('Save {}'.format(info.cafeName))

                except:
                    session.rollback()
                    raise DBError()
        else:
            return

    def __addAll(self, *models):
           with self.__Session() as session:
                try:
                    newModels = []
                    for model in models:
                        if not self.__exist(model):
                            newModels.append(model)
                    if len(newModels) != 0:
                        session.add_all(newModels)
                except:
                    session.rollback()
                    raise DBError()
    
    def __exist(self, model):
        with self.__Session() as session:
            try:
                if isinstance(model, Cafe):
                    query = select(Cafe.id).where(Cafe.name == model.name)
                elif isinstance(model, Type):
                    query = select(Type.id).where(Type.name == model.name)
                elif isinstance(model, Site):
                    query = select(Site.id).where(Site.name == model.name)
                elif isinstance(model, Review):
                    query = select(Review.id).where(Review.cafe == model.cafe and Review.site == model.site)
                elif isinstance(model, CafesType):
                    query = select(CafesType.id).where(CafesType.cafeId == model.cafeId and CafesType.siteId == model.siteId)
                else:
                    return False
                
                result = session.execute(query).all()
                if len(result) != 0:
                    logging.info('Already Exist')
                    return True
                else:
                    return False
            except:
                session.rollback()
                return False

    def __getIDs(self, *models):
        with self.__Session() as session:
            try:
                queries = []
                for model in models:
                    queries.append(select(type(model).id).where(type(model).name == model.name))
                
                ids = self.__query(*queries)
                strCafeAndTypeAndSiteIds = [rawId[0][0] for rawId in ids]
                return strCafeAndTypeAndSiteIds
            
            except:
                session.rollback()
                raise DBError()

    def __query(self, *args):
        with self.__Session() as session:
            try:
                results = []
                for arg in args:
                    results.append(session.execute(arg).all())
                return results
            except:
                session.rollback()
                raise DBError()
        