# -*- coding: utf-8 -*-
"""Ana_Silvia.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1izB-rvrWPP7Fow6V848fbJbpK7IyQJn1
"""

import pandas as pd
import numpy as np
import sqlite3
from sqlite3 import connect
import streamlit as st
from PIL import Image


image = Image.open('Logo-KDT-JU.webp')
st.image(image)

conn= connect('ecsel_database.db')

#read data from the different tables
df_project= pd.read_sql ('SELECT * FROM PROJECTS', conn)
df_participants= pd.read_sql ('SELECT * FROM PARTICIPANTS', conn)
df_countries= pd.read_sql ('SELECT * FROM COUNTRIES', conn)

#merge data from diferent tables into df2
df2= pd.read_sql ('''SELECT p.*, pj.*, c.Country FROM PARTICIPANTS AS p, PROJECTS AS pj, COUNTRIES AS c
WHERE p.projectID=pj.projectID AND p.country=c.Acronym''', conn)
df2=df2.rename(columns={'country':'Acronym'})
df2=df2.rename(columns={'acronym':'organization_acronym'})

st.title('Partner Search App')

country_list = df2['Country'] #selecting the country names list
country_acronyms = {'Belgium': 'BE', 'Bulgaria': 'BG', 'Czechia': 'CZ', 'Denmark': 'DK', 'Germany':
'DE', 'Estonia': 'EE', 'Ireland': 'IE','Greece': 'EL', 'Spain': 'ES', 'France': 'FR', 'Croatia':
'HR', 'Italy': 'IT', 'Cyprus': 'CY', 'Latvia': 'LV', 'Lithuania': 'LT','Luxembourg': 'LU',
'Hungary': 'HU', 'Malta': 'MT', 'Netherlands': 'NL', 'Austria': 'AT', 'Poland': 'PL', 'Portugal':
'PT','Romania': 'RO', 'Slovenia': 'SI', 'Slovakia': 'SK', 'Finland': 'FI', 'Sweden': 'SE'}
countname = st.selectbox('Choose a Country', sorted(country_acronyms.keys())) #input by the user of the name of the country or countries
##countname = input('Choose a Country') #input by the user of the name of the country
def country_to_acronym(countname): #defining a function
  found = False #setting parameter = False, when True it is when the acronym is found.
  while found == False: #while acronym is not found
    if countname in country_acronyms.keys(): #if the country name is in the key of the dictionary
      value = country_acronyms[countname] #getting the acronym associated with the key (name of the country)
      found = True #set parameter to trye
    else:
      st.write("Not a country on the list, try again: ") #if the country doesn't exist in the database it will ask the user again to try again
      ##print("Not a country on the list, try again: ") #if the country doesn't exist in the database it will ask the user again to try again
      found = False
    return(value)

acronym_c = country_to_acronym(countname)
st.write('The selected country is:', acronym_c) #calling the function to display to display the acronym

st.text('Table of Partner Contributions per Country')
### @st.cache
def display_dataframe(df2, acronym_c):
    df2 = df2[df2['Acronym'] == acronym_c]
    df2_part = df2.groupby(['name','shortName', 'activityType', 'organizationURL']).agg({'ecContribution':['sum']})
    df2_part = df2_part.reset_index()
    df2_part = df2_part.sort_values(by=('ecContribution', 'sum'), ascending= False) #sorting by sum of ecContribution in descending order
    return(df2_part)

participants = display_dataframe(df2,acronym_c)
st.write(participants, index=False)

#part4: generate a new project dataframe with project coordinators from the selected country and order it in ascending order by 'shortName'
st.text('Table of Project Coordinators per Country')
df2 = df2[df2['Acronym'] == acronym_c]
#filter project coordinators: 
df2['Coordinator'] = (df2['role']=='coordinator')*1
pjc_df = df2.groupby(['name','shortName', 'activityType', 'organizationURL']).agg({'Coordinator': ['sum']})
#pjc_df = pjc_df[pjc_df[('Coordinator', 'sum')] > 0] #only visualize those which have been coordinators or not?
pjc_df = pjc_df.reset_index()
pjc_df = pjc_df.sort_values('shortName') #ordered by shortName

st.write(pjc_df, index=False)

st.text('Download the Data Below')
#The system shall save the generated datasets (participants, and project coordinators) in anCSV file. (There should be 2 buttons to download data).
@st.cache      # IMPORTANT: Cache the conversion to prevent computation on every rerun
def convert_participants(participants):
     return participants.to_csv().encode('utf-8')
st.download_button(label="Participants CSV",data=convert_participants(participants), file_name='participants.csv', mime='text/csv',)
@st.cache      # IMPORTANT: Cache the conversion to prevent computation on every rerun
def convert_projectcoordinators(pjc_df):
     return pjc_df.to_csv().encode('utf-8')
st.download_button(label="Project Coordinators CSV",data=convert_projectcoordinators(pjc_df), file_name='projectcoordinators.csv', mime='text/csv',)

# Display a graph with the evolution of received grants of the partners in a country according to their activityType.
st.title(f'Evolution of received grants per partners according to Activity Type - {acronym_c}')

df_country = df2[df2['Acronym'] == acronym_c]
# Convert year to whole numbers by first converting into an integer and then into a string 
df_country['year'] = df_country['year'].astype(int)
df_country['year'] = df_country['year'].astype(str)
# Group by activityType and year, then sum the contributions
df_grants = df_country.groupby(['activityType', 'year'])['ecContribution'].sum().reset_index()
# Pivot the data
pivot_grants = df_grants.pivot(index='year', columns='activityType', values='ecContribution')
st.bar_chart(pivot_grants)
option = st.selectbox('Choose to see the specific activity', df2['activityType'].unique())
st.bar_chart(pivot_grants[option])

conn.close()
