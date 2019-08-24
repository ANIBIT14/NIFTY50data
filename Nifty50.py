'''
Important:
    This script extracts data for Nifty 50 from date 1-01-2018 to 31-12-2018. The dates can be changed for extracton.
    The data is stored finally in df as in it's raw form and df_stat a copy of df is uded for stats and plotting.
    This script can be modified furthe for better executin time in many ways one of which is to,
    perform data cleansing on a final combined df : data set, rather then everytime data is extracted in a interval of 99 values.
    Current execution time is very large. Everyone is invited to change and modify the code and make it better.
    I will also keep making changes whenever I have time.
    
    The rolling mean is applied on the open price columns of the dataframe.
    It can be applied on every column in a similar manner.
    
    Author - Aniruddha_Agarwal
'''


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import style
from sklearn.linear_model import LinearRegression
import seaborn as sns

style.use ('ggplot')
from urllib.request import urlopen
import requests
from bs4 import BeautifulSoup 
import sys
from io import StringIO, BytesIO
import re
from datetime import date
import dateutil
from dateutil.parser import parse

#df_org = pd.read_csv('Learn.csv')

u_link = 'http://www.nseindia.com/products/dynaContent/equities/indices/historicalindices.jsp?indexType=%s&fromDate=%s&toDate=%s'


# function that extract data from webssite


def data_extraction(st,en):
    indi = 'Nifty 50'
    
    start1= st
    end1 = en



    url = u_link%(indi.upper().replace(' ','%20'), start1, end1)
    #url = "https://www.nseindia.com/products/dynaContent/equities/indices/historicalindices.jsp?indexType=NIFTY%2050&fromDate=01-01-2018&toDate=01-05-2018"
    agent = {"User-Agent":'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'} 
    page = requests.get(url, headers = agent) 
    dat = BeautifulSoup(page.content, "lxml")
    
    #the url can give dataset for max exact 99 days
    
    rows = dat.find_all('tr')
    list_rows = []
    for row in rows:
        cols=row.find_all('td')
        str_cells = str(cols)
        clean = re.compile('<.*?>')
        clean2 = (re.sub(clean, '',str_cells))
        list_rows.append(clean2)
        
    
    type(list_rows)
    df_new = pd.DataFrame(list_rows)
    
    df_new = df_new.drop([0,1])
    df_new.reset_index(inplace = True)
    df_new = df_new.drop(len(df_new) - 1)
    df_new = df_new.drop(['index'], axis= 1 )
    
    df_mod = df_new[0].str.split(',', expand=True)
    df_mod[0] = df_mod[0].str.strip('[')
    
    col_labels = dat.find_all('th')
    all_header = []
    col_str = str(col_labels)
    cleantext = BeautifulSoup(col_str, "lxml").get_text()
    all_header.append(cleantext)
    df_temp = pd.DataFrame(all_header)
    
    df_temp1 = df_temp[0].str.split(',', expand = True)
    
    df_temp1 = df_temp1.drop([0,1], axis = 1)
    df_temp1.columns = range(df_temp1.shape[1])
    
    
    df_mod = pd.concat([df_temp1, df_mod])
    
    df_mod = df_mod.rename(columns = df_mod.iloc[0])
    df_mod = df_mod.drop(df_mod.index[0])
    
    df_mod.rename(columns = {'[Date': 'Date'}, inplace = True)
    df_mod.rename(columns = {' Turnover (  Cr)]' : 'Turnover (Rs. Cr)'}, inplace = True)
    
    df_mod['Turnover (Rs. Cr)'] = df_mod['Turnover (Rs. Cr)'].str.strip(']')
    return (df_mod)

# extraction function ends

#

df = pd.DataFrame()

#dates here taken for the last complete year 2018, they can be modified and be taken as input from user

start = input('Start date in format mm-dd-yyyy ')
end = input('end date in format mm-dd-yyyy ')


date_start = parse(start)
date_end = parse(end)


diff = date_end.date().toordinal() - date_start.date().toordinal() 

x = diff // 100
y = diff % 100

e_d = date_start.date()
s_d = date.fromordinal(e_d.toordinal())


for i in range(1,x + 1):
    
   
   
    e_d = date.fromordinal(e_d.toordinal() + 100)
    
    # data extraction function is called here
    df = pd.concat([df,data_extraction(s_d.strftime("%d-%m-%Y"),e_d.strftime("%d-%m-%Y" ))], ignore_index = True)
    
    s_d = date.fromordinal(e_d.toordinal() + 1) 
   
s_d = date.fromordinal(e_d.toordinal() + 1)
e_d = date.fromordinal(e_d.toordinal() + y)
df = pd.concat([df,data_extraction(s_d.strftime("%d-%m-%Y"),e_d.strftime("%d-%m-%Y" ))], ignore_index = True)

# cleaning data more
df.columns = df.columns.str.strip(' ')

#modifying data further to achieve it's original form

df["Open"]= df["Open"].astype("float")
df["High"]= df["High"].astype("float")
df["Low"]= df["Low"].astype("float")
df["Close"]= df["Close"].astype("float")
df["Shares Traded"]= df["Shares Traded"].astype("int64")
df["Turnover (Rs. Cr)"]= df["Turnover (Rs. Cr)"].astype("float")


#df.info()

# For storing in system uncomment the next line
df.to_csv('Nifty50.csv')

# making a copy dataset for applying statisitcs and making further changes
'''df_stat = df.copy()

df_stat['Date'] = pd.to_datetime(df_stat['Date'])

df_stat.set_index('Date', inplace = True)
df_stat= df_stat.drop(['Shares Traded'],1)
df_stat= df_stat.drop(['Turnover (Rs. Cr)'],1)


#plotting graphs for open price data column

fig = plt.figure()
ax1 = fig.add_subplot(111)
ax1.set_xlabel('Date')
ax1.set_ylabel('Opening Price')

ax1.set_title('Original Plot')
ax1.plot(df_stat['Open'])

fig1 = plt.figure()
#calculating rolling mean for open price column
df_stat['Rolling_Mean'] = df_stat['Open'].rolling(window = 10, min_periods = 1).mean()

ax2 = fig1.add_subplot(111)
ax2.plot( df_stat['Rolling_Mean'] )
ax2.set_xlabel('Date')
ax2.set_title('Rolling_Mean')
ax2.set_ylabel('Smoothed Opening Price')

fig_together = plt.figure()
ax3 = fig_together.add_subplot(111)

ax3.plot(df_stat['Rolling_Mean'], color = (0,0,0), linewidth = 4, alpha = .9, label = 'Smoothed')
ax3.plot(df_stat['Open'],color = (1,0,0), label = 'Original')
ax3.set_title('Original and Smoothed Open Price')
ax3.set_xlabel('Date')
ax3.set_ylabel('Open Price')
ax3.legend(loc = 'lower right')
'''
