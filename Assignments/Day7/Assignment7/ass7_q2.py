import streamlit as st
import requests
import json
from langchain.chat_models import init_chat_model
import os
from dotenv import load_dotenv
load_dotenv()

st.markdown("<h1 style='color:#37A794'>City Weather Explainer</h1>",unsafe_allow_html=True)

llm = init_chat_model(
    model = "llama-3.3-70b-versatile",
    model_provider = "openai",
    base_url = "https://api.groq.com/openai/v1",
    api_key = os.getenv("GROQ_OPENAI_API")
)
conversation = [
    {"role": "system", "content": "You are SQLite expert developer with 10 years of experience."}
    ]


api_key = os.getenv("WEATHER_API")
city = st.chat_input("Enter city: ")
if city:
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
        response = requests.get(url)
        print("status:", response.status_code)
        weather = response.json()
        # print(weather)
        st.write(city)
        st.write("Temperature: ", weather["main"]["temp"])
        st.write("Humidity: ", weather["main"]["humidity"])
        st.write("Wind Speed: ", weather["wind"]["speed"])
        user_input=weather
        if user_input:
                llm_input = f"""
                Question: {weather}
                Instruction:'
                Explain weather details in simple english'
            """
                result = llm.invoke(llm_input)
                print(result.content)
                st.success(result.content)



