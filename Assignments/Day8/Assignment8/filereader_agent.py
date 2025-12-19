from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
from langchain.tools import tool
from dotenv import load_dotenv
import os
import json
import requests
import streamlit as st
load_dotenv()
st.title("File Reader Agent :")
@tool
def read_file(filepath:str)->str:
    """
    this agent read the file content and summurize it in simple english
    
    :param filepath: Description
    """
    with open(filepath, 'r') as file:
        text = file.read()
        return text
    
llm = init_chat_model(
    model = "gemma-2-9b-it",
    model_provider = "openai",
    base_url = "http://127.0.0.1:1234/v1",
    api_key = "non-needed"
)

# create agent
agent = create_agent(
            model=llm, 
            tools=[
                read_file
            ],
            system_prompt="You are a helpful assistant. Answer in short."
        )

user_input = st.chat_input("You: ")
if user_input:
    # invoke the agent with user input
    result = agent.invoke({
        "messages": [
            {"role": "user", "content": user_input}
        ]
    })
    llm_output = result["messages"][-1]
    st.write("AI: ", llm_output.content)
    #print("\n\n", result["messages"])

