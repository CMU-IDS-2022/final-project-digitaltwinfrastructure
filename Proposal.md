# Final Project Proposal

**GitHub Repo URL**: https://github.com/CMU-IDS-2022/final-project-digitaltwinfrastructure/

**Team Members:** Devashri Karve, Maral Doctorarastoo, Tanay Kulkarni

**Problem Description**
Water companies, utilities and boards worldwide have the crucial responsibility of planning, designing, constructing, operating and maintaining the humongous water supply network infrastructure that ensures a sustainable and equitable delivery of clean, potable water to the citizens. The utilities have separate departments and teams of engineers working on different stages of these water supply projects (viz. Plan, design, build, operate, maintain). Utilities face many challenges in getting a holistic singular view of the entire infrastructure which can be accessed from anywhere at anytime on the cloud. A comprehensive cloud-based dashboard that provides access to a geospatial view of this massive infrastructure and historical SCADA (Supervisory Controls and Data Acquisition, especially, Automated Metering Infrastructure) data coming from the field is highly desirable for stakeholders and operators of the water utility.

*Two of the main challenges that water utilities face are listed below:*

**1. Maintenance of water network**
- Aging water infrastructure assets cause breaks, impacted service, malfunctions, water loss, water quality issues, etc.
- Replacement of those assets requires heavy capital investment and manpower.
- Therefore, there is a huge need to identify critical assets that must be replaced or rehabilitated.

**2. Operations of water network**
- Water network operations is a huge task
- Operation of water infrastructure is done in different scales depending on the decision that the operator is trying to make. Some tasks require a complete view of the water network in a city-scale. On the other hand, some tasks need more local information such as total annual consumption and trends on zone level. Therefore, any dashboard provided for water network operators should be able to summarize the information on different levels of detail.

**Project Scope and Assumptions**
- Developing a dashboard that helps operators/utilities understand water consumption trends, identify critical pipes that need replacement or rehabilitation, and identify the customers that will be affected due to repair work.  It ultimately helps stakeholders to prevent or minimize water outage.
- Limited to a small city “Watertown, Connecticut” but it could be replicated for any water network.
- The ‘5 year (2015-2021) pipe break historical data’ and ‘3 year (2019-2022) customer billing data’ for Watertown is provided by Bentley Systems Inc. 
- The physical model of the water network is assumed unchanged because of any modification to the digital model. 
- Water Auditing by tallying how much water is pumped, stored, and consumed. 
- Considering population growth over years and correlating it with the rate of change in water demands. We are not considering new buildings being constructed in the future. (at this stage, we have not finalized on whether to add this to the scope or not).

**Proposed Solution**

**Maintenance Dashboard:**
- The historical data of pipe breakage for 3 years, along with other important independent variables viz., age (year of installation), material, and diameter of pipes, internal water pressures, volume of water in the pipes can be consumed to learn and train a ML model to identify potentially critical pipes that need immediate attention or replacement and predict future breaks on pipes. 
- **Visualization:** The dashboard comprises the GIS enabled aerial map of Watertown that shows the water network elements such as pipes, tanks, pumps, valves, etc. It is going to be an interactive map that allows users to zoom in and out, select, navigate etc. in order to gain knowledge about the past, current and future status of pipelines in the network using a slider. 

**Operations Dashboard:**
- On the operator side, the trend of water consumption is used as a benchmark to predict the future trends of water consumption of the city. This dashboard can provide the operator with insights about the trending water consumption on a meter, zone, and city level. It will also help the operators to correlate the city’s water consumption with other equally important factors like climate (temperature, etc.), population density or growth, etc.
- **Visualization:** The dashboard will have a GIS map showing different zones of the city, and water network assets. The user will be able to interact with the map. There will be bar charts showing the monthly consumption depending on the level which the user selects (i.e., meter level, zone level, or entire city). Similarly there will be time series charts that would show historical trends of consumption and the predicted consumption, etc. There would be sliders, check boxes, etc. to facilitate the user interact with the application as needed. Broadly speaking, a few sketches have been attached to this writeup to best express our thoughts and ideas as of today.

Sketch 1
![image](https://github.com/CMU-IDS-2022/final-project-digitaltwinfrastructure/blob/12e280a92d0c346b5a4f7a6c21d0427d4829a51a/DraftSketch_1.jpeg)

Sketch 2
![image](https://github.com/CMU-IDS-2022/final-project-digitaltwinfrastructure/blob/40662ec9d13dacd70164afd64ec3aa911efbb6d1/DraftSketch_2.jpeg)

Sketch 3
![image](https://github.com/CMU-IDS-2022/final-project-digitaltwinfrastructure/blob/40662ec9d13dacd70164afd64ec3aa911efbb6d1/DraftSketch_3.jpeg)

**Data Processing**

The dataset of watertown consists of two parts: Water network data and costumer bills. We will explore each in the following paragraphs.
Graph 1

![image](https://github.com/CMU-IDS-2022/final-project-digitaltwinfrastructure/blob/01f13c207f95418f14a22725d04122e5f4d7cc90/WhatsApp%20Image%202022-04-15%20at%2010.02.30%20PM.jpeg)

Graph 2

![image](https://github.com/CMU-IDS-2022/final-project-digitaltwinfrastructure/blob/01f13c207f95418f14a22725d04122e5f4d7cc90/WhatsApp%20Image%202022-04-15%20at%2010.02.31%20PM%20(1).jpeg)

Graph 3

![image](https://github.com/CMU-IDS-2022/final-project-digitaltwinfrastructure/blob/01f13c207f95418f14a22725d04122e5f4d7cc90/WhatsApp%20Image%202022-04-15%20at%2010.02.31%20PM.jpeg)

- **Water network data:** This dataset consists of pressure, flow and water level readings of assets of water network at different times of the day. Pressure and flow can be real numbers 


Sketch 1
![image](https://github.com/CMU-IDS-2022/final-project-digitaltwinfrastructure/blob/6f906941a56d225ca8b6d469bbde6d0c83e25e9d/WhatsApp%20Image%202022-04-15%20at%209.42.36%20PM%20(1).jpeg)

Sketch 2
![image](https://github.com/CMU-IDS-2022/final-project-digitaltwinfrastructure/blob/6f906941a56d225ca8b6d469bbde6d0c83e25e9d/WhatsApp%20Image%202022-04-15%20at%209.42.36%20PM.jpeg)

Sketch 3
![image](https://github.com/CMU-IDS-2022/final-project-digitaltwinfrastructure/blob/6f906941a56d225ca8b6d469bbde6d0c83e25e9d/WhatsApp%20Image%202022-04-15%20at%209.42.26%20PM.jpeg)

Sketch 4
![image](https://github.com/CMU-IDS-2022/final-project-digitaltwinfrastructure/blob/6f906941a56d225ca8b6d469bbde6d0c83e25e9d/WhatsApp%20Image%202022-04-15%20at%209.42.32%20PM.jpeg)

Sketch 5
![image](https://github.com/CMU-IDS-2022/final-project-digitaltwinfrastructure/blob/6f906941a56d225ca8b6d469bbde6d0c83e25e9d/WhatsApp%20Image%202022-04-15%20at%209.42.24%20PM.jpeg)

