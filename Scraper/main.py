import os
import sys
from pathlib import Path
rootPath = Path(os.path.abspath(__file__)).parent
sys.path.append(rootPath)

import logging
from config import config
from scrapers import BlueRibbonSurveyScraper
from scrapers import DiningCodeScraper

if __name__ == '__main__':
    logging.basicConfig(filename=config.logPath, encoding='utf-8', level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    
    try:
        if sys.argv[1].lower() == 'blueribbon':
            scraper = BlueRibbonSurveyScraper()

        elif sys.argv[1].lower() == 'diningcode':
            scraper = DiningCodeScraper('./scrapers/chromedriver')

        if scraper.scrape(sys.argv[2:]):
            print('Scrape {} Done'.format(sys.argv[1]))
        else:
            print('Scrape {} Fails'.format(sys.argv[1]))


    except IndexError as e:
        #python main.py blueribbon start 1 30
        #python main.py blueribbon continue
        #python main.py diningcode start 서울 카페
        #python main.py diningcode continue
        sys.stderr.write('python main.py [blueribbon | diningcode] [start | continue] [start end | query]\n')
        exit(1)
    except Exception as e:
        logging.error(e)
    finally:
        logging.info('Scraper Exit')
    