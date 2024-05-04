import pandas as pd
import numpy as np
import sqlite3
from sqlite3 import connect
import streamlit as st
from PIL import Image
import matplotlib.pyplot as plt
import seaborn as sns

# Load the image
image = Image.open('Logo-KDT-JU.webp')
st.image(image)

# Connect to the SQLite database
conn = connect('ecsel_database.db')

# Read data from the different tables
df_project = pd.read_sql('SELECT * FROM PROJECTS', conn)
df_participants = pd.read_sql('SELECT * FROM PARTICIPANTS', conn)
df_countries = pd.read_sql('SELECT * FROM COUNTRIES', conn)

# Merge data from different tables into df2
df2 = pd.read_sql('''
    SELECT p.*, pj.*, c.Country 
    FROM PARTICIPANTS AS p, PROJECTS AS pj, COUNTRIES AS c
    WHERE p.projectID = pj.projectID AND p.country = c.Acronym
''', conn)
df2 = df2.rename(columns={'country': 'Acronym'})
df2 = df2.rename(columns={'acronym': 'organization_acronym'})

st.title('Partner Search App')

# Select multiple countries
country_acronyms = {'Belgium': 'BE', 'Bulgaria': 'BG', 'Czechia': 'CZ', 'Denmark': 'DK', 'Germany': 'DE', 
                    'Estonia': 'EE', 'Ireland': 'IE', 'Greece': 'EL', 'Spain': 'ES', 'France': 'FR', 
                    'Croatia': 'HR', 'Italy': 'IT', 'Cyprus': 'CY', 'Latvia': 'LV', 'Lithuania': 'LT',
                    'Luxembourg': 'LU', 'Hungary': 'HU', 'Malta': 'MT', 'Netherlands': 'NL', 'Austria': 'AT', 
                    'Poland': 'PL', 'Portugal': 'PT', 'Romania': 'RO', 'Slovenia': 'SI', 'Slovakia': 'SK', 
                    'Finland': 'FI', 'Sweden': 'SE'}

selected_countries = st.multiselect('Choose Country(s)', sorted(country_acronyms.keys()))

# Select multiple years
selected_years = st.multiselect('Choose Year(s)', df_project['year'].unique())

# Select multiple activity types
selected_activity_types = st.multiselect('Choose Activity Type(s)', df_project['activityType'].unique())

# Filter data based on selected criteria
filtered_df = df2[df2['Acronym'].isin(selected_countries) &
                  df2['year'].isin(selected_years) &
                  df2['activityType'].isin(selected_activity_types)]

# Display filtered data
st.write(filtered_df)

# Display a table of Partner Contributions per Country
st.text('Table of Partner Contributions per Country')
def display_dataframe(df, country_acronym):
    df_filtered = df[df['Acronym'] == country_acronym]
    df_part = df_filtered.groupby(['name', 'shortName', 'activityType', 'organizationURL']).agg({'ecContribution': ['sum']})
    df_part = df_part.reset_index()
    df_part = df_part.sort_values(by=('ecContribution', 'sum'), ascending=False) 
    return df_part

if selected_countries:
    for country in selected_countries:
        participants = display_dataframe(df2, country)
        st.write(participants, index=False)

# Generate a new project dataframe with project coordinators from the selected country and order it in ascending order by 'shortName'
st.text('Table of Project Coordinators per Country')
def display_project_coordinators(df, country_acronym):
    df_filtered = df[df['Acronym'] == country_acronym]
    df_filtered['Coordinator'] = (df_filtered['role'] == 'coordinator') * 1
    pjc_df = df_filtered.groupby(['name', 'shortName', 'activityType', 'organizationURL']).agg({'Coordinator': ['sum']})
    pjc_df = pjc_df.reset_index()
    pjc_df = pjc_df.sort_values('shortName')
    return pjc_df

if selected_countries:
    for country in selected_countries:
        pjc_df = display_project_coordinators(df2, country)
        st.write(pjc_df, index=False)

# Download the generated datasets (participants and project coordinators) as CSV files
st.text('Download the Data Below')

@st.cache
def convert_participants(participants):
    return participants.to_csv().encode('utf-8')

if selected_countries:
    for country in selected_countries:
        participants = display_dataframe(df2, country)
        st.download_button(label=f"Participants CSV - {country}", data=convert_participants(participants), 
                           file_name=f'participants_{country}.csv', mime='text/csv')

@st.cache
def convert_project_coordinators(pjc_df):
    return pjc_df.to_csv().encode('utf-8')

if selected_countries:
    for country in selected_countries:
        pjc_df = display_project_coordinators(df2, country)
        st.download_button(label=f"Project Coordinators CSV - {country}", data=convert_project_coordinators(pjc_df), 
                           file_name=f'project_coordinators_{country}.csv', mime='text/csv')

# Display a graph with evolution of received grants of the partners in a country according to their activityType
st.text('Graph with evolution of received grants per partners according to activityType')
if selected_countries:
    for country in selected_countries:
        df_country = df2[df2['Acronym'] == country] 
        df_grants = df_country.groupby('activityType')['ecContribution'].sum().reset_index() 
        plt.figure(figsize=(10,6))
        sns.barplot(x='activityType', y='ecContribution', data=df_grants)
        plt.title(f'Evolution of Received Grants by Activity Type in {country}')
        plt.xlabel('Activity Type')
        plt.ylabel('Received Grants')
        st.pyplot(plt)

# Close the SQLite connection
conn.close()

