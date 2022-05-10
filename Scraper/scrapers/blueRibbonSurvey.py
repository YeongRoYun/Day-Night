import os
import sys
from pathlib import Path
rootPath = Path(os.path.abspath(__file__)).parent.parent
sys.path.append(rootPath)

import re
import logging
import requests
from bs4 import BeautifulSoup
from urllib.error import HTTPError, URLError

from .common import *


class BlueRibbonSurveyScraper:
    def __init__(self):
        self.rootUrl = 'https://www.bluer.co.kr'
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

    def setHeaders(self, path, cookie = '', csrf_token = ''):
        self.__headers['path'] = path
        if len(cookie) != 0:
            self.__headers['cookie'] = cookie
        if len(csrf_token) != 0:
            self.__headers['csrf_token'] = csrf_token
    
    def getHeaders(self):
        return self.__headers

    def scrape(self, relativeUrl):
        targetUrl = self.rootUrl + relativeUrl
        try:
            res = requests.get(targetUrl, headers=self.__headers)
        except HTTPError as e:
            logging.error('HTTPError: 404 NOT FOUND')
            return {}
        except URLError as e:
            raise e

        html = res.text
        bs = BeautifulSoup(html, 'html.parser')

        if bs.find('div', {'class':'text-lg mb-lg'}) is not None: #Invalid Address
            return {}
        else:
            shopType = bs.find('ol', {'class':'foodtype'}).get_text()
            cafeTypes = CafeType.getTypes(shopType)
            
            if len(cafeTypes) == 0:
                return {}
            else:
                info = bs.find('div', {'class': 'restaurant-info'})
                cafeName = bs.find('div', {'class':'header-title'}).h1.get_text()
                cafeLoc = info.find('button', {'class': 'copy-address'}).parent.get_text()
                cafeReviews = info.find('div', {'class': re.compile('info-4')}).findAll('dd')
                cafeReviews = list(map(lambda review: review.get_text().strip(), cafeReviews))
                siteName = '블루리본서베이'
                return {'siteName': siteName, 'cafeName': cafeName, 'cafeTypes': cafeTypes, 'cafeLoc': cafeLoc, 'cafeReviews': cafeReviews}