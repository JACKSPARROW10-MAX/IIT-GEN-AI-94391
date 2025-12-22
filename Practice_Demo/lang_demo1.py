from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv
load_dotenv()

#api_key = os.getenv("GROQ_OPENAI_API")
#llm = ChatGroq(model="openai/gpt-oss-120b", api_key=api_key)

#api_key = os.getenv("GEMINI_API")
#llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", api_key=api_key)

llm_url = "http://127.0.0.1:1234/v1"
llm = ChatOpenAI(
     base_url=llm_url,
     model="gemma-2-9b-it",
     api_key="dummy-key"
 )

user_input = input("You: ")
# result = llm.invoke(user_input)
# print("AI: ", result.content)
result = llm.stream(user_input)
for chunk in result:
    print(chunk.content, end="")
     
