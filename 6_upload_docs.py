import os
import PyPDF2
import hashlib
import numpy as np
from src.supabase_integration import get_supabase_client, insert_docs

import streamlit as st
from streamlit.logger import get_logger

from langchain.document_loaders import PyPDFLoader

from pathlib import Path


# Note: As a system admin, you only run this script directly from bash to upload the PDF or Markdown files for RAG. 
# The users of Sales Comp Agents will not use this functionality.
# Run using "streamlit run rag.py"

# Initialize logger
LOGGER = get_logger(__name__)


# Convert PDF file to text string
def pdf_to_text(uploaded_file):
    pdfReader = PyPDF2.PdfReader(uploaded_file)
    count = len(pdfReader.pages)
    text=""
    for i in range(count):
        page = pdfReader.pages[i]
        text=text+page.extract_text()
    return text

# Convert Markdown file to text string
def md_to_text(uploaded_file):
    # Read markdown file content directly as text
    return uploaded_file.getvalue().decode('utf-8')

    

def upload_file(org_id: int, account_id: int, file_bytes: bytes, filename: str, file_type: str, doc_category: list, doc_name: str):
    params = {
        "org_id": org_id,
        "account_id": account_id,
        "doc_category": doc_category,
        "doc_contents": file_bytes,
        "doc_src": file_bytes,
        "doc_title": doc_name,
    }

    st.sidebar.json(params)

    supabase = get_supabase_client()
    insert_docs(supabase, params)


# In Python file, if you set __name__ variable to '__main__', any code
# inside that if statement is run when the file is run directly.
if __name__ == '__main__':
    # Section 1: Direct Text Input
    # Creates a text area where users can paste or type text directly   
    org_id = st.number_input("org_id", min_value=1000, step=1, format="%i")
    account_id = st.number_input("account_id", min_value=1000, step=1, format="%i")
    

    doc_category=st.pills("Select the category that applies", ["Policy", "Product", "Other"])
    doc_name=st.text_input("Document Name",value="")

    st.markdown("# Upload text directly")
    uploaded_text = st.text_area("Enter Text","")
    if st.button('Process and Upload Text'):
        upload_file(org_id, account_id, uploaded_text,"Anonymous", "text", doc_category, doc_name)

    # Section 2: File Upload. 
    # Allows users to upload either PDF or Markdown files and add to Pinecone
    st.markdown("# Upload file: PDF or Markdown")
    uploaded_file = st.file_uploader("Upload file", type=["pdf", "md"])
    if uploaded_file is not None:
        if st.button('Process and Upload File'):
            # Determine file type and process accordingly
            file_extension = Path(uploaded_file.name).suffix.lower()
            if file_extension == '.pdf':
                # Convert PDF to text using PyPDF2
                file_text = pdf_to_text(uploaded_file)
            else:  # .md file
                # Read markdown file directly as text
                file_text = md_to_text(uploaded_file)
            # Convert text to embeddings and store in Pinecone using original filename
            upload_file(org_id, account_id, file_text, uploaded_file.name, uploaded_file.type, doc_category, doc_name)

            #upload_file_to_firestore(uploaded_file, )
        