import re
import time
import logging
from functools import reduce

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
        options.add_argument(':authority=www.diningcode.com')
        options.add_argument(':scheme=https')
        options.add_argument('accept=text/plain, */*; q=0.01')
        options.add_argument('accept-encoding=gzip, deflate, br')
        options.add_argument('accept-language=ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7')
        options.add_argument('content-type=application/x-www-form-urlencoded; charset=UTF-8')
        options.add_argument('cookie=dcadid=WZARTH1652193174; _fbp=fb.1.1652193175380.172649470; _ga=GA1.2.521285454.1652193176; \
             __gads=ID=9ae8ad2ee21a27ad-22cbe6371fd30027:T=1652193175:RT=1652193175:S=ALNI_ManDRpRHraLhnevvX0i52G0sH6CzQ; \
                 dclogid=ik1652194650; __gpi=UID=0000054108afe315:T=1652194681:RT=1652272992:S=ALNI_MayE29xhTmEP6k6ASUzjxZXd_5viw; \
                     PHPSESSID=h8h8mv6bgggqc9uqpq7v3g28cj; _gid=GA1.2.1411254905.1652453581')
        options.add_argument('origin=https://www.diningcode.com')
        options.add_argument('Referer=https://www.diningcode.com/')
        options.add_argument('User-Agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko)\
             Chrome/101.0.4951.64 Safari/537.36')
        
        service = Service(driverUrl)
        self.driver = webdriver.Chrome(service=service, options=options)
        self.driver.implicitly_wait(60)
        self.db = DB(secret.dbConfig.user, secret.dbConfig.password, secret.dbConfig.host, secret.dbConfig.port, secret.dbConfig.db)
    

    def scrape(self, args):
        try:
            if args[0] == 'start':
                url = self.__queryAtListPage(*args[1:])
                cafeList = []
                
            elif args[0] == 'continue':
                savePoint = readSavePoint(ScraperType.DiningCode)
                if savePoint != None:
                    cafeList = savePoint['unvisited']
                    logging.info('load savePoint {}'.format('DiningCode'))

                else:
                    logging.warning('load fails')
                    return False
            else:
                raise IndexError
    
            if args[0] == 'start':
                self.driver.get(url)
                defaultWindow = self.driver.window_handles[0]
                cafeList.extend(self.__getUrlAtListPage(defaultWindow))

            while len(cafeList) != 0:
                cafeUrl = cafeList[0]
                self.driver.get(cafeUrl)
                defaultWindow = self.driver.window_handles[0]
                newCafeList, info = self.__scrapePage(defaultWindow)
                
                if info != None:
                    self.db.saveInfo(info)
                
                del cafeList[0]

                cafeList.extend(newCafeList)
                cafeList = list(set(cafeList))

        except IndexError as e:
            raise e

        except ScraperError as e:
            writeSavePoint(ScraperType.DiningCode, cafeList)
            raise e
                
        except KeyboardInterrupt as e:
            writeSavePoint(ScraperType.DiningCode, cafeList)
            raise e

        except Exception as e:
            writeSavePoint(ScraperType.DiningCode, cafeList)
            raise e
        
        else:
            logging.info('Done Scraping!!!')
        
        finally:
            self.db.engine.dispose()
            self.driver.quit()

    def __scrapePage(self, defaultWindow):
        try:
            cafeList = []
            selectors = DiningCodeScraper.__selectors
            self.__spreadAllReviews()

            cafeName = WebDriverWait(self.driver, 60).until(EC.presence_of_element_located((By.CSS_SELECTOR, selectors['title']))).text.strip()
            rawTypes = WebDriverWait(self.driver, 60).until(EC.presence_of_element_located((By.CSS_SELECTOR, selectors['type'])))
            cafeTypes = CafeType.getTypes(rawTypes.text.strip())
            
            isExist = reduce(lambda ret, type: ret and self.db.isAlreadyScraped(cafeName, self.__siteName__, type), cafeTypes, True)
            if not isExist:
                cafeLocation = WebDriverWait(self.driver, 60).until(EC.presence_of_element_located((By.CSS_SELECTOR, selectors['location']))).text.strip()
                rawCafePreference = WebDriverWait(self.driver, 60).until(EC.presence_of_element_located((By.CSS_SELECTOR, selectors['cafePreference'])))
                cafePreference = float(rawCafePreference.text[:-1])*2
            
                rawReviewContents = self.driver.find_elements(by=By.CLASS_NAME, value = selectors['reviewContent'])
                rawReviewTags = self.driver.find_elements(by=By.CLASS_NAME, value=selectors['reviewTag'])
                rawReviewPreferences = self.driver.find_elements(by=By.CLASS_NAME, value=selectors['reviewPreference'][0])
                cafeReviews = self.__getReviews(rawReviewContents, rawReviewTags, rawReviewPreferences)
                
                cafeList.extend(self.__getUrlAtCafePage(defaultWindow))
                return cafeList, Information(siteName=DiningCodeScraper.__siteName__, cafeName=cafeName, cafeTypes=cafeTypes, \
                    cafeLocation=cafeLocation, cafePreference=cafePreference, cafeReviews=cafeReviews)

            else:
                return cafeList, None

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

    def __getUrlAtCafePage(self, defaultWindow):
        keywordComponent = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'delisor-search')))
        keyword = keywordComponent.find_element(by=By.TAG_NAME,value='strong').text.strip("'")
        
        self.driver.execute_script("window.open();")
        currentWindow = self.driver.window_handles[-1]
        self.driver.switch_to.window(window_name=currentWindow)
        
        url = self.__queryAtListPage(keyword)
        self.driver.get(url)
        
        cafeList = self.__getUrlAtListPage(currentWindow)
        
        self.driver.close()
        self.driver.switch_to.window(window_name=defaultWindow)
        
        return cafeList

    def __queryAtListPage(self, *args):
        url = 'https://www.diningcode.com/list?'
        for arg in args:
            url += "query={}&".format(arg)
        
        url = url[:-1]
        logging.info('Query: {}'.format(url))

        return url

    def __getUrlAtListPage(self, defaultWindow):
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

            cafeList = []
            for title, page in zip(titles, pages):
                cafeTypes = self.__getTypes(page)
                if cafeTypes != set():
                    cafeName = title.find_element(by=By.TAG_NAME, value='h2').text
                    cafeName = re.split('^[0-9]+.', cafeName)[1].strip()
                    
                    isExist = reduce(lambda ret, type: ret and self.db.isAlreadyScraped(cafeName, self.__siteName__, type), cafeTypes, True)
                    if not isExist:
                        page.click()
                        self.driver.switch_to.window(window_name=self.driver.window_handles[-1])
                        cafeList.append(self.driver.current_url)
                        self.driver.close()
                        self.driver.switch_to.window(window_name=defaultWindow)
                else:
                    continue
            return cafeList
                

    def __getTypes(self, page):
            pageType = page.find_element(by=By.CLASS_NAME, value='Category').text
            return CafeType.getTypes(pageType)
    
    def __getReviews(self, rawContents, rawTags, rawPreferences):
        selectors = DiningCodeScraper.__selectors
        reviews = []

        for rawContent, rawTag, rawPreference in zip(rawContents, rawTags, rawPreferences):
            stars = rawPreference.find_elements(by=By.CLASS_NAME, value=selectors['reviewPreference'][1])
            preference = 0.0
            for star in stars:
                preference += float(star.text)
            preference = (preference/len(stars)) * 2

            review = Review(rawContent.text.strip(), [tag.strip() for tag in rawTag.text.split()], preference)
            if self.__isUniqueReview(review, reviews):
                reviews.append(review)
            else:
                continue
        return reviews

    def __isUniqueReview(self, newReview, reviews):
        for review in reviews:
            if newReview == review:
                return False
        return True
            
    