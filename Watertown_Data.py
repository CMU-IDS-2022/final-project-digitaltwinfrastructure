import numpy as np
import pandas as pd
import streamlit as st
import base64
import altair as alt
import datetime
#import pytz

from streamlit_option_menu import option_menu
from sklearn.decomposition import PCA
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
from sklearn.metrics import accuracy_score, explained_variance_score
from sklearn.tree import DecisionTreeClassifier
from sklearn.tree import DecisionTreeRegressor

from operator import itemgetter


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
@st.cache(allow_output_mutation=True)
def load(url):
    df = pd.read_csv(create_onedrive_directdownload(url))
    return df

# Used to specify end date in case of empty end date input from user.
def set_default():
    if not (ymd_range[0]):
        # minimum
        ymd_range[0] = datetime.date(2019, 1, 1)
    elif not (ymd_range[1]):
        # maximum
        ymd_range[1] = datetime.date(2023, 12, 31)

def change_unit(data, column_name, quantity, unit):
    data[[column_name]] = data[[column_name]].astype(float)

    coef = 1
    if quantity == "water level":
        if unit == 'meter':
            unit_symbol = 'm'
            coef = 0.3048
        else:
            unit_symbol = 'ft'
    elif quantity == "flow":
        if unit == 'gallon per minute':
            unit_symbol = 'gpm'
        elif unit == 'cubic meter per second':
            unit_symbol = 'm^3/sec'
            coef = 0.0000630902
        elif unit == 'cubic foot per second':
            unit_symbol = 'ft^3/sec'
            coef = 0.0022280093
        elif unit == 'acre-foot per day':
            unit_symbol = 'ac*ft/day'
            coef = 0.0044191742
        elif unit == 'acre-inch per hour':
            unit_symbol = 'ac*in/hour'
            coef = 0.0026536140977965
    elif quantity == "pressure":
        if unit == 'pressure per square inch':
            unit_symbol = 'psi'
        elif unit == 'meter of head':
            unit_symbol = 'm'
            coef = 0.70324961490205
        elif unit == 'kilogram per square centimeter':
            unit_symbol = 'kg/cm^2'
            coef = 0.070307
    elif quantity == "diameter":
        if unit == 'mm':
            unit_symbol = 'mm'
            coef = 25.4
        else:
            unit_symbol = 'in'
    elif ((quantity == "length") | (quantity == "ground water depth")):
        if unit == 'meter':
            unit_symbol = 'm'
            coef = 0.3048
        else:
            unit_symbol = 'ft'
    elif quantity == "discharge":
        if unit == 'liter per second':
            unit_symbol = 'lps'
            coef = 0.0631
        else:
            unit_symbol = 'gpm'
    elif quantity == "water usage":
        if water_usage_unit == 'kilogallon':
            unit_symbol = 'kgal'
            coef = 0.0631
        elif unit == 'gallon':
            unit_symbol = 'gal'
            coef = 1000
        elif unit == 'cubic meter':
            unit_symbol = 'm^3'
            coef = 3.79
        elif unit == 'cubic foot':
            unit_symbol = 'ft^3'
            coef = 133.68
        elif unit == 'centum cubic foot':
            unit_symbol = 'ccf'
            coef = 1.34
    data[[column_name]] = data[[column_name]] * coef
    return data, unit_symbol


def mask_year(df, selected_years):
    selected_years = [int(i) for i in selected_years]
    df['year'] = df['Time'].dt.year
    mask = df['year'] == 0
    for i in selected_years:
        mask = (mask | (df['year'].astype(int) == i))
    df = df.loc[mask]
    return df


def rename_months(df):
    df['month'] = df['month'].astype(str)
    df['month'] = df['month'].replace(
        {"1": "January", "2": "February", "3": "March", "4": "April", "5": "May", "6": "June",
         "7": "July", "8": "August", "9": "September", "10": "October", "11": "November",
         "12": "December"})
    return df

def mask_month(df, selected_months):
    selected_months_numeric = []
    df['month'] = df['Time'].dt.month
    mask = df['month'] == 0
    for i in selected_months:
        selected_months_numeric.append(numeric_month[i])
    for i in selected_months_numeric:
        mask = (mask | (df['month'].astype(int) == i))
    df = df.loc[mask]
    df = rename_months(df)
    return df


def def_line_chart(data, x, y, scale_zero_x, scale_zero_y, color, legend_title, condition1_val, condition2_val,
                   selection, tooltip, width, height):
    chart = alt.Chart(data).mark_line().encode(
        alt.X(x, scale=alt.Scale(zero=scale_zero_x)),
        alt.Y(y, scale=alt.Scale(zero=scale_zero_y)),
        alt.Color(color, legend=alt.Legend(title=legend_title)),
        opacity=alt.condition(selection, condition1_val, condition2_val),
        tooltip=tooltip
    ).properties(
        width=width, height=height
    ).interactive().add_selection(
        selection
    )
    return chart


def def_bars(data, x, y, scale_zero_x, label_y, color, selection, extent):
    bars = alt.Chart(data).mark_bar().encode(
        x=alt.X(f"mean({x})", scale=alt.Scale(zero=scale_zero_x)),
        y=alt.Y(y, axis=alt.Axis(labels=label_y)),
        color=alt.Color(color),
    ).transform_filter(selection)
    error_bars = alt.Chart().mark_errorbar(extent=extent).encode(
        x=alt.X(f"mean({x})", scale=alt.Scale(zero=scale_zero_x)),
        y=y
    )
    bars = alt.layer(bars, error_bars, data=data).transform_filter(selection)

    return bars
def def_distribution_chart(data, selected_asset, x, y, color, legend, condition1_value, condition2_value, selection,
                       width_point, height_point, y_bar, width_bar, height_bar, bin, stack, maxbins):
    # left panel: scatter plot

    points = alt.Chart(data).mark_point(filled=False).encode(
        x=alt.X(x, scale=alt.Scale(zero=False)),
        y=alt.Y(y, scale=alt.Scale(zero=False)),
        color=alt.Color(color, legend=alt.Legend(title=legend)),
        opacity=alt.condition(selection, condition1_value, condition2_value)
    ).add_selection(selection).properties(
        width=width_point,
        height=height_point
    )
    st.subheader(f"{selected_asset}")
    # right panel: histogram
    mag = (alt.Chart(data).mark_bar().encode(
        x=alt.X(y, bin=bin),
        y=alt.Y(y_bar, stack=stack),
        color=alt.Color(color, legend=alt.Legend(title=legend)),
    ).properties(
        width=width_bar,
        height=height_bar
    ).transform_filter(
        selection
    ))
    chart = alt.hconcat(points, mag).transform_bin(f"{y} binned",
                                                   field=y, bin=alt.Bin(maxbins=maxbins))
    return chart



# Main Code
df = load("https://1drv.ms/u/s!AnhaxtVMqKpxgolL9YaQaQcQqgtxBQ?e=xRNBhX")
df_org = df.loc[:, ~df.columns.str.contains('^Unnamed')]

df_pipe = load("https://1drv.ms/u/s!AnhaxtVMqKpxgok-XtdjTGpjIUIW3w?e=6swM00")
df_pipe[['Diameter']] = df_pipe[['Diameter']].astype(float)
df_pipe[['LENGTH_FT']] = df_pipe[['LENGTH_FT']].astype(str).astype(float)
df_pipe[['Qmax_gpm']] = df_pipe[['Qmax_gpm']].astype(str).astype(float)
df_pipe[['Pmax_Psi']] = df_pipe[['Pmax_Psi']].astype(str).astype(float)
df_pipe[['Dist_GWT']] = df_pipe[['Dist_GWT']].astype(str).astype(float)

dfu = load("https://1drv.ms/u/s!AnhaxtVMqKpxgolMm2YgAiaWnYNRSg?e=owus29")
dfu['Time'] = pd.to_datetime(dfu['Time'], errors='coerce')

numeric_month = {"January": 1,
                 "February": 2,
                 "March": 3,
                 "April": 4,
                 "May": 5,
                 "June": 6,
                 "July": 7,
                 "August": 8,
                 "September": 9,
                 "October": 10,
                 "November": 11,
                 "December": 12}

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

# define the main menu with its options
with st.sidebar:
    selected = option_menu("Main Menu", ["Water Network Exploration", "Water Usage Exploration",
                                         "Pipe Data Exploration", "Pipe-Break Prediction", "Water Network Management"],
                           icons=['bi bi-bounding-box-circles', 'bi bi-bezier', 'droplet-half',
                                  'bi bi-exclamation-triangle-fill','bi bi-columns-gap', 'person-lines-fill'],
                           menu_icon="cast", default_index=0)

# if "Water Network Exploration" is selected in the main menu do the following
if selected == "Water Network Exploration":
    st.title(selected)
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]

    # The default value of date range
    ymd_range = [datetime.date(2019, 1, 1), datetime.date(2019, 1, 2)]
    col1, col2 = st.columns((2, 2))
    st.header("Data Tables")
    if st.checkbox("Show Raw Data"):
        with st.spinner('Writing in progress...'):
            st.write(df)

    with st.sidebar:
        st.header(':gear: Settings')
        st.subheader('Choose the time span:')
        # Date selector with default values and min and max values specified.
        ymd_range_temp = st.date_input("Start day - End day", [datetime.date(2019, 1, 1), datetime.date(2019, 1, 2)],
                                       min_value=datetime.date(2019, 1, 1), max_value=datetime.date(2023, 12, 31),
                                       on_change=set_default())

        if len(ymd_range_temp) == 2:
            ymd_range = ymd_range_temp
        else:
            # if user only selected starting date write this message.
            st.error('Error: You must choose an end date. Otherwise, the default value for the end date is used for'
                     ' filtering the data.')

        # divide sidebar to two columns to write end and start next to each other
        col1, col2 = st.columns((1, 1))
        with col1:
            # take time of the start day as input
            hms_start_day = st.time_input("Time of the start day", datetime.time(8, 30))
        with col2:
            # take time of the end day as input
            hms_end_day = st.time_input("Time of the end day", datetime.time(8, 30))

        st.subheader('Choose units:')  # For flow, pressure and water level
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
    selected_options = st.multiselect('Select charts ', ['Water level', 'Flow', 'Pressure'],
                                      default=['Water level', 'Flow', 'Pressure'])

    # must be used to avoid time shifting is charts
    df['Time'] = df['Time'].dt.tz_localize('EST')

    if "Water level" in selected_options:
        # rename the columns to the name that must be shown in the legend of chart (only name of the asset should remain)
        # save the result in dummy dataset called df1
        df_temp = df.rename(columns={'Bald Hill Tank_Level_ft': 'Bald Hill Tank',
                                'Scovill Tank_Level_ft':'Scovill Tank'})

        # reshape the data so that the values of different assets are all in the same column.
        # we need this reformatting for plotting based on color.
        df_temp = df_temp[['Time', 'Bald Hill Tank', 'Scovill Tank']].melt('Time', var_name='Asset', value_name='Water_Level')


        df_temp, unit_symbol  = change_unit(df_temp, 'Water_Level', 'water level', water_level_unit)

        # rename the column so that it contains the selected unit. This name is shown on the y axis
        column_name_new = f"Water Level ({unit_symbol})"
        df_temp = df_temp.rename(columns={'Water_Level': column_name_new})

        # selection to allow highlight when click on legend
        selection = alt.selection_multi(fields=['Asset'], bind='legend')

        Water_Level_Line_Chart = def_line_chart(df_temp, 'Time', column_name_new, False, False, 'Asset:N', "Asset", alt.value(1), alt.value(0.1),
                       selection, ['Time', 'Asset', column_name_new], 700, 370)

        # Create bar plot that responds to selection based on legend.
        # bar show mean values and standard deviation in selected time span.
        bars = def_bars(df_temp, column_name_new, "Asset", False, False, "Asset:O", selection, 'ci')
        chart = alt.hconcat(Water_Level_Line_Chart, bars).properties(
            title="Click on the legend to show/hide lines:")
        st.subheader("Water level charts")
        st.write(chart)

    if "Flow" in selected_options:
        df_temp = df.rename(columns={'Bald Hill Tank_Net_Flow_Out_gpm' : 'Bald Hill Tank',
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

        df_temp = df_temp[['Time', 'Bald Hill Tank', 'PRV-1',
                  'PRV-2', 'PRV-3', 'PRV-4', 'PRV-5',
                  'PRV-6', 'PRV-7', 'Well PMP-1',
                  'Well PMP-2', 'Well PMP-3', 'Well Station',
                  'WTP PMP-1', 'WTP PMP-2', 'WTP PMP-3',
                  'WTP Station', 'School']].melt('Time', var_name='Asset', value_name='Flow')

        df_temp, unit_symbol  = change_unit(df_temp, 'Flow', 'flow', flow_unit)
        column_name_new = f"Flow ({unit_symbol})"
        df_temp = df_temp.rename(columns={'Flow': column_name_new})

        # selection to allow highlight when click on legend
        selection = alt.selection_multi(fields=['Asset'], bind='legend')

        Flow_Line_Chart = def_line_chart(df_temp, 'Time', column_name_new, False, False, 'Asset:N', "Asset",
                                         alt.value(1), alt.value(0.1), selection,
                                         ['Time', 'Asset', column_name_new], 700, 370)

        # Create bar plot that responds to selection based on legend.
        # bar show mean values and standard deviation in selected time span.
        bars = def_bars(df_temp, column_name_new, "Asset", False, False, "Asset:O", selection, 'ci')
        chart = alt.hconcat(Flow_Line_Chart, bars).properties(
            title="Click on the legend to show/hide lines:"
        )
        st.subheader("Flow charts")
        st.write(chart)

    if "Pressure" in selected_options:
        df_temp = df.rename(columns={'PRV-1_FromPressure_psi' : 'PRV-1 (from)',
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

        df_temp = df_temp[['Time', 'PRV-1 (from)', 'PRV-2 (from)', 'PRV-3 (from)',
                  'PRV-4 (from)', 'PRV-5 (from)', 'PRV-6 (from)', 'PRV-7 (from)',
                  'PRV-1 (to)', 'PRV-2 (to)', 'PRV-3 (to)','PRV-4 (to)',
                  'PRV-5 (to)', 'PRV-6 (to)', 'PRV-7 (to)', 'Well (discharge)', 'Well (suction)',
                  'Well PMP-1 (discharge)', 'Well PMP-1 (suction)',
                  'Well PMP-2 (discharge)', 'Well PMP-2 (suction)',
                  'Well PMP-3 (discharge)', 'Well PMP-3 (suction)',
                  'WTP (discharge)', 'WTP (suction)', 'WTP PMP-1 (suction)', 'WTP PMP-2 (suction)',
                  'WTP PMP-3 (suction)']].melt('Time', var_name='Asset', value_name='Pressure')

        df_temp, unit_symbol = change_unit(df_temp, 'Pressure', 'pressure', pressure_unit)
        column_name_new = f"Pressure ({unit_symbol})"
        df_temp = df_temp.rename(columns={'Pressure': column_name_new})

        # selection to allow highlight when click on legend
        selection = alt.selection_multi(fields=['Asset'], bind='legend')
        Pressure_Line_Chart = def_line_chart(df_temp, 'Time', column_name_new, False, False, 'Asset:N', "Asset",
                                         alt.value(1), alt.value(0.1), selection,
                                         ['Time', 'Asset', column_name_new], 700, 370)

        # Create bar plot that responds to selection based on legend.
        # bar show mean values and standard deviation in selected time span.
        bars = def_bars(df_temp, column_name_new, "Asset", False, False, "Asset:O", selection, 'ci')
        chart = alt.hconcat(Flow_Line_Chart, bars).properties(
            title="Click on the legend to show/hide lines:"
        )
        # plot charts next to each other horizontally
        chart = alt.hconcat(Pressure_Line_Chart, bars).properties(
            title="Click on the legend to show/hide lines:"
        )
        st.subheader("Pressure charts")
        st.write(chart)

    # Explore the distribution of data
    st.header("Distributions")
    if st.checkbox("Explore distributions:"):
        selected_options_dist = st.multiselect('Select distribution variables ', ['Water level', 'Flow', 'Pressure'],
                                               default=['Water level'])

        if "Water level" in selected_options_dist:
            st.subheader("Water Level")

            df_temp = df_org
            # must be used to avoid time shifting is charts

            df_temp = df_temp.rename(columns={'Bald Hill Tank_Level_ft': 'Bald Hill Tank',
                                       'Scovill Tank_Level_ft': 'Scovill Tank'})

            # reshape the data so that the values of different assets are all in the same column.
            # we need this reformatting for plotting based on color.
            df_temp = df_temp[['Time', 'Bald Hill Tank', 'Scovill Tank']].melt('Time', var_name='Asset',
                                                                               value_name='Water_Level')

            # change values based on selected unit.
            df_temp, unit_symbol = change_unit(df_temp, 'Water_Level', 'water level', water_level_unit)

            # rename the column so that it contains the selected unit. This name is shown on the y axis
            column_name_new = f"Water Level ({unit_symbol})"
            df_temp = df_temp.rename(columns={'Water_Level': column_name_new})

            #Scatter and histogram
            colL, colM, colR = st.columns([1, 1, 1])

            with colL:
                selected_assets = st.multiselect('Select assets:', ['Bald Hill Tank', 'Scovill Tank'],
                                                      default='Bald Hill Tank')
            with colM:
                selected_years = st.multiselect('Select years:', ['2019', '2020', '2021'], default='2019')
                df_temp = mask_year(df_temp, selected_years)

            with colR:
                selected_months = st.multiselect('Select months:', ['January', 'February', 'March', 'April', 'May',
                                                                    'June', 'July', 'August', 'September', 'October',
                                                                    'November', 'December'],
                                                                    default=['January', 'February'])
                df_temp = mask_month(df_temp, selected_months)


            breakdown_selection = st.radio("Breakdown based on:", ["year", "month", "none"])
            if breakdown_selection == "none":
                df_temp['none'] = True
            df_temp_copy = df_temp
            selection = alt.selection(type="interval", encodings=["x"])
            for i in selected_assets:
                df_temp = df_temp_copy
                mask = df_temp['Asset'] == i
                df_temp = df_temp.loc[mask]
                chart = def_distribution_chart(df_temp, i, 'dayhoursminutes(Time):O', column_name_new, f"{breakdown_selection}:N", breakdown_selection, alt.value(1), alt.value(0.1), selection, 650, 350, 'count()', 300, 300, True, True, 20)
                st.write(chart)

        if "Flow" in selected_options_dist:
            st.subheader("Flow")
            df_temp = df_org
            # must be used to avoid time shifting is charts
            # reshape the data so that the values of different assets are all in the same column.
            # we need this reformatting for plotting based on color.
            df_temp = df_temp.rename(columns={'Bald Hill Tank_Net_Flow_Out_gpm': 'Bald Hill Tank',
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

            df_temp = df_temp[['Time', 'Bald Hill Tank', 'PRV-1',
                         'PRV-2', 'PRV-3', 'PRV-4', 'PRV-5',
                         'PRV-6', 'PRV-7', 'Well PMP-1',
                         'Well PMP-2', 'Well PMP-3', 'Well Station',
                         'WTP PMP-1', 'WTP PMP-2', 'WTP PMP-3',
                         'WTP Station', 'School']].melt('Time', var_name='Asset', value_name='Flow')

            # change values based on selected unit.
            df_temp, unit_symbol = change_unit(df_temp, 'Flow', 'flow', flow_unit)

            # rename the column so that it contains the selected unit. This name is shown on the y axis
            column_name_new = f"Flow ({unit_symbol})"
            df_temp = df_temp.rename(columns={'Flow': column_name_new})

            # Scatter and histogram
            colL, colM, colR = st.columns([1, 1, 1])

            with colL:
                selected_assets = st.multiselect('Select assets :', ['Bald Hill Tank', 'PRV-1','PRV-2', 'PRV-3',
                                                                    'PRV-4', 'PRV-5','PRV-6', 'PRV-7', 'Well PMP-1',
                                                                    'Well PMP-2', 'Well PMP-3', 'Well Station',
                                                                    'WTP PMP-1', 'WTP PMP-2', 'WTP PMP-3',
                                                                    'WTP Station', 'School'], default='Bald Hill Tank')
            with colM:
                selected_years = st.multiselect('Select years :', ['2019', '2020', '2021'], default="2019")
                df_temp = mask_year(df_temp, selected_years)

            with colR:
                selected_months = st.multiselect('Select months :', ['January', 'February', 'March', 'April', 'May',
                                                                    'June', 'July', 'August', 'September', 'October',
                                                                    'November', 'December'],
                                                 default=['January', 'February'])
                df_temp = mask_month(df_temp, selected_months)

            breakdown_selection = st.radio("Breakdown based on :", ["year", "month", "none"])
            if breakdown_selection == "none":
                df_temp['none'] = True
            df_temp_copy = df_temp
            selection = alt.selection(type="interval", encodings=["x"])
            for i in selected_assets:
                df_temp = df_temp_copy
                mask = df_temp['Asset'] == i
                df_temp = df_temp.loc[mask]
                chart = def_distribution_chart(df_temp, i, 'dayhoursminutes(Time):O', column_name_new,
                                               f"{breakdown_selection}:N", breakdown_selection, alt.value(1),
                                               alt.value(0.1), selection, 650, 350, 'count()', 300, 300, True, True, 20)
                st.write(chart)

        if "Pressure" in selected_options_dist:
            st.subheader("Pressure")
            df_temp = df_org
            # must be used to avoid time shifting is charts
            df_temp = df_temp.rename(columns={'PRV-1_FromPressure_psi': 'PRV-1 (from)',
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

            df_temp = df_temp[['Time', 'PRV-1 (from)', 'PRV-2 (from)', 'PRV-3 (from)',
                       'PRV-4 (from)', 'PRV-5 (from)', 'PRV-6 (from)', 'PRV-7 (from)',
                       'PRV-1 (to)', 'PRV-2 (to)', 'PRV-3 (to)', 'PRV-4 (to)',
                       'PRV-5 (to)', 'PRV-6 (to)', 'PRV-7 (to)', 'Well (discharge)', 'Well (suction)',
                       'Well PMP-1 (discharge)', 'Well PMP-1 (suction)',
                       'Well PMP-2 (discharge)', 'Well PMP-2 (suction)',
                       'Well PMP-3 (discharge)', 'Well PMP-3 (suction)',
                       'WTP (discharge)', 'WTP (suction)', 'WTP PMP-1 (suction)', 'WTP PMP-2 (suction)',
                       'WTP PMP-3 (suction)']].melt('Time', var_name='Asset', value_name='Pressure')
            # change values based on selected unit.
            df_temp, unit_symbol = change_unit(df_temp, 'Pressure', 'pressure', pressure_unit)

            # rename the column so that it contains the selected unit. This name is shown on the y axis
            column_name_new = f"Pressure ({unit_symbol})"
            df_temp = df_temp.rename(columns={'Pressure': column_name_new})

            # Scatter and histogram
            colL, colM, colR = st.columns([1, 1, 1])

            with colL:
                selected_assets = st.multiselect('Select assets', ['PRV-1 (from)', 'PRV-2 (from)', 'PRV-3 (from)',
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
            with colM:
                selected_years = st.multiselect('Select years', ['2019', '2020', '2021'], default="2019")
                df_temp = mask_year(df_temp, selected_years)

            with colR:
                selected_months = st.multiselect('Select months', ['January', 'February', 'March', 'April', 'May',
                                                                    'June', 'July', 'August', 'September', 'October',
                                                                    'November', 'December'],
                                                 default=['January', 'February'])
                df_temp = mask_month(df_temp, selected_months)

            breakdown_selection = st.radio("Breakdown based on", ["year", "month", "none"])
            if breakdown_selection == "none":
                df_temp['none'] = True
            df_temp_copy = df_temp
            selection = alt.selection(type="interval", encodings=["x"])
            for i in selected_assets:
                df_temp = df_temp_copy
                mask = df_temp['Asset'] == i
                df_temp = df_temp.loc[mask]
                chart = def_distribution_chart(df_temp, i, 'dayhoursminutes(Time):O', column_name_new,
                                               f"{breakdown_selection}:N", breakdown_selection, alt.value(1),
                                               alt.value(0.1), selection, 650, 350, 'count()', 300, 300, True, True, 20)
                st.write(chart)

if selected == "Pipe Data Exploration":
    st.title(selected)
    df_pipe_orig = df_pipe

    with st.sidebar:
        st.header(':gear: Settings')
        st.subheader('Choose the units')
        # SET UNITS
        diameter_unit = st.selectbox("Diameter:", ["inch", "millimeter"])
        length_unit = st.selectbox("Length:", ["foot", "meter"])
        discharge_unit = st.selectbox("Discharge:", ["gallon per minute", "liter per second"])
        pressure_unit = st.selectbox("Pressure:", ["pressure per square inch", "kilogram per square centimeter"])
        groundwater_unit = st.selectbox("Groundwater Depth:", ["foot", "meter"])
    st.header("Data Tables")
    if st.checkbox("Show Raw Data"):
        with st.spinner('Writing in progress...'):
            st.write(df_pipe)

    st.header("Charts")
    selected_options = st.multiselect('Select attributes ', ['Diameter', 'Length', 'Material', 'Installation Year',
                                                             'Discharge', 'Pressure', 'Pipe Bed-Soil Type',
                                                             'Groundwater Depth'], default = ['Diameter',
                                                             'Installation Year', 'Discharge',  'Pipe Bed-Soil Type'])

    # if "Data Exploration" is selected in the main menu do the following
    ### READING AND SETTING THE UNITS AND RENAMING DATAFRAME

    df_pipe, unit_symbol = change_unit(df_pipe, 'Diameter', 'diameter', diameter_unit)
    df_pipe[['Diameter']] = df_pipe[['Diameter']].round(1)
    # rename the column so that it contains the selected unit. This name is shown on the y axis
    dia_col_name = f"Diameter ({unit_symbol})"
    df_pipe = df_pipe.rename(columns={'Diameter': dia_col_name}).astype('category')

    df_pipe, unit_symbol = change_unit(df_pipe, 'LENGTH_FT', 'length', length_unit)
    df_pipe[['LENGTH_FT']] = df_pipe[['LENGTH_FT']].round(1)
    # rename the column so that it contains the selected unit. This name is shown on the y axis
    len_col_name = f"Length ({unit_symbol})"
    df_pipe = df_pipe.rename(columns={'LENGTH_FT': len_col_name})

    mat_col_name = "Material"
    df_pipe = df_pipe.rename(columns={'MATERIAL': mat_col_name}).astype('category')

    year_col_name = "Installation Year"
    df_pipe = df_pipe.rename(columns={'Install_ye': year_col_name}).astype('category')

    df_pipe, unit_symbol = change_unit(df_pipe, 'Qmax_gpm', 'discharge', discharge_unit)
    df_pipe[['Qmax_gpm']] = df_pipe[['Qmax_gpm']].round(1)
    # rename the column so that it contains the selected unit. This name is shown on the y axis
    discharge_col_name = f"Discharge ({unit_symbol})"
    df_pipe = df_pipe.rename(columns={'Qmax_gpm': discharge_col_name})

    df_pipe, unit_symbol = change_unit(df_pipe, 'Pmax_Psi', 'pressure', pressure_unit)
    df_pipe[['Pmax_Psi']] = df_pipe[['Pmax_Psi']].round(1)
    # rename the column so that it contains the selected unit. This name is shown on the y axis
    press_col_name = f"Pressure ({unit_symbol})"
    df_pipe = df_pipe.rename(columns={'Pmax_Psi': press_col_name})

    soil_col_name = "Bed-Soil"
    df_pipe = df_pipe.rename(columns={'PAR_MAT': soil_col_name}).astype('category')

    ph_col_name = "Bed-Soil pH"
    df_pipe = df_pipe.rename(columns={'PH': ph_col_name})

    df_pipe, unit_symbol = change_unit(df_pipe, 'Dist_GWT', 'ground water depth', groundwater_unit)
    df_pipe[['Dist_GWT']] = df_pipe[['Dist_GWT']].round(1)
    # rename the column so that it contains the selected unit. This name is shown on the y axis
    gwd_col_name = f"Groundwater Depth ({unit_symbol})"
    df_pipe = df_pipe.rename(columns={'Dist_GWT': gwd_col_name})

    # FOR DIAMETER
    if "Diameter" in selected_options:
        # plot the chart
        Pipe_DiaMaterial_Histogram_Chart = alt.Chart(df_pipe).mark_bar(size=20).encode(
            alt.X(dia_col_name, scale=alt.Scale(zero=False)),
            alt.Y(year_col_name, scale=alt.Scale(zero=False, type='sqrt')),
            alt.Color(mat_col_name, legend=alt.Legend(title="Material")),
            tooltip=[dia_col_name, mat_col_name, year_col_name, 'count()']
        ).properties(
            title=f"{dia_col_name} vs. Year of Installation",
            width=450, height=250
        ).interactive()

        text_DiaMaterial = alt.Chart(df_pipe).mark_text(dx=-15, dy=3, color='white').encode(
            x=alt.X(dia_col_name, stack='zero'),
            y=alt.Y(year_col_name),
            text=alt.Text('count():Q')
        )

        Pipe_DiaLength_Histogram_Chart = alt.Chart(df_pipe).mark_bar(size=20).encode(
            alt.X(dia_col_name, scale=alt.Scale(zero=True)),
            alt.Y(f"sum({len_col_name}):Q", scale=alt.Scale(zero=True)),
            alt.Color(mat_col_name, legend=alt.Legend(title="Material")),
            tooltip=[dia_col_name, mat_col_name, f"sum({len_col_name}):Q", 'count()']
        ).properties(
            title=f"{dia_col_name} vs. {len_col_name}",
            width=450, height=250
        ).interactive().resolve_scale(y='independent')
        st.write(Pipe_DiaMaterial_Histogram_Chart + text_DiaMaterial | Pipe_DiaLength_Histogram_Chart)

    # FOR LENGTH
    if "Length" in selected_options:
        # plot the chart
        Pipe_Len_Histogram_Chart = alt.Chart(df_pipe).mark_bar(size=20).encode(
            alt.X(len_col_name, type='quantitative', scale=alt.Scale(zero=False, type='log', base=2)),
            alt.Y('count()', scale=alt.Scale(zero=False, type='sqrt')),
            alt.Color(len_col_name, type='quantitative', sort="descending", legend=alt.Legend(title=f"{len_col_name}")),
            tooltip=[len_col_name, 'count()']
        ).properties(
            title=f"{len_col_name} Histogram",
            width=450, height=250
        ).interactive()

        Pipe_ZoneLength_Histogram_Chart = alt.Chart(df_pipe).mark_bar(size=20).encode(
            alt.X('ZONE', scale=alt.Scale(zero=True), sort='-y'),
            alt.Y(f"sum({len_col_name}):Q", scale=alt.Scale(zero=True)),
            alt.Color('Material', legend=alt.Legend(title="Material")),
            tooltip=['ZONE', f"sum({len_col_name}):Q", 'Material', 'count()']
        ).properties(
            title=f"Zone vs. {len_col_name}",
            width=450, height=250
        ).interactive().resolve_scale(y='independent')

        st.write(Pipe_Len_Histogram_Chart | Pipe_ZoneLength_Histogram_Chart)

    # FOR MATERIAL
    if "Material" in selected_options:
        # plot the chart
        Pipe_Mat_Histogram_Chart = alt.Chart(df_pipe).mark_bar(size=20).encode(
            alt.X(mat_col_name, type='nominal', scale=alt.Scale(zero=True), sort='-y'),
            alt.Y(f"sum({len_col_name}):Q", scale=alt.Scale(zero=True)),
            alt.Color(mat_col_name, legend=alt.Legend(title="Material")),
            tooltip=[mat_col_name, f"sum({len_col_name}):Q", 'count()']
        ).properties(
            title=f"Material vs. {len_col_name}",
            width=450, height=250
        ).interactive()

        Pipe_MatBreak_Histogram_Chart = alt.Chart(df_pipe).mark_bar(size=20).encode(
            alt.X(mat_col_name, type='nominal', scale=alt.Scale(zero=True), sort='-y'),
            alt.Y('sum(Breaks_No)', type='quantitative', scale=alt.Scale(zero=True), title="Sum of No. of Pipe Breaks"),
            alt.Color(mat_col_name, legend=alt.Legend(title="Material")),
            tooltip=[mat_col_name, 'sum(Breaks_No):Q', 'count()']
        ).properties(
            title="Material vs. Pipe Breaks reported between (2015-2020)",
            width=450, height=250
        ).interactive()

        st.write(Pipe_Mat_Histogram_Chart | Pipe_MatBreak_Histogram_Chart)

    if "Installation Year" in selected_options:
        len_unit = f"{len_col_name}"
        df_pipe = df_pipe.rename(columns={'LENGTH_FT': len_col_name})
        # plot the chart
        Pipe_YOIMaterial_Histogram_Chart = alt.Chart(df_pipe).mark_bar(size=20).encode(
            alt.X(year_col_name, type='nominal', scale=alt.Scale(zero=False), sort='-y'),
            alt.Y(f"sum({len_col_name}):Q", scale=alt.Scale(zero=False)),
            # alt.Column(YOI_unit, type='ordinal'),
            alt.Color('Material', legend=alt.Legend(title="Material")),
            tooltip=[year_col_name, f"sum({len_col_name})", 'Material', 'count()']
        ).properties(
            title=f"{len_col_name} wise Installation Year (High to Low)",
            width=450, height=250
        ).interactive()

        # plot the chart
        Pipe_YOIDiameter_Histogram_Chart = alt.Chart(df_pipe).mark_bar(size=20).encode(
            alt.X(year_col_name, type='nominal', scale=alt.Scale(zero=False), sort='x'),
            alt.Y('sum(Breaks_No):Q', scale=alt.Scale(zero=True), title="Sum of No. of Pipe Breaks"),
            alt.Color('Material', legend=alt.Legend(title="Material")),
            tooltip=[year_col_name, 'count()']
        ).properties(
            title="Year of Installation of Pipes vs. Pipe Breaks reported between (2015-2020)",
            width=450, height=250
        ).interactive()

        st.write(Pipe_YOIMaterial_Histogram_Chart | Pipe_YOIDiameter_Histogram_Chart)

    # FOR DISCHARGE
    if "Discharge" in selected_options:
        # plot the chart
        Pipe_Dis_Histogram_Chart = alt.Chart(df_pipe).mark_bar(size=10).encode(
            alt.X(discharge_col_name, type='quantitative', scale=alt.Scale(zero=True, type='quantile')),
            alt.Y('count()', scale=alt.Scale(zero=False, type='sqrt')),
            alt.Color(discharge_col_name, type='quantitative', sort="descending", legend=alt.Legend(title=f"{discharge_col_name}")),
            tooltip=[discharge_col_name, 'count()']
        ).properties(
            title=f"{discharge_col_name} Histogram",
            width=450, height=250
        ).interactive()

        Pipe_DisBreak_Histogram_Chart = alt.Chart(df_pipe).mark_bar(size=10).encode(
            alt.X(discharge_col_name, type='quantitative', scale=alt.Scale(zero=True, type='quantile')),
            alt.Y('sum(Breaks_No):Q', scale=alt.Scale(zero=False, type='sqrt'), title="Sum of No. of Pipe Breaks"),
            alt.Color(discharge_col_name, type='quantitative', sort="descending", legend=alt.Legend(title=f"{discharge_col_name}")),
            tooltip=[discharge_col_name, 'count()']
        ).properties(
            title=f"{discharge_col_name} vs. Pipe Breaks reported between (2015-2020)",
            width=450, height=250
        ).interactive()

        Pipe_DisYOI_Histogram_Chart = alt.Chart(df_pipe).mark_bar(size=20).encode(
            alt.X(f"sum({discharge_col_name}):Q", scale=alt.Scale(zero=True)),
            alt.Y(year_col_name, scale=alt.Scale(zero=True), sort='y'),
            alt.Color('Material', legend=alt.Legend(title="Material")),
            tooltip=[f"sum({discharge_col_name}):Q", 'Material', 'count()']
        ).properties(
            title=f"{discharge_col_name} wise Installation Year (High to Low)",
            width=450, height=250
        ).interactive().resolve_scale(y='independent')

        st.write((Pipe_Dis_Histogram_Chart & Pipe_DisBreak_Histogram_Chart) | Pipe_DisYOI_Histogram_Chart)

    # FOR PRESSURE
    if "Pressure" in selected_options:
        # plot the chart
        Pipe_Pre_Histogram_Chart = alt.Chart(df_pipe).mark_bar(size=10).encode(
            alt.X(press_col_name, type='quantitative', scale=alt.Scale(zero=False)),
            alt.Y('count()', scale=alt.Scale(zero=False, type='linear', base=2)),
            alt.Color(press_col_name, type='quantitative', sort="descending", legend=alt.Legend(title=f"{press_col_name}")),
            tooltip=[press_col_name, 'count()']
        ).properties(
            title=f"{press_col_name} Histogram",
            width=650, height=450
        ).interactive().resolve_scale(x='independent', y='independent')

        st.write(Pipe_Pre_Histogram_Chart)  # | Pipe_PreBreak_Histogram_Chart)
    # FOR BED SOILPH
    if "Pipe Bed-Soil Type" in selected_options:
        # plot the chart
        Pipe_BS_Histogram_Chart = alt.Chart(df_pipe).mark_bar(size=20).encode(
            alt.X(ph_col_name, scale=alt.Scale(zero=False)),
            alt.Y('sum(Breaks_No):Q', scale=alt.Scale(zero=False), title="Sum of No. of Pipe Breaks"),
            alt.Color('Material', legend=alt.Legend(title="Bed-Soil pH")),
            tooltip=[ph_col_name, 'sum(Breaks_No):Q', mat_col_name, 'count()']
        ).properties(
            title="Soil pH vs. Pipe Breaks reported between (2015-2020)",
            width=650, height=450
        ).interactive()
        st.write(Pipe_BS_Histogram_Chart)

    # FOR GROUNDWATER
    if "Groundwater Depth" in selected_options:
        # plot the chart
        Pipe_GWD_Histogram_Chart = alt.Chart(df_pipe).mark_circle(size=20).encode(
            alt.X(ph_col_name, scale=alt.Scale(zero=False), sort='x'),
            alt.Y(gwd_col_name, type='quantitative', scale=alt.Scale(zero=False, type='sqrt')),
            alt.Color('sum(Breaks_No):Q', legend=alt.Legend(title="Total Breaks (2015-2020)"),
                      scale=alt.Scale(scheme='reds')),
            tooltip=[gwd_col_name, 'sum(Breaks_No):Q', mat_col_name, 'count()'],
            size='sum(Breaks_No):Q',
        ).properties(
            title=f"{gwd_col_name} vs. Soil pH",
            width=650, height=450
        ).interactive()
        st.write(Pipe_GWD_Histogram_Chart)


if selected == "Water Usage Exploration":
    st.title(selected)
    with st.sidebar:
        st.header(':gear: Settings')
        st.subheader('Choose unit:') # could be flow, pressure and water level
        water_usage_unit = st.selectbox("Water usage:", ["kilogallon", "gallon", "cubic meter", "cubic foot", "centum cubic foot"])

    st.header("Data Tables")
    if st.checkbox("Show Raw Data"):
        with st.spinner('Writing in progress...'):
            st.write(dfu)

    st.header("Charts")
    dfu = dfu.rename(columns={'Water usage (kgal)':'Water usage'})

    colL, colR = st.columns([1, 1])
    with colL:
        selected_years = st.multiselect('Select years:', ['2019', '2020', '2021'], default="2019")
        dfu = mask_year(dfu, selected_years)
    with colR:
        selected_months = st.multiselect('Select months:', ['January', 'February', 'March', 'April', 'May',
                                                            'June', 'July', 'August', 'September', 'October',
                                                            'November', 'December'], default=['January', 'February'])
        dfu = mask_month(dfu, selected_months)


    dfu, unit_u  = change_unit(dfu, 'Water usage', 'water usage', water_usage_unit)

    column_name_u = f"Water usage ({unit_u})"
    dfu = dfu.rename(columns={'Water usage': column_name_u})
    dfu['month'] = dfu['Time'].dt.month
    dfu = rename_months(dfu)
    # selection to allow highlight when click on legend
    selection = alt.selection_interval(encodings=['x'])

    Usage_Line_Chart = alt.Chart(dfu).mark_point(filled = True).encode(
        x=alt.X('month:N', scale=alt.Scale(zero=False)),
        y=alt.Y(f'{column_name_u}:Q', scale=alt.Scale(zero=False)),
        color=alt.Color('Zone:N', legend=alt.Legend(title="Zone")),
        opacity=alt.condition(selection, alt.value(1), alt.value(0.1)),
        tooltip=['Time', 'Zone', column_name_u]
    ).properties(
        width=700, height=370
    ).add_selection(
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

    colLz, colMz, colRzL, colRzR = st.columns([1, 2, 1, 0.5])

    with colLz:
        zone_name = ["All", "Fire District", "Northern", "Oakville High", "Oakville Low", "Straits",
                                   "Town Hall"]
        selection_zone = st.radio("Select zone:", zone_name)

    with colMz:
        sum_z = []

        for i in zone_name:
            mask_z = (dfu["Zone"].astype(str) == f"{i} Zone")
            dfuz = dfu.loc[mask_z]
            dfuz[f"{column_name_u}"] = pd.to_numeric(dfuz[f"{column_name_u}"])
            sum_z.append(dfuz[f"{column_name_u}"].sum())

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
                                range=[f'{color_names[j]}', 'lightgray']))
            )
        st.write(pie_chart)

    with colRzL:
        st.subheader("Zone Statistics:")
        st.write("Number of customers:")
        st.write("Highest monthly water usage:")
        st.write("Month of highest usage:")
    with colRzR:
        if selection_zone != "All":
            mask_z = (dfu["Zone"] == f"{selection_zone} Zone")
            dfuz = dfu.loc[mask_z]
        else:
            dfuz = dfu
        n = len(pd.unique(dfuz['Customer ID']))
        n_index = zone_name.index(selection_zone)

        dfuz['month'] = dfuz['Time'].dt.month
        zone_monthly_water_usage = []
        for i in range(12):
            zone_monthly_water_usage.append(dfuz[f'{column_name_u}'].loc[dfuz["month"] == i].sum())
        max_water_usage = max(zone_monthly_water_usage)
        month_index = zone_monthly_water_usage.index(max_water_usage) + 1
        month_string = "_"
        if (max_water_usage != 0):
            month_string = Reverse_numeric_month[month_index]

        st.subheader("__________")
        st.write(f"{n}")
        st.write(f"{round(max_water_usage,1)}")
        st.write(f"{month_string}")

if selected == "Pipe-Break Prediction":
    st.title(selected)
    df_pipe_orig = df_pipe.drop("FID", axis=1)

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
            "The data model is split in 75% train and 25% test dataset; the 75% train data is further split into 60% "
            "for training and 40% for validation. The ML model is then applied on 25% of unseen data for prediction.")

        bool_learn = st.checkbox("Learn the Model:", value=True)
        if bool_learn:
            df_25 = load("https://1drv.ms/u/s!AnhaxtVMqKpxgok7oN74-f1eTi8BFw?e=yei0ZH")
            df_75 = load("https://1drv.ms/u/s!AnhaxtVMqKpxgok6rtmFtgqn1vUt_Q?e=el633O")

            # defining predictor and response variables
            st.subheader("Training Report")
            Pred = df_75[features].drop(['ID', 'Breaks_No'], axis=1)
            Resp = df_75.Breaks_No
            Pred_train, Pred_test, Resp_train, Resp_test = train_test_split(Pred, Resp, test_size=0.4, random_state=0)

            regressor = DecisionTreeRegressor(random_state=0)
            regressor.fit(Pred_train, Resp_train)
            Resp_pred = regressor.predict(Pred_test)

            MSE = metrics.mean_squared_error(Resp_test, Resp_pred)
            score = accuracy_score(Resp_test, Resp_pred)
            report = classification_report(Resp_test, Resp_pred)

            report_train_df = get_classification_report(Resp_test, Resp_pred)
            st.write(report_train_df)

            st.subheader("Testing Report")
            X_4test = df_25[features].drop(['ID', 'Breaks_No'], axis=1)
            yReal_4test = df_25.Breaks_No
            yPrediction_4test = regressor.predict(X_4test)  # Prediction on unseen test data
            report_test_df = get_classification_report(yReal_4test, yPrediction_4test)
            st.write(report_test_df)

    with col2:
        st.header("3. Enter Data")
        predi_bool = st.button("Predict number of breaks")

        st.caption(
            "Enter values for selected features to predict number of breaks based on the machine learnt algorithm.")
        if Dia_CheckBox:
            UD_Dia_in = st.selectbox('Select Diameter (in)', [4, 6, 8, 10, 12, 14, 16], index=1)
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

        input_reg = np.array(UD_features).reshape(1, -1)

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


if selected == "Water Network Management":
    df_pipe_orig = df_pipe.drop("FID", axis=1)
    st.title(selected)

    km_df = pd.DataFrame()
    features = ['ID', 'Breaks_No']

    with st.sidebar:
        st.header(':gear: Settings')

        # Input Present Year for Calculating Age
        year = st.number_input("Select year for age calculation:", value=2022)
        df_pipe_orig['Age'] = (year - df_pipe_orig['Install_ye'])

        st.subheader('Select features')

        # SELECT FEATURES FOR Classification
        col1, col2 = st.columns((1, 1))
        with col1:
            Dia_CheckBox = st.checkbox("Diameter", value=True)
            if Dia_CheckBox:
                features.append('Diameter')

            Len_CheckBox = st.checkbox("Length", value=True)
            if Len_CheckBox:
                features.append('LENGTH_FT')

            Cus_CheckBox = st.checkbox("No of Customers", value=True)
            if Cus_CheckBox:
                features.append('Ncustomers')

            Dis_CheckBox = st.checkbox("Discharge", value=True)
            if Dis_CheckBox:
                features.append('Qmax_gpm')

        with col2:
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
        km_df = df_pipe_orig[features]

        # handling outliers and scaling features
        scaler = MinMaxScaler()

        # scaling breaks
        km_df['Scaled Breaks'] = scaler.fit_transform(km_df[['Breaks_No']])

        features_pca = ['Scaled Breaks']

        def scale_feature(data, column_name, column_name_output, quantile, features, coef1, cpef2):
            IQR_Dia = data[column_name].quantile(1-quantile) - data[column_name].quantile(quantile)
            lower_bound = data[column_name].quantile(quantile) - (IQR_Dia * coef1)
            upper_bound = data[column_name].quantile(quantile) + (IQR_Dia * cpef2)
            data.loc[data[column_name] <= lower_bound, column_name] = lower_bound
            data.loc[data[column_name] >= upper_bound, column_name] = upper_bound
            data[column_name_output] = scaler.fit_transform(data[[column_name]])
            features.append(column_name)
            return data, features

        if Dia_CheckBox:
            km_df, features_pca = scale_feature(km_df, 'Diameter', 'Scaled Diameter', 0.25, features_pca, 1.5, 3)

        if Len_CheckBox:
            km_df, features_pca = scale_feature(km_df, 'LENGTH_FT', 'Scaled Length', 0.25, features_pca, 1.5, 1.5)

        if Cus_CheckBox:
            km_df, features_pca = scale_feature(km_df, 'Ncustomers', 'Scaled No of Customers', 0.25, features_pca, 3, 3)

        if Dis_CheckBox:
            km_df, features_pca = scale_feature(km_df, 'Qmax_gpm', 'Scaled Discharge', 0.25, features_pca, 1.5, 1.5)

        if Pre_CheckBox:
            km_df, features_pca = scale_feature(km_df, 'Pmax_Psi', 'Scaled Pressure', 0.25, features_pca, 1.5, 1.5)

        if Sph_CheckBox:
            km_df, features_pca = scale_feature(km_df, 'PH', 'Scaled Bed-Soil pH', 0.25, features_pca, 1.5, 1.5)

        if Age_CheckBox:
            km_df, features_pca = scale_feature(km_df, 'Age', 'Scaled Age', 0.25, features_pca, 3, 3)

        st.success("Outliers handled and features scaled successfully.")

    if st.checkbox("Show Raw Data"):
        with st.spinner('Writing in progress...'):
            st.write(df_pipe)

    if st.checkbox("Show Transformed Data"):
        with st.spinner('Writing in progress...'):
            st.write(km_df.sort_values('Breaks_No', axis=0, ascending=False))

    if st.button("Run Clustering Algorithm"):
        # dataframe for pca and kmeans
        km_df_transformed = km_df[features_pca]
        pca = PCA(n_components=2)
        pca.fit(km_df_transformed)
        scores_pca = pca.fit_transform(km_df_transformed)
        km = KMeans(n_clusters=3, random_state=0)
        y_predict_clusters = km.fit_predict(scores_pca)
        km_df['Cluster'] = y_predict_clusters

        def def_bar_chart(data, x, y, sort_x, sort_y, height, width, scheme):
            chart = alt.Chart(data).mark_bar(tooltip=True).encode(
                x=alt.X(x, sort=sort_x),
                y=alt.Y(y, sort=sort_y),
                color=alt.Color(x, scale=alt.Scale(scheme=scheme))
            ).properties(
                height=height,
                width=width).interactive()
            return chart

        def def_box_chart(data, x, y, sort_x, sort_y, height, width, scheme, mark_boxplot_size, mark_boxplot_extent):
            chart = alt.Chart(data).mark_boxplot(size=mark_boxplot_size, extent=mark_boxplot_extent).encode(
                x=alt.X(x, sort=sort_x),
                y=alt.Y(y, sort=sort_y),
                color=alt.Color(x, scale=alt.Scale(scheme=scheme))
            ).properties(
                height=height,
                width=width).interactive()
            return chart

        def def_line_chart(data, x, y, sort_x, sort_y, strokeWidth, color, point):
            chart = alt.Chart(data).mark_line(strokeWidth=strokeWidth, color=color, point=point).encode(
                x=alt.X(x, title=None, sort=sort_x),
                y=alt.Y(y, sort = sort_y),
            )
            return chart

        st.write(def_bar_chart(km_df, 'Cluster:O', 'count()', 'x', 'y', 200, 200, 'dark2'))

        boxDia = def_box_chart(km_df, 'Cluster:O', 'Scaled Diameter:Q', '-y', 'y', 200, 200, 'dark2', 50, 0)
        boxLen = def_box_chart(km_df, 'Cluster:O', 'Scaled Diameter:Q', '-y', 'y', 200, 200, 'dark2', 50, 0.5)
        boxBreak = def_box_chart(km_df, 'Cluster:O', 'Scaled Breaks:Q', '-y', 'y', 200, 200, 'dark2', 50, 0.5)
        boxAge = def_box_chart(km_df, 'Cluster:O', 'Scaled Age:Q', '-y', 'y', 200, 200, 'dark2', 50, 0.5)
        boxCust = def_box_chart(km_df, 'Cluster:O', 'Scaled No of Customers:Q', '-y', 'y', 200, 200, 'dark2', 50, 0.5)
        boxPH = def_box_chart(km_df, 'Cluster:O', 'Scaled Bed-Soil pH:Q', '-y', 'y', 200, 200, 'dark2', 50, 0.5)
        boxPmax = def_box_chart(km_df, 'Cluster:O', 'Scaled Pressure:Q', '-y', 'y', 200, 200, 'dark2', 50, 0.5)
        boxQmax = def_box_chart(km_df, 'Cluster:O', 'Scaled Discharge:Q', '-y', 'y', 200, 200, 'dark2', 50, 0.5)

        lineDia = def_line_chart(km_df, 'Cluster:O', 'mean(Scaled Diameter):Q', '-y', 'y', 1, 'black', True)
        lineLen = def_line_chart(km_df, 'Cluster:O', 'mean(Scaled Length):Q', '-y', 'y', 1, 'black', True)
        lineBreak = def_line_chart(km_df, 'Cluster:O', 'mean(Scaled Breaks):Q', '-y', 'y', 1, 'black', True)
        lineAge = def_line_chart(km_df, 'Cluster:O', 'mean(Scaled Age):Q', '-y', 'y', 1, 'black', True)
        lineCust = def_line_chart(km_df, 'Cluster:O', 'mean(Scaled No of Customers):Q', '-y', 'y', 1, 'black', True)
        linePH = def_line_chart(km_df, 'Cluster:O', 'mean(Scaled Bed-Soil pH):Q', '-y', 'y', 1, 'black', True)
        linePmax = def_line_chart(km_df, 'Cluster:O', 'mean(Scaled Pressure):Q', '-y', 'y', 1, 'black', True)
        lineQmax = def_line_chart(km_df, 'Cluster:O', 'mean(Scaled Discharge):Q', '-y', 'y', 1, 'black', True)

        st.altair_chart((boxDia + lineDia | boxLen + lineLen | boxBreak + lineBreak | boxAge + lineAge
                         | boxCust + lineCust | boxPH + linePH | boxPmax + linePmax | boxQmax + lineQmax
                         ).resolve_scale(x='independent'))
