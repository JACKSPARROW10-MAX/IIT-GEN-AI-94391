from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
from langchain.tools import tool
import streamlit as st



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
    
llm = init_chat_model(
model = "gemma-2-9b-it",
model_provider = "openai",
base_url = "http://127.0.0.1:1234/v1",
api_key = "non-needed")

agent = create_agent(
            model=llm, 
            tools=[
                calculator
            ],
            system_prompt="You are a helpful assistant. Answer in short."
        )       
st.markdown("<h1>CALCULATOR AGENT</h1>",unsafe_allow_html=True)
user_input = st.chat_input("You: ")
if user_input:
    result = agent.invoke({
        "messages": [
            {"role": "user", "content": user_input}
        ]
    })
    llm_output = result["messages"][-1]
    st.write(user_input)
    st.write("AI: ", llm_output.content)
   # st.write("\n\n", result["messages"])

    tool_found=False
    for msg in result["messages"]:
        if hasattr(msg,"tool_calls") and msg.tool_calls:
            tool_found=True
            for tool in msg.tool_calls :
                st.write("tool name",tool["name"])
    if not tool_found:
        st.error("No tools are used !")            
        