import streamlit as st
from typing import List
from src.create_llm_message import create_llm_msg
from langchain_core.messages import BaseMessage
from src.prompt_store import get_prompt
from src.google_firestore_integration import list_files, get_text_content

@st.cache_data
def get_full_planexplainer_content():
    files = list_files()
    planexplainer_files = [f for f in files if "Plan explainer" in (f.get("doc_category") or [])]
    total_content = []

    for file in planexplainer_files:
        content_filename = file["file_name"]
        content = get_text_content(content_filename)
        total_content.append(content)
    return "\n".join(total_content)

class PlanExplainerAgent:
    def __init__(self, client, model, index, embedding_model):
        self.client = client
        self.index = index
        self.model = model
        self.embedding_model = embedding_model

    @st.cache_data
    def retrieve_documents(_self, query: str) -> List[str]:
        return get_full_planexplainer_content()
        embedding = _self.client.embeddings.create(model=_self.embedding_model, input=query).data[0].embedding
        results = _self.index.query(vector=embedding, top_k=3, namespace="", include_metadata=True)
        retrieved_content = [r['metadata']['text'] for r in results['matches']]
        return retrieved_content

    def generate_response(self, retrieved_content: List[str], messageHistory: list[BaseMessage]) -> str:
        plan_explainer_prompt = get_prompt("planexplainer").format(retrieved_content=retrieved_content)
        llm_messages = create_llm_msg(plan_explainer_prompt, messageHistory)
        return self.model.stream(llm_messages)

    def plan_explainer_agent(self, state: dict) -> dict:
        retrieved_content = self.retrieve_documents(state['initialMessage'])
        return {
            "lnode": "plan_explainer_agent", 
            "incrementalResponse": self.generate_response(retrieved_content, state['message_history']),
            "category": "planexplainer"
        }