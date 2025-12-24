from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
import os
import streamlit as st
from sentence_transformers import SentenceTransformer
import numpy as np

st.title("Resume Chooser")

loader=PyPDFDirectoryLoader("D:\IIT-GENAI-94391\Assignments\Day11\RESUME")
docs=loader.load()
count=len(docs)
print(count)
st.write("Document Count :",count)

text_splitter=RecursiveCharacterTextSplitter(
    separators="\n\n,\n,",
    chunk_size=400,
    chunk_overlap=50,
)

chunks=text_splitter.split_documents(docs)

count_chunk=len(chunks)
st.write("Chunk Count :",count_chunk)


# for i in range(0,24):
#     st.write(chunks[i].page_content)
#     st.write("\n----------------------\n")
def consine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

embed_model = SentenceTransformer("all-MiniLM-L6-v2")
texts = [doc.page_content for doc in chunks]
embeddings = embed_model.encode(texts)
# for embed_vect in embeddings:
#     st.write("Len:", len(embed_vect), " --> ", embed_vect[:4])

user_input=st.chat_input("Ask Anything ...")
userembedd=embed_model.encode(user_input)


