from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
from langchain.tools import tool
from dotenv import load_dotenv
import os
import json
import requests
import streamlit as st

load_dotenv() 

st.markdown("<h1>Smart Chatbot</h1>",unsafe_allow_html=True)
#st.markdown("<h1>CALCULATOR AGENT</h1>",unsafe_allow_html=True)
city=st.chat_input("You :")

llm = init_chat_model(
    model = "gemma-2-9b-it",
    model_provider = "openai",
    base_url = "http://127.0.0.1:1234/v1",
    api_key = "non-needed"
)


@tool
def get_weather(city):
    """
    This get_weather() function gets the current weather of given city.
    If weather cannot be found, it returns 'Error'.
    This function doesn't return historic or general weather of the city.

    :param city: str input - city name
    :returns current weather in json format or 'Error'    
    """
    try:
        api_key = os.getenv("WEATHER_API")
        url = f"https://api.openweathermap.org/data/2.5/weather?appid={api_key}&units=metric&q={city}"
        response = requests.get(url)
        weather = response.json()
        return json.dumps(weather)
    except:
        return "Error"

@tool
def read_file(filepath:str)->str:
    """
    this agent read the file content and summurize it in simple english
    
    :param filepath: Description
    """
    with open(filepath, 'r') as file:
        text = file.read()
        return text

@tool
def calculator(expression):
    """
    This calculator function solves any arithmetic expression containing all constant values.
    It supports basic arithmetic operators +, -, *, /, and parenthesis. 
    
    :param expression: str input arithmetic expression
    :returns expression result as str
    """
    try:
        result = eval(expression)
        return str(result)
    except:
        return "Error: Cannot solve expression"

    
agent = create_agent(
            model=llm, 
            tools=[
                get_weather,
                calculator,
                read_file
            ],
            system_prompt="You are a helpful assistant. Answer in short"
            "use tool calculator only when maths related questions are asked." 
            "use tool get_weather only when weather related questions are asked" 
            "use tool read_file only when file path is given" 
            "dont use tools for genral questions like who,what" 
        )

user_input = city
if user_input :
    result = agent.invoke({
        "messages": [
            {"role": "user", "content": user_input}
        ]
    })
    llm_output = result["messages"][-1]
    st.write("AI: ", llm_output.content)
    #print("\n\n", result["messages"])

    tool_found=False
    for msg in result["messages"]:
        if hasattr(msg,"tool_calls") and msg.tool_calls:
            tool_found=True
            for tool in msg.tool_calls :
                st.write("tool name :",tool["name"])
    if not tool_found:
        st.error("No tools are used !") 