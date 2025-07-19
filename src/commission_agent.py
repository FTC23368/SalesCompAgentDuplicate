import streamlit as st
from src.create_llm_message import create_llm_msg
from langchain_core.messages import BaseMessage
from src.prompt_store import get_prompt

class CommissionAgent:
    def __init__(self, model):
        self.model = model

    def generate_commission_response(self, messageHistory: list[BaseMessage]) -> str:
        commission_prompt = get_prompt("commission")
        llm_messages = create_llm_msg(commission_prompt, messageHistory)
        return self.model.stream(llm_messages)

    def commission_agent(self, state: dict) -> dict:
        return {
            "lnode": "commission_agent", 
            "incrementalResponse": self.generate_commission_response(state['message_history']),
            "category": "commission"
        }