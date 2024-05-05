import pandas as pd
import numpy as np
import sqlite3
from sqlite3 import connect
import streamlit as st
from PIL import Image

image = Image.open('Logo-KDT-JU.webp')
st.image(image)

conn= connect('ecsel_database.db')

# Read data from the different tables
df_project = pd.read_sql('SELECT * FROM PROJECTS', conn)
df_participants = pd.read_sql('SELECT * FROM PARTICIPANTS', conn)
df_countries = pd.read_sql('SELECT * FROM COUNTRIES', conn)

# Merge data from different tables into df2
df2 = pd.read_sql('''
    SELECT p.*, pj.*, c.Country 
    FROM PARTICIPANTS AS p, PROJECTS AS pj, COUNTRIES AS c
    WHERE p.projectID=pj.projectID AND p.country=c.Acronym
''', conn)
df2 = df2.rename(columns={'country': 'Acronym'})
df2 = df2.rename(columns={'acronym': 'organization_acronym'})

st.title('Partner Search App')

country_list = df2['Country'].unique()  # Selecting the unique country names list
country_acronyms = {'Belgium': 'BE', 'Bulgaria': 'BG', 'Czechia': 'CZ', 'Denmark': 'DK', 'Germany':
                    'DE', 'Estonia': 'EE', 'Ireland': 'IE', 'Greece': 'EL', 'Spain': 'ES', 'France': 'FR',
                    'Croatia': 'HR', 'Italy': 'IT', 'Cyprus': 'CY', 'Latvia': 'LV', 'Lithuania': 'LT',
                    'Luxembourg': 'LU', 'Hungary': 'HU', 'Malta': 'MT', 'Netherlands': 'NL', 'Austria': 'AT',
                    'Poland': 'PL', 'Portugal': 'PT', 'Romania': 'RO', 'Slovenia': 'SI', 'Slovakia': 'SK',
                    'Finland': 'FI', 'Sweden': 'SE'}
countnames = st.multiselect('Choose Countries', sorted(country_acronyms.keys()))  # Input by the user of the name of the country or countries
years = st.multiselect('Choose Years', sorted(df_project['year'].unique()))
activity_types = st.multiselect('Choose Activity Types', sorted(df_participants['activityType'].unique()))

def countries_to_acronyms(countnames):  # Defining a function
    acronyms = []
    for countname in countnames:
        if countname in country_acronyms.keys():
            acronyms.append(country_acronyms[countname])
    return acronyms

acronym_c = countries_to_acronyms(countnames)
st.write('The selected countries are:', acronym_c)  # Calling the function to display the acronyms

st.text('Table of Partner Contributions per Country')
def display_dataframe(df2, acronyms):
    df2 = df2[df2['Acronym'].isin(acronyms)]
    df2_part = df2.groupby(['name','shortName', 'activityType', 'organizationURL']).agg({'ecContribution':['sum']})
    df2_part = df2_part.reset_index()
    df2_part = df2_part.sort_values(by=('ecContribution', 'sum'), ascending=False)  # Sorting by sum of ecContribution in descending order
    return df2_part

participants = display_dataframe(df2, acronym_c)
st.write(participants, index=False)

# Part 4: generate a new project dataframe with project coordinators from the selected countries and order it in ascending order by 'shortName'
st.text('Table of Project Coordinators per Country')
df2 = df2[df2['Acronym'].isin(acronym_c)]
df2['Coordinator'] = (df2['role'] == 'coordinator') * 1
pjc_df = df2.groupby(['name','shortName', 'activityType', 'organizationURL']).agg({'Coordinator': ['sum']})
pjc_df = pjc_df.reset_index()
pjc_df = pjc_df.sort_values('shortName')  # Ordered by shortName

st.write(pjc_df, index=False)

st.text('Download the Data Below')
# The system shall save the generated datasets (participants, and project coordinators) in CSV files. (There should be 2 buttons to download data).
@st.cache  # IMPORTANT: Cache the conversion to prevent computation on every rerun
def convert_participants(participants):
    return participants.to_csv().encode('utf-8')
st.download_button(label="Participants CSV", data=convert_participants(participants), file_name='participants.csv', mime='text/csv')
@st.cache  # IMPORTANT: Cache the conversion to prevent computation on every rerun
def convert_projectcoordinators(pjc_df):
    return pjc_df.to_csv().encode('utf-8')
st.download_button(label="Project Coordinators CSV", data=convert_projectcoordinators(pjc_df), file_name='projectcoordinators.csv', mime='text/csv')

"""Optional"""

import streamlit as st

# Display a graph with evolution of received grants of the partners in a country according to their activityType.
st.text('Graph with evolution of received grants per partners according to activityType')

# Filter data for the selected countries, years, and activity types
df_country = df2[df2['Acronym'].isin(acronym_c) & df2['year'].isin(years) & df2['activityType'].isin(activity_types)]

# Group by activityType and sum the contributions
df_grants = df_country.groupby('activityType')['ecContribution'].sum().reset_index()

# Plot the graph with customized y-axis range
st.bar_chart(df_grants.set_index('activityType'))

conn.close()
















 

