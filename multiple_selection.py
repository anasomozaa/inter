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
years = st.multiselect('Choose Years', sorted(df_project['year'].unique()), format_func=lambda x: str(x))  # Format years as strings for display
activity_types = st.multiselect('Choose Activity Types', sorted(df2['activityType'].unique()))

def countries_to_acronyms(countnames):  # Defining a function
    acronyms = []
    for countname in countnames:
        if countname in country_acronyms.keys():
            acronyms.append(country_acronyms[countname])
    return acronyms

acronym_c = countries_to_acronyms(countnames)
selected_years = [str(year) for year in years]  # Convert selected years to strings for display
selected_activity_types = [f"'{activity_type}'" for activity_type in activity_types]  # Format activity types for display

st.write('The selected countries are:', ', '.join(acronym_c))  # Display selected countries as a string
st.write('The selected years are:', ', '.join(selected_years))  # Display selected years as a string
st.write('The selected activity types are:', ', '.join(selected_activity_types))  # Display selected activity types as a string

st.text('Table of Partner Contributions per Country')
def display_dataframe(df2, acronyms, activity_types):
    df2 = df2[df2['Acronym'].isin(acronyms) & df2['activityType'].isin(activity_types)]
    df2_part = df2.groupby(['name','shortName', 'activityType', 'organizationURL']).agg({'ecContribution':['sum']})
    df2_part = df2_part.reset_index()
    df2_part = df2_part.sort_values(by=('ecContribution', 'sum'), ascending=False)  # Sorting by sum of ecContribution in descending order
    return df2_part

participants = display_dataframe(df2, acronym_c, activity_types)
st.write(participants, index=False)

# Part 4: generate a new project dataframe with project coordinators from the selected countries and order it in ascending order by 'shortName'
st.text('Table of Project Coordinators per Country')
df2 = df2[df2['Acronym'].isin(acronym_c) & df2['activityType'].isin(activity_types)]
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


# Optional 


for country in countnames:
    st.subheader(f"Total Contributions Evolution for {country}")
    selected_country_data = df2[df2['Country'] == country]
    selected_country_data['year'] = selected_country_data['year'].astype(int) #so that the year is displayed as 2023 not 2,2023
    selected_country_data['year'] = selected_country_data['year'].astype(str)

    # Group by year and activity type to get total contributions
    contributions_by_year_activity = selected_country_data.groupby(['year', 'activityType'])['ecContribution'].sum().unstack()

    # Plotting
    st.line_chart(contributions_by_year_activity)


conn.close()
 

