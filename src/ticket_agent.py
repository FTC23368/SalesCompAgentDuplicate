from src.create_llm_message import create_llm_msg
from src.send_email import send_email
from pydantic import BaseModel
from typing import Optional
from src.prompt_store import get_prompt

class TicketResponse(BaseModel):
    response: str
    createTicket: bool
    email: Optional[str] 

class TicketEmail(BaseModel):
    response: str
    htmlEmail: str
    
class TicketAgent:
    def __init__(self, model):
        self.model = model

    def generate_ticket_response(self, state: dict) -> str:
        user_query = state.get('initialMessage', '')
        ticket_prompt = get_prompt("ticket").format(user_query=user_query)
        llm_messages = create_llm_msg(ticket_prompt, state['message_history'])
        llm_response = self.model.with_structured_output(TicketResponse).invoke(llm_messages)
        full_response = llm_response
        return full_response

    def generate_ticket_email(self, state: dict) -> str:
        ticket_email_prompt = get_prompt("ticketemail")
        llm_messages = create_llm_msg(ticket_email_prompt, state['message_history'])
        llm_response = self.model.with_structured_output(TicketEmail).invoke(llm_messages)
        ticket_email_response = llm_response.htmlEmail
        return ticket_email_response

    def ticket_agent(self, state: dict) -> dict:
        full_response = self.generate_ticket_response(state)
        if full_response.createTicket:
            ticket_email_response = self.generate_ticket_email(state)
            send_email('malihajburney@gmail.com', 'i_jahangir@hotmail.com', 'New Ticket from SalesCompAgent', ticket_email_response)
        return {
            "lnode": "ticket_agent", 
            "responseToUser": full_response.response,
            "category": "ticket"
        }