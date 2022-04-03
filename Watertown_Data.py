# -*- coding: utf-8 -*-
"""
#Maral has changed this file
Created on Sat Apr  2 10:02:55 2022
#Now tanay has changed this file
@author: Tanay
#Devashri has changed this file
"""

import numpy as np
import pandas as pd


#df = pd.read_table("C:/Users/Tanay/Desktop/GIS Data From TWalski/SCADA.txt", header = None)
#print(df.head())

import pyodbc
print("opening db...")

conn_string = (
    r"Driver={Microsoft Access Driver (*.mdb, *.accdb)};"
    r"DBQ=C:\Users\Tanay\Desktop\GIS Data From TWalski\SCADA.accdb;"
    )

conn = pyodbc.connect(conn_string)
print("selecting...")
sql = "Select * From SCADA"
data = pd.read_sql(sql, conn)
print(data.head())

conn.close()
