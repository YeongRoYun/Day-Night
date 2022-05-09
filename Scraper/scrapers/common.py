from enum import Enum, unique, auto

@unique
class CafeType(Enum):
    Cafe = auto()
    Bar = auto()

    @classmethod
    def getType(cls, query):
        cafeKeywords = '디저트 차 커피 베이커리 카페 빙수'.split()
        barKeywords = ''
        cafeTypes = set()
        
        if cls.__isType(cls.Cafe, query, cafeKeywords):
            cafeTypes.add(cls.Cafe)
        if cls.__isType(cls.Bar, query, barKeywords):
            cafeTypes.add(cls.Bar)
        
        return cafeTypes
        
    
    @classmethod
    def __isType(cls, type, query, keywords):
        for keyword in keywords:
            if query.find(keyword) != -1:
                return True
        return False