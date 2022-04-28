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
The raw pipe Dataframe has pipe features such as diameter, length, bed-soil pH, number of customers, discharge, pressure, age, and number of breaks. These features are used to create visualization charts that reveal more insights on these features. The user interface has a main window and a sidebar. The ‘settings’ on the sidebar allows to interactively change the units of various features and shift between US Customary and Systems International (SI) units. The chart on the main window responsively updates as per the set units.

***Pipe-Breaks Prediction***:
The pipe Dataframe is split in 75% model and 25% test Datasets. The 75% model dataset is further split into 60% train and 40% validation datasets. The ML model is trained on the train dataset and then checked against the validation data. The validated model is then applied to the remaining 25% of the unseen test data for prediction. The Decision-Tree Regressor algorithm uses pipe data viz. diameter, length, bed-soil pH, number of customers, discharge, pressure, and age as predictor variables, and number of breaks as the response variable.
The sidebar allows the user to interactively select predictor variables of their choice to train - test the model. The training and testing model reports are displayed. The precision, recall, f1-scores, and support. 

***Water Network Management***:
KMeans clustering is deployed for classifying pipes. There are a total of 1219 pipe data rows in the original dataframe; also consisting of feature outliers. Therefore, to preserve data, the outliers are snapped to upper and lower bounds at 25% Inter-quartile range and 75% inter-quartile range, respectively. K-Means is a distance-based algorithm and therefore scaling all the features is quintessential. The features are then scaled between 0 to 1. The user can interactively select attributes from a list of features viz., diameter, length, bed-soil pH, number of customers, discharge, pressure, age, and number of breaks. 


## Results

## Discussion

## Future Work
This project can be a good starting point towards a more sophisticated cloud application that can collected real-time data from utility systems such as SCADA. More work can be performed in the real-time visualization and monitoring space. Utility's Revenue Management System can be connected and customer billing records can be accessed to predict the monthly or annual consumption and billing. A lot can also be done to handle water auditing and minimize NRW.

## Acknowledgement
The authors thanks and acknowledges the support of Dr. Tom Walski and Shar Govindan from Bentley Systems Inc.(www.bentley.com) for sharing the dataset for this project. A special thanks to Dr. Adam Perer- the course instructor, and the course TAs: Venkat Sivaraman, Aditi Sharma, and Jingyi Zhang.

