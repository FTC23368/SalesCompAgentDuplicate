import streamlit as st
from typing import List
from langchain_core.messages import BaseMessage
from src.create_llm_message import create_llm_msg
from src.prompt_store import get_prompt
from src.google_firestore_integration import list_files, get_text_content
from src.supabase_integration import get_docs
 
@st.cache_data
def get_full_policy_content(_supabase_client, account_id):
    response = get_docs(_supabase_client, account_id, "Policy")
    total_content = [""]
    if response and len(response) > 0:
        total_content = [r.get('doc_contents') for r in response]

    return "\n".join(total_content)

class PolicyAgent:
    def __init__(self, client, model, index, embedding_model, supabase_client, user_record):
        self.client = client
        self.index = index
        self.model = model
        self.embedding_model = embedding_model
        self.supabase_client = supabase_client
        self.user_record = user_record
        #st.success(f"Policy Agent: {user_record}")
    
    @st.cache_data
    def retrieve_documents(_self, query: str) -> List[str]:
        account_id = _self.user_record.get("account_id", 1111)
        return get_full_policy_content(_self.supabase_client, account_id)
        embedding = _self.client.embeddings.create(model=self.embedding_model, input=query).data[0].embedding
        results = _self.index.query(vector=embedding, top_k=1, namespace="", include_metadata=True)
        retrieved_content = [r['metadata']['text'] for r in results['matches']]
        full_content = get_full_policy_content()
        retrieved_content.append(full_content)
        return retrieved_content

    def generate_response(self, retrieved_content: List[str], messageHistory: list[BaseMessage]) -> str:
        policy_prompt = get_prompt("policy").format(retrieved_content=retrieved_content)
        llm_messages = create_llm_msg(policy_prompt, messageHistory)
        return self.model.stream(llm_messages)

    def policy_agent(self, state: dict) -> dict:
        retrieved_content = self.retrieve_documents(state['initialMessage'])
        #with st.expander("policy_response"):
        #    st.write(retrieved_content)
        return {
            "lnode": "policy_agent", 
            "incrementalResponse": self.generate_response(retrieved_content, state['message_history']),
            "category": "policy"
        }