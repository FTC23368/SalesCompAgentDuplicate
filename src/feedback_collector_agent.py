from typing import Optional
from src.create_llm_message import create_llm_msg
from src.send_email import send_email
from src.prompt_store import get_prompt
from pydantic import BaseModel

class FeedbackResponse(BaseModel):
    response: str
    createFeedback: bool
    email: Optional[str]

class FeedbackEmail(BaseModel):
    response: str
    htmlEmail: str

class FeedbackCollectorAgent:
    def __init__(self, model):
        self.model = model

    def generate_response(self, state: dict) -> str:
        user_query = state.get('initialMessage', '')
        feedback_collector_prompt = get_prompt("feedbackcollector").format(user_query=user_query)
        llm_messages = create_llm_msg(feedback_collector_prompt, state['message_history'])
        llm_response = self.model.with_structured_output(FeedbackResponse).invoke(llm_messages)
        feedback_collector_response = llm_response
        return feedback_collector_response
    
    def generate_feedback_email(self, state: dict) -> str:
        feedback_email_prompt = get_prompt("feedbackemail")
        llm_messages = create_llm_msg(feedback_email_prompt, state['message_history'])
        llm_response = self.model.with_structured_output(FeedbackEmail).invoke(llm_messages)
        feedback_email_response = llm_response.htmlEmail
        return feedback_email_response

    def feedback_collector_agent(self, state: dict) -> dict:
        full_response = self.generate_response(state)
        if full_response.createFeedback:
            print("Generating and sending feedback email...")
            feedback_email_response = self.generate_feedback_email(state)
            print(f"Sending email to: i_jahangir@hotmail.com")
            send_email('malihajburney@gmail.com', 'i_jahangir@hotmail.com', "Feedback for Sales Comp", feedback_email_response)
        
        return {
            "lnode": "feedback_collector_agent", 
            "responseToUser": full_response.response,
            "category": "feedbackcollector"
        }