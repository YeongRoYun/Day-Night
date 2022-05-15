import os
import json
import logging
from pathlib import Path
from enum import Enum, unique, auto

blueRibbonSurveySave = Path(os.path.abspath(__file__)).parent / 'save' / 'blueRibbonSurvey.save'
diningCodeSave = Path(os.path.abspath(__file__)).parent / 'save' / 'diningCode.save'


@unique
class CafeType(Enum):
    Cafe = auto()
    Bar = auto()

    @classmethod
    def getTypes(cls, query):
        cafeTypes = set()
        if cls.__isType(query, cls.getKeywords('cafe')):
            cafeTypes.add('카페')
        if cls.__isType(query, cls.getKeywords('bar')):
            cafeTypes.add('바')
        
        return cafeTypes
        
    
    @classmethod
    def __isType(cls, query, keywords):
        for keyword in keywords:
            if query.find(keyword) != -1:
                return True
        return False
    
    @classmethod
    def getKeywords(cls, type):
        keywords = {
        'cafe': '디저트 차 커피 베이커리 카페 빙수 cafe'.split(),
        'bar': '칵테일 와인바 샴페인바 bar 와인 샴페인'.split()
    }
        return keywords[type]

@unique
class ScraperType(Enum):
    BlueRibbonSurvey = auto()
    DiningCode = auto()


def writeSavePoint(type, *args):
    if type == ScraperType.BlueRibbonSurvey:
        with open(blueRibbonSurveySave, 'w') as fd:
            log = {'start': args[0], 'current': args[1], 'end': args[2]}
            json.dump(log, fd)
   
    elif type == ScraperType.DiningCode:
        with open(diningCodeSave, 'w') as fd:
            log = {'unvisited': args[0]}
            json.dump(log, fd)
    else:
        pass
    logging.info('write savePoint')


def readSavePoint(type):
    if type == ScraperType.BlueRibbonSurvey:
        path = blueRibbonSurveySave
    elif type == ScraperType.DiningCode:
        path = diningCodeSave
    else:
        path = None
    
    if path != None:
        if path.exists():
            
            with open(path, 'r') as fd:
                savePoint = json.load(fd)
        else:
            savePoint = None
    else:
        savePoint = None

    logging.info('read savePoint')
    return savePoint