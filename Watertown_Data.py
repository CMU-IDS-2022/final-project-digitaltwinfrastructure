import numpy as np
import pandas as pd
import streamlit as st
import base64
import altair as alt
import datetime
import pytz
from streamlit_option_menu import option_menu

from sklearn.cluster import KMeans
from sklearn.preprocessing import MinMaxScaler
import sklearn.metrics as metrics
from sklearn import tree
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error
from sklearn.metrics import mean_squared_error
from sklearn.metrics import confusion_matrix
from sklearn.metrics import classification_report
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score, explained_variance_score

#Change the layout of screen
st.set_page_config(layout="wide")

# Functions
# This function makes it possible to download the data from onedrive by creating a downloadable link
def create_onedrive_directdownload (onedrive_link):
    data_bytes64 = base64.b64encode(bytes(onedrive_link, 'utf-8'))
    data_bytes64_String = data_bytes64.decode('utf-8').replace('/','_').replace('+','-').rstrip("=")
    resultUrl = f"https://api.onedrive.com/v1.0/shares/u!{data_bytes64_String}/root/content"
    return resultUrl

# Cache is used to enhance speed. So the data is downloaded once even when the code is executed multiple times.
# Load function reads the csv file from onedrive
@st.cache
def load(url):
    df = pd.read_csv(create_onedrive_directdownload(url))
    return df

def load_sensor(url):
    df = pd.read_csv(create_onedrive_directdownload(url))
    df_org = df
    # Dataframe is processed here. But later I will replace the data file with the processed one.
    # Time colomn is changed to datetime format.
    df['Time'] = pd.to_datetime(df['Time'], errors='coerce')

    # Dummy colomns are generated to be used for sorting based on time.
    df['year_sort'] = df['Time'].dt.year
    df['month_sort'] = df['Time'].dt.month
    df['day_sort'] = df['Time'].dt.day
    df['hour_sort'] = df['Time'].dt.hour
    df['min_sort'] = df['Time'].dt.minute
    df = df.sort_values(by=['year_sort', 'month_sort', 'day_sort', 'hour_sort', 'min_sort'])
    # Removing dummy colomns
    df = df.drop(columns=['year_sort', 'month_sort', 'day_sort', 'hour_sort', 'min_sort'])
    #df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    df = df.reset_index(drop=True)
    df = df.drop(columns=['WTP PMP-1_PumpStatus','Well PMP-3_PumpStatus','Well PMP-1_PumpStatus', 'Well PMP-1_RelativeSpeed', 'Well PMP-1_WirePower_kW','Well PMP-2_PumpStatus', 'Well PMP-2_RelativeSpeed', 'Well PMP-2_WirePower_kW', 'Well PMP-3_RelativeSpeed', 'Well PMP-3_WirePower_kW', 'WTP PMP-1_RelativeSpeed', 'WTP PMP-1_WirePower_kW', 'WTP PMP-2_PumpStatus', 'WTP PMP-2_RelativeSpeed', 'WTP PMP-2_WirePower_kW', 'WTP PMP-3_PumpStatus', 'WTP PMP-3_RelativeSpeed', 'WTP PMP-3_WirePower_kW'])

    return df

@st.cache
def load_usage(url):
    dfu = pd.read_csv(create_onedrive_directdownload(url))
    dfu = dfu.rename(columns={'ID': 'Customer ID', 'Billing month': 'Time', 'Value': 'Water usage (kgal)'})
    dfu['Time'] = pd.to_datetime(dfu['Time'], errors='coerce')
    dfu = dfu.drop(['Units'], axis=1)
    mask_d1 = (dfu['Water usage (kgal)'] < 250)
    dfu = dfu.loc[mask_d1]
    return dfu
@st.cache
def load_pipe(url):
    dfu = pd.read_csv(create_onedrive_directdownload(url))
    return dfu

# Used to specify end date in case of empty end date input from user.
def set_default():
    if not (ymd_range[0]):
        # minimum
        ymd_range[0] = datetime.date(2019, 1, 1)
    elif not (ymd_range[1]):
        # maximum
        ymd_range[1] = datetime.date(2023, 12, 31)

#Main Code
# load water network data
df = load_sensor("https://1drv.ms/u/s!AnhaxtVMqKpxgoYMvc0XlCSMCQcHYQ?e=NGl6vK")
df_org = df.loc[:, ~df.columns.str.contains('^Unnamed')]
df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
df_pipe = load_pipe("https://1drv.ms/u/s!AnhaxtVMqKpxgok-XtdjTGpjIUIW3w?e=6swM00")
df_pipe_orig = df_pipe.drop("FID", axis = 1)

dfu = load_usage("https://1drv.ms/u/s!AnhaxtVMqKpxgok8LpetXE7Hfb1www?e=JQu4W0")
df_75 = load("https://1drv.ms/u/s!AnhaxtVMqKpxgok6rtmFtgqn1vUt_Q?e=el633O")
df_25 = load("https://1drv.ms/u/s!AnhaxtVMqKpxgok7oN74-f1eTi8BFw?e=yei0ZH")

numeric_month = {
                    "January": "1",
                    "February": "2",
                    "March": "3",
                    "April": "4",
                    "May": "5",
                    "June": "6",
                    "July": "7",
                    "August":"8",
                    "September": "9",
                    "October": "10",
                    "November":"11",
                    "December":"12"
                }

Reverse_numeric_month = {
                    1: "January",
                    2: "February",
                    3: "March",
                    4: "April",
                    5: "May",
                    6: "June",
                    7: "July",
                    8: "August",
                    9: "September",
                    10: "October",
                    11: "November",
                    12: "December"
                }

# define the main menu with two options ["Data Exploration", 'Water Network Management']
with st.sidebar:
    selected = option_menu("Main Menu", ["Water Network Exploration", "Pipe Data Exploration", "Water Usage Exploration", "Pipe-Break Prediction", "Water Network Management"],
               icons=['bi bi-bounding-box-circles', 'bi bi-bezier', 'droplet-half', 'bi bi-exclamation-triangle-fill',
                      'bi bi-columns-gap', 'person-lines-fill'], menu_icon="cast",
               default_index=0)

#if "Data Exploration" is selected in the main menu do the following
############################################################WATER NETWORK EXPLORATION##################################################

if selected == "Water Network Exploration":
    st.title(selected)

    # The default value of date range
    ymd_range = [datetime.date(2019, 1, 1), datetime.date(2019, 1, 2)]
    col1, col2 = st.columns((2, 2))
    st.header("Data Tables")
    if st.checkbox("Show Raw Data"):
        with st.spinner('Writing in progress...'):
            st.write(df)
        #st.success('Done!')

    with st.sidebar:
        st.header(':gear: Settings')

        st.subheader('Choose the time span:')
        # Date selector with default values and min and max values specified.
        ymd_range_temp = st.date_input("Start day - End day", [datetime.date(2019, 1, 1), datetime.date(2019, 1, 2)], min_value=datetime.date(2019, 1, 1), max_value=datetime.date(2023, 12, 31), on_change= set_default())

        if (len(ymd_range_temp) == 2):
            ymd_range = ymd_range_temp
        else:
            # if user only selected starting date write this message.
            st.error('Error: You must choose an end date. Otherwise, the default value for the end date is used for filtering the data.')

        # divide sidebar to two columns to write end and start next to each other
        col1, col2 = st.columns((1, 1))
        with col1:
            # take time of the start day as input
            hms_start_day = st.time_input("Time of the start day", datetime.time(8, 45))
        with col2:
            # take time of the end day as input
            hms_end_day = st.time_input("Time of the end day", datetime.time(8, 30))

        st.subheader('Choose units:') # could be flow, pressure and water level

        water_level_unit = st.selectbox("Water level:", ["foot", "meter"])

        flow_unit = st.selectbox("Flow:",
                                 ["gallon per minute", "cubic meter per second", "cubic foot per second",
                                  "acre-inch per hour",
                                  "acre-foot per day"])

        pressure_unit = st.selectbox("Pressure:", ["pressure per square inch", "meter of head"])

        # combine date and time of day to be able to mask dataset
        start_datetime = datetime.datetime.combine(ymd_range[0], hms_start_day)
        end_datetime = datetime.datetime.combine(ymd_range[1], hms_end_day)

        # filter the data based on selected time range
        mask = ((df['Time'] >= np.datetime64(start_datetime)) & (df['Time'] <= np.datetime64(end_datetime)))
        df = df.loc[mask]

    if st.checkbox("Show filtered data:"):
        with st.spinner('Writing in progress...'):
            st.write(df)

    st.header("Charts")
    selected_options = st.multiselect('Select charts ', ['Water level', 'Flow', 'Pressure'], default = ['Water level', 'Flow', 'Pressure'])
    selected_options.append("None")

    # must be used to avoid time shifting is charts
    df['Time'] = df['Time'].dt.tz_localize('EST')

    if ((selected_options[0]) == "Water level"): #option_1: #water level
        del selected_options[0]

        # rename the columns to the name that must be shown in the legend of chart (only name of the asset should remain)
        # save the result in dummy dataset called df1
        df1 = df.rename(columns={'Bald Hill Tank_Level_ft': 'Bald Hill Tank',
                                'Scovill Tank_Level_ft':'Scovill Tank'})

        # reshape the data so that the values of different assets are all in the same column.
         # we need this reformatting for plotting based on color.
        df1 = df1[['Time', 'Bald Hill Tank', 'Scovill Tank']].melt('Time', var_name='Asset', value_name='Water_Level')

        # change values based on selected unit.
        if water_level_unit == 'meter':
            unit_1 = 'm'
            df1[['Water_Level']] = df1[['Water_Level']] * 0.3048
        else:
            unit_1 = 'ft'

        # rename the column so that it contains the selected unit. This name is shown on the y axis
        column_name_1 = f"Water Level ({unit_1})"
        df1 = df1.rename(columns={'Water_Level': column_name_1})

        # selection to allow highlight when click on legend
        selection = alt.selection_multi(fields=['Asset'], bind='legend')

        # plot the chart
        Water_Level_Line_Chart = alt.Chart(df1).mark_line().encode(
            alt.X('Time', scale=alt.Scale(zero=False)),
            alt.Y(column_name_1, scale=alt.Scale(zero=False)),
            alt.Color('Asset:N', legend=alt.Legend(title="Asset")),
            opacity=alt.condition(selection, alt.value(1), alt.value(0.1)),
            tooltip=['Time', 'Asset', column_name_1]
        ).properties(
            width=700, height=370
        ).interactive().add_selection(
            selection
        )

        # Create bar plot that responds to selection based on legend.
        # bar show mean values and standard deviation in selected time span.
        bars = (
            alt.Chart(df1).mark_bar().encode(
                y=alt.Y("Asset",axis=alt.Axis(labels=False)),
                color=alt.Color("Asset:O"),
                x=alt.X(f"mean({column_name_1})", scale=alt.Scale(zero = False)),
            ).transform_filter(selection)
        )

        # stdv of data
        error_bars = alt.Chart().mark_errorbar(extent='ci').encode(
            x=alt.X(f"mean({column_name_1})", scale=alt.Scale(zero=False)),
            y="Asset"
        )

        bars = alt.layer(bars, error_bars, data=df1).transform_filter(selection)

        # plot charts next to each other horizontally
        chart = alt.hconcat(Water_Level_Line_Chart, bars).properties(
            title="Click on the legend to show/hide lines:")
        st.subheader("Water level charts")
        st.write(chart)


    if ((selected_options[0]) == "Flow"): # if option_2:Flow
        del selected_options[0]
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
            opacity=alt.condition(selection, alt.value(1), alt.value(0.1)),
            tooltip=['Time', 'Asset', column_name_2]
        ).properties(
            width=700, height=370
        ).interactive().add_selection(
            selection
        )
        bars = (
            alt.Chart(df2).mark_bar().encode(
                y=alt.Y("Asset", axis=alt.Axis(labels=False)),
                color=alt.Color("Asset:O"),
                x=alt.X(f"mean({column_name_2})", scale=alt.Scale(zero=False)),
            ).transform_filter(selection)
        )

        error_bars = alt.Chart().mark_errorbar(extent='ci').encode(
            x=alt.X(f"mean({column_name_2})", scale=alt.Scale(zero=False)),
            y="Asset"
        )

        bars = alt.layer(bars, error_bars, data=df2).transform_filter(selection)


        # Concatenate bar plot and scatter plot vertically
        chart = alt.hconcat(Flow_Line_Chart, bars).properties(
            title="Click on the legend to show/hide lines:"
        )
        st.subheader("Flow charts")
        st.write(chart)

    if (selected_options[0]) == "Pressure":  # if option_3:: #Pressure
        del selected_options[0]

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
        brush = alt.selection_interval(encodings=['x'])
        #.add_selection(
        #    brush
        #).transform_filter(brush)
        # scatterplot showing the correlation between two features for all genres
        Pressure_Line_Chart = alt.Chart(df3).mark_line().encode(
            x=alt.X('Time', scale=alt.Scale(zero=False)),
            y=alt.Y(column_name_3, scale=alt.Scale(zero=False)),
            color=alt.Color('Asset:N', legend=alt.Legend(title="Asset")),
            opacity=alt.condition(selection,alt.value(1), alt.value(0.1)),
            tooltip=['Time', 'Asset', column_name_3]
        ).properties(
            width=700, height=370
        ).add_selection(
            selection
        )

        bars = (
            alt.Chart(df3).mark_bar().encode(
                y=alt.Y("Asset",axis=alt.Axis(labels=False)),
                color=alt.Color("Asset:O"),
                x=alt.X(f"mean({column_name_3})", scale=alt.Scale(zero=False)),
            ).transform_filter(selection)
        )

        # stdv of data
        error_bars = alt.Chart().mark_errorbar(extent='ci').encode(
            x=alt.X(f"mean({column_name_3})", scale=alt.Scale(zero=False)),
            y="Asset"
        )

        bars = alt.layer(bars, error_bars, data=df3).transform_filter(selection)

        # plot charts next to each other horizontally
        chart = alt.hconcat(Pressure_Line_Chart, bars).properties(
            title="Click on the legend to show/hide lines:"
        )
        st.subheader("Pressure charts")
        st.write(chart)
        #st.write(Pressure_Line_Chart)


###############################################################################################

    st.header("Distributions")
    selected_options_dist = ["None","None","None"]
    selected_options_dist_temp = st.multiselect('Select distribution variables ', ['Water level', 'Flow', 'Pressure'], default =  ['Water level', 'Flow', 'Pressure'])
    j = 0
    for i in selected_options_dist_temp:
        selected_options_dist[j] = i
        j = j + 1

    dfd = df_org
    # must be used to avoid time shifting is charts
    dfd['Time'] = dfd['Time'].dt.tz_localize('EST')

    if ((selected_options_dist[0] == "Water level") | (selected_options_dist[1] == "Water level") | (selected_options_dist[2] == "Water level")): #option_1: #water level
        st.subheader("Water Level")
        dfd1 = dfd.rename(columns={'Bald Hill Tank_Level_ft': 'Bald Hill Tank',
                                   'Scovill Tank_Level_ft': 'Scovill Tank'})

        # reshape the data so that the values of different assets are all in the same column.
        # we need this reformatting for plotting based on color.
        dfd1 = dfd1[['Time', 'Bald Hill Tank', 'Scovill Tank']].melt('Time', var_name='Asset', value_name='Water_Level')

        # change values based on selected unit.
        if water_level_unit == 'meter':
            unit_1 = 'm'
            dfd1[['Water_Level']] = dfd1[['Water_Level']] * 0.3048
        else:
            unit_1 = 'ft'

        # rename the column so that it contains the selected unit. This name is shown on the y axis
        column_name_1 = f"Water Level ({unit_1})"
        dfd1 = dfd1.rename(columns={'Water_Level': column_name_1})

        #del selected_options_dist[0]
        #Scatter and histogram
        colL, colM, colR = st.columns([1, 1, 1])

        with colL:
            selected_assets = ["0", "0"]
            selected_assets_temp = st.multiselect('Select assets:', ['Bald Hill Tank', 'Scovill Tank'], default = 'Bald Hill Tank')
            j = 0
            for i in selected_assets_temp:
                selected_assets[j] = i
                j = j + 1

        with colM:
            selected_years = ["0", "0", "0"]
            selected_years_temp = st.multiselect('Select years:', ['2019', '2020', '2021'], default = "2019")
            j = 0
            for i in selected_years_temp:
                selected_years[j] = i
                j = j + 1
            dfd1['year'] = dfd1['Time'].dt.year
            mask_d1 = ((dfd1['year'].astype(int) == int(selected_years[0])) | (dfd1['year'] == int(selected_years[1])) | (dfd1['year'] == int(selected_years[2])))
            dfd1 = dfd1.loc[mask_d1]

        with colR:
            selected_months = ["0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0"]
            selected_months_temp = st.multiselect('Select months:', ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'], default = ['January', 'February', 'March'])
            dfd1['month'] = dfd1['Time'].dt.month
            if len(selected_months_temp) != 0:
                j = 0
                for i in selected_months_temp:
                    selected_months[j] = numeric_month[i]
                    j = j + 1
                mask_h = ((dfd1['month'].astype(int) == int(selected_months[0])) | (
                            dfd1['month'].astype(int) == int(selected_months[1])) | (
                            dfd1['month'].astype(int) == int(selected_months[2])) | (
                            dfd1['month'].astype(int) == int(selected_months[3])) | (
                            dfd1['month'].astype(int) == int(selected_months[4])) | (
                            dfd1['month'].astype(int) == int(selected_months[5])) | (
                            dfd1['month'].astype(int) == int(selected_months[6])) | (
                            dfd1['month'].astype(int) == int(selected_months[7])) | (
                            dfd1['month'].astype(int) == int(selected_months[8])) | (
                            dfd1['month'].astype(int) == int(selected_months[9])) | (
                            dfd1['month'].astype(int) == int(selected_months[10])) | (
                            dfd1['month'].astype(int) == int(selected_months[11]))
                          )
                dfd1 = dfd1.loc[mask_h]


        selection_x = st.radio("Breakdown based on:", ["year", "month", "none"])
        if selection_x == "none":
            dfd1['none'] = 1

        # interval selection in the scatter plot
        dfd1_copy = dfd1
        for i in range(len(selected_assets_temp)):
            pts = alt.selection(type="interval", encodings=["x"])
            dfd1 = dfd1_copy
            mask_d1 = (dfd1['Asset'] == selected_assets[i])
            dfd1 = dfd1.loc[mask_d1]
            # left panel: scatter plot
            points = alt.Chart(dfd1).mark_point(filled=False).encode(
                x=alt.X('dayhoursminutes(Time):O', scale=alt.Scale(zero=False)),
                y=alt.Y(column_name_1, scale=alt.Scale(zero=False)),
                color = alt.Color(f"{selection_x}:N", legend=alt.Legend(title=f"{selection_x}")),
                opacity=alt.condition(pts, alt.value(1), alt.value(0.1))
            ).add_selection(pts).properties(
                width=650,
                height=350
            )
            st.subheader(f"{selected_assets[i]}")
            #st.write(points)
            # right panel: histogram
            mag = (alt.Chart(dfd1).mark_bar().encode(
                x=alt.X(column_name_1, bin=True),
                y=alt.Y('count()', stack= True),
                #opacity=alt.condition(pts, alt.value(1), alt.value(0)),
                color=alt.Color(f"{selection_x}:N", legend=alt.Legend(title=f"{selection_x}")),

            ).properties(
                width=300,
                height=300
            ).transform_filter(
                pts
            ))


            #st.write(mag)
            # build the chart:
            scatter = alt.hconcat(points,mag).transform_bin(f"{column_name_1} binned",field=column_name_1,bin=alt.Bin(maxbins=20))
            st.write(scatter)
    if ((selected_options_dist[0] == "Flow") | (selected_options_dist[1] == "Flow") | (
            selected_options_dist[2] == "Flow")):
        st.subheader("Flow")
        dfd1 = dfd.rename(columns={'Bald Hill Tank_Net_Flow_Out_gpm': 'Bald Hill Tank',
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
                                 'Well Station Discharge_Flow_gpm': 'Well Station',
                                 'WTP PMP-1_Flow_gpm': 'WTP PMP-1',
                                 'WTP PMP-2_Flow_gpm': 'WTP PMP-2',
                                 'WTP PMP-3_Flow_gpm': 'WTP PMP-3',
                                 'WTP Station Discharge_Flow_gpm': 'WTP Station'})

        dfd1 = dfd1[['Time', 'Bald Hill Tank', 'PRV-1',
                   'PRV-2', 'PRV-3', 'PRV-4', 'PRV-5',
                   'PRV-6', 'PRV-7', 'Well PMP-1',
                   'Well PMP-2', 'Well PMP-3', 'Well Station',
                   'WTP PMP-1', 'WTP PMP-2', 'WTP PMP-3',
                   'WTP Station', 'School']].melt('Time', var_name='Asset', value_name='Flow')

        if flow_unit == 'gallon per minute':
            unit_2 = 'gpm'
        elif flow_unit == 'cubic meter per second':
            unit_2 = 'm^3/sec'
            dfd1[['Flow']] = dfd1[['Flow']] * 0.0000630902
        elif flow_unit == 'cubic foot per second':
            unit_2 = 'ft^3/sec'
            dfd1[['Flow']] = dfd1[['Flow']] * 0.0022280093
        elif flow_unit == 'acre-foot per day':
            unit_2 = 'ac*ft/day'
            dfd1[['Flow']] = dfd1[['Flow']] * 0.0044191742
        elif flow_unit == 'acre-inch per hour':
            unit_2 = 'ac*in/hour'
            dfd1[['Flow']] = dfd1[['Flow']] * 0.0026536140977965

        dfd1 = dfd1.rename(columns={'Flow': f'Flow ({unit_2})'})

        column_name_1 = f"Flow ({unit_2})"

        dfd1 = dfd1.rename(columns={'Flow': column_name_1})

        # del selected_options_dist[0]
        # Scatter and histogram
        colL, colM, colR = st.columns([1, 1, 1])

        with colL:
            selected_assets = ["0", "0", "0","0","0","0", "0", "0", "0","0","0","0","0","0","0","0","0"]
            selected_assets_temp = st.multiselect('Select assets:', ['Bald Hill Tank', 'PRV-1','PRV-2', 'PRV-3', 'PRV-4', 'PRV-5','PRV-6', 'PRV-7', 'Well PMP-1','Well PMP-2', 'Well PMP-3', 'Well Station','WTP PMP-1', 'WTP PMP-2', 'WTP PMP-3','WTP Station', 'School'],
                                                  default='Bald Hill Tank')
            j = 0
            for i in selected_assets_temp:
                selected_assets[j] = i
                j = j + 1

        with colM:
            selected_years = ["0", "0", "0"]
            selected_years_temp = st.multiselect('Select years :', ['2019', '2020', '2021'], default="2019")
            j = 0
            for i in selected_years_temp:
                selected_years[j] = i
                j = j + 1
            dfd1['year'] = dfd1['Time'].dt.year
            mask_d1 = ((dfd1['year'].astype(int) == int(selected_years[0])) | (
                        dfd1['year'] == int(selected_years[1])) | (dfd1['year'] == int(selected_years[2])))
            dfd1 = dfd1.loc[mask_d1]

        with colR:
            selected_months = ["0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0"]
            selected_months_temp = st.multiselect('Select months :',
                                                  ['January', 'February', 'March', 'April', 'May', 'June', 'July',
                                                   'August', 'September', 'October', 'November', 'December'],default = ['January', 'February', 'March'])
            dfd1['month'] = dfd1['Time'].dt.month
            if len(selected_months_temp) != 0:
                j = 0
                for i in selected_months_temp:
                    selected_months[j] = numeric_month[i]
                    j = j + 1
                mask_h = ((dfd1['month'].astype(int) == int(selected_months[0])) | (
                        dfd1['month'].astype(int) == int(selected_months[1])) | (
                                  dfd1['month'].astype(int) == int(selected_months[2])) | (
                                  dfd1['month'].astype(int) == int(selected_months[3])) | (
                                  dfd1['month'].astype(int) == int(selected_months[4])) | (
                                  dfd1['month'].astype(int) == int(selected_months[5])) | (
                                  dfd1['month'].astype(int) == int(selected_months[6])) | (
                                  dfd1['month'].astype(int) == int(selected_months[7])) | (
                                  dfd1['month'].astype(int) == int(selected_months[8])) | (
                                  dfd1['month'].astype(int) == int(selected_months[9])) | (
                                  dfd1['month'].astype(int) == int(selected_months[10])) | (
                                  dfd1['month'].astype(int) == int(selected_months[11]))
                          )
                dfd1 = dfd1.loc[mask_h]

        selection_x = st.radio("Breakdown based on :", ["year", "month", "none"])
        if selection_x == "none":
            dfd1['none'] = 1

        # interval selection in the scatter plot
        dfd1_copy = dfd1
        for i in range(len(selected_assets_temp)):
            pts = alt.selection(type="interval", encodings=["x"])
            dfd1 = dfd1_copy
            mask_d1 = (dfd1['Asset'] == selected_assets[i])
            dfd1 = dfd1.loc[mask_d1]
            # left panel: scatter plot
            points = alt.Chart(dfd1).mark_point(filled=False).encode(
                x=alt.X('dayhoursminutes(Time):O', scale=alt.Scale(zero=False)),
                y=alt.Y(column_name_1, scale=alt.Scale(zero=False)),
                color=alt.Color(f"{selection_x}:N", legend=alt.Legend(title=f"{selection_x}")),
                opacity=alt.condition(pts, alt.value(1), alt.value(0.1))
            ).add_selection(pts).properties(
                width=650,
                height=350
            )
            st.subheader(f"{selected_assets[i]}")
            # st.write(points)
            # right panel: histogram
            mag = (alt.Chart(dfd1).mark_bar().encode(
                x=alt.X(column_name_1, bin=True),
                y=alt.Y('count()', stack=True),
                # opacity=alt.condition(pts, alt.value(1), alt.value(0)),
                color=alt.Color(f"{selection_x}:N", legend=alt.Legend(title=f"{selection_x}")),

            ).properties(
                width=300,
                height=300
            ).transform_filter(
                pts
            ))

            # st.write(mag)
            # build the chart:
            scatter = alt.hconcat(points, mag).transform_bin(f"{column_name_1} binned", field=column_name_1,
                                                             bin=alt.Bin(maxbins=20))
            st.write(scatter)

    if ((selected_options_dist[0] == "Pressure") | (selected_options_dist[1] == "Pressure") | (
            selected_options_dist[2] == "Pressure")):
        st.subheader("Pressure")
        dfd1 = dfd.rename(columns={'PRV-1_FromPressure_psi': 'PRV-1 (from)',
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
                                 'Well Discharge_Pressure_psi': 'Well (discharge)',
                                 'Well Suction_Pressure_psi': 'Well (suction)',
                                 'Well PMP-1_DischargePressure_psi': 'Well PMP-1 (discharge)',
                                 'Well PMP-2_DischargePressure_psi': 'Well PMP-2 (discharge)',
                                 'Well PMP-3_DischargePressure_psi': 'Well PMP-3 (discharge)',
                                 'Well PMP-1_SuctionPressure_psi': 'Well PMP-1 (suction)',
                                 'Well PMP-2_SuctionPressure_psi': 'Well PMP-2 (suction)',
                                 'Well PMP-3_SuctionPressure_psi': 'Well PMP-3 (suction)',
                                 'WTP Discharge_Pressure_psi': 'WTP (discharge)',
                                 'WTP Suction_Pressure_psi': 'WTP (suction)',
                                 'WTP PMP-1_SuctionPressure_psi': 'WTP PMP-1 (suction)',
                                 'WTP PMP-2_SuctionPressure_psi': 'WTP PMP-2 (suction)',
                                 'WTP PMP-3_SuctionPressure_psi': 'WTP PMP-3 (suction)'
                                 })

        dfd1 = dfd1[['Time', 'PRV-1 (from)', 'PRV-2 (from)', 'PRV-3 (from)',
                   'PRV-4 (from)', 'PRV-5 (from)', 'PRV-6 (from)', 'PRV-7 (from)',
                   'PRV-1 (to)', 'PRV-2 (to)', 'PRV-3 (to)', 'PRV-4 (to)',
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
            df3[['Pressure']] = dfd1[['Pressure']] * 0.70324961490205

        dfd1 = dfd1.rename(columns={'Pressure': f'Pressure ({unit_3})'})

        column_name_1 = f"Pressure ({unit_3})"


        dfd1 = dfd1.rename(columns={'Flow': column_name_1})

        # del selected_options_dist[0]
        # Scatter and histogram
        colL, colM, colR = st.columns([1, 1, 1])

        with colL:
            selected_assets = ["0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0","0", "0", "0", "0", "0", "0", "0", "0", "0", "0"]
            selected_assets_temp = st.multiselect('Select assets',
                                                  ['PRV-1 (from)', 'PRV-2 (from)', 'PRV-3 (from)',
                                                   'PRV-4 (from)', 'PRV-5 (from)', 'PRV-6 (from)', 'PRV-7 (from)',
                                                   'PRV-1 (to)', 'PRV-2 (to)', 'PRV-3 (to)', 'PRV-4 (to)',
                                                   'PRV-5 (to)', 'PRV-6 (to)', 'PRV-7 (to)', 'Well (discharge)',
                                                   'Well (suction)',
                                                   'Well PMP-1 (discharge)', 'Well PMP-1 (suction)',
                                                   'Well PMP-2 (discharge)', 'Well PMP-2 (suction)',
                                                   'Well PMP-3 (discharge)', 'Well PMP-3 (suction)',
                                                   'WTP (discharge)', 'WTP (suction)', 'WTP PMP-1 (suction)',
                                                   'WTP PMP-2 (suction)',
                                                   'WTP PMP-3 (suction)'],
                                                  default='PRV-1 (from)')

            j = 0
            for i in selected_assets_temp:
                selected_assets[j] = i
                j = j + 1

        with colM:
            selected_years = ["0", "0", "0"]
            selected_years_temp = st.multiselect('Select years', ['2019', '2020', '2021'], default="2019")
            j = 0
            for i in selected_years_temp:
                selected_years[j] = i
                j = j + 1
            dfd1['year'] = dfd1['Time'].dt.year
            mask_d1 = ((dfd1['year'].astype(int) == int(selected_years[0])) | (
                    dfd1['year'] == int(selected_years[1])) | (dfd1['year'] == int(selected_years[2])))
            dfd1 = dfd1.loc[mask_d1]

        with colR:
            selected_months = ["0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0"]
            selected_months_temp = st.multiselect('Select months',
                                                  ['January', 'February', 'March', 'April', 'May', 'June', 'July',
                                                   'August', 'September', 'October', 'November', 'December'], default = ['January', 'February', 'March'])
            dfd1['month'] = dfd1['Time'].dt.month
            if len(selected_months_temp) != 0:
                j = 0
                for i in selected_months_temp:
                    selected_months[j] = numeric_month[i]
                    j = j + 1
                mask_h = ((dfd1['month'].astype(int) == int(selected_months[0])) | (
                        dfd1['month'].astype(int) == int(selected_months[1])) | (
                                  dfd1['month'].astype(int) == int(selected_months[2])) | (
                                  dfd1['month'].astype(int) == int(selected_months[3])) | (
                                  dfd1['month'].astype(int) == int(selected_months[4])) | (
                                  dfd1['month'].astype(int) == int(selected_months[5])) | (
                                  dfd1['month'].astype(int) == int(selected_months[6])) | (
                                  dfd1['month'].astype(int) == int(selected_months[7])) | (
                                  dfd1['month'].astype(int) == int(selected_months[8])) | (
                                  dfd1['month'].astype(int) == int(selected_months[9])) | (
                                  dfd1['month'].astype(int) == int(selected_months[10])) | (
                                  dfd1['month'].astype(int) == int(selected_months[11]))
                          )
                dfd1 = dfd1.loc[mask_h]

        selection_x = st.radio("Breakdown based on", ["year", "month", "none"])
        if selection_x == "none":
            dfd1['none'] = 1

        # interval selection in the scatter plot
        dfd1_copy = dfd1
        for i in range(len(selected_assets_temp)):
            pts = alt.selection(type="interval", encodings=["x"])
            dfd1 = dfd1_copy
            mask_d1 = (dfd1['Asset'] == selected_assets[i])
            dfd1 = dfd1.loc[mask_d1]
            # left panel: scatter plot
            points = alt.Chart(dfd1).mark_point(filled=False).encode(
                x=alt.X('dayhoursminutes(Time):O', scale=alt.Scale(zero=False)),
                y=alt.Y(column_name_1, scale=alt.Scale(zero=False)),
                color=alt.Color(f"{selection_x}:N", legend=alt.Legend(title=f"{selection_x}")),
                opacity=alt.condition(pts, alt.value(1), alt.value(0.1))
            ).add_selection(pts).properties(
                width=650,
                height=350
            )
            st.subheader(f"{selected_assets[i]}")
            # st.write(points)
            # right panel: histogram
            mag = (alt.Chart(dfd1).mark_bar().encode(
                x=alt.X(column_name_1, bin=True),
                y=alt.Y('count()', stack=True),
                # opacity=alt.condition(pts, alt.value(1), alt.value(0)),
                color=alt.Color(f"{selection_x}:N", legend=alt.Legend(title=f"{selection_x}")),

            ).properties(
                width=300,
                height=300
            ).transform_filter(
                pts
            ))

            # st.write(mag)
            # build the chart:
            scatter = alt.hconcat(points, mag).transform_bin(f"{column_name_1} binned", field=column_name_1,
                                                             bin=alt.Bin(maxbins=20))
            st.write(scatter)


#########PIPE DATA EXPLORATION#################################################
if selected == "Pipe Data Exploration":
    st.title(selected)

    with st.sidebar:
        st.header(':gear: Settings')
        st.subheader('Choose the units')
        # SET UNITS
        diameter_unit = st.selectbox("Choose Diameter units:", ["in", "mm"])
        length_unit = st.selectbox("Choose Length units:", ["ft", "m"])
        discharge_unit = st.selectbox("Choose Discharge units:", ["gpm", "lps"])
        pressure_unit = st.selectbox("Choose Presure units:", ["psi", "kg/cm^2"])
        groundwater_unit = st.selectbox("Choose Groundwater Depth units:", ["ft", "m"])
    st.header("Data Tables")
    if st.checkbox("Show Raw Data"):
        with st.spinner('Writing in progress...'):
            st.write(df_pipe)
        st.success('Done!')

    st.header("Charts")
    selected_options = st.multiselect('Select attributes ', ['Diameter', 'Length', 'Material', 'Installation Year',
                                                             'Discharge', 'Pressure', 'Pipe Bed-Soil Type',
                                                             'Groundwater Depth'], default= ['Diameter', 'Installation Year'])
    selected_options.append("None")

    # if "Data Exploration" is selected in the main menu do the following

    ### READING AND SETTING THE UNITS AND RENAMING DATAFRAME
    # 1 Diameter
    if diameter_unit == 'mm':
        unit_a = 'mm'
        df_pipe[['Diameter']] = (df_pipe[['Diameter']].astype(float) * 25.4).round(1)
    else:
        unit_a = 'in'
    # rename the column so that it contains the selected unit. This name is shown on the y axis
    dia_unit = f"Diameter ({unit_a})"
    df_pipe = df_pipe.rename(columns={'Diameter': dia_unit}).astype('category')

    # 2 Length
    df_pipe[['LENGTH_FT']].astype(str).astype(float)
    if length_unit == 'm':
        unit_b = 'm'
        df_pipe[['LENGTH_FT']] = (df_pipe[['LENGTH_FT']].astype(float) * 0.3048).round(1)
    else:
        unit_b = 'ft'
    # rename the column so that it contains the selected unit. This name is shown on the y axis
    len_unit = f"Length ({unit_b})"
    df_pipe = df_pipe.rename(columns={'LENGTH_FT': len_unit})

    # 3 Material
    mat_unit = "Material"
    df_pipe = df_pipe.rename(columns={'MATERIAL': mat_unit}).astype('category')

    # 4 Year of Installation
    YOI_unit = "Installation Year"
    df_pipe = df_pipe.rename(columns={'Install_ye': YOI_unit}).astype('category')

    # 5 Discharge
    df_pipe[['Qmax_gpm']].astype(str).astype(float)
    if discharge_unit == 'lps':
        unit_c = 'lps'
        df_pipe[['Qmax_gpm']] = (df_pipe[['Qmax_gpm']].astype(float) * 0.0631).round(1)
    else:
        unit_c = 'gpm'
    # rename the column so that it contains the selected unit. This name is shown on the y axis
    q_unit = f"Discharge ({unit_c})"
    df_pipe = df_pipe.rename(columns={'Qmax_gpm': q_unit})

    # 6 Pressure
    df_pipe[['Pmax_Psi']].astype(str).astype(float)
    if pressure_unit == 'kg/cm^2':
        unit_d = 'kg/cm^2'
        df_pipe[['Pmax_Psi']] = (df_pipe[['Pmax_Psi']].astype(float) * 0.070307).round(1)
    else:
        unit_d = 'psi'
    # rename the column so that it contains the selected unit. This name is shown on the y axis
    p_unit = f"Pressure ({unit_d})"
    df_pipe = df_pipe.rename(columns={'Pmax_Psi': p_unit})

    # 7 Pipe bed-soil type
    bedsoil_unit = "Bed-Soil"
    df_pipe = df_pipe.rename(columns={'PAR_MAT': bedsoil_unit}).astype('category')

    # 8 Bed-Soil PH
    df_pipe[['PH']].astype(str).astype(float)

    ph_unit = "Bed-Soil pH"
    df_pipe = df_pipe.rename(columns={'PH': ph_unit})

    # GW Depth
    df_pipe[['Dist_GWT']].astype(str).astype(float)
    if groundwater_unit == 'm':
        unit_e = 'm'
        df_pipe[['Dist_GWT']] = (df_pipe[['Dist_GWT']].astype(float) * 0.3048).round(1)
    else:
        unit_e = 'ft'
    # rename the column so that it contains the selected unit. This name is shown on the y axis
    gwd_unit = f"Groundwater Depth ({unit_e})"
    df_pipe = df_pipe.rename(columns={'Dist_GWT': gwd_unit})

    # FOR DIAMETER
    if ((selected_options[0]) == "Diameter"):  # option_1: #diameter
        del selected_options[0]

        # plot the chart
        Pipe_DiaMaterial_Histogram_Chart = alt.Chart(df_pipe).mark_bar(size=20).encode(
            alt.X(dia_unit, scale=alt.Scale(zero=False)),
            alt.Y(YOI_unit, scale=alt.Scale(zero=False, type='sqrt')),
            alt.Color(mat_unit, legend=alt.Legend(title="Material")),
            tooltip=[dia_unit, mat_unit, YOI_unit, 'count()']
        ).properties(
            title=f"Diameter ({unit_a}) vs. Year of Installation",
            width=450, height=250
        ).interactive()

        text_DiaMaterial = alt.Chart(df_pipe).mark_text(dx=-15, dy=3, color='white').encode(
            x=alt.X(dia_unit, stack='zero'),
            y=alt.Y(YOI_unit),
            text=alt.Text('count():Q')
        )

        Pipe_DiaLength_Histogram_Chart = alt.Chart(df_pipe).mark_bar(size=20).encode(
            alt.X(dia_unit, scale=alt.Scale(zero=True)),
            alt.Y(f"sum(Length ({unit_b})):Q", scale=alt.Scale(zero=True)),
            alt.Color(mat_unit, legend=alt.Legend(title="Material")),
            tooltip=[dia_unit, mat_unit, f"sum(Length ({unit_b})):Q", 'count()']
        ).properties(
            title=f"Diameter ({unit_a}) vs. Length ({unit_b})",
            width=450, height=250
        ).interactive().resolve_scale(y='independent')
        st.write(Pipe_DiaMaterial_Histogram_Chart + text_DiaMaterial | Pipe_DiaLength_Histogram_Chart)

    # FOR LENGTH
    if ((selected_options[0]) == "Length"):  # option_2: #length
        del selected_options[0]

        # plot the chart
        Pipe_Len_Histogram_Chart = alt.Chart(df_pipe).mark_bar(size=20).encode(
            alt.X(len_unit, type='quantitative', scale=alt.Scale(zero=False, type='log', base=2)),
            alt.Y('count()', scale=alt.Scale(zero=False, type='sqrt')),
            alt.Color(len_unit, type='quantitative', sort="descending", legend=alt.Legend(title=f"Length ({unit_b})")),
            tooltip=[len_unit, 'count()']
        ).properties(
            title=f"Length ({unit_b}) Histogram",
            width=450, height=250
        ).interactive()

        Pipe_ZoneLength_Histogram_Chart = alt.Chart(df_pipe).mark_bar(size=20).encode(
            alt.X('ZONE', scale=alt.Scale(zero=True), sort='-y'),
            alt.Y(f"sum(Length ({unit_b})):Q", scale=alt.Scale(zero=True)),
            alt.Color('Material', legend=alt.Legend(title="Material")),
            tooltip=['ZONE', f"sum(Length ({unit_b})):Q", 'Material', 'count()']
        ).properties(
            title=f"Zone vs. Length ({unit_b})",
            width=450, height=250
        ).interactive().resolve_scale(y='independent')

        st.write(Pipe_Len_Histogram_Chart | Pipe_ZoneLength_Histogram_Chart)

    # FOR MATERIAL
    if ((selected_options[0]) == "Material"):  # option_3: #material
        del selected_options[0]

        # plot the chart
        Pipe_Mat_Histogram_Chart = alt.Chart(df_pipe).mark_bar(size=20).encode(
            alt.X(mat_unit, type='nominal', scale=alt.Scale(zero=True), sort='-y'),
            alt.Y(f"sum(Length ({unit_b})):Q", scale=alt.Scale(zero=True)),
            alt.Color(mat_unit, legend=alt.Legend(title="Material")),
            tooltip=[mat_unit, f"sum(Length ({unit_b})):Q", 'count()']
        ).properties(
            title=f"Material vs. Length ({unit_b})",
            width=450, height=250
        ).interactive()

        Pipe_MatBreak_Histogram_Chart = alt.Chart(df_pipe).mark_bar(size=20).encode(
            alt.X(mat_unit, type='nominal', scale=alt.Scale(zero=True), sort='-y'),
            alt.Y('sum(Breaks_No)', type='quantitative', scale=alt.Scale(zero=True), title="Sum of No. of Pipe Breaks"),
            alt.Color(mat_unit, legend=alt.Legend(title="Material")),
            tooltip=[mat_unit, 'sum(Breaks_No):Q', 'count()']
        ).properties(
            title="Material vs. Pipe Breaks reported between (2015-2020)",
            width=450, height=250
        ).interactive()

        st.write(Pipe_Mat_Histogram_Chart | Pipe_MatBreak_Histogram_Chart)

    # FOR INSTALLATION YEAR
    if ((selected_options[0]) == "Installation Year"):  # option_1: #install year
        del selected_options[0]
        len_unit = f"Length ({unit_b})"
        df_pipe = df_pipe.rename(columns={'LENGTH_FT': len_unit})
        # plot the chart
        Pipe_YOIMaterial_Histogram_Chart = alt.Chart(df_pipe).mark_bar(size=20).encode(
            alt.X(YOI_unit, type='nominal', scale=alt.Scale(zero=False), sort='-y'),
            alt.Y(f"sum(Length ({unit_b})):Q", scale=alt.Scale(zero=False)),
            # alt.Column(YOI_unit, type='ordinal'),
            alt.Color('Material', legend=alt.Legend(title="Material")),
            tooltip=[YOI_unit, f"sum(Length ({unit_b}))", 'Material', 'count()']
        ).properties(
            title=f"Length ({unit_b}) wise Installation Year (High to Low)",
            width=450, height=250
        ).interactive()  # .resolve_scale(y = 'independent')

        # plot the chart
        Pipe_YOIDiameter_Histogram_Chart = alt.Chart(df_pipe).mark_bar(size=20).encode(
            alt.X(YOI_unit, type='nominal', scale=alt.Scale(zero=False), sort='x'),
            alt.Y('sum(Breaks_No):Q', scale=alt.Scale(zero=True), title="Sum of No. of Pipe Breaks"),
            # alt.Column(YOI_unit, type='ordinal'),
            alt.Color('Material', legend=alt.Legend(title="Material")),
            tooltip=[YOI_unit, 'count()']
        ).properties(
            title="Year of Installation of Pipes vs. Pipe Breaks reported between (2015-2020)",
            width=450, height=250
        ).interactive()  # .resolve_scale(y = 'independent')

        # text_YOIDiameter = alt.Chart(df_pipe).mark_text(dx=-15, dy=3, color='white').encode(
        # x=alt.X(YOI_unit, stack='zero'),
        # y=alt.Y(dia_unit),
        # text=alt.Text('count():Q')
        # )

        st.write(Pipe_YOIMaterial_Histogram_Chart | Pipe_YOIDiameter_Histogram_Chart)

    # FOR DISCHARGE
    if ((selected_options[0]) == "Discharge"):  # option_2: #discharge
        del selected_options[0]

        # plot the chart
        Pipe_Dis_Histogram_Chart = alt.Chart(df_pipe).mark_bar(size=10).encode(
            alt.X(q_unit, type='quantitative', scale=alt.Scale(zero=True, type='quantile')),
            alt.Y('count()', scale=alt.Scale(zero=False, type='sqrt')),
            alt.Color(q_unit, type='quantitative', sort="descending", legend=alt.Legend(title=f"Discharge ({unit_c})")),
            tooltip=[q_unit, 'count()']
        ).properties(
            title=f"Discharge ({unit_c}) Histogram",
            width=450, height=250
        ).interactive()

        Pipe_DisBreak_Histogram_Chart = alt.Chart(df_pipe).mark_bar(size=10).encode(
            alt.X(q_unit, type='quantitative', scale=alt.Scale(zero=True, type='quantile')),
            alt.Y('sum(Breaks_No):Q', scale=alt.Scale(zero=False, type='sqrt'), title="Sum of No. of Pipe Breaks"),
            alt.Color(q_unit, type='quantitative', sort="descending", legend=alt.Legend(title=f"Discharge ({unit_c})")),
            tooltip=[q_unit, 'count()']
        ).properties(
            title=f"Discharge ({unit_c}) vs. Pipe Breaks reported between (2015-2020)",
            width=450, height=250
        ).interactive()

        Pipe_DisYOI_Histogram_Chart = alt.Chart(df_pipe).mark_bar(size=20).encode(
            alt.X(f"sum(Discharge ({unit_c})):Q", scale=alt.Scale(zero=True), sort='y'),
            alt.Y(YOI_unit, scale=alt.Scale(zero=True), sort='-x'),
            alt.Color('Material', legend=alt.Legend(title="Material")),
            tooltip=[f"sum(Discharge ({unit_c})):Q", 'Material', 'count()']
        ).properties(
            title=f"Discharge ({unit_c}) wise Installation Year (High to Low)",
            width=450, height=250
        ).interactive().resolve_scale(y='independent')

        st.write((Pipe_Dis_Histogram_Chart & Pipe_DisBreak_Histogram_Chart) | Pipe_DisYOI_Histogram_Chart)

    # FOR PRESSURE
    if ((selected_options[0]) == "Pressure"):  # option_2: #discharge
        del selected_options[0]

        # plot the chart
        Pipe_Pre_Histogram_Chart = alt.Chart(df_pipe).mark_bar(size=10).encode(
            alt.X(p_unit, type='quantitative', scale=alt.Scale(zero=False)),
            alt.Y('count()', scale=alt.Scale(zero=False, type='linear', base=2)),
            alt.Color(p_unit, type='quantitative', sort="descending", legend=alt.Legend(title=f"Pressure ({unit_d})")),
            tooltip=[p_unit, 'count()']
        ).properties(
            title=f"Pressure ({unit_d}) Histogram",
            width=650, height=450
        ).interactive().resolve_scale(x='independent', y='independent')

        # Pipe_PreBreak_Histogram_Chart = alt.Chart(df_pipe).mark_bar(size=10).encode(
        # alt.X(p_unit, type='quantitative', scale=alt.Scale(zero=True), sort='-y'),
        # alt.Y('sum(Breaks_No):Q', scale=alt.Scale(zero=True), title="Sum of No. of Pipe Breaks"),
        # alt.Color(mat_unit, type='nominal', legend=alt.Legend(title="Material")),
        # tooltip=[p_unit, 'count()']
        # ).properties(
        #     title=f"Pressure ({unit_d}) vs. Pipe Breaks reported between (2015-2020)",
        #     width=450, height=250
        # ).interactive().resolve_scale(x='independent', y='independent')

        st.write(Pipe_Pre_Histogram_Chart)  # | Pipe_PreBreak_Histogram_Chart)
    # FOR BED SOILPH
    if ((selected_options[0]) == "Pipe Bed-Soil Type"):  # option_3: #material
        del selected_options[0]

        # plot the chart
        Pipe_BS_Histogram_Chart = alt.Chart(df_pipe).mark_bar(size=20).encode(
            alt.X(ph_unit, scale=alt.Scale(zero=False)),
            alt.Y('sum(Breaks_No):Q', scale=alt.Scale(zero=False), title="Sum of No. of Pipe Breaks"),
            alt.Color('Material', legend=alt.Legend(title="Bed-Soil pH")),
            tooltip=[ph_unit, 'sum(Breaks_No):Q', mat_unit, 'count()']
        ).properties(
            title="Soil pH vs. Pipe Breaks reported between (2015-2020)",
            width=650, height=450
        ).interactive()
        st.write(Pipe_BS_Histogram_Chart)

    # FOR GROUNDWATER
    if ((selected_options[0]) == "Groundwater Depth"):  # option_3: #material
        del selected_options[0]

        # plot the chart
        Pipe_GWD_Histogram_Chart = alt.Chart(df_pipe).mark_circle(size=20).encode(
            alt.X(ph_unit, scale=alt.Scale(zero=False), sort='x'),
            alt.Y(gwd_unit, type='quantitative', scale=alt.Scale(zero=False, type='sqrt')),
            alt.Color('sum(Breaks_No):Q', legend=alt.Legend(title="Total Breaks (2015-2020)"),
                      scale=alt.Scale(scheme='reds')),
            tooltip=[gwd_unit, 'sum(Breaks_No):Q', mat_unit, 'count()'],
            size='sum(Breaks_No):Q',
        ).properties(
            title=f"Groundwater Depth ({unit_e}) vs. Soil pH",
            width=650, height=450
        ).interactive()
        st.write(Pipe_GWD_Histogram_Chart)

#dfu = pd.read_csv("C:/Users/14129/Desktop/Water usage.csv")


if selected == "Water Usage Exploration":
    st.title(selected)
    ymd_range = [datetime.date(2019, 1, 1), datetime.date(2019, 1, 2)]
    with st.sidebar:
        st.header(':gear: Settings')

        st.subheader('Choose unit:') # could be flow, pressure and water level

        water_usage_unit = st.selectbox("Water usage:", ["kilogallon", "gallon", "cubic meter", "cubic foot", "centum cubic foot"])

    st.header("Data Tables")
    if st.checkbox("Show Raw Data"):
        with st.spinner('Writing in progress...'):
            st.write(dfu)
        #st.success('Done!')

    st.header("Charts")
    dfu = dfu.rename(columns={'Water usage (kgal)':'Water usage'})

    colL, colR = st.columns([1, 1])

    with colL:
        selected_years = ["0", "0", "0"]
        selected_years_temp = st.multiselect('Select years:', ['2019', '2020', '2021'], default = "2019")
        j = 0
        for i in selected_years_temp:
            selected_years[j] = i
            j = j + 1
        dfu['year'] = dfu['Time'].dt.year
        mask_d1 = ((dfu['year'].astype(int) == int(selected_years[0])) | (dfu['year'] == int(selected_years[1])) | (
                    dfu['year'] == int(selected_years[2])))
        dfu = dfu.loc[mask_d1]

    with colR:
        selected_months = ["0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0"]
        selected_months_temp = st.multiselect('Select months ',
                                              ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August',
                                               'September', 'October', 'November', 'December'], default = ['January', 'February', 'March'])
        dfu['month'] = dfu['Time'].dt.month
        if len(selected_months_temp) != 0:
            numeric_month = {
                "January": "1",
                "February": "2",
                "March": "3",
                "April": "4",
                "May": "5",
                "June": "6",
                "July": "7",
                "August": "8",
                "September": "9",
                "October": "10",
                "November": "11",
                "December": "12"
            }
            j = 0
            for i in selected_months_temp:
                selected_months[j] = numeric_month[i]
                j = j + 1
            mask_h = ((dfu['month'].astype(int) == int(selected_months[0])) | (
                    dfu['month'].astype(int) == int(selected_months[1])) | (
                              dfu['month'].astype(int) == int(selected_months[2])) | (
                              dfu['month'].astype(int) == int(selected_months[3])) | (
                              dfu['month'].astype(int) == int(selected_months[4])) | (
                              dfu['month'].astype(int) == int(selected_months[5])) | (
                              dfu['month'].astype(int) == int(selected_months[6])) | (
                              dfu['month'].astype(int) == int(selected_months[7])) | (
                              dfu['month'].astype(int) == int(selected_months[8])) | (
                              dfu['month'].astype(int) == int(selected_months[9])) | (
                              dfu['month'].astype(int) == int(selected_months[10])) | (
                              dfu['month'].astype(int) == int(selected_months[11]))
                      )
            dfu = dfu.loc[mask_h]

    #dfu = dfu[['Time', 'Customer ID', 'Water usage', 'Water usage', 'Zone']].melt(var_name='Zone', value_name='Water Usage')

    if water_usage_unit == 'kilogallon':
        unit_u = 'kgal'
    elif water_usage_unit == 'gallon':
        unit_u = 'gal'
        dfu[['Water usage']] = dfu[['Water usage']] * 1000
    elif water_usage_unit == 'cubic meter':
        unit_u = 'm^3'
        dfu[['Water usage']] = dfu[['Water usage']] * 3.79
    elif water_usage_unit == 'cubic foot':
        unit_u = 'ft^3'
        dfu[['Water usage']] = dfu[['Water usage']] * 133.68
    elif water_usage_unit == 'centum cubic foot':
        unit_u = 'ccf'
        dfu[['Water usage']] = dfu[['Water usage']] * 1.34

    column_name_u = f"Water usage ({unit_u})"

    dfu = dfu.rename(columns={'Water usage': column_name_u})

    # selection to allow highlight of genre when click on legend
    #selection = alt.selection_multi(fields=['Asset'], bind='legend')
    selection = alt.selection_interval(encodings=['x'])

    # scatterplot showing the correlation between two features for all genres
    Usage_Line_Chart = alt.Chart(dfu).mark_point(filled = True).encode(
        x=alt.X('Time:T', scale=alt.Scale(zero=False)),
        y=alt.Y(f'{column_name_u}:Q', scale=alt.Scale(zero=False)),
        color=alt.Color('Zone:N', legend=alt.Legend(title="Zone")),
        opacity=alt.condition(selection, alt.value(1), alt.value(0.1)),
        tooltip=['Time', 'Zone', column_name_u]
    ).properties(
        width=700, height=370
    ).interactive().add_selection(
        selection
    )
    bars = (
        alt.Chart(dfu).mark_bar().encode(
            y=alt.Y("Zone", axis=alt.Axis(labels=False)),
            color=alt.Color("Zone:O"),
            x=alt.X(f"mean({column_name_u})", scale=alt.Scale(zero=False)),
        ).transform_filter(selection)
    )

    # Concatenate bar plot and scatter plot vertically
    chart = alt.hconcat(Usage_Line_Chart, bars).properties(
        title="Use the interval of interest:"
    )
    st.subheader("Water usage in time:")
    st.write(chart)



########################################################################
    colLz, colMz, colRzL, colRzR = st.columns([1, 2, 1, 0.5])


    with colLz:
        zone_name = ["All", "Fire District", "Northern", "Oakville High", "Oakville Low", "Straits",
                                   "Town Hall"]
        selection_zone = st.radio("Select zone:", zone_name)

    with colMz:
        sum_z = [0,0,0,0,0,0,0]
        #sum_z[0] = dfu[f"{column_name_u}"].sum()

        mask_z = ((dfu["Zone"] == "Fire District Zone" ))
        dfuz = dfu.loc[mask_z]
        dfuz[f"{column_name_u}"] = pd.to_numeric(dfuz[f"{column_name_u}"])
        sum_z[1] = dfuz[f"{column_name_u}"].sum()

        mask_z = ((dfu["Zone"] == "Northern Zone" ))
        dfuz = dfu.loc[mask_z]
        dfuz[f"{column_name_u}"] = pd.to_numeric(dfuz[f"{column_name_u}"])
        sum_z[2]= dfuz[f"{column_name_u}"].sum()

        mask_z = ((dfu["Zone"] == "Oakville High Zone" ))
        dfuz = dfu.loc[mask_z]
        dfuz[f"{column_name_u}"] = pd.to_numeric(dfuz[f"{column_name_u}"])
        sum_z[3] = dfuz[f"{column_name_u}"].sum()

        mask_z = ((dfu["Zone"] == "Oakville Low Zone" ))
        dfuz = dfu.loc[mask_z]
        dfuz[f"{column_name_u}"] = pd.to_numeric(dfuz[f"{column_name_u}"])
        sum_z[4] = dfuz[f"{column_name_u}"].sum()

        mask_z = ((dfu["Zone"] == "Straits Zone" ))
        dfuz = dfu.loc[mask_z]
        dfuz[f"{column_name_u}"] = pd.to_numeric(dfuz[f"{column_name_u}"])
        sum_z[5] = dfuz[f"{column_name_u}"].sum()

        mask_z = ((dfu["Zone"] == "Town Hall Zone" ))
        dfuz = dfu.loc[mask_z]
        dfuz[f"{column_name_u}"] = pd.to_numeric(dfuz[f"{column_name_u}"])
        sum_z[6] = dfuz[f"{column_name_u}"].sum()

        color_names = ["black","blue","orange","red","navy","green","yellow"]

        if selection_zone == "All":
            source = pd.DataFrame({"category": ["Fire District", "Northern", "Oakville High", "Oakville Low", "Straits",
                                       "Town Hall"], "value": [sum_z[1], sum_z[2], sum_z[3], sum_z[4], sum_z[5],sum_z[6]]})
            pie_chart = alt.Chart(source).mark_arc().encode(
                theta=alt.Theta(field="value", type="quantitative"),
                color=alt.Color(field="category", type="nominal"),
            )
        else:
            sum_other = 0
            for i in range(1,7):
                if selection_zone != zone_name[i]:
                    sum_other = sum_other + sum_z[i]
                else:
                    sum_selected = sum_z[i]
                    j = i
            source = pd.DataFrame({"category": [f"{selection_zone}", "other"], "value": [sum_selected, sum_other]})

            pie_chart = alt.Chart(source).mark_arc().encode(
                theta=alt.Theta(field="value", type="quantitative"),
                #color=alt.Color(field="category", type="nominal"),
                color=alt.Color('category',
                                scale=alt.Scale(
                                    domain=[f"{selection_zone}", "other"],
                                    range=[f'{color_names[j]}', 'lightgray'])
            ))



        st.write(pie_chart)

    with colRzL:
        st.subheader("Zone Statistics:")
        st.write("Number of customers:")
        st.write("Highest monthly water usage:")
        st.write("Month of highest usage:")
    with colRzR:

        mask_z = (dfu["Zone"] == f"{selection_zone} Zone")
        dfuz = dfu.loc[mask_z]

        n = [6605, 1039, 369, 1749, 1492, 527, 1438]


        n_index = zone_name.index(selection_zone)

        #n = len(pd.unique(dfuz['Customer ID']))

        dfuz['month'] = dfuz['Time'].dt.month
        zone_monthly_water_usage = [dfuz[f'{column_name_u}'].loc[dfuz["month"] == 1].sum(),dfuz[f'{column_name_u}'].loc[dfuz["month"] == 2].sum(),dfuz[f'{column_name_u}'].loc[dfuz["month"] == 3].sum(),
                                    dfuz[f'{column_name_u}'].loc[dfuz["month"] == 4].sum(),dfuz[f'{column_name_u}'].loc[dfuz["month"] == 5].sum(),dfuz[f'{column_name_u}'].loc[dfuz["month"] == 6].sum(),
                                    dfuz[f'{column_name_u}'].loc[dfuz["month"] == 7].sum(),dfuz[f'{column_name_u}'].loc[dfuz["month"] == 8].sum(),dfuz[f'{column_name_u}'].loc[dfuz["month"] == 9].sum(),
                                    dfuz[f'{column_name_u}'].loc[dfuz["month"] == 10].sum(),dfuz[f'{column_name_u}'].loc[dfuz["month"] == 11].sum(),dfuz[f'{column_name_u}'].loc[dfuz["month"] == 12].sum()]
        max_water_usage = max(zone_monthly_water_usage)
        month_index = zone_monthly_water_usage.index(max_water_usage) + 1
        month_string = "_"
        if (max_water_usage != 0):
            month_string = Reverse_numeric_month[month_index]

        st.subheader("__________")
        st.write(f"{n[n_index]}")
        st.write(f"{round(max_water_usage,1)}")
        st.write(f"{month_string}")

#########PREDICTING NUMBER OF BREAKS###########################################

if selected == "Pipe-Break Prediction":
    st.title(selected)


    # define a blank data frame
    def get_classification_report(y_test, y_pred):
        from sklearn import metrics
        report = metrics.classification_report(y_test, y_pred, output_dict=True)
        df_classification_report = pd.DataFrame(report).transpose()
        df_classification_report = df_classification_report
        return df_classification_report


    dtreg = pd.DataFrame()

    # #Converting Material into a factored variable
    le_material = LabelEncoder()
    df_pipe_orig['MATERIAL_ENCO'] = le_material.fit_transform(df_pipe_orig['MATERIAL'])

    # create a list
    features = ['ID', 'Breaks_No']
    UD_features = []  # for later use
    UD_names = []
    # UD_Predictors = pd.DataFrame()
    # UD_PredictedBreaks = 0
    with st.sidebar:
        st.header(':gear: Settings')

        # Input Present Year for Calculating Age
        st.subheader("Year settings")
        year = st.number_input("Current year for calculating age", value=2022)
        df_pipe_orig['Age'] = (year - df_pipe_orig['Install_ye'])

        st.subheader('Select features')
        # SELECT FEATURES FOR Regression

        col1, col2 = st.columns((1, 1))
        with col1:
            Dia_CheckBox = st.checkbox("Diameter", value=True)
            if Dia_CheckBox:
                features.append('Diameter')

            Len_CheckBox = st.checkbox("Length", value=True)
            if Len_CheckBox:
                features.append('LENGTH_FT')

            Cus_CheckBox = st.checkbox("No. of Customers", value=True)
            if Cus_CheckBox:
                features.append('Ncustomers')

        with col2:
            Dis_CheckBox = st.checkbox("Discharge", value=True)
            if Dis_CheckBox:
                features.append('Qmax_gpm')

            Pre_CheckBox = st.checkbox("Pressure", value=True)
            if Pre_CheckBox:
                features.append('Pmax_Psi')

            Sph_CheckBox = st.checkbox("Bed-Soil pH", value=True)
            if Sph_CheckBox:
                features.append('PH')

            Age_CheckBox = st.checkbox("Age", value=True)
            if Age_CheckBox:
                features.append('Age')

        # Reading Original Dataframe with Selected Features
        dtreg = df_pipe_orig[features]

    col1, col2, col3, col4 = st.columns((1, 1, 1, 0.25))

    with col1:
        # st.write(features)
        st.header("1. Data Tables")
        if st.checkbox("Show Raw Data"):
            with st.spinner('Writing in progress...'):
                st.write(df_pipe)
            st.success('Done!')

        if st.checkbox("Show selected data"):
            with st.spinner('Writing in progress...'):
                st.write(dtreg.sort_values('Breaks_No', axis=0, ascending=False))
            st.success('Done!')

        st.header("2. Machine Learning")
        st.subheader("Learn Model")
        st.write(
            "The data model is split in 75% train and 25% test dataset; the 75% train data is further split into 60% for training and 40% for validation. The ML model is then applied on 25% of unseen data for prediction.")
        bool_learn = st.checkbox("Learn the Model:")
        if bool_learn:
            # defining predictor and response variables
            st.subheader("Training Report")
            ##df_75 = load("https://1drv.ms/u/s!AnhaxtVMqKpxgok6rtmFtgqn1vUt_Q?e=el633O")
            # df_75['MATERIAL_ENCO'] =le_material.fit_transform(df_75['MATERIAL'])
            Pred = df_75[features].drop(['ID', 'Breaks_No'], axis=1)
            Resp = df_75.Breaks_No
            Pred_train, Pred_test, Resp_train, Resp_test = train_test_split(Pred, Resp, test_size=0.4, random_state=0)
            from sklearn.tree import DecisionTreeRegressor

            regressor = DecisionTreeRegressor(random_state=0)
            regressor.fit(Pred_train, Resp_train)
            Resp_pred = regressor.predict(Pred_test)

            MSE = metrics.mean_squared_error(Resp_test, Resp_pred)
            score = accuracy_score(Resp_test, Resp_pred)
            report = classification_report(Resp_test, Resp_pred)

            report_train_df = get_classification_report(Resp_test, Resp_pred)
            st.write(report_train_df)

            st.subheader("Testing Report")
            ##df_25 = load("https://1drv.ms/u/s!AnhaxtVMqKpxgok7oN74-f1eTi8BFw?e=yei0ZH")
            X_4test = df_25[features].drop(['ID', 'Breaks_No'], axis=1)
            yReal_4test = df_25.Breaks_No
            yPrediction_4test = regressor.predict(X_4test)  # Prediction on unseen test data
            report_test_df = get_classification_report(yReal_4test, yPrediction_4test)
            st.write(report_test_df)
            # st.write(reg.predict(input_reg))

            # UD_Predictors = pd.DataFrame(UD_features)
            # UD_PredictedBreaks = regressor.predict(UD_Predictors)

    with col2:
        st.header("3. Enter Data")
        predi_bool = st.button("Predict number of breaks")

        # DataEntry_CheckBox = st.checkbox("Show Data-entry Fields")
        # if DataEntry_CheckBox:
        st.write(
            "Enter values for selected features to predict number of breaks based on the machine learnt algorithm.")
        if Dia_CheckBox:
            UD_Dia_in = st.selectbox('Select Diameter (in)', [4, 6, 8, 10, 12, 14, 16], index=1)
            # UD_Dia_in.as_type(int)
            UD_features.append(UD_Dia_in)
            UD_names.append('Diameter')

        if Len_CheckBox:
            UD_Len_ft = st.number_input("Enter Length (ft)", min_value=0.0, step=0.5, value=2500.0)
            UD_features.append(UD_Len_ft)
            UD_names.append('LENGTH_FT')

        if Cus_CheckBox:
            UD_Cus = st.number_input("Enter No. of Customers", min_value=0, step=1, value=20)
            UD_features.append(UD_Cus)
            UD_names.append('NCustomers')

        if Dis_CheckBox:
            UD_Dis_gpm = st.number_input("Enter Discharge (gpm)", min_value=0.0, step=0.5, value=5.0)
            UD_features.append(UD_Dis_gpm)
            UD_names.append('Qmax_gpm')

        if Pre_CheckBox:
            UD_Pre_psi = st.number_input("Enter Pressure (psi)", min_value=0.0, step=0.5, value=100.0)
            UD_features.append(UD_Pre_psi)
            UD_names.append('Pmax_psi')

        if Sph_CheckBox:
            UD_Sph = st.number_input("Enter Bed-Soil pH", min_value=0.0, step=0.1, value=5.3)
            UD_features.append(UD_Sph)
            UD_names.append('PH')

        if Age_CheckBox:
            UD_Age = st.number_input("Enter Age", min_value=0, step=1, value=65)
            UD_features.append(UD_Age)
            UD_names.append('Age')

        input_reg = np.array(UD_features)
        input_reg = input_reg.reshape(1, -1)

    with col3:
        st.header("Predicted Break(s):")
        if bool_learn == 0:
            st.error("Learn the model first and then predict number of breaks!")
        # st.write(UD_PredictedBreaks)
    with col4:
        if bool_learn == 0:
            st.header("?")
        else:
            if predi_bool:
                prediction_output = regressor.predict(input_reg)
                st.header(int(prediction_output.item(0)))
            else:
                st.header("?")
