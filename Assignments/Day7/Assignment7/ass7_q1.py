import streamlit as st
import requests
import json
from langchain.chat_models import init_chat_model
import pandas as pd
import os
import pandasql as ps
from dotenv import load_dotenv
load_dotenv()

st.markdown("<h1 style='color:#37A794'>CSV Explorer</h1>",unsafe_allow_html=True)
def gemini_chatbot(gemini_prompt):
    api_key = "dummy-key"
    url = "http://127.0.0.1:1234/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    req_data = {
        "model": "gemma-2-9b-it",
        "messages": [
            {"role": "user", "content": gemini_prompt}
        ],
    }

    response = requests.post(url, data=json.dumps(req_data), headers=headers)
    resp = response.json()
    return resp["choices"][0]["message"]["content"]



llm = init_chat_model(
    model = "llama-3.3-70b-versatile",
    model_provider = "openai",
    base_url = "https://api.groq.com/openai/v1",
    api_key = os.getenv("GROQ_OPENAI_API")
)
conversation = [
    {"role": "system", "content": "You are SQLite expert developer with 10 years of experience."}
    ]

data_file = st.file_uploader("Upload a CSV file", type=["csv"])
if data_file:
    df = pd.read_csv(data_file)
    st.write(df.dtypes)
    st.dataframe(df)
 

    user_input=st.chat_input("Ask anything :",key="uin")
    if user_input:
        llm_input = f"""
        Table Name: data
        Table Schema: {df.dtypes}
        Question: {user_input}
        Instruction:
            Write a SQL query for the above question. 
            Generate SQL query only in plain text format and nothing else.
            If you cannot generate the query, then output 'Error'.
    """
        result = llm.invoke(llm_input)
        print(result.content)
        rt_var=result.content
        st.write(rt_var)

        query=rt_var
        result=ps.sqldf(query,{"data":df})
        st.dataframe(result)

        if user_input:
         llm_input2 = f"""
        Table Name: data
        Table Schema: {df.dtypes}
        Question: {query}
        Instruction:
            explain the query in simple english.
    """
        result2 = llm.invoke(llm_input2)
        st.success(result2.content)