import streamlit as st
from langchain_text_splitters import CharacterTextSplitter
text_splitter = CharacterTextSplitter(chunk_size=500,chunk_overlap=50)
docs = text_splitter.create_documents(["Gen Ai is leading area in IT sector , it replace humans but create new opportunity"])
st.write(docs)
print(docs)
