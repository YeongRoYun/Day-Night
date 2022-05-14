import time
import signal
import logging
from .dbModel import *
import sqlalchemy as db
from .errors import DBError
from sqlalchemy import select, and_
from sqlalchemy.orm import sessionmaker, scoped_session


class DB:
    def __init__(self, user='root', password='', host='localhost', port='3306', db=''):
        self.url = 'mysql+pymysql://{user}:{password}@{host}:{port}/{db}'
        self.url = self.url.format(user=user, password=password, host=host, port=port, db=db)
        self.__connect()

    def __connect(self):
        self.engine = db.create_engine(self.url, convert_unicode=True, pool_size=1, pool_recycle=1800, max_overflow=0) #pool_size: 세션 호출 가능 자원 수


    def saveInfo(self, info):
        if info != None:
            try:
                Session = sessionmaker(bind=self.engine, autocommit=False, autoflush=True)
                with Session() as session:
                    cafe = Cafe(name=info.cafeName, location=info.cafeLocation, preference=info.cafePreference, keywords=' '.join(info.cafeKeywords))
                    types = [Type(name=type) for type in info.cafeTypes]
                    site = Site(name=info.siteName)
                    
                    self.__addAll(session, cafe, *types, site)
                    session.commit()
                    
                    cafeId, siteId = self.__getIDs(session, cafe, site)
                    typeIds = self.__getIDs(session, *types)

                    reviews = []
                    for review in info.cafeReviews:
                        reviews.append(Review(content=review.content, cafe=cafeId, site=siteId, preference=review.preference, keywords=' '.join(review.keywords)))
                    
                    cafeAndTypes = []
                    for typeId in typeIds:
                        cafeAndTypes.append(CafesType(cafeId=cafeId, typeId=typeId))
                    
                    self.__addAll(session, *reviews, *cafeAndTypes)
                    session.commit()
                    logging.info('Save {}'.format(info.cafeName))
            except KeyboardInterrupt as e:
                raise e
        else:
            return

    def __addAll(self, session, *models):
        newModels = []
        for model in models:
            if not self.__exist(session, model):
                newModels.append(model)
        if len(newModels) != 0:
            session.add_all(newModels)
               
    
    def __exist(self, session, model):
        if isinstance(model, Cafe):
            query = select(Cafe.id).where(Cafe.name == model.name)
        elif isinstance(model, Type):
            query = select(Type.id).where(Type.name == model.name)
        elif isinstance(model, Site):
            query = select(Site.id).where(Site.name == model.name)
        elif isinstance(model, Review):
            query = select(Review.id).where(and_(Review.cafe == model.cafe, Review.site == model.site, Review.content == model.content, Review.keywords == model.keywords))
        elif isinstance(model, CafesType):
            query = select(CafesType.id).where(and_(CafesType.cafeId == model.cafeId, CafesType.typeId == model.typeId))
        else:
            return False
        
        result = session.execute(query).all()
        if len(result) != 0:
            logging.info('Already Exist')
            return True
        else:
            return False

    def __getIDs(self, session, *models):
        queries = []
        for model in models:
            queries.append(select(type(model).id).where(type(model).name == model.name))
        
        ids = self.__query(session, *queries)
        strCafeAndTypeAndSiteIds = [rawId[0][0] for rawId in ids]
        return strCafeAndTypeAndSiteIds
          

    def __query(self, session, *args):
        results = []
        for arg in args:
            results.append(session.execute(arg).all())
        return results
           