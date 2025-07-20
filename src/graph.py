import streamlit as st
from openai import OpenAI
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
from langchain_anthropic import ChatAnthropic
from langchain_xai import ChatXAI
from typing import TypedDict, Annotated, Dict
from langgraph.graph import StateGraph, START, END
from pydantic import BaseModel
from langchain_core.messages import AnyMessage, BaseMessage
from pinecone import Pinecone
from src.policy_agent import PolicyAgent
from src.commission_agent import CommissionAgent
from src.contest_agent import ContestAgent
from src.ticket_agent import TicketAgent 
from src.clarify_agent import ClarifyAgent
from src.small_talk_agent import SmallTalkAgent
from src.plan_explainer_agent import PlanExplainerAgent
from src.feedback_collector_agent import FeedbackCollectorAgent
from src.create_llm_message import create_llm_msg
from src.analytics_agent import AnalyticsAgent
from src.research_agent import ResearchAgent
from langgraph.graph.message import AnyMessage, add_messages
from src.prompt_store import get_prompt

class AgentState(TypedDict):
    agent: str
    initialMessage: str
    responseToUser: str
    incrementalResponse: str
    lnode: str
    category: str
    #sessionState: Dict
    #sessionHistory: Annotated[list[AnyMessage], add_messages]
    message_history: list[BaseMessage]
    email: str
    name: str
    csv_data: str
    analytics_question: str

class Category(BaseModel):
    category: str

VALID_CATEGORIES = ["policy", "commission", "contest", "ticket", "smalltalk", "clarify", "planexplainer", "feedbackcollector", "analytics"]

class salesCompAgent():
    def __init__(self, api_key, embedding_model):
        self.client = OpenAI(api_key=api_key)
        #self.model = ChatOpenAI(model=st.secrets['OPENAI_MODEL'], temperature=0, api_key=api_key)
        self.model = ChatOpenAI(model=st.secrets['OPENAI_MODEL'], api_key=api_key)
        #self.model = ChatGroq(model=st.secrets['GROQ_MODEL'], temperature=0, api_key=st.secrets['GROQ_API_KEY'])
        #self.model = ChatAnthropic(model=st.secrets['ANTHROPIC_MODEL'], temperature=0, api_key=st.secrets['ANTHROPIC_API_KEY'])
        #self.model = ChatXAI(model=st.secrets['XAI_MODEL'], temperature=0, api_key=st.secrets['XAI_API_KEY'])

        self.pinecone_api_key = st.secrets['PINECONE_API_KEY']
        self.pinecone_env = st.secrets['PINECONE_API_ENV']
        self.pinecone_index_name = st.secrets['PINECONE_INDEX_NAME']

        self.pinecone = Pinecone(api_key=self.pinecone_api_key)
        self.index = self.pinecone.Index(self.pinecone_index_name)

        self.policy_agent_class = PolicyAgent(self.client, self.model, self.index, embedding_model)
        self.commission_agent_class = CommissionAgent(self.model)
        self.contest_agent_class = ContestAgent(self.client, self.model, self.index, embedding_model)
        self.ticket_agent_class = TicketAgent(self.model)
        self.clarify_agent_class = ClarifyAgent(self.model) # Capable of passing reference to the main agent
        self.small_talk_agent_class = SmallTalkAgent(self.client, self.model)
        self.plan_explainer_agent_class = PlanExplainerAgent(self.client, self.model, self.index, embedding_model)
        self.feedback_collector_agent_class = FeedbackCollectorAgent(self.model)
        self.analytics_agent_class = AnalyticsAgent(self.model)
        self.research_agent_class = ResearchAgent(self.client, self.model)

        workflow = StateGraph(AgentState)
        workflow.add_node("classifier", self.initial_classifier)
        workflow.add_node("policy", self.policy_agent_class.policy_agent)
        workflow.add_node("commission", self.commission_agent_class.commission_agent)
        workflow.add_node("contest", self.contest_agent_class.contest_agent)
        workflow.add_node("ticket", self.ticket_agent_class.ticket_agent)
        workflow.add_node("clarify", self.clarify_agent_class.clarify_agent)
        workflow.add_node("smalltalk", self.small_talk_agent_class.small_talk_agent)
        workflow.add_node("planexplainer", self.plan_explainer_agent_class.plan_explainer_agent)
        workflow.add_node("feedbackcollector", self.feedback_collector_agent_class.feedback_collector_agent)
        workflow.add_node("analytics", self.analytics_agent_class.analytics_agent)
        workflow.add_node("research", self.research_agent_class.research_agent)

        workflow.add_conditional_edges("classifier", self.main_router)
        workflow.add_edge(START, "classifier")
        workflow.add_edge("policy", END)
        workflow.add_edge("commission", END)
        workflow.add_edge("contest", END)
        workflow.add_edge("ticket", END)
        workflow.add_edge("clarify", END)
        workflow.add_edge("smalltalk", END)
        workflow.add_edge("planexplainer", END)
        workflow.add_edge("feedbackcollector", END)
        workflow.add_edge("analytics", END)
        workflow.add_edge("research", END)

        self.graph = workflow.compile()

    def initial_classifier(self, state: AgentState):
        print("initial classifier")
        CLASSIFIER_PROMPT = get_prompt("classifier")
        llm_messages = create_llm_msg(CLASSIFIER_PROMPT, state['message_history'])
        llm_response = self.model.with_structured_output(Category).invoke(llm_messages)
        category = llm_response.category
        print(f"category is {category}")
        return{
            "lnode": "initial_classifier", 
            "category": category,
        }
    
    def main_router(self, state: AgentState):
        my_category = state['category']
        if my_category in VALID_CATEGORIES:
            return my_category
        else:
            print(f"unknown category: {my_category}")
            return END