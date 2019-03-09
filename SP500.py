import pandas_datareader.data as pdr
import pandas as pd
import json
import os

class SP500_Info:
	def __init__(self,path='C://Users/user/Desktop/Anjestan/sp500_info.json'):
		self.file_path=path
		self.update()
	
	def update(self):
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

		file=open(self.file_path,'w')
		json.dump(sort_data,file)
		file.close()
		print('The Information of SP500 have been update')

	def load(self,exclude=None):
		file=open(self.file_path,'r')
		js=json.load(file)
		if exclude != None:
			assert type(exclude) is list
			num=0
			for sector in js:
				com=js[sector]
				for symbol in exclude:
					if symbol in com.keys():
						del js[sector][symbol]
				num+=len(js[sector])
			else:
				print(f'EXCLUDE {len(exclude)} symbol. Remain {num} Symbol')	
		return js

class Get_Data:
	def __init__(self,start,end,path='C://Users/user/Desktop/Anjestan/data'):
		self.start=start
		self.end=end
		self.path=path
		self.sp500_info=SP500_Info().load()
		self.quandl_key='AjyqXY_BTjNUxmDjPh_w'
		self.get_data()

	def get_data(self):
		sector=self.sp500_info.keys()
		error_list=[]
		times=0
		for i in sector:
			com=self.sp500_info[i]
			folder=os.path.join(self.path,i)
			if not os.path.exists(folder):
				os.mkdir(folder)
			for symbol in com.keys():
				try:
					data=pdr.get_data_yahoo(symbol,start=self.start,end=self.end)
				except:
					error_list.append(symbol)
					continue
				data.sort_index(inplace=True)
				file_path=f'{os.path.join(folder,symbol)}.csv'
				data.to_csv(file_path)
				times+=1
			else:
				print(f'Sector:{i} have been download')
		else:
			print(f'There are {times} data have been download!')
			print('='*60)
			for k in error_list:
				print(k,end='|')