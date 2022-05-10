from . import dbModel, userModel
from enum import Enum, unique, auto

class ModelChanger:
    @staticmethod
    def dbToUser(model):
        if not isinstance(model, dbModel.Base):
            raise NameError('dbToUser(): invalid model')
        
        elif isinstance(model, dbModel.Cafe):
            newModel = userModel.Cafe(id=model.id, name=model.name, location=model.location, createdAt=model.createdAt, updatedAt=model.updatedAt, deletedAt=model.deletedAt)
        elif isinstance(model, dbModel.Site):
            newModel = userModel.Site(id=model.id, name=model.name, createdAt=model.createdAt, updatedAt=model.updatedAt, deletedAt=model.deletedAt)
        elif isinstance(model, dbModel.Type):
            newModel = userModel.Type(id=model.id, name=model.name, createdAt=model.createdAt, updatedAt=model.updatedAt, deletedAt=model.deletedAt)
        elif isinstance(model, dbModel.CafesType):
            newModel = userModel.CafesType(id=model.id, cafeId=model.cafeId, typeId=model.typeId)
        else:
            newModel = userModel.Review(id=model.id, content=model.content, preference=model.preference, cafe=model.cafe, site=model.site, createdAt=model.createdAt, updatedAt=model.updatedAt, deletedAt=model.deletedAt)
        
        return newModel
    
    @staticmethod
    def userToDb(model):
        if not isinstance(model, userModel.Base):
            raise NameError('userToDb(): invalid model')

        elif isinstance(model, userModel.Cafe):
            if model.isComplete:
                newModel = dbModel.Cafe(id=model.id, name=model.name, location=model.location, createdAt=model.createdAt, updatedAt=model.updatedAt, deletedAt=model.deletedAt)
            else:
                newModel = dbModel.Cafe(name=model.name, location=model.location)
        elif isinstance(model, userModel.Site):
            if model.isComplete:
                newModel = dbModel.Site(id=model.id, name=model.name, createdAt=model.createdAt, updatedAt=model.updatedAt, deletedAt=model.deletedAt)
            else:
                newModel = dbModel.Site(name=model.name)
        elif isinstance(model, userModel.Type):
            if model.isComplete:
                newModel = dbModel.Type(id=model.id, name=model.name, createdAt=model.createdAt, updatedAt=model.updatedAt, deletedAt=model.deletedAt)
            else:
                newModel = dbModel.TYpe(name=model.name)
        elif isinstance(model, userModel.CafesType):
            if model.isComplete:
                newModel = dbModel.CafesType(id=model.id, cafeId=model.cafeId, typeId=model.typeId)
            else:
                newModel = dbModel.CafesType(cafeId=model.cafeId, typeId=model.typeId)
        else:
            if model.isComplete:
                newModel = dbModel.Review(id=model.id, content=model.content, preference=model.preference, cafe=model.cafe, site=model.site, createdAt=model.createdAt, updatedAt=model.updatedAt, deletedAt=model.deletedAt)
            else:
                newModel = dbModel.Review(content=model.content, preference=model.preference, cafe=model.cafe, site=model.site)
        return newModel



@unique
class Mode(Enum):
    User = auto()
    DB = auto()