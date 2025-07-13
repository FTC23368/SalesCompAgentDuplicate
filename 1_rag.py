import os
import PyPDF2
import hashlib
import numpy as np

import streamlit as st
from streamlit.logger import get_logger

from pinecone import Pinecone
from openai import OpenAI

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import PyPDFLoader

from pathlib import Path

from src.google_firestore_integration import upload_file

# Note: As a system admin, you only run this script directly from bash to upload the PDF or Markdown files for RAG. 
# The users of Sales Comp Agents will not use this functionality.
# Run using "streamlit run rag.py"

# Initialize logger
LOGGER = get_logger(__name__)

# Get API keys and configuration from Streamlit secrets
PINECONE_API_KEY=st.secrets['PINECONE_API_KEY']
PINECONE_API_ENV=st.secrets['PINECONE_API_ENV']
PINECONE_INDEX_NAME=st.secrets['PINECONE_INDEX_NAME']

# Initialize OpenAI client
client=OpenAI(api_key=st.secrets['OPENAI_API_KEY'])

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

# Create embeddings for text and store in Pinecone
def embed(text,filename, filetype, doc_category, doc_name):
    pc = Pinecone(api_key=st.secrets['PINECONE_API_KEY'])
    index = pc.Index(PINECONE_INDEX_NAME)
    text_splitter = RecursiveCharacterTextSplitter(chunk_size = 10000,chunk_overlap  = 200,length_function = len,is_separator_regex = False)
    docs=text_splitter.create_documents([text])
    st.sidebar.write(f"{filename=}, {filetype=}, {doc_category=}, {doc_name=}")
    upload_file(text, filename, filetype, doc_category, doc_name)
    
    # Process each chunk
    for idx,d in enumerate(docs):
        # Create unique hash for the chunk
        hash=hashlib.md5(d.page_content.encode('utf-8')).hexdigest()
        # Generate embedding using OpenAI
        embedding=client.embeddings.create(model=st.secrets['EMBEDDING_MODEL'], input=d.page_content).data[0].embedding
        # Create metadata for the chunk
        metadata={"hash":hash,"text":d.page_content,"index":idx,"model":st.secrets['EMBEDDING_MODEL'],"docname":filename}
        # Store in Pinecone
        index.upsert([(hash,embedding,metadata)])
    
    #upload_file(text, filename, filetype, doc_category, doc_name)

    return

# In Python file, if you set __name__ variable to '__main__', any code
# inside that if statement is run when the file is run directly.
if __name__ == '__main__':
    # Section 1: Direct Text Input
    # Creates a text area where users can paste or type text directly   

    doc_category=st.multiselect("Select all categories that apply", ["Policy", "Product", "Other"])
    doc_name=st.text_input("Document Name",value="")

    st.markdown("# Upload text directly")
    uploaded_text = st.text_area("Enter Text","")
    if st.button('Process and Upload Text'):
        embedding = embed(uploaded_text,"Anonymous", "text", doc_category, doc_name)

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
            embedding = embed(file_text, uploaded_file.name, uploaded_file.type, doc_category, doc_name)

            #upload_file_to_firestore(uploaded_file, )
        