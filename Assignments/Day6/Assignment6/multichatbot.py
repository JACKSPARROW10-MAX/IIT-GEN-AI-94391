import streamlit as st
import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()
st.markdown("<h1 style='color:#37A794'>Multi-ChatbotInterface</h1>", unsafe_allow_html=True)
st.sidebar.title("Chatbot Selector")

with st.sidebar:
    chatbot_option = st.selectbox(
        "Choose a Chatbot:",
        ("GROQ CHATBOT", "GEMINI CHATBOT"),
        index=None,
        placeholder="Select a chatbot"
    )

st.write(f"You have selected: {chatbot_option}")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

def groq_chatbot(user_prompt):
    api_key = os.getenv("GROQ_OPENAI_API")
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    req_data = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "user", "content": user_prompt}
        ],
    }
    response = requests.post(url, data=json.dumps(req_data), headers=headers)
    rp = response.json()
    return rp["choices"][0]["message"]["content"]


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


if chatbot_option is None:
    st.warning("Please select a chatbot from the sidebar.")
elif chatbot_option == "GROQ CHATBOT":
    user_prompt = st.chat_input("Ask anything:")
    if user_prompt:
        response = groq_chatbot(user_prompt)
        st.session_state.chat_history.append({
            "bot": "GROQ CHATBOT",
            "user": user_prompt,
            "response": response
        })

elif chatbot_option == "GEMINI CHATBOT":
    gemini_prompt = st.chat_input("Ask anything:", key="gemini")
    if gemini_prompt:
        response = gemini_chatbot(gemini_prompt)
        st.session_state.chat_history.append({
            "bot": "GEMINI CHATBOT",
            "user": gemini_prompt,
            "response": response
        })


for chat in reversed(st.session_state.chat_history):
    if chat["bot"] == chatbot_option:
        st.markdown(
            f"""
            <div style='text-align: left; background-color: #FFAC00;
                        padding: 10px; border-radius: 10px; margin: 5px 0;'>
                👱🏼:{chat["user"]}
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown(
            f"""
            <div style='text-align: left; background-color: #009FEF;
                        padding: 10px; border-radius: 10px; margin: 5px 0;'>
                💀:{chat["response"]}
            </div>
            """,
            unsafe_allow_html=True
        )


def sidebar_style():
    st.markdown(
        """
        <style>
        [data-testid="stSidebar"] {
            background-color: #004753;
            color: white;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

sidebar_style()
