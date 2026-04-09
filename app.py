import streamlit as st

pages = [
    st.Page("pages/1_Complaint_Register.py", title="Complaint Register"),
    st.Page("pages/2_Government_Panel.py", title="Government Panel"),
    st.Page("pages/3_Complaint_History.py", title="Complaint History"),
    st.Page("pages/4_Dashboard.py", title="Dashboard"),
    st.Page("pages/5_About_page.py", title="About Page")
]

pg = st.navigation(pages)
pg.run()


