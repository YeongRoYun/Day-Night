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
            
            scraper = DiningCodeScraper(Path(os.path.abspath(__file__)).parent / 'scrapers' / 'chromedriver')
        else:
            raise IndexError

        scraper.scrape(sys.argv[2:])
        sys.exit(0) #Normal Termination

    except IndexError as e:
        #python main.py blueribbon start 1 30
        #python main.py blueribbon continue
        #python main.py diningcode start 서울 카페
        #python main.py diningcode continue
        sys.stderr.write('python main.py [blueribbon | diningcode] [start | continue] [start end | query]\n')
        sys.exit(2) #Abnormal Termination and need to check paramenters
    except KeyboardInterrupt:
        logging.info('Forced Termination by User')
        sys.exit(3) #Forced Termination
    
    except Exception as e:
        logging.error(e)
        sys.exit(4) #Abnormal Termination
    finally:
        logging.info('Scraper is over')
    