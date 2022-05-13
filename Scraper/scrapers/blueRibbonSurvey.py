import re
import time
import logging
import requests
from bs4 import BeautifulSoup
from urllib.error import HTTPError, URLError

from config import secret
from .common import *
from .errors import ScraperError
from models.db import DB
from models.information import *


class BlueRibbonSurveyScraper:
    __siteName__ = '블루리본서베이'

    def __init__(self):
        self.baseUrl = 'https://www.bluer.co.kr'
        self.__headers = {
        'authority': 'www.bluer.co.kr',
        'method': 'GET',
        'scheme': 'https',
        'accept': 'text/html, */*; q=0.01',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
        'referer': 'https://www.bluer.co.kr/',
        'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="101", "Google Chrome";v="101"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest',
    }
        self.db = DB(secret.dbConfig.user, secret.dbConfig.password, secret.dbConfig.host, secret.dbConfig.port, secret.dbConfig.db)

    def scrape(self, args):
        try:
            if args[0] == 'start':
                start = int(args[1])
                end = int(args[2])
            elif args[0] == 'continue':
                savePoint = readSavePoint(ScraperType.BlueRibbonSurvey)
                if savePoint != None:
                    start = int(savePoint['current'])
                    end = int(savePoint['end'])
                    logging.info('load savePoint {}'.format('BlueRibbonSurvey'))
                else:
                    logging.warning('load fails')
                    return False
            else:
                raise IndexError
        except IndexError as e:
            raise e

        current = start
        try:
            while current <= end:
                current += 1
                path = '/restaurants/{}'.format(current)
                self.__setHeaders(path)
                if current % 3600 == 0:
                    try:
                        response = requests.get(self.baseUrl)
                        bs = BeautifulSoup(response.text, 'html.parser')
                        csrf_token = bs.find('meta', {'name':'_csrf'}).attrs['content']
                        cookie = response.headers['set-cookie']
                        self.__setHeaders(path, cookie, csrf_token)
                    except Exception as e:
                        writeSavePoint(ScraperType.BlueRibbonSurvey, start, current, end)
                        raise e

                if current % 200 == 0:
                    time.sleep(5)
            
                try:
                    info = self.__scrape(path)
                    if info == None:
                        continue
                    else:
                        self.db.saveInfo(info)

                except ScraperError as e:
                    writeSavePoint(ScraperType.BlueRibbonSurvey, start, current, end)
                    raise e
                
                except URLError as e:
                    writeSavePoint(ScraperType.BlueRibbonSurvey, start, current, end)
                    raise e
            
            self.db.engine.dispose()
            logging.info('Done Scraping!!!')
            return
        
        except KeyboardInterrupt:
            writeSavePoint(ScraperType.BlueRibbonSurvey, start, current, end)
            self.db.engine.dispose()
            logging.info('Scraper Interrupted')
            exit(1)
        
        except Exception as e:
            writeSavePoint(ScraperType.BlueRibbonSurvey, start, current, end)
            raise e
        

    def __scrape(self, relativeUrl):
        targetUrl = self.baseUrl + relativeUrl
        try:
            res = requests.get(targetUrl, headers=self.__headers)
        except HTTPError:
            logging.error('HTTPError: 404 NOT FOUND')
            return None
        except URLError as e:
            raise e

        html = res.text
        bs = BeautifulSoup(html, 'html.parser')

        if bs.find('div', {'class':'text-lg mb-lg'}) is not None: #Invalid Address
            return None
        else:
            shopType = bs.find('ol', {'class':'foodtype'}).get_text()
            cafeTypes = CafeType.getTypes(shopType)
            
            if len(cafeTypes) == 0:
                return None
            else:
                info = bs.find('div', {'class': 'restaurant-info'})
                cafeName = bs.find('div', {'class':'header-title'}).h1.get_text()
                cafeLocation = info.find('button', {'class': 'copy-address'}).parent.get_text()

                rawCafeReviews = info.find('div', {'class': re.compile('info-4')}).findAll('dd')
                cafeReviews = list(map(lambda review: Review(content=review.get_text().strip()), rawCafeReviews))
                
                return Information(siteName=BlueRibbonSurveyScraper.__siteName__, cafeName=cafeName, cafeTypes=cafeTypes,cafeLocation=cafeLocation,cafeReviews=cafeReviews)

    def __setHeaders(self, path, cookie = '', csrf_token = ''):
        self.__headers['path'] = path
        if len(cookie) != 0:
            self.__headers['cookie'] = cookie
        if len(csrf_token) != 0:
            self.__headers['csrf_token'] = csrf_token