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
