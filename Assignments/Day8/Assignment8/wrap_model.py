from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
from langchain.agents.middleware import wrap_model_call
import streamlit as st
import requests
#-------------wraper model call---------------
@wrap_model_call
def limit_model_context(requestes,handler):
    st.write("limit_model_context Called")
    response=handler(requestes)
    response.result[0].content = response.result[0].content.upper()
    return response

@wrap_model_call
def model_logging(requests,handler):
    requests.message = requests.messages[-5:]
    response = handler(requests)
    response.result[0].content=response.result[0].content.upper()
    return response


    
# -------- UI --------
st.title("Agentic LLM 🤖")

# -------- Session State --------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "conversation" not in st.session_state:
    st.session_state.conversation = [
        {"role": "system", "content": "You are an experienced assistant."}
    ]

# -------- Display Chat --------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# -------- Model --------
llm = init_chat_model(
    model="phi-3.1-mini-4k-instruct",
    model_provider="openai",
    base_url="http://127.0.0.1:1234/v1",
    api_key="my_openai_api_key"
)

agent = create_agent(
    model=llm,
    tools=[],
    middleware=[limit_model_context,model_logging],
    system_prompt="You are a helpful assistant. Answer in short.output : Short answer with main steps"
)

# -------- Input --------
user_input = st.chat_input("Ask anything...")

if user_input:
    st.session_state.messages.append(
        {"role": "user", "content": user_input}
    )
    st.session_state.conversation.append(
        {"role": "user", "content": user_input}
    )

    with st.chat_message("user"):
        st.markdown(user_input)

    response = agent.invoke(
        {"messages": st.session_state.conversation}
    )
    print(response)
    assistant_reply = response["messages"][-1].content

    st.session_state.messages.append(
        {"role": "assistant", "content": assistant_reply}
    )
    st.session_state.conversation.append(
        {"role": "assistant", "content": assistant_reply}
    )
    with st.chat_message("assistant"):
        st.markdown(assistant_reply)