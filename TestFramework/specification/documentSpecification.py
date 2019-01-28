import json
import time
from datetime import datetime
from numpy.random import normal
from scipy.stats import norm
class DateRangeBuilder:
    @staticmethod
    def simpleBuilder(numberOfObjects:int,minUnixDate:int,maxUnixDate:int):
        """
        .simpleBuilder

        @params minUnixDate     -> the minimum date of the sample
        @params maxUnixDate     -> the maximum date of the sample
        @params numberOfFiles   -> the number of files returned
        This method returns an array of iso8601 strings , following a  Normal
        Distribution of N(m=maxUnixDate/minUnixDate),s=#one month from mean(2592000))
        
        """
        m=(minUnixDate+maxUnixDate)/2
        s=2592000
        return DateRangeBuilder._build_raw(numberOfObjects,m,s)

    @staticmethod
    def _build_raw(numberOfObjects:int,mean:int,stddev:int):
        retval=list()
        for i in range(numberOfObjects):
            retval.append(  datetime.utcfromtimestamp(normal(mean,stddev)).strftime('%Y-%m-%d %H:%M:%S'))
        return retval
    
        
class DateRangeRetriever:
    @staticmethod
    def getMaxOfGivenPercent(minUnixDate:int,maxUnixDate:int,percent:int)->int:
        assert percent>0 and percent<1
        m=(minUnixDate+maxUnixDate)/2
        s=2592000
        return norm.ppf(percent,m,s)

class Utills:
    
    @staticmethod
    def _to8601(unixTimestamp:int)->str:
        return datetime.utcfromtimestamp(unixTimestamp).strftime('%Y-%m-%d %H:%M:%S')
    
    @staticmethod
    def _to8601_array(unixTimestampArray:list)->list:
        return filter(lambda x :Utills._to8601(x),unixTimestampArray)
