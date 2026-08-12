import streamlit as st


pages = [
    st.Page("pages/0_Home.py", title="Home", default=True),
    st.Page("pages/1_Option_Pricer.py", title="Option Pricer"),
    st.Page("pages/2_Greeks_and_Sensitivity.py", title="Greeks & Sensitivity"),
    st.Page("pages/3_Delta_Hedging.py", title="Delta Hedging"),
    st.Page("pages/4_Monte_Carlo_Research.py", title="Monte Carlo"),
    st.Page("pages/5_Research_Lab.py", title="Research Lab"),
    st.Page("pages/6_Scenario_Mode.py", title="Scenario Mode"),
    st.Page("pages/7_Model_and_Data.py", title="Model & Data"),
]

st.navigation(pages, position="top").run()
