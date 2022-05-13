import re
import time
import logging

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException, StaleElementReferenceException

from .common import *
from models.db import DB
from config import secret
from .errors import ScraperError
from models.information import *
from models.errors import DBError





class DiningCodeScraper:
    __siteName__ = '다이닝코드'
    __selectors = {
                'title': '#div_profile > div.s-list.pic-grade > div.tit-point > p',
                'location': '#div_profile > div.s-list.basic-info > ul > li.locat',
                'type': '#div_profile > div.s-list.pic-grade > div.btxt',
                'cafePreference': '#lbl_review_point',
                'reviewContent': 'review_contents.btxt',
                'reviewTag': 'tags',
                'reviewPreference': ['point-detail', 'star']
    }

    def __init__(self, driverUrl):
        options = webdriver.ChromeOptions()
        options.add_argument('headless')
        options.add_argument('incognito')
        options.add_argument('--blink-settings=imagesEnabled=false')
        
        service = Service(driverUrl)
        self.driver = webdriver.Chrome(service=service, options=options)
        self.driver.implicitly_wait(60)
        self.db = DB(secret.dbConfig.user, secret.dbConfig.password, secret.dbConfig.host, secret.dbConfig.port, secret.dbConfig.db)
    

    def scrape(self, args):
        cafeList = set()
        scrapedList = set()
        try:
            if args[0] == 'start':
                url = self.__queryAtListPage(*args[1:])
                
            elif args[0] == 'continue':
                savePoint = readSavePoint(ScraperType.DiningCode)
                if savePoint != None:
                    savePoint
                    cafeList = set(savePoint['unvisited'])
                    scrapedList = set(savePoint['visited'])
                    logging.info('load savePoint {}'.format('DiningCode'))

                else:
                    logging.warning('load fails')
                    return False
            else:
                raise IndexError
        except IndexError as e:
            raise e
        
        try:
            if args[0] == 'start':
                self.driver.get(url)
                defaultWindow = self.driver.window_handles[0]
                cafeList.update(self.__getUrlAtListPage(defaultWindow, scrapedList))

            while len(cafeList) != 0:
                cafeUrl = cafeList.pop()
                self.driver.get(cafeUrl)
                defaultWindow = self.driver.window_handles[0]
                newCafeList, info = self.__scrapePage(defaultWindow, scrapedList)
                cafeList.update(newCafeList)
                self.db.saveInfo(info)
                scrapedList.add(info.cafeName)
                time.sleep(2)
            
            self.db.engine.dispose()
            logging.info('Done Scraping!!!')
            return

        except ScraperError as e:
            writeSavePoint(ScraperType.DiningCode, list(cafeList), list(scrapedList))
            raise e
                
        except KeyboardInterrupt:
            writeSavePoint(ScraperType.DiningCode, list(cafeList), list(scrapedList))
            self.db.engine.dispose()
            logging.info('Scraper Interrupted')
            exit(1)

        except Exception as e:
            writeSavePoint(ScraperType.DiningCode, list(cafeList), list(scrapedList))
            raise e
        
        finally:
            self.driver.quit() #모든 탭 종료


    def __queryAtListPage(self, *args):
        url = 'https://www.diningcode.com/list?'
        for arg in args:
            url += "query={}&".format(arg)
        
        url = url[:-1]
        logging.info('Query: {}'.format(url))

        return url

    def __getUrlAtListPage(self, defaultWindow, scrapedList):
        updatedBtnSelector = '#map > button.SearchMore.upper'
        try:
            while True:
                btn = WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, updatedBtnSelector)))
                self.driver.execute_script('arguments[0].click();', btn)
                time.sleep(.5)

        except ElementClickInterceptedException:
            raise ScraperError()
        except StaleElementReferenceException:
            raise ScraperError()

        except TimeoutException:
            pages = self.driver.find_elements(by=By.CLASS_NAME, value='PoiBlock')
            titles = self.driver.find_elements(by=By.CLASS_NAME, value='InfoHeader')

            cafeList = set()
            for title, page in zip(titles, pages):
                if self.__isCafeOrBar(page):
                    tit = title.find_element(by=By.TAG_NAME, value='h2').text
                    tit = re.split('^[0-9]+.', tit)[1]
                    if tit in scrapedList:
                        continue
                    else:
                        page.click()
                        self.driver.switch_to.window(window_name=self.driver.window_handles[-1])
                        cafeList.add(self.driver.current_url)
                        self.driver.close()
                        self.driver.switch_to.window(window_name=defaultWindow)
                else:
                    continue
            return cafeList
                

    def __isCafeOrBar(self, page):
            pageType = page.find_element(by=By.CLASS_NAME, value='Category').text

            for keyword in CafeType.getKeywords('cafe'):
                if pageType.find(keyword) != -1:
                    return True
            for keyword in CafeType.getKeywords('bar'):
                if pageType.find(keyword) != -1:
                    return True
            return False

    def __scrapePage(self, defaultWindow, scrapedList):
        try:
            self.__spreadAllReviews()
            selectors = DiningCodeScraper.__selectors

            cafeName = WebDriverWait(self.driver, 60).until(EC.presence_of_element_located((By.CSS_SELECTOR, selectors['title']))).text
            cafeLocation = WebDriverWait(self.driver, 60).until(EC.presence_of_element_located((By.CSS_SELECTOR, selectors['location']))).text
            rawTypes = WebDriverWait(self.driver, 60).until(EC.presence_of_element_located((By.CSS_SELECTOR, selectors['type'])))
            cafeTypes = CafeType.getTypes(rawTypes.text)
            
            rawCafePreference = WebDriverWait(self.driver, 60).until(EC.presence_of_element_located((By.CSS_SELECTOR, selectors['cafePreference'])))
            cafePreference = float(rawCafePreference.text[:-1])*2
        
            rawReviewContents = self.driver.find_elements(by=By.CLASS_NAME, value = selectors['reviewContent'])
            rawReviewTags = self.driver.find_elements(by=By.CLASS_NAME, value=selectors['reviewTag'])
            rawReviewPreferences = self.driver.find_elements(by=By.CLASS_NAME, value=selectors['reviewPreference'][0])
            cafeReviews = self.__getReviews(rawReviewContents, rawReviewTags, rawReviewPreferences)
            
            cafeList = self.__getUrlAtCafePage(defaultWindow, scrapedList | set([self.driver.current_url])) #현재 페이지 제외

            return cafeList, Information(siteName=DiningCodeScraper.__siteName__, cafeName=cafeName, cafeTypes=cafeTypes, cafeLocation=cafeLocation, cafePreference=cafePreference, cafeReviews=cafeReviews)
        
        except ElementClickInterceptedException:
            raise ScraperError()
        except StaleElementReferenceException:
            raise ScraperError()
   
    def __spreadAllReviews(self):
        while True:
            try:
                btn = WebDriverWait(self.driver, 5).until((EC.presence_of_element_located((By.ID, 'div_more_review'))))
                self.driver.execute_script('arguments[0].click();', btn)
                time.sleep(.5)
            
            except ElementClickInterceptedException:
                raise ScraperError()
            except StaleElementReferenceException:
                raise ScraperError()
            except TimeoutException:
                return
    
    def __getReviews(self, rawContents, rawTags, rawPreferences):
        selectors = DiningCodeScraper.__selectors
        reviews = []

        for rawContent, rawTag, rawPreference in zip(rawContents, rawTags, rawPreferences):
            stars = rawPreference.find_elements(by=By.CLASS_NAME, value=selectors['reviewPreference'][1])
            preference = 0.0
            for star in stars:
                preference += float(star.text)
            preference = (preference/len(stars)) * 2

            review = Review(rawContent.text, rawTag.text.split(), preference)
            reviews.append(review)
        return reviews

    def __getUrlAtCafePage(self, defaultWindow, scrapedList):
        keywordComponent = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'delisor-search')))
        keyword = keywordComponent.find_element(by=By.TAG_NAME,value='strong').text.strip("'")
        
        self.driver.execute_script("window.open();")
        currentWindow = self.driver.window_handles[-1]
        self.driver.switch_to.window(window_name=currentWindow)
        
        url = self.__queryAtListPage(keyword)
        self.driver.get(url)
        
        cafeList = self.__getUrlAtListPage(currentWindow, scrapedList)
        
        self.driver.close()
        self.driver.switch_to.window(window_name=defaultWindow)
        
        return cafeList