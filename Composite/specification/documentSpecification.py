from specification.DateTimeUtills import DateRangeBuilder,Utills
import json
import random


class Document:
    def __init__(self,templateFilePath):
        self.templateFilePath=templateFilePath

    def loadTemplateFile(self):
        with open(self.templateFilePath,"r") as tfile:
            return tfile.read()


    def _builder(self,\
        name:str,\
        timestamp_unix:int,\
        duration_secs:int,\
        timeslot:int,\
        model:str,\
        variables:str,\
        results:str,\
        exp_data_pc:dict,\
        exp_data_pe:dict):
    
        rawjson=self.loadTemplateFile()
        jsonObject=json.loads(rawjson)
        
        jsonObject["exp_meta"]["name"]=str(name)
        jsonObject["exp_meta"]["period"]["timestamp_start"]=int(timestamp_unix)
        jsonObject["exp_meta"]["period"]["duration"]=int(duration_secs)
        jsonObject["exp_meta"]["period"]["timeslot"]=int(timeslot)
        jsonObject["exp_data_main"]["model"]=str(model)
        jsonObject["exp_data_main"]["variables"]=str(variables)
        jsonObject["exp_data_main"]["results"]=str(results)
        jsonObject["exp_data_pc"]=dict(exp_data_pc)
        jsonObject["exp_data_pe"]=dict(exp_data_pe)

        return json.dumps(jsonObject)
        
    def simpleBuilder(self,unixDateTimeGenerator:object,category="NO_CATEGORY"):
        return self._builder((category+" Experiment"),\
                next(unixDateTimeGenerator),\
                random.randint(1200,7200),\
                random.randint(1,10000),\
                "Unknown model",\
                "X~N(0,1)",\
                "0.66",\
                dict(),\
                dict())

    def massBuilder(self,unixDateTimeGenerator:object,category="NO CATEGORY"):
        while(True):  #this has designed to wrap an generator , so when the parent generator throws the exception , the exception
                        #will follow the stack and also this generator will stop!, this workaround is because something like
                        # return [yield x for i in ...] is not supported
            yield self.simpleBuilder(unixDateTimeGenerator,category)

      
