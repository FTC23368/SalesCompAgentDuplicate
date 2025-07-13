from langchain_core.messages import BaseMessage
from src.create_llm_message import create_llm_message, create_llm_msg
from src.send_email import send_email
from src.prompt_store import get_prompt
from typing import List

class ContestAgent:
    def __init__(self, client, model, index, embedding_model):
        self.client = client
        self.index = index
        self.model = model
        self.embedding_model = embedding_model

    def retrieve_documents(self, query: str) -> List[str]:
        embedding = self.client.embeddings.create(model=self.embedding_model, input=query).data[0].embedding
        results = self.index.query(vector=embedding, top_k=3, namespace="", include_metadata=True)
        retrieved_content = [r['metadata']['text'] for r in results['matches']]
        print(f"{query=},{retrieved_content=}")
        return retrieved_content

    def generate_contest_response(self, retrieved_content: List[str], user_query: str, messageHistory: list[BaseMessage]) -> str:
        contest_prompt = get_prompt("contest").format(retrieved_content=retrieved_content)
        llm_messages = create_llm_msg(contest_prompt, messageHistory)
        llm_response = self.model.invoke(llm_messages)
        full_response = llm_response.content
        return full_response

    def contest_agent(self, state: dict) -> dict:
        print("starting contest agent")
        retrieved_content = self.retrieve_documents(state['initialMessage'])
        full_response = self.generate_contest_response(retrieved_content, state['initialMessage'], state['message_history'])
        #llm_response.decision = llm_response.decision.replace("[", "").replace("]", "") #this line is for Groq LLM because it adds square brackets
        print("completed contest agent")
        return {
            "lnode": "contest_agent", 
            "responseToUser": full_response,
            "category": "contest"
        }