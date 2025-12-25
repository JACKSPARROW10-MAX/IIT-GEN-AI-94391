# app.py - AI Resume Shortlisting Application

import streamlit as st
import os
from datetime import datetime
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import ChatOpenAI
from langchain_community.vectorstores import Chroma
import tempfile
from sentence_transformers import SentenceTransformer
from langchain_huggingface import HuggingFaceEmbeddings


# Load environment variables
load_dotenv()

# Configuration
CHROMA_PATH = "./chroma_db"
COLLECTION_NAME = "resumes"

# Initialize session state
if 'vector_store' not in st.session_state:
    st.session_state.vector_store = None

# from langchain.vectorstores import Chroma
# from langchain.document_loaders import PyPDFLoader
# from langchain.text_splitter import RecursiveCharacterTextSplitter
# from datetime import datetime
# import tempfile
# import os
# import streamlit as st

def initialize_vector_store():
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    vector_store = Chroma(
        persist_directory=CHROMA_PATH,
        embedding_function=embeddings,
        collection_name=COLLECTION_NAME
    )

    return vector_store


def process_pdf(uploaded_file):
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_path = tmp_file.name

        loader = PyPDFLoader(tmp_path)
        documents = loader.load()
        os.unlink(tmp_path)

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )

        return splitter.split_documents(documents)

    except Exception as e:
        st.error(f"Error processing PDF: {str(e)}")
        return None


def upload_resume(uploaded_file, vector_store):
    try:
        chunks = process_pdf(uploaded_file)

        if not chunks:
            return False

        for chunk in chunks:
            chunk.metadata.update({
                "filename": uploaded_file.name,
                "upload_date": datetime.now().isoformat()
            })

        vector_store.add_documents(chunks)
        vector_store.persist()

        return True

    except Exception as e:
        st.error(f"Error uploading resume: {str(e)}")
        return False


def update_resume(old_filename, uploaded_file, vector_store):
    """Update existing resume"""
    try:
        # Delete old resume
        delete_resume(old_filename, vector_store)
        
        # Upload new resume
        return upload_resume(uploaded_file, vector_store)
    
    except Exception as e:
        st.error(f"Error updating resume: {str(e)}")
        return False

def list_resumes(vector_store):
    """List all stored resumes"""
    try:
        collection = vector_store._collection
        results = collection.get()
        
        if results and results['metadatas']:
            # Extract unique filenames
            filenames = set()
            resume_info = {}
            
            for metadata in results['metadatas']:
                if 'filename' in metadata:
                    filename = metadata['filename']
                    if filename not in filenames:
                        filenames.add(filename)
                        resume_info[filename] = {
                            'upload_date': metadata.get('upload_date', 'Unknown')
                        }
            
            return resume_info
        return {}
    
    except Exception as e:
        st.error(f"Error listing resumes: {str(e)}")
        return {}

def delete_resume(filename, vector_store):
    """Delete resume from vector store"""
    try:
        collection = vector_store._collection
        results = collection.get()
        
        # Find IDs with matching filename
        ids_to_delete = []
        for i, metadata in enumerate(results['metadatas']):
            if metadata.get('filename') == filename:
                ids_to_delete.append(results['ids'][i])
        
        if ids_to_delete:
            collection.delete(ids=ids_to_delete)
            return True
        return False
    
    except Exception as e:
        st.error(f"Error deleting resume: {str(e)}")
        return False

def shortlist_resumes(job_description, num_resumes, vector_store):
    """Shortlist resumes based on job description"""
    try:
        # Perform similarity search
        retriever = vector_store.as_retriever(
            search_kwargs={"k": num_resumes * 3}
        )
        
        docs = retriever.invoke(job_description)
        
        # Group by filename and calculate relevance
        resume_scores = {}
        for doc in docs:
            filename = doc.metadata.get('filename', 'Unknown')
            if filename not in resume_scores:
                resume_scores[filename] = {
                    'chunks': [],
                    'content': []
                }
            resume_scores[filename]['chunks'].append(doc)
            resume_scores[filename]['content'].append(doc.page_content)
        
        # Get top N resumes
        sorted_resumes = list(resume_scores.items())[:num_resumes]
        
        # Generate detailed analysis using LLM
        llm =ChatOpenAI(
            model="gemma-2-9b-it",
            base_url="http://localhost:1234/v1",
            api_key="lm-studio"
        )
        
        results = []
        for filename, data in sorted_resumes:
            combined_content = "\n\n".join(data['content'][:3])
            
            prompt = f"""Based on the following job description and resume content, 
            provide a brief analysis of why this candidate is a good match.
            
            Job Description:
            {job_description}
            
            Resume Content:
            {combined_content}
            
            Provide a concise 10-15 sentence explanation of the match."""
            
            analysis = llm.invoke(prompt).content
            

            results.append({
                'filename': filename,
                'analysis': analysis,
                'chunks_found': len(data['chunks'])
            })
        
        return results
    
    except Exception as e:
        st.error(f"Error shortlisting resumes: {str(e)}")
        return []

# Streamlit UI
def main():
    st.set_page_config(
        page_title="AI Resume Shortlisting",
        page_icon="📄",
        layout="wide"
    )
    
    st.title("📄 AI-Powered Resume Shortlisting System")
    st.markdown("*Powered by RAG and Vector Search*")
    
    # Initialize vector store
    if st.session_state.vector_store is None:
        with st.spinner("Initializing vector database..."):
            st.session_state.vector_store = initialize_vector_store()
    
    vector_store = st.session_state.vector_store
    
    # Sidebar
    st.sidebar.header("📋 Navigation")
    page = st.sidebar.radio(
        "Select Action",
        ["Upload Resume", "Update Resume", "List Resumes", 
         "Delete Resume", "Shortlist Candidates"]
    )
    
    # Main content based on page selection
    if page == "Upload Resume":
        st.header("📤 Upload New Resume")
        
        uploaded_file = st.file_uploader(
            "Choose a PDF file",
            type=['pdf'],
            help="Upload resume in PDF format"
        )
        
        if uploaded_file:
            if st.button("Upload Resume", type="primary"):
                with st.spinner("Processing resume..."):
                    success = upload_resume(uploaded_file, vector_store)
                    if success:
                        st.success(f"✅ Resume '{uploaded_file.name}' uploaded successfully!")
                    else:
                        st.error("❌ Failed to upload resume")
    
    elif page == "Update Resume":
        st.header("🔄 Update Existing Resume")
        
        resumes = list_resumes(vector_store)
        
        if resumes:
            selected_resume = st.selectbox(
                "Select resume to update",
                options=list(resumes.keys())
            )
            
            uploaded_file = st.file_uploader(
                "Choose new PDF file",
                type=['pdf']
            )
            
            if uploaded_file and st.button("Update Resume", type="primary"):
                with st.spinner("Updating resume..."):
                    success = update_resume(selected_resume, uploaded_file, vector_store)
                    if success:
                        st.success(f"✅ Resume updated successfully!")
                    else:
                        st.error("❌ Failed to update resume")
        else:
            st.info("No resumes found in database")
    
    elif page == "List Resumes":
        st.header("📋 All Stored Resumes")
        
        resumes = list_resumes(vector_store)
        
        if resumes:
            st.write(f"**Total Resumes:** {len(resumes)}")
            
            for i, (filename, info) in enumerate(resumes.items(), 1):
                with st.expander(f"{i}. {filename}"):
                    st.write(f"**Upload Date:** {info['upload_date'][:10]}")
        else:
            st.info("No resumes found in database")
    
    elif page == "Delete Resume":
        st.header("🗑️ Delete Resume")
        
        resumes = list_resumes(vector_store)
        
        if resumes:
            selected_resume = st.selectbox(
                "Select resume to delete",
                options=list(resumes.keys())
            )
            
            if st.button("Delete Resume", type="primary"):
                if delete_resume(selected_resume, vector_store):
                    st.success(f"✅ Resume '{selected_resume}' deleted successfully!")
                    st.rerun()
                else:
                    st.error("❌ Failed to delete resume")
        else:
            st.info("No resumes found in database")
    
    elif page == "Shortlist Candidates":
        st.header("🎯 Shortlist Resumes for Job")
        
        resumes = list_resumes(vector_store)
        
        if resumes:
            st.write(f"**Available Resumes:** {len(resumes)}")
            
            job_description = st.text_area(
                "Enter Job Description",
                height=200,
                placeholder="Paste the complete job description here..."
            )
            
            num_resumes = st.slider(
                "Number of resumes to shortlist",
                min_value=1,
                max_value=min(10, len(resumes)),
                value=min(5, len(resumes))
            )
            
            if st.button("🔍 Shortlist Candidates", type="primary"):
                if job_description:
                    with st.spinner("Analyzing resumes..."):
                        results = shortlist_resumes(
                            job_description,
                            num_resumes,
                            vector_store
                        )
                        
                        if results:
                            st.success(f"✅ Found {len(results)} matching candidates!")
                            
                            for i, result in enumerate(results, 1):
                                with st.expander(
                                    f"#{i} - {result['filename']}", 
                                    expanded=(i==1)
                                ):
                                    st.markdown(f"**Match Analysis:**")
                                    st.write(result['analysis'])
                                    st.caption(
                                        f"Relevant sections found: {result['chunks_found']}"
                                    )
                        else:
                            st.warning("No matching resumes found")
                else:
                    st.warning("Please enter a job description")
        else:
            st.info("No resumes found. Please upload resumes first.")
    
    # Footer
    st.sidebar.markdown("---")
    st.sidebar.info(
        "**About:** This application uses RAG (Retrieval Augmented Generation) "
        "to match resumes with job descriptions using semantic similarity."
    )

if __name__ == "__main__":
    main()