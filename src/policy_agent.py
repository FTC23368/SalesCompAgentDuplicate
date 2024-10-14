# src/policy_agent.py

from typing import List
from src.create_llm_message import create_llm_message

# When PolicyAgent object is created, it's initialized with a client, a model, and an index. 
# The main entry point is the policy_agent method. You can see workflow.add_node for policy_agent node in graph.py

class PolicyAgent:
    
    def __init__(self, client, model, index):
        """
        Initialize the PolicyAgent with necessary components.
        
        :param client: OpenAI client for API calls
        :param model: Language model for generating responses
        :param index: Pinecone index for document retrieval
        """
        self.client = client
        self.index = index
        self.model = model

    def retrieve_documents(self, query: str) -> List[str]:
        """
        Retrieve relevant documents based on the given query.
        
        :param query: User's query string
        :return: List of relevant document contents
        """
        # Generate an embedding for the query and retrieve relevant documents from Pinecone.
        embedding = self.client.embeddings.create(model="text-embedding-ada-002", input=query).data[0].embedding
        results = self.index.query(vector=embedding, top_k=3, namespace="", include_metadata=True)
        
        retrieved_content = [r['metadata']['text'] for r in results['matches']]
        return retrieved_content

    def generate_response(self, retrieved_content: List[str], user_query: str) -> str:
        """
        Generate a response based on retrieved content and user query.
        
        :param retrieved_content: List of relevant document contents
        :param user_query: Original user query
        :return: Generated response string
        """
        # Construct the prompt to guide the language model in generating a response
        policy_prompt = f"""
        You are an expert with deep knowledge of sales compensation policy. The user's query seems to be about
        company policy. Always maintain a friendly, professional, and helpful tone. 
        
        Step 1: Retrieve relevant documents from company policy: {retrieved_content}
        
        Step 2: Explain the policy using the retrieved document.

        Step 3: If you are not able to find a relevant company policy, tell them that you were not able
        to find specific company policy on this topic. 
        
        Step 4: Answer the user based on your knowledge of sales compensation terminologies, policies, and 
        practices in a large Enterprise software company. 

        """
        # Create a well-formatted message for LLM by passing the retrieved information above to create_llm_messages
        llm_messages = create_llm_message(policy_prompt)

        # Invoke the model with the well-formatted prompt, including SystemMessage, HumanMessage, and AIMessage
        llm_response = self.model.invoke(llm_messages)

        # Extract the content attribute from the llm_response object 
        policy_response = llm_response.content

        return policy_response

    def policy_agent(self, state: dict) -> dict:
        """
        Main entry point for policy-related queries.
        
        :param state: Current state dictionary containing user's initial message
        :return: Updated state dictionary with generated response and category
        """
        # Handle policy-related queries by retrieving relevant documents and generating a response.
        
        # Retrieve relevant documents based on the user's initial message
        retrieved_content = self.retrieve_documents(state['initialMessage'])
        
        # Generate a response using the retrieved documents and the user's initial message
        full_response = self.generate_response(retrieved_content, state['initialMessage'])
        
        # Return the updated state with the generated response and the category set to 'policy'
        return {
            "lnode": "policy_agent", 
            "responseToUser": full_response,
            "category": "policy"
        }
