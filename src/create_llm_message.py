import streamlit as st
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, BaseMessage

def create_llm_msg(system_prompt: str, messageHistory: list[BaseMessage]):
    resp = []
    resp.append(SystemMessage(content=system_prompt))
    resp.extend(messageHistory)
    return resp