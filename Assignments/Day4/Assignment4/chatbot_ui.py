import streamlit as st
import time

st.set_page_config(page_title="Simple Chatbot", page_icon="💬")

st.title("💬 Chatbot UI (Streamlit)")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# User input
user_input = st.chat_input("Type your message...")

def stream_reply(text):
    for word in text.split():
        yield word + " "
        time.sleep(0.2)  # delay for chat-like effect

if user_input:
    # Store and show user message
    st.session_state.messages.append(
        {"role": "user", "content": user_input}
    )
    with st.chat_message("user"):
        st.markdown(user_input)

    # Bot reply (echo)
    bot_reply = f"You said: {user_input}"

    st.session_state.messages.append(
        {"role": "assistant", "content": bot_reply}
    )

    with st.chat_message("assistant"):
        st.write_stream(stream_reply(bot_reply))
