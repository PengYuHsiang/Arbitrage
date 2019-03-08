import pandas as pd
import json

url_sp500='https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
list_sp500=pd.read_html(url_sp500)[0].copy()
list_sp500.columns=list_sp500.iloc[0,:]
list_sp500.drop(0,inplace=True)
list_sp500.set_index('Symbol',inplace=True)

sort_data={}
sector=list_sp500['GICS Sector'].value_counts().index
for i in sector:
	com=list_sp500[list_sp500['GICS Sector']==i]
	info={j:{'security':com['Security'][j],'industry':com['GICS Sub Industry'][j]} for j in com.index}
	sort_data[i]=info

file=open('C://Users/user/Desktop/Anjestan/sp500_info.json','w')
json.dump(sort_data,file)
file.close()