from SP500 import SP500_Info
import json
import numpy as np
import pandas as pd
from datetime import datetime

symbol=['BRK.B','BF.B']
sp500_info=SP500_Info().load(exclude=symbol)
# start=datetime.now()
df={}
for sector in sp500_info:
	com=sp500_info[sector]
	industry=pd.DataFrame({symbol:pd.read_csv(f'C://Users/user/Desktop/Anjestan/data/{sector}/{symbol}.csv',index_col='Date')['Adj Close'] for symbol in com})
	df[sector]=industry
# end=datetime.now()
# diff=(end-start).seconds
# print(f'cost {diff} seconds')
pairs_info={}
for sector in sp500_info:
	data=df[sector].copy()
	data.index=pd.to_datetime(data.index)
	data=data['20130101':'20161231'].copy()
	data.dropna(axis=1,inplace=True)
	corr=np.abs(data.corr())
	corr[corr<=0.90]=0
	for i in corr.index:
		corr[i][i]=0
	corr.replace(0,np.nan,inplace=True)
	corr.dropna(how='all',axis=1,inplace=True)
	obs=corr.idxmax()
	# prin(obs)
	pairs_info[sector]={i:j for i,j in obs.items() if obs[j]==i}

pairs={}
for sector in sp500_info:
	storage=[]
	for i,j in pairs_info[sector].items():
		if (j,i) not in storage:
			storage.append((i,j))
	pairs[sector]=storage

	# df[sector]=data

# num=0
# for sector in df:
# 	num+=len(df[sector].columns)
