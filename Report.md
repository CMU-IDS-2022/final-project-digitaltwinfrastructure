# Final Project Report

**Project URL**: TODO
**Video URL**: TODO
**Project Team Members**: Devashri Karve, Maral Doctor Arastoo, Tanay Kulkarni

**Abstract**: 
Every year water utilities world wide spend million of dollars on reparing and replacing water infrastructure assets. These aging assets result in many issues including but not limited to non-revenue water (NRW), leakages, etc. The subsurface (buried) assets such as pipes are also exposed to severe aging and the condition assessment of such inaccessible assets is challenging. Utilities face a major challenge to understand the inspection priority, predict breaks, or detect anamolies in consumption. This project tries to address these critical issues using a web interface that interactively visualizes sensed pressure, flow, and tank water levels; and pipe metadata viz., diameter, material, year of installation, number of reported breaks, etc. The web-app also uses advanced machine learning in the background to predict the future number of breaks on any given pipe sample and also categorizes all the pipes to identify the inspection priority based on assessed condition.

## Introduction

## Related Work
Many infrastructure software companies have started offering digital solutions for real time operations and maintenance of water infrastructure systems. These include, but are not limited to, Bentley Systems Inc., Autodesk Inc., Xylem Inc., etc. The cloud-based applications are accessible remotely from any device and greatly add value in terms of capital, time, and manpower investments for water utilities. The inspiration for this work comes from one such cloud-based application - Bentley OpenFlows WaterSight (https://www.bentley.com/en/products/product-line/hydraulics-and-hydrology-software/openflows-watersight) that provides a unified platform for Utility GIS, Hydraulic Modeling, SCADA (Supervisory Control and Data Acquisition) Systems, and Customer Information Systems. This 'digital twin' technology for smarter operations of water infrastructure systems is widely desirable by water utilities as it enables computation of present, historic, and forecasted performance for every asset within the system. A few of the advanced capabilities of this tool includes, managing system emergency response, detecting system anomalies, controlling pressures, managing energy use, identifying water loss/ flow, and elevating engineering and operations efficiency. 


## Methods

***Pipe Data Exploration***:
Pipe properties such as diameter, length, bed-soil pH, number of customers, discharge, pressure, age, and number of breaks are used to create visualization charts. The charts are created using altair and deployed using Streamlit.

***Pipe-Breaks Prediction***:
The aglorithm used here is Decision-Tree Regressor. The algorithm uses pipe data viz. diameter, length, bed-soil pH, number of customers, discharge, pressure, and age as predictor variables, and number of breaks as the response variable. Streamlit is used to deploy the app on the web.

***Water Network Management***:
KMeans clustering is deployed for classifying pipes. The attributes considered are diameter, length, bed-soil pH, number of customers, discharge, pressure, age, and number of breaks. The visualizations are made using Altair and deployed on the web using Streamlit.

## Results

## Discussion

## Future Work
This project can be a good starting point towards a more sophisticated cloud application that can collected real-time data from utility systems such as SCADA. More work can be performed in the real-time visualization and monitoring space. Utility's Revenue Management System can be connected and customer billing records can be accessed to predict the monthly or annual consumption and billing. A lot can also be done to handle water auditing and minimize NRW.

## Acknowledgement
The authors thanks and acknowledges the support of Dr. Tom Walski and Shar Govindan from Bentley Systems Inc.(www.bentley.com) for sharing the dataset for this project. A special thanks to Dr. Adam Perer- the course instructor, and the course TAs: Venkat Sivaraman, Aditi Sharma, and Jingyi Zhang.

