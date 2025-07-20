import streamlit as st
from typing import List
from langchain_core.messages import BaseMessage
from src.create_llm_message import create_llm_msg
from src.prompt_store import get_prompt

class ContestAgent:
    def __init__(self, client, model, index, embedding_model):
        self.client = client
        self.index = index
        self.model = model
        self.embedding_model = embedding_model
    
    @st.cache_data
    def retrieve_documents(_self, query: str) -> List[str]:
        embedding = _self.client.embeddings.create(model=_self.embedding_model, input=query).data[0].embedding
        results = _self.index.query(vector=embedding, top_k=3, namespace="", include_metadata=True)
        retrieved_content = [r['metadata']['text'] for r in results['matches']]
        return retrieved_content

    def generate_response(self, retrieved_content: List[str], messageHistory: list[BaseMessage]) -> str:
        contest_prompt = get_prompt("contest").format(retrieved_content=retrieved_content)
        llm_messages = create_llm_msg(contest_prompt, messageHistory)
        return self.model.stream(llm_messages)

    def contest_agent(self, state: dict) -> dict:
        retrieved_content = self.retrieve_documents(state['initialMessage'])
        return {
            "lnode": "contest_agent", 
            "incrementalResponse": self.generate_response(retrieved_content, state['message_history']),
            "category": "contest"
        }