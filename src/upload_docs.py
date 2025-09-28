import PyPDF2
from src.supabase_integration import get_supabase_client, insert_docs, get_accounts, get_orgs
import streamlit as st
from streamlit.logger import get_logger
from langchain.document_loaders import PyPDFLoader
from pathlib import Path

# Note: As a system admin, you only run this script directly from bash to upload the PDF or Markdown files for RAG. 

LOGGER = get_logger(__name__)

def pdf_to_text(uploaded_file):
    pdfReader = PyPDF2.PdfReader(uploaded_file)
    count = len(pdfReader.pages)
    text=""
    for i in range(count):
        page = pdfReader.pages[i]
        text=text+page.extract_text()
    return text

def md_to_text(uploaded_file):
    return uploaded_file.getvalue().decode('utf-8')
    
def upload_file(org_id: int, account_id: int, file_bytes: bytes, filename: str, file_type: str, doc_category: list, doc_name: str):
    params = {
        "org_id": org_id,
        "account_id": account_id,
        "doc_category": doc_category,
        "doc_contents": file_bytes,
        #"doc_src": file_bytes,
        "doc_title": doc_name,
    }
    st.sidebar.json(params)
    supabase = get_supabase_client()
    insert_docs(supabase, params)

def upload_docs():
    st.title("Document Loader")
    supabase = get_supabase_client()
    orgs = get_orgs(supabase)
    org_names = [r.get('name') for r in orgs]
    org_map = {r.get('name'): r.get('id') for r in orgs}
    option = st.selectbox("Organization Name", org_names, key="upload_docs_org_names")
    org_id = org_map.get(option, -1)

    accounts = get_accounts(supabase, org_id)
    account_names = [r.get('name') for r in accounts]
    account_map = {r.get('name'): r.get('id') for r in accounts}
    option_account = st.selectbox("Account Name", account_names, key="upload_docs_account_names")
    account_id = account_map.get(option_account, -2)

    doc_category=st.pills("Select the category that applies", ["Policy", "Product", "Other"])
    doc_name=st.text_input("Document Name",value="")
    
    # Section 1: Direct Text Input
    st.markdown("# Upload text directly")
    uploaded_text = st.text_area("Enter Text","")
    if st.button('Process and Upload Text'):
        upload_file(org_id, account_id, uploaded_text,"Anonymous", "text", doc_category, doc_name)

    # Section 2: File Upload. 
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
            upload_file(org_id, account_id, file_text, uploaded_file.name, uploaded_file.type, doc_category, doc_name)


if __name__ == '__main__':
    upload_docs() 