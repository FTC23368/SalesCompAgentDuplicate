# src/commission_agent.py

import streamlit as st
from src.create_llm_message import create_llm_message
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

# When CommissionAgent object is created, it's initialized with a model and an index. 
# The main entry point is the commission_agent method. You can see workflow.add_node for commission_agent node in graph.py

class CommissionAgent:
    
    def __init__(self, model):
        """
        Initialize the CommissionAgent with a ChatOpenAI model.
        
        :param model: An instance of the ChatOpenAI model used for generating responses.
        """
        self.model = model

    def generate_commission_response(self, user_query: str) -> str:
        """
        Generate a response for commission-related queries using the ChatOpenAI model.
        
        :param user_query: The original query from the user.
        :return: A string response generated by the language model.
        """
        commission_prompt = f"""
        You are a Sales Commissions expert. Users will ask you about what their commission
        will be for a particular deal. You will use the following method to calculate commission:
        
        Step 1: Check if the user has provided you the Deal value in dollars, on-target incentive (OTI),
        and annual quota in dollars.

        Step 2: If the user did not provide complete information ask them to provide it.

        Step 3:  If the output includes the dollar sign, please escape it to prevent markdown rendering issues. Calculate Base Commission Rate (BCR). BCR is equal to on-target
        incentive divided by annual quota. 
        
        Step 4: Compute the commission by multiplying BCR by deal value. 

        Step 5: Please provide the user with their expected commission in a properly formatted sentence 
        and explain how it was calculated.

        Step 6: Please provide the response without using any LaTeX. 
        Format any calculations or equations in simple plain text or markdown. 
        Do not use LaTeX for formatting.

        If the output includes the dollar sign, please escape it to prevent markdown rendering issues.
        
        """
        
        # Create a well-formatted message for LLM by passing the retrieved information above to create_llm_messages
        llm_messages = create_llm_message(commission_prompt)

        # Invoke the model with the well-formatted prompt, including SystemMessage, HumanMessage, and AIMessage
        llm_response = self.model.invoke(llm_messages)
        
        # Extract the content attribute from the llm_response object 
        full_response = llm_response.content
        return full_response

    def commission_agent(self, state: dict) -> dict:
        """
        Handle commission-related queries by generating a response using the ChatOpenAI model.
        
        :param state: A dictionary containing the state of the current conversation, including the user's initial message.
        :return: A dictionary with the updated state, including the response and the node category.
        """
        # Generate a response based on the user's initial message
        full_response = self.generate_commission_response(state['initialMessage'])
        
        # Return the updated state with the generated response and the category set to 'commission'
        return {
            "lnode": "commission_agent", 
            "responseToUser": full_response,
            "category": "commission"
        }
