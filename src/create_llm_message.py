import streamlit as st
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, BaseMessage

def create_llm_msg(system_prompt: str, sessionHistory: list[BaseMessage]):
    resp = []
    resp.append(SystemMessage(content=system_prompt))
    resp.extend(sessionHistory)
    return resp