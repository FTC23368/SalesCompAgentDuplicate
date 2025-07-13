import streamlit as st
from typing import List
from langchain_core.messages import BaseMessage
from src.create_llm_message import create_llm_msg
from src.prompt_store import get_prompt
from src.google_firestore_integration import list_files, get_text_content
 
@st.cache_data
def get_full_policy_content():
    files = list_files()
    policy_files = [f for f in files if "Policy" in (f.get("doc_category") or [])]
    total_content = []

    for file in policy_files:
        content_filename = file["file_name"]
        content = get_text_content(content_filename)
        total_content.append(content)
    return "\n".join(total_content)

class PolicyAgent:
    def __init__(self, client, model, index):
        self.client = client
        self.index = index
        self.model = model
    
    @st.cache_data
    def retrieve_documents(_self, query: str) -> List[str]:
        embedding = _self.client.embeddings.create(model="text-embedding-ada-002", input=query).data[0].embedding
        results = _self.index.query(vector=embedding, top_k=1, namespace="", include_metadata=True)
        retrieved_content = [r['metadata']['text'] for r in results['matches']]
        full_content = get_full_policy_content()
        retrieved_content.append(full_content)
        return retrieved_content

    def generate_response(self, retrieved_content: List[str], user_query: str, messageHistory: list[BaseMessage]) -> str:
        policy_prompt = get_prompt("policy").format(retrieved_content=retrieved_content)
        llm_messages = create_llm_msg(policy_prompt, messageHistory)
        return self.model.stream(llm_messages)

    def policy_agent(self, state: dict) -> dict:
        retrieved_content = self.retrieve_documents(state['initialMessage'])
        return {
            "lnode": "policy_agent", 
            "incrementalResponse": self.generate_response(retrieved_content, state['initialMessage'], state['message_history']),
            "category": "policy"
        }