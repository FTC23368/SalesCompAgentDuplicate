import streamlit as st
from src.create_llm_message import create_llm_msg
from langchain_core.messages import BaseMessage
from src.prompt_store import get_prompt

class ClarifyAgent:
    def __init__(self, model):
        self.model = model
    
    def clarify_and_classify(self, messageHistory: list[BaseMessage]) -> str:
        user_query = messageHistory[-1].content
        clarify_prompt = get_prompt("clarify").format(user_query=user_query)
        llm_messages = create_llm_msg(clarify_prompt, messageHistory)
        return self.model.stream(llm_messages)
     
    def clarify_agent(self, state: dict) -> dict:
        return {
            "lnode": "clarify_agent", 
            "incrementalResponse": self.clarify_and_classify(state['message_history']),
            "category": "clarify"
        }