# Final Project Report

**Project URL**: TODO
**Video URL**: TODO
**Project Team Members**: Devashri Karve, Maral Doctor Arastoo, Tanay Kulkarni

**Abstract**: 
Every year water utilities worldwide spend millions of dollars on repairing and replacing water infrastructure assets. These aging assets result in many issues including but not limited to non-revenue water (NRW), leakages, etc. The subsurface (buried) assets such as pipes are also exposed to severe aging and the condition assessment of such inaccessible assets is challenging. Utilities face a major challenge to understand the inspection priority, predict breaks, or detect anomalies in consumption. This project tries to address these critical issues using a web interface that interactively visualizes sensed pressure, flow, and tank water levels, and pipe metadata viz., diameter, material, year of installation, number of reported breaks, etc. The web-app also uses advanced machine learning in the background to predict the future number of breaks on any given pipe sample and categorizes all the pipes to identify the inspection priority based on assessed condition.

## Introduction



## Related Work
Many infrastructure software companies have started offering digital solutions for real time operations and maintenance of water infrastructure systems. These include, but are not limited to, Bentley Systems Inc., Autodesk Inc., Xylem Inc., etc. The cloud-based applications are accessible remotely from any device and greatly add value in terms of capital, time, and manpower investments for water utilities. The inspiration for this work comes from one such cloud-based application - Bentley OpenFlows WaterSight (https://www.bentley.com/en/products/product-line/hydraulics-and-hydrology-software/openflows-watersight) that provides a unified platform for Utility GIS, Hydraulic Modeling, SCADA (Supervisory Control and Data Acquisition) Systems, and Customer Information Systems. This 'digital twin' technology for smarter operations of water infrastructure systems is widely desirable by water utilities as it enables computation of present, historic, and forecasted performance for every asset within the system. A few of the advanced capabilities of this tool includes, managing system emergency response, detecting system anomalies, controlling pressures, managing energy use, identifying water loss/ flow, and elevating engineering and operations efficiency.


## Methods

***Water Network Exploration***:

***Water Usage Exploration***:


***Pipe Data Exploration***:
The Pipe Data Exploration page in the application helps the user visualize feature data in an exploratory manner that establishes inter-feature correlation and generates useful insights.
The raw pipe Dataframe has pipe features such as diameter, length, bed-soil pH, number of customers, discharge, pressure, age, and number of breaks. These features are used to create visualization charts that reveal more insights on these features. The user interface has a main "Charts" window and a sidebar. 

![PipeDataExploration_SettingsSidebar](https://user-images.githubusercontent.com/97647504/165863839-d44fa564-6229-4236-82e9-02c6b7a4fdac.png)

The ‘settings’ on the sidebar allows to interactively change the units of various features and shift between US Customary and Systems International (SI) units. The chart on the main window responsively updates as per the set units. The 'Show Raw Data' checkbox below the "Data Tables" heading allows user to navigate through the raw data. The users can select multiple attributes of their interest and the application will show insightful charts thus enabling users to understand relations between various features.

***Pipe-Breaks Prediction***:
This page allows the user to predict the number of breaks on any sample pipe based on the features (or sample data) that the user selects based on a ML algorithm. The page has a settings sidebar and a main "Pipe Break Prediction" window. Under the 'Settings' options the user can define the year for calculating 'Age' of the pipes and select the features interactively to train and test the model. On the main “Pipe-Break Prediction” window, under the “1. Data Tables” header, the user can look at the original raw data and the data only for user-selected features by checking “Show raw data” and “Show selected data” checkboxes. Under the “2. Machine Learning” header, the user can allow the app to train and learn the ML algorithm by checking the “Learn the Model:” checkbox. Upon selecting that checkbox, the model generates “Training Report” and “Testing Report” for the user to understand “how well?” the ML model performed. Based on the “accuracy score” interactively select or remove any feature and understand the influence of that feature on the model. Under the “3. Enter Data”, the user can enter the values of selected features from the “Select Feature” option under Settings in sidebar, and the ML model will predict the number of breaks when the user hits “Predict number of breaks” button above the data entry fields. The predicted number of breaks are shown under the “Predicted Break(s):” header on the extreme right of the window.

![PipeBreakPrediction_SettingsSidebar](https://user-images.githubusercontent.com/97647504/165863695-cfc48e12-1ab0-4680-8c30-3cd56a94d660.png)

The pipe Dataframe is split in 75% model and 25% test Datasets. The 75% model dataset is further split into 60% train and 40% validation datasets. The ML model is trained on the train dataset and then checked against the validation data. The validated model is then applied to the remaining 25% of the unseen test data for prediction. The Decision-Tree Regressor algorithm uses pipe data viz. diameter, length, bed-soil pH, number of customers, discharge, pressure, and age as predictor variables, and number of breaks as the response variable.
The sidebar allows the user to interactively select predictor variables of their choice to train - test the model. The training and testing model reports are displayed. The precision, recall, f1-scores, and support. 

***Water Network Management***:
The Water Network Management page of the web application allow the user to better understand the data based on different clusters. These insights can be used to strategically fix inspection priorities of various pipeline clusters. Under the 'Settings' options the user can select the features interactively develop clusters. On the main “Water Network Management” window, the user can look at the original raw data and the data only for user-selected features by checking “Show raw data” and “Show transformed data” checkboxes. The application runs a KMeans clustering algorithm to generate clusters based on the selection of features and displays it on the main window.
![WaterNetworkManagement_SettingsSidebar](https://user-images.githubusercontent.com/97647504/165865228-702e96e2-efbd-4779-95e7-8a280b706c5c.png)

KMeans clustering is deployed for classifying pipes. There are a total of 1219 pipe data rows in the original dataframe: also consisting of feature outliers. Therefore, to preserve data, the outliers are snapped to upper and lower bounds at 25% Inter-quartile range and 75% inter-quartile range, respectively. K-Means is a distance-based algorithm and therefore scaling all the features is quintessential. The features are then scaled between 0 to 1. The user can interactively select attributes from a list of features viz., diameter, length, bed-soil pH, number of customers, discharge, pressure, age, and number of breaks. 

## Results


## Discussion
***Pipe Data Exploration***:
![Diameter vs  Year of Installation](https://user-images.githubusercontent.com/98185275/165869717-502166d8-a36e-4959-82aa-40695a2ec55e.png)
Maximum pipes in the network are Ductile Iron and Cast Iron and they are older than 70 years. Hence, these pipes are close to their theorotical life expectancy. 
![Year of Installation vs  Sum of Pipe Breaks](https://user-images.githubusercontent.com/98185275/165869830-8f5dba95-064c-4907-a5b0-af9178724eb8.png)
Maximum number of breaks are recorded in Ductile Iron and Cast Iron pipes which were installed before 1955.
![Discharge vs  Installation year](https://user-images.githubusercontent.com/98185275/165869898-fc7477f1-7a6f-4352-aebb-05eb7a1b3b36.png)
Significant amount of discharge is carried by the Ductile/Cast Iron pipes installed before 1955, which are more prone to breaks. The network reliability is lower as these pipes affect significant number of consuers.
![Bed Soil pH vs  Sum of Pipe Breaks](https://user-images.githubusercontent.com/98185275/165870036-7ef1b1c0-9ec6-4fd2-a36d-cab016cbc27f.png)
Most of the breaks are observed in the pipes which are burried in the soils with pH<6. As lower pH indicates higher acidity in the soils, the corrosion rate of the pipe material in these soils is more.

***Pipe-Breaks Prediction***:



***Water Network Management***:


## Future Work
This project can be a good starting point towards a more sophisticated cloud application that can collected real-time data from utility systems such as SCADA. More work can be performed in the real-time visualization and monitoring space. Utility's Revenue Management System can be connected, and customer billing records can be accessed to predict the monthly or annual consumption and billing. A lot can also be done to handle water auditing and minimize NRW.

## Acknowledgement
The authors thanks and acknowledges the support of Dr. Tom Walski and Shar Govindan from Bentley Systems Inc.(www.bentley.com) for sharing the Watertown, Connecticut dataset for this project. A special thanks to Dr. Adam Perer- the course instructor, and the course TAs: Venkat Sivaraman, Aditi Sharma, and Jingyi Zhang.

