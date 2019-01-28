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
            retval.append(normal(mean,stddev))
        return retval
    
        
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
