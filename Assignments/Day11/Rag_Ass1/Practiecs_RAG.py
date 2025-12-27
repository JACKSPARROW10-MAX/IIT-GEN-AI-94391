import streamlit as st
import os
import tempfile
from datetime import datetime
from dotenv import load_dotenv
import time
import chromadb
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_openai import ChatOpenAI
load_dotenv()
CHROMA_API_KEY = os.getenv("CHROMA_API_KEY")
if not CHROMA_API_KEY:
    raise RuntimeError(" CHROMA_API_KEY not set")

TENANT =os.getenv("TENANT_ID")
DATABASE = "Chroma_db"
COLLECTION_NAME = "resumes"

if "vector_store" not in st.session_state:
    st.session_state.vector_store = None

def initialize_vector_store():
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    cloud_client = chromadb.CloudClient(
        api_key=CHROMA_API_KEY,
        tenant=TENANT,
        database=DATABASE
    )

    return Chroma(
        client=cloud_client,
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings
    )

def process_pdf(uploaded_file):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(uploaded_file.getvalue())
        path = tmp.name

    docs = PyPDFLoader(path).load()
    os.remove(path)

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    return splitter.split_documents(docs)

def upload_resume(uploaded_file, vector_store):
    chunks = process_pdf(uploaded_file)

    for chunk in chunks:
        chunk.metadata = {
            "filename": uploaded_file.name,
            "upload_date": datetime.now().isoformat()
        }

    vector_store.add_documents(chunks)
    return True

def list_resumes(vector_store):
    try:
        docs = vector_store.similarity_search(query="resume", k=50)
        resumes = {}
        for d in docs:
            fname = d.metadata.get("filename")
            if fname and fname not in resumes:
                resumes[fname] = d.metadata.get("upload_date", "Unknown")
        return resumes
    except Exception as e:
        st.error(f"Error listing resumes: {e}")
        return {}

def delete_resume(filename, vector_store):
    try:
        docs = vector_store.similarity_search(query=filename, k=100)
        ids = [d.metadata.get("id") for d in docs if d.metadata.get("filename") == filename]
        if ids:
            vector_store._collection.delete(ids=ids)
            return True
        return False
    except Exception as e:
        st.error(f"Delete error: {e}")
        return False

def safe_similarity_search(retriever, query, max_retries=3, wait=2):
    for i in range(max_retries):
        try:
            return retriever.invoke(query)
        except Exception as e:
            if i < max_retries - 1:
                time.sleep(wait)
            else:
                st.error(f"Error during similarity search: {e}")
                return []

def shortlist_resumes(job_desc, num_resumes, vector_store):
  
    MAX_K = min(num_resumes * 3, 20)
    job_desc_short = job_desc[:1000]  

    retriever = vector_store.as_retriever(search_kwargs={"k": MAX_K})
    docs = safe_similarity_search(retriever, job_desc_short)

    grouped = {}
    for d in docs:
        fname = d.metadata.get("filename", "Unknown")
        grouped.setdefault(fname, []).append(d.page_content)

    llm = ChatOpenAI(
        model="gemma-2-9b-it",       
        base_url="http://localhost:1234/v1",
        api_key="lm-studio",
        timeout=60,
        max_retries=3
    )

    results = []
    for fname, chunks in list(grouped.items())[:num_resumes]:
        prompt = f"""
Job Description:
{job_desc_short}

Resume Content:
{chr(10).join(chunks[:3])}

Explain in 8–12 sentences why this candidate matches the job.
"""
        try:
            analysis = llm.invoke(prompt).content
        except Exception as e:
            analysis = f"LLM error: {e}"

        results.append({
            "filename": fname,
            "analysis": analysis,
            "chunks_found": len(chunks)
        })

    return results

def main():
    st.set_page_config("AI Resume Shortlisting", "📄", "wide")
    st.title("📄 AI Resume Shortlisting (Chroma Cloud SAFE)")

    if st.session_state.vector_store is None:
        with st.spinner("Connecting to Chroma Cloud..."):
            st.session_state.vector_store = initialize_vector_store()

    vs = st.session_state.vector_store

    page = st.sidebar.radio(
        "Action",
        ["Upload Resume", "List Resumes", "Delete Resume", "Shortlist Candidates"]
    )

    if page == "Upload Resume":
        f = st.file_uploader("Upload PDF Resume", type="pdf")
        if f and st.button("Upload"):
            upload_resume(f, vs)
            st.success("✅ Uploaded to Chroma Cloud")

    elif page == "List Resumes":
        resumes = list_resumes(vs)
        st.write(f"Total resumes found: {len(resumes)}")
        for k, v in resumes.items():
            st.write(f"📄 {k} — {v[:10]}")

    elif page == "Delete Resume":
        resumes = list_resumes(vs)
        if resumes:
            sel = st.selectbox("Select resume", resumes.keys())
            if st.button("Delete"):
                delete_resume(sel, vs)
                st.success("Deleted")
                st.rerun()

    elif page == "Shortlist Candidates":
        jd = st.text_area("Job Description", height=200)
        k = st.slider("Number of candidates", 1, 5, 3)
        if st.button("Shortlist") and jd:
            results = shortlist_resumes(jd, k, vs)
            for i, r in enumerate(results, 1):
                with st.expander(f"#{i} — {r['filename']}", expanded=i == 1):
                    st.write(r["analysis"])
                    st.caption(f"Relevant chunks: {r['chunks_found']}")

if __name__ == "__main__":
    main()
