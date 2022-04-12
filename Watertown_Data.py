import numpy as np
import pandas as pd
import streamlit as st
import base64
import altair as alt
import datetime

st.set_page_config(layout="wide")

#Functions
def create_onedrive_directdownload (onedrive_link):
    data_bytes64 = base64.b64encode(bytes(onedrive_link, 'utf-8'))
    data_bytes64_String = data_bytes64.decode('utf-8').replace('/','_').replace('+','-').rstrip("=")
    resultUrl = f"https://api.onedrive.com/v1.0/shares/u!{data_bytes64_String}/root/content"
    return resultUrl

@st.cache
def load(url):
    df = pd.read_csv(create_onedrive_directdownload(url))
    #df.drop('Unnamed: 0')
    df['Time'] = pd.to_datetime(df['Time'], errors='coerce')
    return df

def set_default():
    if not (ymd_range[0]):
        ymd_range[0] = datetime.date(2019, 1, 1)
    elif not (ymd_range[1]):
        ymd_range[1] = datetime.date(2023, 12, 31)

#Main Code
df = load("https://1drv.ms/u/s!AnhaxtVMqKpxgoYMvc0XlCSMCQcHYQ?e=NGl6vK")

from streamlit_option_menu import option_menu

with st.sidebar:
    selected = option_menu("Main Menu", ["Home", 'Settings'],
        icons=['house', 'gear'], menu_icon="cast", default_index=1)

st.header("Watertown Water Network")

if st.checkbox("Show Raw Data"):
    with st.spinner('Writing in progress...'):
        st.write(df)
    st.success('Done!')

col1, col2 = st.columns((2, 2))

ymd_range = [datetime.date(2019, 1, 1), datetime.date(2019, 1, 2)]

#with col1:
#if selected == 'Settings':
with st.sidebar:
    #if(st.button('Settings')):
    st.subheader('Choose date range of data:')
    ymd_range_temp = st.date_input("Start Day - End Day", [datetime.date(2019, 1, 1), datetime.date(2019, 1, 2)], min_value=datetime.date(2019, 1, 1), max_value=datetime.date(2023, 12, 31), on_change= set_default())
    if (len(ymd_range_temp) == 2):
        ymd_range = ymd_range_temp
    else:
        st.error('Error: You must choose an end date. Otherwise, the default value for the end date is used for filtering the data.')
    col1, col2 = st.columns((1, 1))

    with col1:
        hms_start_day = st.time_input("Time of Start Day", datetime.time(8, 45))

    with col2:
        hms_end_day = st.time_input("Time of End Day", datetime.time(8, 30))

    st.subheader('Select variables of charts:')
    option_1 = st.checkbox('Water level')
    water_level_unit = st.selectbox("Choose unit:", ["meter", "foot"])
    #if option_1:

    option_2 = st.checkbox('Flow')
    flow_unit = st.selectbox("Choose unit:",
                             ["gallon per minute", "cubic meter per second", "cubic foot per second",
                              "acre-inches per hour",
                              "acre feet per day"])
    #if option_2:

    option_3 = st.checkbox('Pressure')
    pressure_unit = st.selectbox("Choose unit:", ["pressure per Square Inch (psi)", "meter"])
    #if option_3:

    start_datetime = datetime.datetime.combine(ymd_range[0], hms_start_day)
    end_datetime = datetime.datetime.combine(ymd_range[1], hms_end_day)

    start_datetime_str = start_datetime.strftime("%m/%d/%Y, %H:%M:%S")
    end_datetime_str = end_datetime.strftime("%m/%d/%Y, %H:%M:%S")
    # st.success('Selected time span starts from `%s` until `%s`' %(start_datetime_str, end_datetime_str))

    # st.write('Selected time span starts from ', start_datetime, 'until', end_datetime)
    mask = ((df['Time'] > np.datetime64(start_datetime)) & (df['Time'] <= np.datetime64(end_datetime)))
    df = df.loc[mask]

if option_1:
    df1 = df[['Time', 'Bald Hill Tank_Level_ft', 'Scovill Tank_Level_ft']].melt('Time', var_name='Tank_Name', value_name='Water_Level')
    # brush (click and drag) for selecting specific values on chart
    #brush = alt.selection_interval(encodings=["x"])

    # selection to allow highlight of genre when click on legend
    selection = alt.selection_multi(fields=['Tank_Name'], bind='legend')

    # scatterplot showing the correlation between two features for all genres
    scatterplot = alt.Chart(df1).mark_line().encode(
        alt.X('Time', scale=alt.Scale(zero=False)),
        alt.Y('Water_Level', scale=alt.Scale(zero=False)),
        alt.Color('Tank_Name:N', legend=alt.Legend(title="Tank Name")),
        opacity=alt.condition(selection, alt.value(1), alt.value(0.2)),
        tooltip=['Time', 'Tank_Name', 'Water_Level']
    ).properties(
        width=650, height=350
    ).interactive().add_selection(
        selection
    )
    st.write(scatterplot)

# Create Radio Buttons
#start_date = st.date_input('Start date', default_start_day)
#end_date = st.date_input('End date', default_end_day)
#if start_date < end_date:
 #   st.success('Start date: ` %s`\n\nEnd date:` %s`' % (start_date, end_date))
#else:
   # st.error('Error: End date must fall after start date.')

#pd.to_datetime(df['Date'])

#df = pd.DataFrame(
    #columns=['lat', 'lon'])

#st.map(df)