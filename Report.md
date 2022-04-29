# Final Project Report

**Project URL**: https://share.streamlit.io/cmu-ids-2022/final-project-digitaltwinfrastructure/main/Streamlit_app.py

**Video URL**: https://github.com/CMU-IDS-2022/final-project-digitaltwinfrastructure/blob/7835633049c16a0f77698f392dd9bc2f86d31cb4/DigitalTwinInfrastructure.mp4

**Project Team Members**: Devashri Karve, Maral Doctor Arastoo, Tanay Kulkarni

**Abstract**: 
Every year water utilities worldwide spend millions of dollars on repairing and replacing water infrastructure assets. These aging assets result in many issues including but not limited to non-revenue water (NRW), leakages, etc. The subsurface (buried) assets such as pipes are also exposed to severe aging and the condition assessment of such inaccessible assets is challenging. Utilities face a major challenge to understand the inspection priority, predict breaks, or detect anomalies in consumption. This project tries to address these critical issues using a web interface that interactively visualizes sensed pressure, flow, and tank water levels, monthly water usage of customer and pipe metadata viz., diameter, material, year of installation, number of reported breaks, etc. The web-app also uses advanced machine learning in the background to predict the future number of breaks on any given pipe sample and categorizes all the pipes to identify the inspection priority based on assessed condition.

## Introduction
This is an interactive web based application that reads data of water infrastrcutre assets such as pipe, customer consumption records, and sensor data from various assets such as tanks, valves and pumps. It enables user to derive insights about these data through five of its tabs using different kinds of visualizations. There are five tabs in this web app viz., Water Network Exploration, Water Usage Exploration, Pipe Data Exploration, Pipe-Break Prediction, and Water Network Management. 

## Related Work
Many infrastructure software companies have started offering digital solutions for real time operations and maintenance of water infrastructure systems. These include, but are not limited to, Bentley Systems Inc., Autodesk Inc., Xylem Inc., etc. The cloud-based applications are accessible remotely from any device and greatly add value in terms of capital, time, and manpower investments for water utilities. The inspiration for this work comes from one such cloud-based application - Bentley OpenFlows WaterSight (https://www.bentley.com/en/products/product-line/hydraulics-and-hydrology-software/openflows-watersight) that provides a unified platform for Utility GIS, Hydraulic Modeling, SCADA (Supervisory Control and Data Acquisition) Systems, and Customer Information Systems. This 'digital twin' technology for smarter operations of water infrastructure systems is widely desirable by water utilities as it enables computation of present, historic, and forecasted performance for every asset within the system. A few of the advanced capabilities of this tool includes, managing system emergency response, detecting system anomalies, controlling pressures, managing energy use, identifying water loss/ flow, and elevating engineering and operations efficiency.

## Methods

***Water Network Exploration***:
In the "Water Network Exploration" the sensor readings of water level in tanks, flow in tanks and valves and pumps and also pressure at valves and pumps are explored. User can view the raw data by selecting the related checkbox. Using the settings the user can filter these data by selecting a "Start date" and "End date" and specifying the hour of these days. By checking the "Show filtered data" checkbox the user can see data in the specified time span. The filtered data is then used to plot time series of sensor readings. For each reading type selected in multiselect box a chart will be depicted that shows how the sensor reading of each asset changes over time. Also, a bar chart is used to show the average and standard deviation (using a tick mark) of the shown data. Using the settings user can change the unit of the chart to her desired unit to make have a better sense of values. As in some charts there might be a lot of assets, it has been made possible to hide some layers using the legend of the chart.


![maral2](https://user-images.githubusercontent.com/97647504/165880280-09a470ac-9b77-4dfe-a791-a5cf6b7a0349.jpeg)

![maral4](https://user-images.githubusercontent.com/97647504/165880297-fe8d4e2f-1bb2-4448-b76c-bc823a6d4d24.jpeg)
By checking the "Distribution" checkbox a multiselect box appears. User can select variables of interest and for each variable three multiselect boxes appear. One of the multiselect boxes is used to choose assets of interest. For each selected asset a chart will be ploted that show how values change during the weeks of selected years and months. These distruibution charts are important in water network management as the decisions are made under uncertainty. Using this charts decision makers can decide for operation of water network with their desired confidence interval. The right-hand side histogram shows the distribution of data in all weeks of selected time span. User can filter specific times of week to explore the distribution say in times of highest demand. Using the radio button user can choose to see different colors for different years or months.

***Water Usage Exploration***:
In the "Water Usage Exploration" the monthly water usage of the water network customers is explored. User can view the raw data by selecting the related checkbox. Using the multiselect boxes the user can filter based on years and months. The filtered data is used to plot monthly water usage of customers color coded based on the six zones of the city (see the legend). The barchart shows the average monthly water usage of customers of each zone. This chart is very insigtful as abrupt jumps in this chart can be a sign of possible pipe leakages in that zone. User can also filter the data using the scatter plot. 

![Maral1](https://user-images.githubusercontent.com/97647504/165880043-b6d5eedb-09df-42aa-8a07-d3a6684c806c.png)



![Maral](https://user-images.githubusercontent.com/97647504/165880071-61fa1420-cd1a-445d-acb0-8b1aded0a3ab.png)


At the buttom of the page a pie chart is used that show the portion of each zone from total water usage in selected time span. A summary of zone characteristics is written on the right hand side of the page showing information about "Number of customers", "Highest monthly water usage" and "Month of highest usage". User can see the information of her zone of interest using the radio button. This chart helps the decision maker to decide for size of the tanks and power of the pumps in each zone by knowing the demand that each zone puts on the water netwrok.

***Pipe Data Exploration***:
The Pipe Data Exploration page in the application helps the user visualize feature data in an exploratory manner that establishes inter-feature correlation and generates useful insights. The raw pipe Dataframe has pipe features such as diameter, length, bed-soil pH, number of customers, discharge, pressure, age, and number of breaks. These features are used to create visualization charts that reveal more insights on these features. The user interface has a main "Charts" window and a sidebar. 

![PipeDataExploration_SettingsSidebar](https://user-images.githubusercontent.com/97647504/165863839-d44fa564-6229-4236-82e9-02c6b7a4fdac.png)

The ‘settings’ on the sidebar allows to interactively change the units of various features and shift between US Customary and Systems International (SI) units. The chart on the main window responsively updates as per the set units. The 'Show Raw Data' checkbox below the "Data Tables" heading allows user to navigate through the raw data. The users can select multiple attributes of their interest and the application will show insightful charts thus enabling users to understand relations between various features.

***Pipe-Breaks Prediction***:
This page allows the user to predict the number of breaks on any sample pipe based on the features (or sample data) that the user selects based on a ML algorithm. The page has a settings sidebar and a main "Pipe Break Prediction" window. Under the 'Settings' options the user can define the year for calculating 'Age' of the pipes and select the features interactively to train and test the model. On the main “Pipe-Break Prediction” window, under the “1. Data Tables” header, the user can look at the original raw data and the data only for user-selected features by checking “Show raw data” and “Show selected data” checkboxes. Under the “2. Machine Learning” header, the user can allow the app to train and learn the ML algorithm by checking the “Learn the Model:” checkbox. Upon selecting that checkbox, the model generates “Training Report” and “Testing Report” for the user to understand “how well?” the ML model performs. Based on the “accuracy score” interactively select or remove any feature and understand the influence of that feature on the model. Under the “3. Enter Data”, the user can enter the values of selected features from the “Select Feature” option under Settings in sidebar, and the ML model will predict the number of breaks when the user hits “Predict number of breaks” button above the data entry fields. The predicted number of breaks are shown under the “Predicted Break(s):” header on the extreme right of the window.

![PipeBreakPrediction_SettingsSidebar](https://user-images.githubusercontent.com/97647504/165863695-cfc48e12-1ab0-4680-8c30-3cd56a94d660.png)

The pipe Dataframe is split in 75% model and 25% test Datasets. The 75% model dataset is further split into 60% train and 40% validation datasets. The ML model is trained on the train dataset and then checked against the validation data. The validated model is then applied to the remaining 25% of the unseen test data for prediction. The Decision-Tree Regressor algorithm uses pipe data viz. diameter, length, bed-soil pH, number of customers, discharge, pressure, and age as predictor variables, and number of breaks as the response variable.
The sidebar allows the user to interactively select predictor variables of their choice to train - test the model. The training and testing model reports are displayed. The precision, recall, f1-scores, and support. 

***Water Network Management***:
The Water Network Management page of the web application allow the user to better understand the data based on different clusters. These insights can be used to strategically fix inspection priorities of various pipeline clusters. Under the 'Settings' options the user can select the features interactively develop clusters. On the main “Water Network Management” window, the user can look at the original raw data and the data only for user-selected features by checking “Show raw data” and “Show transformed data” checkboxes. The application runs a KMeans clustering algorithm to generate clusters based on the selection of features and displays it on the main window.
![WaterNetworkManagement_SettingsSidebar](https://user-images.githubusercontent.com/97647504/165865228-702e96e2-efbd-4779-95e7-8a280b706c5c.png)

KMeans clustering is deployed for classifying pipes. There are a total of 1219 pipe data rows in the original dataframe: also consisting of feature outliers. Therefore, to preserve data, the outliers are snapped to upper and lower bounds at 25% Inter-quartile range and 75% inter-quartile range, respectively. K-Means is a distance-based algorithm and therefore scaling all the features is quintessential. The features are then scaled between 0 to 1. The user can interactively select attributes from a list of features viz., diameter, length, bed-soil pH, number of customers, discharge, pressure, age, and number of breaks. 

## Results

***Pipe-Break Prediction***
The Decision Tree Regressor ML model performs fairly good in predicting the number of breaks with selected sets of features. The model, when all the features are selected bears a prediction accuracy of 68.5% on testing dataset. This can be further improved by training the model on larger datasets and with more variety of data features. Additionally, a Random Forest or other Regressions can also be used in future to check any improvement in the accuracy.

***KMeans Clustering***
The optimum number of clusters identified as 3 for this particular data by the Elbow Method. The pipes with similar traits are divided into 3 clusters using K-means clustering. The clusters generated produces meaningful insights from the dataset. The this is discussed in the above section.


## Discussion
***Pipe Data Exploration***:

![Diameter vs  Year of Installation](https://user-images.githubusercontent.com/98185275/165871302-0901ea2b-abed-4093-85ff-9e16a0d9ee7c.png)

The above chart shows that maximum number of pipes in the network are Ductile Iron and Cast Iron and they are older than 70 years. Hence, these pipes are close to their theorotical life expectancy.

![Year of Installation vs  Sum of Pipe Breaks](https://user-images.githubusercontent.com/98185275/165870571-74b3396c-c4d8-44cd-bf81-a8bb22a58537.png)

The above chart shows that maximum number of breaks are recorded in Ductile Iron and Cast Iron pipes which were installed before 1955.

![Discharge vs  Installation year](https://user-images.githubusercontent.com/98185275/165870578-2e825685-55eb-478a-b3fb-249e167bec17.png)

The above chart shows that significant amount of discharge is carried by the Ductile/Cast Iron pipes installed before 1955, which are more prone to breaks. The network reliability is lower as these pipes affect significant number of consuers.

![Bed Soil pH vs  Sum of Pipe Breaks](https://user-images.githubusercontent.com/98185275/165870587-09ba82e8-c19c-4ff4-9ed3-49de7ba86eaa.png)

The above chart shows that most of the breaks are observed in the pipes which are burried in the soils with pH<6. As lower pH indicates higher acidity in the soils, the corrosion rate of the pipe material in these soils is more.

These key insights gained from the exploratory analysis of pipe data can help the water utility better understand their network infrastructure in order to strategize key inspection schedules, replacement strategies, or any other maintenance/ repairs activities.

***Pipe-Breaks Prediction***:
The selection of features to learn the model is flexible. The user can choose any/all the features and the app will show summary results for the model. This helps user understand the importance or role of various features to acieve more model accuracy. The year settings allow users to select any year as current year using which, the app calculates age of pipe to be used in the model. 

![ML Model building](https://user-images.githubusercontent.com/98185275/165872033-71444a94-471b-48c2-bf6b-e1dc668068fa.png)

These features enable the user to dynamicaly understand the changes in ML model with changes in features, allowing them to easily choose a model with more accuracy.
Once the model is created and tested, the app allows user to enter any values for the selected features to dynamically predict number of breaks for a pipe having those feature values.

![Dynamic Prediction](https://user-images.githubusercontent.com/98185275/165872193-e3289e47-c346-4345-b9b9-a0a1d200b7d9.png)

This feature applies the learnt model on user entered set of predictor variable to predict the target variable.

***Water Network Management***:
This tab enables user to visualize clustering results. The box plots show that the cluster number 1 (orange color) has pipes with higher length, more number of recorded breaks, comparitively (slightly) lower ages, more number of customers, burried in soils having lower pH(that is more corrosion rate), undergo higher water pressures and slightly lower water discharges. These clusters with common traits of pipes may help the user to interprete the potential risk of pipe condition deterioration/damage on pipe and decide the inspection priority accordingly.
![visualization (1)](https://user-images.githubusercontent.com/98185275/165873542-aa344069-2480-4e02-bca3-c9456412d5d1.png)


## Future Work
This project can be a good starting point towards a more sophisticated cloud application that can collected real-time data from utility systems such as SCADA. More work can be performed in the real-time visualization and monitoring space. Utility's Revenue Management System can be connected, and customer billing records can be accessed to predict the monthly or annual consumption and billing. A lot can also be done to handle water auditing and minimize NRW.

## Acknowledgement
The authors thanks and acknowledges the support of Dr. Tom Walski and Shar Govindan from Bentley Systems Inc.(www.bentley.com) for sharing the Watertown, Connecticut dataset for this project. A special thanks to Dr. Adam Perer- the course instructor, and the course TAs: Venkat Sivaraman, Aditi Sharma, and Jingyi Zhang.

