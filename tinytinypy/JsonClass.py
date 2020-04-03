class JsonClass:
    @classmethod
    def getClassKey(cls, jsonKey):
        for key, val in cls.TRANS.items():
            if val == jsonKey or (key == jsonKey and val == True):
                return key
        return None
    @classmethod
    def getJsonKey(cls, classKey):
        val = cls.TRANS.get(classKey, None)
        return classKey if val == True else val
    @classmethod
    def fromJson(cls, dataDict):
        return cls(**{cls.getClassKey(key): val for key, val in dataDict.items() if cls.getClassKey(key) is not None and val is not None})
    def toJson(self):
        return {self.__class__.getJsonKey(key): val for key, val in self.__dict__.items() if self.__class__.getJsonKey(key) is not None and val is not None}
