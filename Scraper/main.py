import time
import logging
import requests
from bs4 import BeautifulSoup
from urllib.error import HTTPError, URLError

from config import *
from models.db import *
from models import userModel
from models.middlewares import *
from scrapers import BlueRibbonSurveyScraper

if __name__ == '__main__':
    logging.basicConfig(filename=config.logPath, encoding='utf-8', level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    scraper = BlueRibbonSurveyScraper()
    db = DB(secret.dbConfig.user, secret.dbConfig.password, secret.dbConfig.host, secret.dbConfig.port, secret.dbConfig.db)
    
    for n, _ in enumerate(iter(bool, True), start=0):
        path = '/restaurants/{}'.format(n)
        scraper.setHeaders(path)
        if n % 3600 == 0:
            try:
                response = requests.get(scraper.rootUrl)
                
            except HTTPError as e:
                logging.error(e)
                time.sleep(5)
                continue
            except URLError as e:
                logging.critical(e)
                time.sleep(10)
                continue
            except Exception as e:
                logging.error(e)
                time.sleep(5)

            bs = BeautifulSoup(response.text, 'html.parser')
            csrf_token = bs.find('meta', {'name':'_csrf'}).attrs['content']
            cookie = response.headers['set-cookie']
            scraper.setHeaders(path, cookie, csrf_token)

        if n != 0 and n % 200 == 0:
            logging.info('processing... {}'.format(n))
            time.sleep(5)
        
        try:
            info = scraper.scrape(path)

            if info == {}:
                continue
            else:
                with db.Session() as session:
                    try:
                        cafe = userModel.Cafe(name=info['cafeName'], location=info['cafeLoc'])
                        types = [userModel.Type(name=type) for type in info['cafeTypes']]
                        site = userModel.Site(name=info['siteName'])
                        db.addAll(cafe, *types, site)
                        
                        cafeId, siteId = db.getIDs(cafe, site)
                        typeIds = db.getIDs(*types)

                        reviews = []
                        for content in info['cafeReviews']:
                            reviews.append(userModel.Review(content=content, cafe=cafeId, site=siteId))
                        
                        cafeAndTypes = []
                        for typeId in typeIds:
                            cafeAndTypes.append(userModel.CafesType(cafeId=cafeId, typeId=typeId))
                        
                        db.addAll(*reviews, *cafeAndTypes)
                        
                    except Exception as e:
                        logging.error(e)
                        logging.critical('DBError')

        except URLError as e:
            logging.error(e)
            time.sleep(10)

        except Exception as e:
            logging.error(e)
            time.sleep(5)