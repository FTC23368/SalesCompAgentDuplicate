# src/plan_explainer_agent.py

from typing import List
from src.create_llm_message import create_llm_message, create_llm_msg
from langchain_core.messages import BaseMessage
from src.prompt_store import get_prompt

# When PlanExplainerAgent object is created, it's initialized with a client, a model, and an index. 
# The main entry point is the plan_explainer_agent method. You can see workflow.add_node for plan_explainer_agent 
# node in graph.py

class PlanExplainerAgent:
    
    def __init__(self, client, model, index, embedding_model):
        """
        Initialize the PlanExplainerAgent with necessary components.
        
        :param client: OpenAI client for API calls
        :param model: Language model for generating responses
        :param index: Pinecone index for document retrieval
        """
        self.client = client
        self.index = index
        self.model = model
        self.embedding_model = embedding_model

    def retrieve_documents(self, query: str) -> List[str]:
        """
        Retrieve relevant documents based on the given query.
        
        :param query: User's query string
        :return: List of relevant document contents
        """
        # Generate an embedding for the query and retrieve relevant documents from Pinecone.
        embedding = self.client.embeddings.create(model=self.embedding_model, input=query).data[0].embedding
        results = self.index.query(vector=embedding, top_k=3, namespace="", include_metadata=True)
        
        retrieved_content = [r['metadata']['text'] for r in results['matches']]
        return retrieved_content

    def generate_response(self, retrieved_content: List[str], user_query: str, messageHistory: list[BaseMessage]) -> str:
        """
        Generate a response based on retrieved content and user query.
        
        :param retrieved_content: List of relevant document contents
        :param user_query: Original user query
        :return: Generated response string
        """
        # Get plan explainer prompt from prompt_store.py
        plan_explainer_prompt = get_prompt("planexplainer").format(retrieved_content=retrieved_content)

        # Create a well-formatted message for LLM by passing the retrieved information above to create_llm_msg
        llm_messages = create_llm_msg(plan_explainer_prompt, messageHistory)

        # Invoke the model with the well-formatted prompt, including SystemMessage, HumanMessage, and AIMessage
        llm_response = self.model.invoke(llm_messages)

        # Extract the content attribute from the llm_response object 
        plan_explainer_response = llm_response.content

        return plan_explainer_response

    def plan_explainer_agent(self, state: dict) -> dict:
        """
        Main entry point for plan-related queries.
        
        :param state: Current state dictionary containing user's initial message
        :return: Updated state dictionary with generated response and category
        """
        # Handle plan type, construct, mechanics related queries by retrieving relevant documents and generating 
        # a response.
        
        # Retrieve relevant documents based on the user's initial message
        retrieved_content = self.retrieve_documents(state['initialMessage'])
        
        # Generate a response using the retrieved documents and the user's initial message
        full_response = self.generate_response(retrieved_content, state['initialMessage'], state['message_history'])
        
        # Return the updated state with the generated response and the category set to 'policy'
        return {
            "lnode": "plan_explainer_agent", 
            "responseToUser": full_response,
            "category": "planexplainer"
        }
