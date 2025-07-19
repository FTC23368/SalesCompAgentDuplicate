from src.create_llm_message import create_llm_msg
from langchain_core.messages import BaseMessage
from src.prompt_store import get_prompt

class SmallTalkAgent:
    def __init__(self, client, model):
        self.client = client
        self.model = model

    def generate_response(self, user_query: str, messageHistory: list[BaseMessage]) -> str:
        small_talk_prompt = get_prompt("smalltalk").format(user_query=user_query)
        llm_messages = create_llm_msg(small_talk_prompt, messageHistory)
        return self.model.stream(llm_messages)

    def small_talk_agent(self, state: dict) -> dict:
        return {
            "lnode": "small_talk_agent", 
            "incrementalResponse": self.generate_response(state['initialMessage'], state['message_history']),
            "category": "smalltalk"
        }