# Data Labelling Outsourcing for EV Charging Infrastructure feasibility study
Data extraction pipeline from Google StreetView API + Streamlit UI to outsource Labelling for MIT EV research
---
Main components:
- Streamlit interface with authentication to allow multiple users to label data at the same time
- Data extraction pipeline that samples points (from a pre-collected dataset) in the drivable streets of Detroit, MI
- AWS interfacing: datapoints are organized and stored on S3
