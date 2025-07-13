import streamlit as st
from src.create_llm_message import create_llm_msg
from langchain_core.messages import BaseMessage
from src.prompt_store import get_prompt

class CommissionAgent:
    def __init__(self, model):
        self.model = model

    def generate_commission_response(self, user_query: str, messageHistory: list[BaseMessage]) -> str:
        commission_prompt = get_prompt("commission")
        llm_messages = create_llm_msg(commission_prompt, messageHistory)
        llm_response = self.model.invoke(llm_messages)
        full_response = llm_response.content
        return full_response

    def commission_agent(self, state: dict) -> dict:
        full_response = self.generate_commission_response(state['initialMessage'], state['message_history'])
        return {
            "lnode": "commission_agent", 
            "responseToUser": full_response,
            "category": "commission"
        }