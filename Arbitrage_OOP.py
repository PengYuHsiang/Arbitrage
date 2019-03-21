import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from statsmodels.tsa.stattools import adfuller

class load_data:
	def __init__(self,start='20100101',end='20190308'):
		self.start=start
		self.end=end
		self.sp500_info=self.load_json()
		self.data=self.aggregate_data()
		
	def load_json(self):
		file=open('./sp500_info.json','r')
		sp500_info=json.load(file)
		return sp500_info

	def aggregate_data(self):
		df={}
		for sector in self.sp500_info:
			com=self.sp500_info[sector]
			industry=pd.DataFrame({symbol:pd.read_csv(f'./data/{sector}/{symbol}.csv',index_col='Date')['Adj Close'] for symbol in com})
			industry.index=pd.to_datetime(industry.index)
			industry=industry[self.start:self.end].copy()
			df[sector]=industry.dropna(axis=1)
		return df

class get_pairs:
	def __init__(self,start,end,cor=0.9,alpha=0.01):
		self.start_date=start
		self.end_date=end
		self.correlation=cor
		self.alpha=alpha
		self.train_data=load_data(start=self.start_date,end=self.end_date).data
		self.pairs=self.examine_corr(self.train_data)
		self.qualify_pairs=self.unit_root_test()

	def examine_corr(self,train):
		pairs_info={}
		for sector in self.train_data:
			data=self.train_data[sector].copy()
			corr=np.abs(data.corr())
			corr[corr<=self.correlation]=0
			for i in corr.index:
				corr[i][i]=0
			corr.replace(0,np.nan,inplace=True)
			corr.dropna(how='all',axis=1,inplace=True)
			obs=corr.idxmax()
			pairs_info[sector]={i:j for i,j in obs.items() if obs[j]==i}
		pairs=self.stream_corr(pairs_info)
		return pairs

	def stream_corr(self,pairs_info):
		pairs={}
		for sector in self.train_data:
			storage=[]
			for i,j in pairs_info[sector].items():
				if (j,i) not in storage:
					storage.append((i,j))
			pairs[sector]=storage
		return pairs

	def unit_root_test(self):
		qualify={sector:[(i,j) for i,j in self.pairs[sector] if adfuller(self.train_data[sector][i]/self.train_data[sector][j])[1]<self.alpha] for sector in self.pairs}
		return qualify





pairs_info={}
for sector in sp500_info:
	data=df[sector].copy()
	data.index=pd.to_datetime(data.index)
	data=data['20100101':'20171231'].copy()
	data.dropna(axis=1,inplace=True)
	df[sector]=data
	corr=np.abs(data.corr())
	corr[corr<=0.85]=0
	for i in corr.index:
		corr[i][i]=0
	corr.replace(0,np.nan,inplace=True)
	corr.dropna(how='all',axis=1,inplace=True)
	obs=corr.idxmax()
	pairs_info[sector]={i:j for i,j in obs.items() if obs[j]==i}

pairs={}
for sector in sp500_info:
	storage=[]
	for i,j in pairs_info[sector].items():
		if (j,i) not in storage:
			storage.append((i,j))
	pairs[sector]=storage

# Unit Root Test
qualify={sector:[(i,j) for i,j in pairs[sector] if adfuller(df[sector][i]/df[sector][j])[1]<0.05] for sector in pairs }

measures_data={sector:df[sector]['20170101':'20171231'] for sector in df}
measures={}
for sector in qualify:
	data={}
	for i,j in qualify[sector]:
		ratio=measures_data[sector][i]/measures_data[sector][j]
		data[(i,j)]={'mean':ratio.mean(),
					'signal_up':ratio.mean()+ratio.std(),
					'signal_down':ratio.mean()-ratio.std(),
					'stopout_up':ratio.mean()+3*ratio.std(),
					'stopout_down':ratio.mean()-3*ratio.std()}
	measures[sector]=data


test_data={}
for sector in sp500_info:
	com=sp500_info[sector]
	industry=pd.DataFrame({symbol:pd.read_csv(f'C://Users/user/Desktop/Anjestan/data/{sector}/{symbol}.csv',index_col='Date')['Adj Close'] for symbol in com})
	test_data[sector]=industry
	data=test_data[sector].copy()
	data.index=pd.to_datetime(data.index)
	data=data['20180101':'20181231'].copy()
	data.dropna(axis=1,inplace=True)
	test_data[sector]=data


for sector in qualify:
	for x,y in qualify[sector]:
		example=test_data[sector][[x, y]]
		signal=measures[sector][(x, y)]
		ratio=example[x]/example[y]
		fig=plt.figure()
		plt.plot(ratio,'k-')
		plt.plot(measures_data[sector][x]/measures_data[sector][y],'c-')
		plt.hlines(signal['mean'],'20170101','20181231',color='k',linestyles=':')
		plt.hlines(signal['signal_up'],'20170101','20181231',color='b',linestyles='--')
		plt.hlines(signal['signal_down'],'20170101','20181231',color='b',linestyles='--')
		plt.hlines(signal['stopout_up'],'20170101','20181231',color='r',linestyles='--')
		plt.hlines(signal['stopout_down'],'20170101','20181231',color='r',linestyles='--')
		plt.title(f'{x}/{y}')
		fig.savefig(f'C://Users/user/Desktop/Anjestan/images/{x}_{y}.png')
		print()

principle=1000000
tax=0

backtest_data=pd.DataFrame({(i,j):test_data[sector][i]/test_data[sector][j] for sector in qualify for i,j in qualify[sector]})
signal={(i,j):0 for sector in qualify for i,j in qualify[sector]}
for i in backtest_data.index:
	data=backtest_data.loc[i,:]
	for j in data: