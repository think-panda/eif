import matplotlib.pyplot as plt  
import pandas as pd
import streamlit as st
import requests
from pandas import json_normalize

st.set_page_config(layout="wide")

#Load & cache data. Clear cache periodically - 5mins - so that any changes to the Airtable data source will be pulled in
@st.cache(ttl=60*5)
def load_data():
	url = "https://v1.nocodeapi.com/essiesee/airtable/uYDVvsGUSfXBMszU?tableName=ServicesInterventions&view="
	params = {}
	r = requests.get(url = url, params = params)
	result = r.json()
	data = json_normalize(result['records'])
	#remove fields. prefix from imported records
	data.columns = data.columns.str.replace(r'fields.', '')
	data = data[['Minimum age in months', 'Maximum age in months', 'Intervention Name', 'Primary Domain/Need','Universal/Targeted/Specialist']]
	data = data.dropna(how='any', subset=['Minimum age in months', 'Maximum age in months'])
	return data
df = load_data()

df=df.sort_values(['Primary Domain/Need','Minimum age in months']) 
size=df['Intervention Name'].count()

#add new column for colour coding of domains/needs and make black by default
df['Colour']='Black'

#Dictionary to map domains to colours
lookupDict = {'Vulnerable families': 'Red', 
	'Additional learning needs': 'Blue',
	'Physical development and health': 'Green',
	'Social and emotional': 'Brown',
	'Cognitive development/Education': 'Grey',	
	'Speech, language and communication': 'Violet'}

mask = df['Primary Domain/Need'].isin(lookupDict.keys())
df.loc[mask, 'Colour'] = df.loc[mask, 'Primary Domain/Need'].map(lookupDict)

st.title("Torfaen Early Years Provision")

#Identify unique domain names and an options for select all
services = pd.DataFrame(df['Primary Domain/Need'].unique())
services.loc[-1] = ['Show All']  # adding a row
services.index = services.index + 1  # shifting index
services = services.sort_index()  # sorting by index

#Identify unique values for Universal/Targeted/Specialist and add option for select all
unitarspec = pd.DataFrame(df['Universal/Targeted/Specialist'].unique())
unitarspec.loc[-1] = ['Show All']  # adding a row
unitarspec.index = unitarspec.index + 1  # shifting index
unitarspec = unitarspec.sort_index()  # sorting by index

#Select a Service
servicearea = st.selectbox('Select a Domain/Need:', services)
unitarspec = st.selectbox('Select whether Universal, Targeted or Specialist:', unitarspec)

st.image('key.png')

#Subset dataframe based on values selected in dropdowns
if (servicearea != 'Show All') & (unitarspec != 'Show All'):	
	df = df[(df['Primary Domain/Need']==servicearea) & (df['Universal/Targeted/Specialist']==unitarspec)]
	size=df['Intervention Name'].count()
if (servicearea != 'Show All') & (unitarspec == 'Show All'):	
	df = df[(df['Primary Domain/Need']==servicearea)]
	size=df['Intervention Name'].count()
if (servicearea == 'Show All') & (unitarspec != 'Show All'):	
	df = df[(df['Universal/Targeted/Specialist']==unitarspec)]
	size=df['Intervention Name'].count()

#Plot lollipop chart, using fivethirtyeight theme        
plt.style.use('fivethirtyeight')
fig, ax = plt.subplots()
figure = plt.gcf()
figure.set_size_inches(8,(size/2))
plt.hlines(y=df['Intervention Name'], xmin=df['Minimum age in months'], xmax=df['Maximum age in months'], color=df['Colour'], alpha=0.6)
plt.scatter(df['Minimum age in months'], df['Intervention Name'], color='black', alpha=1)
plt.scatter(df['Maximum age in months'], df['Intervention Name'], color='black', alpha=1)

plt.xlabel('Age (Months)')
plt.ylabel('Intervention Name')

st.pyplot(figure)	
