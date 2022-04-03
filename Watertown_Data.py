import numpy as np
import pandas as pd
import streamlit as st
import base64

#Functions
def create_onedrive_directdownload (onedrive_link):
    data_bytes64 = base64.b64encode(bytes(onedrive_link, 'utf-8'))
    data_bytes64_String = data_bytes64.decode('utf-8').replace('/','_').replace('+','-').rstrip("=")
    resultUrl = f"https://api.onedrive.com/v1.0/shares/u!{data_bytes64_String}/root/content"
    return resultUrl

@st.cache
def load(url):
    return pd.read_csv(create_onedrive_directdownload(url))

#Main Code

st.header("Watertown Water Network")
df = load("https://1drv.ms/u/s!AnhaxtVMqKpxgoV60EUsXBEpQ-YQUA?e=BGYuTT")
print("Reading dataset...")

if st.checkbox("Show Raw Data"):
    st.write(df)