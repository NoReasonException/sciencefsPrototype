import json
import time
from datetime import datetime
from numpy.random import normal
from scipy.stats import norm
class DateRangeBuilder:
    
    simpleBuilderLambda=lambda numberOfObjects,minUnix,maxUnix:DateRangeBuilder._build_raw(numberOfObjects,(minUnix+maxUnix)/2,2592000)


    @staticmethod
    def _build_raw(numberOfObjects:int,mean:int,stddev:int):
        for i in range(numberOfObjects):
            yield (normal(mean,stddev))
    
        
class DateRangeRetriever:

    @staticmethod
    def getMaxOfGivenPercent(percent:float,minUnixDate:int,maxUnixDate:int)->int:
        return DateRangeRetriever._getRawMaxOfGivenPercent(percent,(minUnixDate+maxUnixDate)/2,2592000)

    @staticmethod
    def _getRawMaxOfGivenPercent(percent:float,mean:int,stddev:int)->int:
        assert percent>0 and percent<1
        return norm.ppf(percent,mean,stddev)


class Utills:
    
    @staticmethod
    def _to8601(unixTimestamp:int)->str:
        return datetime.utcfromtimestamp(unixTimestamp).strftime('%Y-%m-%d %H:%M:%S')
    
    @staticmethod
    def _to8601_array(unixTimestampArray:list)->list:
        return list(map(lambda x :Utills._to8601(x),unixTimestampArray))
