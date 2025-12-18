import pandas as pd
import streamlit as st
import pandasql as ps
st.title("CSV Explorer")

# upload a CSV file
data_file = st.file_uploader("Upload a CSV file", type=["csv"])
# load it as dataframe
if data_file:
    df = pd.read_csv(data_file)
    # display the dataframe
    st.dataframe(df)
    empid=st.text_input("Enter your empid :")
    query=f"SELECT * FROM data WHERE empno = '{empid}'"
    result=ps.sqldf(query,{"data":df})
    st.dataframe(result)
    