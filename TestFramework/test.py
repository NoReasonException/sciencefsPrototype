
from specification.documentSpecification import DateRangeBuilder,Utills,DateRangeRetriever
import sys
list_unix=DateRangeBuilder.simpleBuilder(int(sys.argv[1]),1483232461,1488330061)
list_8601=Utills._to8601_array(list_unix)


percentile=float(sys.argv[2])
max_percentile_date=DateRangeRetriever.getMaxOfGivenPercent(percentile,1483232461,1488330061)

total=len(list_unix)
cnt=0
for i in range(len(list_unix)):
    if(list_unix[i]<max_percentile_date):
        print(list_8601[i]+"under "+str(percentile))
        cnt+=1
print("\n"+str(cnt/total)+"actual percentile")




