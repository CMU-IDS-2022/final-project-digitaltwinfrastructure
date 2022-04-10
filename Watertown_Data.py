import numpy as np
import pandas as pd
import streamlit as st
import base64
import altair as alt
import datetime

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

#Main Code

st.header("Watertown Water Network")
df = load("https://1drv.ms/u/s!AnhaxtVMqKpxgoYMvc0XlCSMCQcHYQ?e=NGl6vK")

if st.checkbox("Show Raw Data"):
    with st.spinner('Writing in progress...'):
        st.write(df)
    st.success('Done!')

st.title('Choose date range of data: ')

col1, col2 = st.columns((1, 1))

ymd_range = [datetime.date(2019, 1, 1), datetime.date(2020, 1, 1)]

def set_default():
    if not (ymd_range[0]):
        ymd_range[0] = datetime.date(2019, 1, 1)
    elif not (ymd_range[1]):
        ymd_range[1] = datetime.date(2023, 12, 31)

with col1:
    ymd_range_temp = st.date_input("Start Day - End Day", [datetime.date(2019, 1, 1), datetime.date(2020, 1, 1)], min_value=datetime.date(2019, 1, 1), max_value=datetime.date(2023, 12, 31), on_change= set_default())

if (len(ymd_range_temp) == 2):
    ymd_range = ymd_range_temp
else:
    st.error('Error: You must choose an end date. Otherwise, the default value for the end date is used for filtering the data.')

with col2:
    hms_start_day = st.time_input("Time of Start Day", datetime.time(8, 45))
    hms_end_day = st.time_input("Time of End Day", datetime.time(8, 30))

start_datetime = datetime.datetime.combine(ymd_range[0], hms_start_day)
end_datetime = datetime.datetime.combine(ymd_range[1], hms_end_day)

start_datetime_str = start_datetime.strftime("%m/%d/%Y, %H:%M:%S")
end_datetime_str = end_datetime.strftime("%m/%d/%Y, %H:%M:%S")
st.success('Selected time span starts from `%s` until `%s`' %(start_datetime_str, end_datetime_str))

#st.write('Selected time span starts from ', start_datetime, 'until', end_datetime)
mask = ((df['Time'] > np.datetime64(start_datetime)) & (df['Time'] <= np.datetime64(end_datetime)))
df = df.loc[mask]

chart = alt.Chart(df).mark_line(tooltip=True).encode(
    y=alt.Y('Bald Hill Tank_Level_ft',
            axis=alt.Axis(title='Bald Hill Tank_Level_ft'),
            scale=alt.Scale(domain=(60, 100))),
    x=alt.X('Time',
            axis=alt.Axis(title='Date/Time'),
            scale=alt.Scale(zero=False),
            ),
    tooltip=['Bald Hill Tank_Level_ft', 'Time']
).properties(
    width=710,
    height=400,
    title=""
).interactive()

st.write(chart)

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