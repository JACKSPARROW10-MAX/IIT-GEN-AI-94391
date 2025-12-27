import os
import math
import tempfile
from datetime import datetime

import streamlit as st
from dotenv import load_dotenv

from langchain.tools import tool
from langchain.agents import create_agent
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_openai import ChatOpenAI


load_dotenv()

CHROMA_PATH = "./chroma_db"
COLLECTION_NAME = "resumes"

st.set_page_config(
    page_title="Agentic Resume RAG",
    page_icon="📄",
    layout="wide"
)

st.title("📄 Agentic RAG – AI Resume Shortlisting")


def initialize_vector_store():
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    return Chroma(
        persist_directory=CHROMA_PATH,
        embedding_function=embeddings,
        collection_name=COLLECTION_NAME
    )


VECTOR_STORE = initialize_vector_store()


def process_pdf(uploaded_file):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(uploaded_file.getvalue())
        tmp_path = tmp.name

    loader = PyPDFLoader(tmp_path)
    docs = loader.load()
    os.unlink(tmp_path)

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )

    return splitter.split_documents(docs)


def upload_resume(uploaded_file):
    chunks = process_pdf(uploaded_file)

    for chunk in chunks:
        chunk.metadata.update({
            "filename": uploaded_file.name,
            "upload_date": datetime.now().isoformat(),
            "skills": "",
            "experience": 0
        })

    VECTOR_STORE.add_documents(chunks)
    VECTOR_STORE.persist()


@tool
def retrive(job_description: str, top_k: int = 3) -> str:
    """
    Retrieve and rank resumes using vector similarity and metadata.
    Uses only uploaded resumes and never hallucinates.
    """

    results = VECTOR_STORE.similarity_search_with_score(job_description, k=10)

    if not results:
        return "No relevant resumes found."

    job_tokens = set(job_description.lower().split())
    ranked = []

    for doc, distance in results:
        meta = doc.metadata

        skills = set(meta.get("skills", "").lower().split(","))
        skill_score = len(job_tokens & skills)

        experience = meta.get("experience", 0)
        exp_score = min(experience / 10, 1.0)

        recency_score = 0
        if "upload_date" in meta:
            days_old = (
                datetime.now() - datetime.fromisoformat(meta["upload_date"])
            ).days
            recency_score = math.exp(-days_old / 180)

        final_score = (
            (1 - distance) * 0.5 +
            skill_score * 0.3 +
            exp_score * 0.1 +
            recency_score * 0.1
        )

        ranked.append({
            "score": final_score,
            "filename": meta.get("filename", "Unknown"),
            "content": doc.page_content
        })

    ranked.sort(key=lambda x: x["score"], reverse=True)
    ranked = ranked[:top_k]

    output = []
    for i, r in enumerate(ranked, 1):
        output.append(
            f"\n--- Rank {i}: {r['filename']} ---\n{r['content']}"
        )

    return "\n".join(output)


llm = ChatOpenAI(
    model="gemma-2-9b-it",
    base_url="http://127.0.0.1:1234/v1",
    api_key="not-needed",
    temperature=0
)

agent = create_agent(
    model=llm,
    tools=[retrive],
    system_prompt=(
        "You are an experienced HR recruiter. "
        "Use tools only for job description queries. "
        "Do not hallucinate. Answer strictly from retrieved resumes."
    )
)


user_input = st.chat_input("Paste job description here...")

if user_input:
    response = agent.invoke({
        "messages": [{"role": "user", "content": user_input}]
    })
    st.write("### 🤖 AI Recommendation")
    st.write(response["messages"][-1].content)


st.sidebar.header("📤 Upload Resume")
uploaded_file = st.sidebar.file_uploader("Upload PDF Resume", type="pdf")

if uploaded_file and st.sidebar.button("Upload Resume"):
    upload_resume(uploaded_file)
    st.sidebar.success("Resume uploaded successfully!")

