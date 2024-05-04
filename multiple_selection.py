import pandas as pd
import sqlite3
from sqlite3 import connect
import streamlit as st
from PIL import Image

image = Image.open('Logo-KDT-JU.webp')
st.image(image)

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

# Display a graph with evolution of received grants per partners according to activityType
if selected_countries:
    for country in selected_countries:
        st.text(f'Graph with evolution of received grants per partners according to activityType for {country}')
        # Filter data for the selected country
        df_country = df2[df2['Acronym'] == country]
        # Group by activityType and sum the contributions
        df_grants = df_country.groupby('activityType')['ecContribution'].sum().reset_index()
        # Plot the graph
        st.bar_chart(df_grants.set_index('activityType'))

conn.close()
