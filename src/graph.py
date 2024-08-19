import streamlit as st
from openai import OpenAI
from langchain_openai import ChatOpenAI
from typing import TypedDict, Annotated, List, Dict
from langgraph.graph import StateGraph, END
#import sqlite3
#from langgraph.checkpoint.sqlite import SqliteSaver
from langchain_core.pydantic_v1 import BaseModel
from langchain_core.messages import AnyMessage, SystemMessage, HumanMessage, AIMessage, ChatMessage
from pinecone import Pinecone
from src.policy_agent import PolicyAgent
from src.commission_agent import CommissionAgent

# Define the structure of the agent state using TypedDict
class AgentState(TypedDict):
    agent: str
    initialMessage: str
    responseToUser: str
    lnode: str
    category: str

# Define the structure for category classification
class Category(BaseModel):
    category: str

class PolicyResponse(BaseModel):
    policy: str
    response: str

class CommissionResponse(BaseModel):
    commission: str
    calculation: str
    response: str

class ContestResponse(BaseModel):
    contestUrl: str
    contestRules: str
    response: str

class TicketResponse(BaseModel):
    ticket: str
    response: str

def get_contest_info():
        with open('contestrules.txt', 'r') as file:
            contestrules = file.read()
        return contestrules

# Define valid categories
VALID_CATEGORIES = ["policy", "commission", "contest", "ticket", "clarify"]

# Define the salesCompAgent class
class salesCompAgent():
    def __init__(self, api_key):
        # Initialize the ChatOpenAI model (from LangChain) and OpenAI client with the given API key
        self.model = ChatOpenAI(model="gpt-4o-mini", temperature=0, api_key=api_key)
        self.client = OpenAI(api_key=api_key)

        #Pinecone configurtion using Streamlit secrets
        self.pinecone_api_key = st.secrets['PINECONE_API_KEY']
        self.pinecone_env = st.secrets['PINECONE_API_ENV']
        self.pinecone_index_name = st.secrets['PINECONE_INDEX_NAME']

        # Initialize Pinecone once
        self.pinecone = Pinecone(api_key=self.pinecone_api_key)
        self.index = self.pinecone.Index(self.pinecone_index_name)

        # Initialize the PolicyAgent and CommissionAgent
        self.policy_agent_class = PolicyAgent(self.client, self.index)
        self.commission_agent_class = CommissionAgent(self.model, self.index)

        # Build the state graph
        builder = StateGraph(AgentState)
        builder.add_node("classifier", self.initial_classifier)
        builder.add_node("policy", self.policy_agent_class.policy_agent)
        builder.add_node("commission", self.commission_agent_class.commission_agent)
        builder.add_node("contest", self.contest_agent)
        builder.add_node("ticket", self.ticket_agent)
        builder.add_node("clarify", self.clarify_agent)

        # Set the entry point and add conditional edges
        builder.set_entry_point("classifier")
        builder.add_conditional_edges("classifier", self.main_router)

        # Define end points for each node
        builder.add_edge("policy", END)
        builder.add_edge("commission", END)
        builder.add_edge("contest", END)
        builder.add_edge("ticket", END)
        builder.add_edge("clarify", END)

        # Set up in-memory SQLite database for state saving
        #memory = SqliteSaver(conn=sqlite3.connect(":memory:", check_same_thread=False))
        #self.graph = builder.compile(checkpointer=memory)

        self.graph = builder.compile()

    # Initial classifier function to categorize user messages
    def initial_classifier(self, state: AgentState):
        print("initial classifier")
        
        CLASSIFIER_PROMPT = f"""
You are an expert in sales operations with deep knowledge of sales compensation. Your job is to accurately classify customer requests into one of the following categories based on context and content, even if specific keywords are not used.

1) **policy**: Select this category if the request is related to any formal sales compensation rules or guidelines, even if the word "policy" is not mentioned. This includes topics like windfall, minimum commission guarantees, bonus structures, or leave-related questions.
   - Example: "What happens to my commission if I go on leave?" (This is about policy.)
   - Example: "Is there any guarantee for minimum commission guarantee or MCG?" (This is about policy.)
   - Example: "Can you tell me what is a windfall?" (This is about policy.)
   - Example: "What is a teaming agreement?" (This is about policy.)
   - Example: "What is a split or commission split?" (This is about policy.)

2) **commission**: Select this category if the request involves the calculation or details of the user's sales commission, such as earnings, rates, or specific deal-related inquiries.
   - Example: "How much commission will I earn on a $500,000 deal?" (This is about commission.)
   - Example: "What is the new commission rate?" (This is about commission.)

3) **contest**: Select this category if the request is about sales contests, such as rules, participation, or rewards.
   - Example: "How do I enter the Q3 sales contest?" (This is about contests.)
   - Example: "What are the rules for the upcoming contest?" (This is about contests.)

4) **ticket**: Select this category if the request involves issues or problems that need to be reported, such as system issues, payment errors, or situations where a service ticket is required.
   - Example: "I can't access my commission report." (This is about a ticket.)
   - Example: "My commission was calculated incorrectly." (This is about a ticket.)

5) **clarify**: Select this category if the request is unclear, ambiguous, or does not fit into the above categories. Ask the user for more details.
   - Example: "Can you clarify your question?" (This is a request for clarification.)

Remember to consider the context and content of the request, even if specific keywords like 'policy' or 'commission' are not used. 
"""

        

        # Invoke the model with the classifier prompt
        llm_response = self.model.with_structured_output(Category).invoke([
            SystemMessage(content=CLASSIFIER_PROMPT),
            HumanMessage(content=state['initialMessage']),
        ])

        category = llm_response.category
        print(f"category is {category}")
        
        # Return the updated state with the category
        return{
            "lnode": "initial_classifier", 
            "responseToUser": "Classifier successful",
            "category": category
        }
    
     # Main router function to direct to the appropriate agent based on the category
    def main_router(self, state: AgentState):
        my_category = state['category']
        if my_category in VALID_CATEGORIES:
            return my_category
        else:
            print(f"unknown category: {my_category}")
            return END

        

    # Placeholder function for the contest agent
    def contest_agent(self, state: AgentState):
        CONTEST_PROMPT = f"""
        You are a Sales Commissions expert. Users will ask you about how to start a sales contest.
        You will send them a URL for a Google form to submit.
        Please follow the contest rules as defined here: 
        {get_contest_info()}
        Please provide user instructions to fill out the Google form.      
        """
        print("contest agent")

        # Invoke the model with the commission agent prompt
        llm_response = self.model.with_structured_output(ContestResponse).invoke([
            SystemMessage(content=CONTEST_PROMPT),
            HumanMessage(content=state['initialMessage']),
        ])

        contestUrl = llm_response.contestUrl
        contestRules = llm_response.contestRules
        response = llm_response.response
        print(f"Contest URL: {contestUrl}")
        print("contest agent")

        # Return the updated state with the category
        return{
            "lnode": "initial_classifier", 
            "responseToUser": f"Please submit the contest form here: {contestUrl}",
            "category": "contest"
        }
        
        

    # Placeholder function for the ticket agent
    def ticket_agent(self, state: AgentState):
        TICKET_PROMPT = f"""
        You are a Sales Commissions expert. Users will ask you about what their commission
        will be for a particular deal. You can assume their on-target incentive to be $100000
        and their annual quota to be $2000000. Also note that Commission is equal to on-target
        incentive divided by annual quota. 
        
        Please provide user commission as well as explain how you computed it.      
        """
        print("ticket agent")

        # Invoke the model with the commission agent prompt
        llm_response = self.model.with_structured_output(TicketResponse).invoke([
            SystemMessage(content=TICKET_PROMPT),
            HumanMessage(content=state['initialMessage']),
        ])

        ticket = llm_response.ticket
        response = llm_response.response
        print(f"ticket: {ticket} response: {response}")
        
        # Return the updated state with the category
        return{
            "lnode": "initial_classifier", 
            "responseToUser": f"ServiceNow email address placeholder",
            "category": "ticket"
        }
        
        
        

    # Placeholder function for the clarify agent
    def clarify_agent(self, state: AgentState):
        print("clarify agent")

    