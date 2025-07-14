import pandas as pd
import numpy as np
from typing import List
from pydantic import BaseModel
from src.create_llm_message import create_llm_msg, create_llm_message
from langchain_core.messages import BaseMessage
from src.prompt_store import get_prompt

class AnalyticsResponse(BaseModel):
    analysis_result: str
    suggested_followup: str

class AnalyticsAgent:
    def __init__(self, model, client=None):
        self.model = model
        self.client = client

    def generate_response(self, csv_data: str, user_query: str, messageHistory: list[BaseMessage]) -> str:
        analytics_prompt = get_prompt("analytics").format(csv_data=csv_data, user_query=user_query)
        llm_messages = create_llm_msg(analytics_prompt, messageHistory)
        llm_response = self.model.with_structured_output(AnalyticsResponse).invoke(llm_messages)
        return llm_response

    def analytics_agent(self, state: dict) -> dict:
        if 'csv_data' not in state:
            # If no CSV file is uploaded yet, ask the user to upload one
            return {
                "lnode": "analytics_agent",
                "responseToUser": "I'd be happy to help you analyze some data. Please upload a CSV file so I can get started.",
                "category": "analytics",
                "waitForFileUpload": True,
                "fileUploadButton": {"text": "Upload CSV File", "accept": ".csv"}
            }
        
        # Check if the user has asked a question about the data
        if 'analytics_question' not in state:
            # If CSV is uploaded but no question asked yet, store the user's message as the analytics question
            if 'initialMessage' in state:
                state['analytics_question'] = state['initialMessage']
            else:
                # If CSV is uploaded but no question asked yet
                return {
                    "lnode": "analytics_agent",
                    "responseToUser": "Thanks for uploading your data! What specific question would you like me to answer about this dataset?",
                    "category": "analytics",
                    "waitForQuestion": True
                }
        
        # Generate analysis based on the CSV data and user's question
        if 'message_history' not in state:
            state['message_history'] = []
        analysis_response = self.generate_response(state['csv_data'], state['analytics_question'], state['message_history'])
        
        # Construct the full response to the user
        full_response = f"""
            Analysis Results: {analysis_response.analysis_result}
            Follow-up Suggestion: {analysis_response.suggested_followup}
            Would you like me to help with anything else about this data?
        """
        return {
            "lnode": "analytics_agent",
            "responseToUser": full_response,
            "category": "analytics"
        }
