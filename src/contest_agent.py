# src/contest_agent.py

from langchain_core.messages import SystemMessage, HumanMessage

class ContestAgent:
    
    def __init__(self, model):
        """
        Initialize the ContestAgent with a ChatOpenAI model.
        
        :param model: An instance of the ChatOpenAI model used for generating responses.
        """
        self.model = model

    def get_contest_info(self) -> str:
        """
        Retrieve contest information from an external source, e.g., a file.
        
        :return: A string containing the contest rules.
        """
        with open('contestrules.txt', 'r') as file:
            contest_rules = file.read()
        return contest_rules

    def generate_contest_response(self, user_query: str) -> str:
        """
        Generate a response for contest-related queries using the ChatOpenAI model.
        
        :param user_query: The original query from the user.
        :return: A string response generated by the language model.
        """
        contest_prompt = f"""
        You are a Sales Commissions expert. Users will ask you about how to start a sales contest.
        You will send them a URL for a Google form to submit.
        Please follow the contest rules as defined here: 
        {self.get_contest_info()}
        Please provide user instructions to fill out the Google form.      
        """
        
        # Generate a response using the ChatOpenAI model's invoke method
        llm_response = self.model.invoke([
            SystemMessage(content=contest_prompt),
            HumanMessage(content=user_query)
        ])
        
        # The response content should include all necessary information, such as the URL
        full_response = llm_response.content
        
        # If the URL is part of the response content, you can extract it here
        contest_url = "URL not found"  # Default value if URL not found
        if "http" in full_response:  # Basic check for a URL in the response
            contest_url = full_response.split()[0]  # Assuming the URL is the first item in the response
        
        return contest_url, full_response

    def contest_agent(self, state: dict) -> dict:
        """
        Handle contest-related queries by generating a response using the ChatOpenAI model.
        
        :param state: A dictionary containing the state of the current conversation, including the user's initial message.
        :return: A dictionary with the updated state, including the response and the node category.
        """
        # Generate a response based on the user's initial message
        contest_url, full_response = self.generate_contest_response(state['initialMessage'])
        
        # Return the updated state with the generated response and the category set to 'contest'
        return {
            "lnode": "contest_agent", 
            "responseToUser": f"Please submit the contest form here: {contest_url}",
            "category": "contest"
        }
