import os
import streamlit as st
import chromadb
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
from openai import OpenAI

# ---------------- CONFIG ----------------
RESUME_DIR = r"D:\IIT-GENAI-94391\Assignments\Day11\RESUME"
CHROMA_PATH = "chroma_db"
COLLECTION_NAME = "resumes"

# ✅ Embedding model (FREE, local)
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

# LLM (LM Studio)
client = OpenAI(
    base_url="http://localhost:1234/v1",
    api_key="lm-studio"
)

SYSTEM_PROMPT = """
You are a resume analysis assistant.
Summarize resumes, list technical skills, answer questions using resume content only,
and shortlist candidates against job requirements.
Do not assume missing information.
"""

# ---------------- CHROMA ----------------
chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
collection = chroma_client.get_or_create_collection(COLLECTION_NAME)

# ---------------- FUNCTIONS ----------------
def count_pdfs():
    return len([f for f in os.listdir(RESUME_DIR) if f.lower().endswith(".pdf")])

def index_resumes():
    loader = PyPDFDirectoryLoader(RESUME_DIR)
    docs = loader.load()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=600,
        chunk_overlap=100
    )

    chunks = splitter.split_documents(docs)

    documents, metadatas, ids, embeddings = [], [], [], []

    for i, chunk in enumerate(chunks):
        text = chunk.page_content
        documents.append(text)
        metadatas.append(chunk.metadata)
        ids.append(f"chunk_{i}")

        # ✅ Create embedding
        emb = embedding_model.encode(text).tolist()
        embeddings.append(emb)

    if not documents:
        st.error("No resumes found!")
        return

    # ✅ Store with embeddings
    collection.upsert(
        documents=documents,
        metadatas=metadatas,
        ids=ids,
        embeddings=embeddings
    )

    st.success(f"Indexed {len(documents)} chunks from {count_pdfs()} PDFs")

def ask_llm(context, query):
    response = client.chat.completions.create(
        model="gemma-2-9b-it",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Context:\n{context}\n\nTask:\n{query}"}
        ],
        temperature=0.2,
        max_tokens=600
    )
    return response.choices[0].message.content

def search_resumes(query):
    query_embedding = embedding_model.encode(query).tolist()

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=5
    )
    return "\n\n".join(results["documents"][0])

# ---------------- STREAMLIT UI ----------------
st.set_page_config(page_title="HR Resume Finder (RAG)", layout="wide")

st.title("📄 HR Resume Finder")

# ✅ Show PDF count
pdf_count = count_pdfs()
st.info(f"📂 Total PDF Resumes Found: **{pdf_count}**")

col1, col2 = st.columns(2)

with col1:
    if st.button("📥 Index All Resumes"):
        index_resumes()

with col2:
    st.info("Put PDF resumes inside the RESUME folder")

st.divider()

query = st.text_input("🔍 Ask anything about resumes (summary, skills, shortlist):")

if st.button("Analyze"):
    if not query:
        st.warning("Enter a query")
    else:
        context = search_resumes(query)
        answer = ask_llm(context, query)

        st.subheader("📌 Result")
        st.write(answer)
