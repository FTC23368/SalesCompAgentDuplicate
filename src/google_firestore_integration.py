from google.cloud import firestore

def get_all_prompts(credentials):
    """
    Retrieves default prompts from Google Firestore database.
    
    Args:
        credentials: Google Cloud credentials object for authentication
        
    Returns:
        list: A list of dictionaries containing prompt documents, where each dictionary
             includes the document ID and all fields from the Firestore document.
             Example: [{'id': 'doc1', 'user': 'default', 'prompt_text': '...'}]
    """
    # Initialize a Firestore client with the provided credentials
    db = firestore.Client(credentials=credentials)
    
    # Get a reference to the 'Prompts' collection in Firestore
    collection_ref = db.collection(u'Prompts')
    
    # Create a query to filter documents where 'user' field equals 'default'
    query = collection_ref.where('user', '==', 'default')
    
    # Execute the query and get a stream of matching documents
    docs = query.stream()
    
    # Create a list of dictionaries containing document data
    # For each document:
    # - doc.id gets the document's unique identifier
    # - doc.to_dict() converts the document data to a Python dictionary
    # - **doc.to_dict() unpacks the dictionary to merge with the id
    results = [{'id': doc.id, **doc.to_dict()} for doc in docs]
    
    return results

def get_one_prompt(credentials, user, prompt_name):
    db = firestore.Client(credentials=credentials)
    
    # Get a reference to the 'Prompts' collection in Firestore
    collection_ref = db.collection(u'Prompts')
    
    # Create a query to filter documents where 'user' field equals 'default'
    query = collection_ref.where('prompt_name', '==', prompt_name)
    
    # Execute the query and get a stream of matching documents
    docs = query.stream()
    
    # Create a list of dictionaries containing document data
    # For each document:
    # - doc.id gets the document's unique identifier
    # - doc.to_dict() converts the document data to a Python dictionary
    # - **doc.to_dict() unpacks the dictionary to merge with the id
    results = [{'id': doc.id, **doc.to_dict()} for doc in docs]
    prompt_value = results[0].get("prompt_value")
   
    return prompt_value

def fetch_prompts_by_name(credentials,user,name):
    db = firestore.Client(credentials=credentials)
    collection_ref = db.collection(u'Prompts')
    query = collection_ref.where('prompt_name', '==', name).where('user', '==', user)

    docs = query.stream()
    
    # Collect document IDs that match the query
    results = [{'id': doc.id, **doc.to_dict()} for doc in docs]
    return results

def add_prompt(credentials, user, prompt_name, new_value):
    db = firestore.Client(credentials=credentials)
    collection_ref = db.collection(u'Prompts').document() 
    collection_ref.set({
        u'user': user,
        u'prompt_name': prompt_name,
        u'prompt_value': new_value
    })

def update_prompt_by_name(credentials, user, prompt_name, new_value):
    res=fetch_prompts_by_name(credentials,user,prompt_name)
    if(len(res)==0):
        add_prompt(credentials, user, prompt_name, new_value)
        return "Found no match. Adding."
    elif len(res)==1:
        document_id=res[0].get('id')
        db = firestore.Client(credentials=credentials)
        collection_ref = db.collection(u'Prompts')
        document_ref = collection_ref.document(document_id)
        document_ref.update({'prompt_value': new_value})
        return f"Found one match {res}. Document {document_id} updated: prompt to {new_value}"
    else:
        return f"Found multiple matches {res}. Not updating"
    
def add_evals(credentials, records):
    db = firestore.Client(credentials=credentials)
    batch = db.batch()
    for record in records:
        #timestamp = record['start_time']
        #duration = record['duration']
        #input = record['input']
        #expected = record['expected']
        collection_ref = db.collection(u'Evals').document() 
        batch.set(collection_ref, record)
    batch.commit()

# ---------------------------------------------------------------------------------------------------
# The code below is used for storage bucket setup in Google Firestore 
# ---------------------------------------------------------------------------------------------------

from datetime import datetime
from io import BytesIO

import firebase_admin
from firebase_admin import credentials, firestore, storage
import streamlit as st
from PyPDF2 import PdfReader


def init_firestore():
    """Initialize and return a Firestore client using Streamlit secrets."""
    if not firebase_admin._apps:
        cred_info = st.secrets.get("firebase")
        if cred_info is None:
            raise RuntimeError("Firebase credentials not found in st.secrets")
        cred = credentials.Certificate(dict(cred_info))

        st.sidebar.dataframe(cred_info)

        # allow overriding the bucket used for uploads
        bucket_name = cred_info.get("bucket_name")
        if not bucket_name:
            raise RuntimeError(
                "project_id or storage_bucket must be provided in st.secrets"
            )
            

        firebase_admin.initialize_app(cred, {"storageBucket": bucket_name})
    return firestore.client()


def get_bucket():
    """Return the default Firebase Storage bucket."""
    init_firestore()  # ensure app initialized
    return storage.bucket()


def extract_text(file_bytes: bytes, filename: str, file_type: str) -> str:
    """Return plain text extracted from PDF or text file bytes."""
    #if file_type == "application/pdf":
    #    reader = PdfReader(filename)
    #    text = "\n".join(page.extract_text() or "" for page in reader.pages)
    #    return text
    # assume utf-8 text for other types
    return file_bytes


def upload_file(file_bytes: bytes, filename: str, file_type: str, doc_category: list, doc_name: str):
    """Upload the file to Firebase Storage and store metadata only."""
    st.sidebar.write(f"uploadfile: {filename=}, {file_type=}")
    db = init_firestore()
    bucket = get_bucket()
    uploaded_at = datetime.utcnow()
    content_text = extract_text(file_bytes, filename, file_type)

    # paths in storage
    file_path = f"files/{filename}"
    content_path = f"file_contents/{filename}.content"

    print(f"In upload file {file_path=}, {content_path=}")
    print(f"{bucket=}")
    

    # upload the original file
    blob = bucket.blob(file_path)
    blob.upload_from_string(file_bytes, content_type=file_type)

    # upload extracted text as separate file
    text_blob = bucket.blob(content_path)
    text_blob.upload_from_string(content_text, content_type="text/plain")

    # metadata record with references to storage paths
    doc_ref = db.collection("files").document(filename)
    doc_ref.set(
        {
            "file_name": filename,
            "file_size": len(file_bytes),
            "file_type": file_type,
            "uploaded_at": uploaded_at,
            "storage_path": file_path,
            "content_path": content_path,
            "doc_category": doc_category,
            "doc_name": doc_name,
        }
    )


def list_files():
    """Return metadata for all uploaded files."""
    db = init_firestore()
    docs = db.collection("files").stream()
    return [doc.to_dict() for doc in docs]


def get_file_content(filename: str) -> bytes:
    """Retrieve binary content for the given filename from Storage."""
    db = init_firestore()
    bucket = get_bucket()
    meta = db.collection("files").document(filename).get()
    if meta.exists:
        storage_path = meta.to_dict().get("storage_path", f"files/{filename}")
        blob = bucket.blob(storage_path)
        if blob.exists():
            return blob.download_as_bytes()
    return b""


def get_text_content(filename: str) -> str:
    """Retrieve text content file from Storage."""
    db = init_firestore()
    bucket = get_bucket()
    meta = db.collection("files").document(filename).get()
    if meta.exists:
        content_path = meta.to_dict().get(
            "content_path", f"file_contents/{filename}.content"
        )
        blob = bucket.blob(content_path)
        if blob.exists():
            return blob.download_as_text()
    return ""

