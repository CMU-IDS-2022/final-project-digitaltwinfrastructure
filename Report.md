# Final Project Report

**Project URL**: TODO
**Video URL**: TODO
**Project Team Members**: Devashri Karve, Maral Doctor Arastoo, Tanay Kulkarni

**Abstract**: 
Every year water utilities world wide spend million of dollars on reparing and replacing water infrastructure assets. These aging assets result in many issues including but not limited to non-revenue water (NRW), leakages, etc. The subsurface (buried) assets such as pipes are also exposed to severe aging and the condition assessment of such inaccessible assets is challenging. Utilities face a major challenge to understand the inspection priority, predict breaks, or detect anamolies in consumption. This project tries to address these critical issues using a web interface that interactively visualizes sensed pressure, flow, and tank water levels; and pipe metadata viz. diameter, material, year of installation, number of reported breaks, etc. The web-app also uses advanced machine learning in the background to predict the future number of breaks on any given pipe sample and also categorizes all the pipes to identify the inspection priority based on assessed condition.

## Introduction

## Related Work

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

