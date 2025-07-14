import streamlit as st
from src.create_llm_message import create_llm_msg
from langchain_core.messages import BaseMessage
from src.prompt_store import get_prompt

class ClarifyAgent:
    def __init__(self, model):
        self.model = model
    
    def clarify_and_classify(self, user_query: str, messageHistory: list[BaseMessage]) -> str:
        clarify_prompt = get_prompt("clarify").format(user_query=user_query)
        llm_messages = create_llm_msg(clarify_prompt, messageHistory)
        llm_response = self.model.invoke(llm_messages)
        full_response = llm_response.content
        return full_response
     
    def clarify_agent(self, state: dict) -> dict:
        full_response = self.clarify_and_classify(state['initialMessage'], state['message_history'])
        return {
            "lnode": "clarify_agent", 
            "responseToUser": full_response,
            "category": "clarify"
        }