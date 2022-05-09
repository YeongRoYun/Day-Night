import time
import logging
import requests
from models import *
from config import *
from sqlalchemy import select
from bs4 import BeautifulSoup
from urllib.error import HTTPError, URLError
from scrapers import BlueRibbonSurveyScraper

if __name__ == '__main__':
    logging.basicConfig(filename=config.logPath, encoding='utf-8', level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    scraper = BlueRibbonSurveyScraper()
    db = DB(secret.dbConfig.user, secret.dbConfig.password, secret.dbConfig.host, secret.dbConfig.port, secret.dbConfig.db)
    
    for n, _ in enumerate(iter(bool, True), start=0):
        path = '/restaurants/{}'.format(27121)
        scraper.setHeaders(path)
        if n % 1800 == 0:
            try:
                response = requests.get(scraper.rootUrl)
                
            except HTTPError as e:
                logging.error('HTTPError: 404 NOT FOUND')
                time.sleep(5)
                continue
            except URLError as e:
                logging.critical('HTTPError: Server NOT FOUND')
                time.sleep(10)
                continue
            except Exception as e:
                logging.critical('UnknownError: ', e.message)
                time.sleep(10)

            bs = BeautifulSoup(response.text, 'html.parser')
            csrf_token = bs.find('meta', {'name':'_csrf'}).attrs['content']
            cookie = response.headers['set-cookie']
            scraper.setHeaders(path, cookie, csrf_token)

        if n != 0 and n % 100 == 0:
            logging.info('processing... {}'.format(n))
            time.sleep(10)
        
        try:
            info = scraper.scrape(path)

            if info == {}:
                continue
            else:
                try:
                    cafe = Cafe(name=info['cafeName'], location=info['cafeLoc'])
                    type = Type(name=info['cafeType'])
                    site = Site(name=info['siteName'])
                    db.addAll(cafe, type, site)
                    
                    queries = []
                    queries.append(select(Cafe.id).where(Cafe.name == cafe.name))
                    queries.append(select(Type.id).where(Type.name == type.name))
                    queries.append(select(Site.id).where(Site.name == site.name))
                    cafeId, typeId, siteId = db.query(*queries)

                    cafeId = cafeId.all()[0][0]
                    typeId = typeId.all()[0][0]
                    siteId = siteId.all()[0][0]

                    reviews = []
                    for content in info['cafeReviews']:
                        reviews.append(Review(content=content, cafe=cafeId, site=siteId))
                    
                    cafeAndType = CafesType(cafeId=cafeId, typeId=typeId)
                    
                    db.addAll(reviews[0], reviews[1], cafeAndType)
                    
                    
                except Exception as e:
                    logging.critical('DBError')

        except URLError as e:
            logging.critical('HTTPError: Server NOT FOUND')
            time.sleep(10)

        except Exception as e:
            logging.critical('UnknownError')
            time.sleep(10)