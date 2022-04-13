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
    water_level_unit = st.selectbox("Choose unit:", ["foot", "meter"])
    #if option_1:

    option_2 = st.checkbox('Flow')
    flow_unit = st.selectbox("Choose unit:",
                             ["gallon per minute", "cubic meter per second", "cubic foot per second",
                              "acre-inch per hour",
                              "acre-foot per day"])
    #if option_2:

    option_3 = st.checkbox('Pressure')
    pressure_unit = st.selectbox("Choose unit:", ["pressure per square inch", "meter of head"])
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
    df1 = df.rename(columns={'Bald Hill Tank_Level_ft' : 'Bald Hill Tank',
                            'Scovill Tank_Level_ft' : 'Scovill Tank'})

    df1 = df1[['Time', 'Bald Hill Tank', 'Scovill Tank']].melt('Time', var_name='Tank_Name', value_name='Water_Level')
    # brush (click and drag) for selecting specific values on chart
    if water_level_unit == 'meter':
        unit_1 = 'm'
        df1[['Water_Level']] = df1[['Water_Level']] * 0.3048
    else:
        unit_1 = 'ft'

    df1 = df1.rename(columns={'Water_Level' : f'Water Level ({unit_1})'})


    column_name_1 = f"Water Level ({unit_1})"

    # selection to allow highlight of genre when click on legend
    selection = alt.selection_multi(fields=['Tank_Name'], bind='legend')

    # scatterplot showing the correlation between two features for all genres
    Water_Level_Line_Chart = alt.Chart(df1).mark_line().encode(
        alt.X('Time', scale=alt.Scale(zero=False)),
        alt.Y(column_name_1, scale=alt.Scale(zero=False)),
        alt.Color('Tank_Name:N', legend=alt.Legend(title="Asset")),
        opacity=alt.condition(selection, alt.value(1), alt.value(0.2)),
        tooltip=['Time', 'Tank_Name', column_name_1]
    ).properties(
        width=650, height=350
    ).interactive().add_selection(
        selection
    )

    st.write(Water_Level_Line_Chart)

if option_2:

    df2 = df.rename(columns={'Bald Hill Tank_Net_Flow_Out_gpm' : 'Bald Hill Tank',
                            'PRV-1_Flow_gpm': 'PRV-1',
                            'PRV-2_Flow_gpm': 'PRV-2',
                            'PRV-3_Flow_gpm': 'PRV-3',
                            'PRV-4_Flow_gpm': 'PRV-4',
                            'PRV-5_Flow_gpm': 'PRV-5',
                            'PRV-6_Flow_gpm': 'PRV-6',
                            'PRV-7_Flow_gpm': 'PRV-7',
                            'School_Flow_gpm': 'School',
                            'Well PMP-1_Flow_gpm': 'Well PMP-1',
                            'Well PMP-2_Flow_gpm': 'Well PMP-2',
                            'Well PMP-3_Flow_gpm': 'Well PMP-3',
                            'Well Station Discharge_Flow_gpm' : 'Well Station',
                            'WTP PMP-1_Flow_gpm': 'WTP PMP-1',
                            'WTP PMP-2_Flow_gpm': 'WTP PMP-2',
                            'WTP PMP-3_Flow_gpm': 'WTP PMP-3',
                            'WTP Station Discharge_Flow_gpm' : 'WTP Station'})

    df2 = df2[['Time', 'Bald Hill Tank', 'PRV-1',
              'PRV-2', 'PRV-3', 'PRV-4', 'PRV-5',
              'PRV-6', 'PRV-7', 'Well PMP-1',
              'Well PMP-2', 'Well PMP-3', 'Well Station',
              'WTP PMP-1', 'WTP PMP-2', 'WTP PMP-3',
              'WTP Station', 'School']].melt('Time', var_name='Asset', value_name='Flow')

    if flow_unit == 'gallon per minute':
        unit_2 = 'gpm'
    elif flow_unit == 'cubic meter per second':
        unit_2 = 'm^3/sec'
        df2[['Flow']] = df2[['Flow']] * 0.0000630902
    elif flow_unit == 'cubic foot per second':
        unit_2 = 'ft^3/sec'
        df2[['Flow']] = df2[['Flow']] * 0.0022280093
    elif flow_unit == 'acre-foot per day':
        unit_2 = 'ac*ft/day'
        df2[['Flow']] = df2[['Flow']] * 0.0044191742
    elif flow_unit == 'acre-inch per hour':
        unit_2 = 'ac*in/hour'
        df2[['Flow']] = df2[['Flow']] * 0.0026536140977965

    df2 = df2.rename(columns={'Flow' : f'Flow ({unit_2})'})


    column_name_2 = f"Flow ({unit_2})"

    # selection to allow highlight of genre when click on legend
    selection = alt.selection_multi(fields=['Asset'], bind='legend')

    # scatterplot showing the correlation between two features for all genres
    Flow_Line_Chart = alt.Chart(df2).mark_line().encode(
        x=alt.X('Time', scale=alt.Scale(zero=False)),
        y=alt.Y(column_name_2, scale=alt.Scale(zero=False)),
        color=alt.Color('Asset:N', legend=alt.Legend(title="Asset")),
        opacity=alt.condition(selection, alt.value(1), alt.value(0.2)),
        tooltip=['Time', 'Asset', column_name_2]
    ).properties(
        width=650, height=350
    ).interactive().add_selection(
        selection
    )

    st.write(Flow_Line_Chart)

if option_3:
    df3 = df.rename(columns={'PRV-1_FromPressure_psi' : 'PRV-1 (from)',
                             'PRV-2_FromPressure_psi': 'PRV-2 (from)',
                             'PRV-3_FromPressure_psi': 'PRV-3 (from)',
                             'PRV-4_FromPressure_psi': 'PRV-4 (from)',
                             'PRV-5_FromPressure_psi': 'PRV-5 (from)',
                             'PRV-6_FromPressure_psi': 'PRV-6 (from)',
                             'PRV-7_FromPressure_psi': 'PRV-7 (from)',
                             'PRV-1_ToPressure_psi': 'PRV-1 (to)',
                             'PRV-2_ToPressure_psi': 'PRV-2 (to)',
                             'PRV-3_ToPressure_psi': 'PRV-3 (to)',
                             'PRV-4_ToPressure_psi': 'PRV-4 (to)',
                             'PRV-5_ToPressure_psi': 'PRV-5 (to)',
                             'PRV-6_ToPressure_psi': 'PRV-6 (to)',
                             'PRV-7_ToPressure_psi': 'PRV-7 (to)',
                             'Well Discharge_Pressure_psi' : 'Well (discharge)',
                             'Well Suction_Pressure_psi': 'Well (suction)',
                             'Well PMP-1_DischargePressure_psi' : 'Well PMP-1 (discharge)',
                             'Well PMP-2_DischargePressure_psi': 'Well PMP-2 (discharge)',
                             'Well PMP-3_DischargePressure_psi': 'Well PMP-3 (discharge)',
                             'Well PMP-1_SuctionPressure_psi': 'Well PMP-1 (suction)',
                             'Well PMP-2_SuctionPressure_psi': 'Well PMP-2 (suction)',
                             'Well PMP-3_SuctionPressure_psi': 'Well PMP-3 (suction)',
                             'WTP Discharge_Pressure_psi': 'WTP (discharge)',
                             'WTP Suction_Pressure_psi': 'WTP (suction)',
                             'WTP PMP-1_SuctionPressure_psi' : 'WTP PMP-1 (suction)',
                             'WTP PMP-2_SuctionPressure_psi': 'WTP PMP-2 (suction)',
                             'WTP PMP-3_SuctionPressure_psi': 'WTP PMP-3 (suction)'
                             })

    df3 = df3[['Time', 'PRV-1 (from)', 'PRV-2 (from)', 'PRV-3 (from)',
              'PRV-4 (from)', 'PRV-5 (from)', 'PRV-6 (from)', 'PRV-7 (from)',
              'PRV-1 (to)', 'PRV-2 (to)', 'PRV-3 (to)','PRV-4 (to)',
              'PRV-5 (to)', 'PRV-6 (to)', 'PRV-7 (to)', 'Well (discharge)', 'Well (suction)',
              'Well PMP-1 (discharge)', 'Well PMP-1 (suction)',
              'Well PMP-2 (discharge)', 'Well PMP-2 (suction)',
              'Well PMP-3 (discharge)', 'Well PMP-3 (suction)',
              'WTP (discharge)', 'WTP (suction)', 'WTP PMP-1 (suction)', 'WTP PMP-2 (suction)',
              'WTP PMP-3 (suction)']].melt('Time', var_name='Asset', value_name='Pressure')


    if pressure_unit == 'pressure per square inch':
        unit_3 = 'psi'
    elif pressure_unit == 'meter of head':
        unit_3 = 'm'
        df3[['Pressure']] = df3[['Pressure']] * 0.70324961490205

    df3 = df3.rename(columns={'Pressure' : f'Pressure ({unit_3})'})


    column_name_3 = f"Pressure ({unit_3})"

    # selection to allow highlight of genre when click on legend
    selection = alt.selection_multi(fields=['Asset'], bind='legend')

    # scatterplot showing the correlation between two features for all genres
    Pressure_Line_Chart = alt.Chart(df3).mark_line().encode(
        alt.X('Time', scale=alt.Scale(zero=False)),
        alt.Y(column_name_3, scale=alt.Scale(zero=False)),
        alt.Color('Asset:N', legend=alt.Legend(title="Asset")),
        opacity=alt.condition(selection, alt.value(1), alt.value(0.2)),
        tooltip=['Time', 'Asset', column_name_3]
    ).properties(
        width=650, height=350
    ).interactive().add_selection(
        selection
    )
    st.write(Pressure_Line_Chart)

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