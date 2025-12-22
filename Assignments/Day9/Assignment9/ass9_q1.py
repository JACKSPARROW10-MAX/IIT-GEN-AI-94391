# import required packages
from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
from langchain.tools import tool
from dotenv import load_dotenv
import os
import json

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv
import streamlit as st
import pandas as pd
load_dotenv()


# start the selenium browser session
chrome_options = Options()
#chrome_options.add_argument("--headless")
driver = webdriver.Chrome(options=chrome_options)
wait = WebDriverWait(driver, 10)
# load desired page in the browser
driver.get("https://www.sunbeaminfo.in/internship")
print("Page Title:", driver.title)
# define wait strategy
driver.implicitly_wait(5)
# interact with web controls
table = wait.until(
    EC.presence_of_element_located(
        (By.XPATH, "//div[@id='collapseSix']//table")
    )
)
rows = table.find_elements(By.XPATH, ".//tbody/tr")

with open("table_data.csv", "w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)

    for row in rows:
        cells = row.find_elements(By.TAG_NAME, "td")
        row_data = [cell.get_attribute("textContent").strip() for cell in cells]
        writer.writerow(row_data)

print("Table saved to table_data.csv")

table2= wait.until(
    EC.presence_of_element_located(
        (By.CLASS_NAME,"table-responsive")
    )
)

rows2 = table2.find_elements(By.XPATH, ".//tbody/tr")
with open("day9_q1.csv", "w", newline="", encoding="utf-8") as file2:
    writer2 = csv.writer(file2)

    for row in rows2:
        cells2 = row.find_elements(By.TAG_NAME, "td")
        row_data2 = [cell.get_attribute("textContent").strip() for cell in cells2]
        writer2.writerow(row_data2)
print("Table saved to day9_q1.csv")

driver.quit()


df=pd.read_csv("D:\IIT-GENAI-94391\Assignments\Day9\Assignment9\day9_q1.csv")
load_dotenv()
st.title("Data Scrapper")
st.dataframe(df)
file_path="D:\IIT-GENAI-94391\Assignments\Day9\Assignment9\day9_q1.csv"
# in this tool we provide file content to the agent also df contains dataframe
@tool
def read_file(file_path: str) -> str:
    """
    Reads the content of a CSV file and returns it as text.
    Args:
        file_path (str): The path to the CSV file.
    Returns:
        str: The content of the CSV file as text.
    answers the user queries related to the file.
    """
    return df.to_string()

    #with open(df, 'r') as file:
        #text = file.read()
        #return text
    
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
            system_prompt="You are a helpful assistant.which helps to read the file content and ans the user queries or question related to the file."
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
    st.write("You: " + user_input)
    st.write("AI: ", llm_output.content)
    