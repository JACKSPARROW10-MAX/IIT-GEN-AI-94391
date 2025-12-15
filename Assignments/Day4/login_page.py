import streamlit as st
import pandas as pd
import os
from dotenv import load_dotenv
import requests

load_dotenv()

st.set_page_config(page_title="Login + Weather App", page_icon="🌦️")

CSV_FILE = "users.csv"
API_KEY = os.getenv("WEATHER_API")

if not API_KEY:
    st.error("Weather API key not found")
    st.stop()

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

def fix_csv():
    if os.path.exists(CSV_FILE):
        df = pd.read_csv(CSV_FILE, header=None)
        if df.shape[1] == 3:
            df.columns = ["Username", "Password", "Email"]
            df.to_csv(CSV_FILE, index=False)

fix_csv()

def signup_page():
    st.title("Sign Up")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    email = st.text_input("Email")
    if st.button("Create Account"):
        if username and password and email:
            df = pd.DataFrame([[username, password, email]],
                              columns=["Username", "Password", "Email"])
            df.to_csv(CSV_FILE, mode="a", header=not os.path.exists(CSV_FILE), index=False)
            st.success("Account created")
            st.session_state.logged_in = False
            st.rerun()
        else:
            st.warning("Fill all fields")

def login_page():
    st.title("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if not os.path.exists(CSV_FILE):
            st.error("No users found")
            return
        users_df = pd.read_csv(CSV_FILE)
        users_df.columns = users_df.columns.str.strip()
        if ((users_df["Username"] == username) &
            (users_df["Password"] == password)).any():
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("Invalid credentials")

def weather_page():
    st.title("Weather App")
    city = st.text_input("City")
    if st.button("Get Weather"):
        if not city:
            st.warning("Enter city name")
            return
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
        response = requests.get(url)
        data = response.json()
        if response.status_code != 200:
            st.error(data.get("message", "Error fetching data"))
            return
        st.success(f"Weather in {city}")
        st.write("Temperature:", data["main"]["temp"], "°C")
        st.write("Condition:", data["weather"][0]["description"])
        st.write("Humidity:", data["main"]["humidity"], "%")
        st.write("Wind Speed:", data["wind"]["speed"], "m/s")
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

if st.session_state.logged_in:
    weather_page()
else:
    option = st.radio("Select Option", ["Login", "Sign Up"])
    if option == "Login":
        login_page()
    else:
        signup_page()
