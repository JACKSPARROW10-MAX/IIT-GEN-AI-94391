import streamlit as s
import mysql.connector
from dotenv import load_dotenv
import os

from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
from langchain.tools import tool

load_dotenv()

host = os.getenv("MYSQL_HOST")
user = os.getenv("MYSQL_USER")
password = os.getenv("MYSQL_PASS")

database = "sunbeam"

api_key = os.getenv("GROQ_API_KEY")



llm = init_chat_model(
     model = "llama-3.3-70b-versatile",
     model_provider = "openai",
     base_url = "https://api.groq.com/openai/v1",
     api_key = api_key
)


if "btn" not in s.session_state:
    s.session_state.btn = False

if "conversation" not in s.session_state:
    s.session_state.conversation = []

if "conn" not in s.session_state:
    s.session_state.conn = None

if "cursor" not in s.session_state:
    s.session_state.cursor = None

if "table_name" not in s.session_state:
    s.session_state.table_name = None

if "metadata" not in s.session_state:
    s.session_state.metadata = None



def fetch_database_data(query: str):
    """
    this method fetch data from database using MySQL query
    
    :param query: SQL query
    :output query result
    """
    if "cursor" not in s.session_state or s.session_state.cursor is None:
        return "Error: Database not connected. Please connect database first."

    try:
        cursor = s.session_state.cursor
        cursor.execute(query)
        data = cursor.fetchall()
        return data
    except mysql.connector.Error as err:
        return f"MySQL Error: {err}"



# Create agent
agent = create_agent(
    model = llm,
    tools= [fetch_database_data],
    system_prompt = "You are a helpful assistant. Give correct answer."

)


# disconnect database.
def disc_database():
    try:
        if s.session_state.cursor:
            s.session_state.cursor.close()
        if s.session_state.conn:
            s.session_state.conn.close()

        s.session_state.cursor = None
        s.session_state.conn = None

        s.success("Database disconnected")

    except Exception as e:
        s.error(e)


def load_database():
    try:
        conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )

        cursor = conn.cursor()

        s.session_state.conn = conn
        s.session_state.cursor = cursor

        s.success("Connected to MYSQL database!")

        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()

        table_name = tables[0][0]
        s.write("Tables in database:", table_name)

        s.session_state.table_name = table_name

        cursor.execute(f"DESCRIBE {table_name}")
        schema = cursor.fetchall()
        s.session_state.metadata = schema

        s.table(schema)

    except mysql.connector.Error as err:
        s.error(err)



s.title("MYSQL Data explorer")



conn_database_btn = s.button("Connect Database", type = "primary")

if conn_database_btn:
    s.session_state.btn=True

    load_database()
    


disc_database_btn = s.button("Disconnect Database", type= "primary")
if disc_database_btn:
    s.session_state.btn = False
    disc_database()
user_question = s.chat_input("Ask something about database...")



if user_question:
    s.subheader("You")
    s.write(user_question)
    s.session_state.conversation.append({"role":"user", "content":user_question})

    agent_input = f"""
                Table name : {s.session_state.table_name}
                Table schema = {s.session_state.metadata}
                Question = {user_question}
                Instruction:
                        You are MYSQL expert developer with extensive knowledge of SQL queries and 10 years of experience.
                        Write SQL query for user question.
                        Generate SQL query only without any explanation in plain text format without markdown formatting.
                        Always use case-insensitive matching for text columns by applying LOWER() on both column name and value.
                        if you cannot generate SQL query for the question, then reply with 'Error: please ask right question.
                """
        
        
    llm_output = llm.invoke(agent_input)
    query = llm_output.content.strip()
    s.markdown(query)

    fetched_data = fetch_database_data(query)
    s.table(fetched_data)

    explanation_input = f"""
                Table name : {s.session_state.table_name}
                Table schema = {s.session_state.metadata}
                SQL Query = {query}
                Query Output = {fetched_data}
                Instruction:
                        You are data analyst expert with extensive knowledge of SQL queries and 10 years of experience.
                        you can explain SQL query output in simple english.
                        explain the query output in simple english so that a non-technical person can understand easily.
                        Generate explanation so that user can understand easily.
                        But do not explain SQL query itself and its syntax.
                        Provide only the explanation.
                        if query output is empty, then reply with 'No data found for the question.'
                        if possible explain why data not founded for the question.
                """
    explanation_result = llm.invoke(explanation_input)
    explanation_output = explanation_result.content.strip()
    s.subheader("Assistant")
    s.write(explanation_output)

    s.session_state.conversation.append({"role":"assiatant", "content": explanation_output})
    # for chat in s.session_state.conversation:
    #         with s.chat_message(chat["role"]):
    #             s.markdown(chat["content"])