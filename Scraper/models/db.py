import logging
from .dbModel import *
import sqlalchemy as db
from sqlalchemy import and_
from sqlalchemy.orm import sessionmaker


class DB:
    def __init__(self, user='root', password='', host='localhost', port='3306', db=''):
        self.url = 'mysql+pymysql://{user}:{password}@{host}:{port}/{db}'
        self.url = self.url.format(user=user, password=password, host=host, port=port, db=db)
        self.__connect()

    def __connect(self):
        self.engine = db.create_engine(self.url, convert_unicode=True, pool_size=1, pool_recycle=1800, max_overflow=0) #pool_size: 세션 호출 가능 자원 수

    def isAlreadyScraped(self, cafeName, siteName, typeName):
        Session = sessionmaker(bind=self.engine, autocommit=False, autoflush=False)
        with Session() as session:
            site = session.query(Site).filter(Site.name == siteName).first()
            if site == None:
                return False

            cafe = session.query(Cafe).filter(Cafe.name == cafeName).first()
            if cafe == None:
                return False

            type = session.query(Type).filter(Type.name == typeName).first()
            if type == None:
                return False

            cafeAndType = session.query(CafesType).filter(and_(CafesType.cafeId == cafe.id, CafesType.typeId == type.id))
            if cafeAndType == None:
                return False

            reviewOfCafeInSite = session.query(Review).filter(and_(Review.cafe == cafe.id, Review.site == site.id))
            if reviewOfCafeInSite == None:
                return False

            return True

            
    def saveInfo(self, info):
        if info != None:
            try:
                Session = sessionmaker(bind=self.engine, autocommit=False, autoflush=True)
                with Session() as session:
                    cafe = Cafe(name=info.cafeName, location=info.cafeLocation, preference=info.cafePreference, keywords=' '.join(info.cafeKeywords))
                    res = self.__exist(session, cafe)
                    if res == None:
                        session.add(cafe)
                    else:
                        cafe = res

                    site = Site(name=info.siteName)
                    res = self.__exist(session, site)
                    if res == None:
                        session.add(site)
                    else:
                        site = res
                    
                    types = [Type(name=type) for type in info.cafeTypes]
                    for idx in range(len(types)):
                        res = self.__exist(session, types[idx])
                        if res == None:
                            session.add(types[idx])
                        else:
                            types[idx] = res

                    session.commit()
                
                    for cafeReview in info.cafeReviews:
                        review = Review(content=cafeReview.content, cafe=cafe.id, site=site.id, preference=cafeReview.preference, keywords=' '.join(cafeReview.keywords))
                        res = self.__exist(session, review)
                        if res == None:
                            session.add(review)
                    
                    for type in types:
                        relration = CafesType(cafeId=cafe.id, typeId=type.id)
                        res = self.__exist(session, relration)
                        if res == None:
                            session.add(relration)

                    session.commit()
                    logging.info('Save {}'.format(info.cafeName))

            except KeyboardInterrupt as e:
                raise e
        else:
            return
    
    def __exist(self, session, instance):
        if isinstance(instance, Cafe):
            query = session.query(Cafe).filter(Cafe.name == instance.name)
        elif isinstance(instance, Type):
            query = session.query(Type).filter(Type.name == instance.name)
        elif isinstance(instance, Site):
            query = session.query(Site).filter(Site.name == instance.name)
        elif isinstance(instance, Review):
            query = session.query(Review).filter(and_(Review.cafe == instance.cafe, \
            Review.site == instance.site, Review.content == instance.content, Review.keywords == instance.keywords))
        elif isinstance(instance, CafesType):
            query = session.query(CafesType).filter(and_(CafesType.cafeId == instance.cafeId, CafesType.typeId == instance.typeId))
        else:
            return False
        
        res = query.first()
        if res != None:
            logging.info('{} (id: {}) already exists'.format(type(res).__tablename__, res.id))
        return res