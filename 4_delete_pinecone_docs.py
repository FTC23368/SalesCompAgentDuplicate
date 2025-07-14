# src/template_agent.py
import streamlit as st
from pinecone import Pinecone

pinecone_api_key = st.secrets['PINECONE_API_KEY']
pinecone_env = st.secrets['PINECONE_API_ENV']
pinecone_index_name = st.secrets['PINECONE_INDEX_NAME']
pinecone = Pinecone(api_key=pinecone_api_key)
index = pinecone.Index(pinecone_index_name)
print(index.delete(filter={"docname": "spif_design_prompt (1).md"}))