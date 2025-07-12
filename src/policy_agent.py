# src/policy_agent.py
import streamlit as st
from typing import List
from src.create_llm_message import create_llm_message, create_llm_msg
from langchain_core.messages import BaseMessage
from src.prompt_store import get_prompt
from src.google_firestore_integration import list_files, get_file_content, get_text_content

# When PolicyAgent object is created, it's initialized with a client, a model, and an index. 
# The main entry point is the policy_agent method. You can see workflow.add_node for policy_agent node in graph.py

@st.cache_data
def get_full_policy_content():
    files = list_files()
    policy_files = [f for f in files if "Policy" in (f.get("doc_category") or [])]
    #st.write(f"{files=}, {policy_files=}")
    #st.dataframe(policy_files)

    total_content = []

    for files in policy_files:
        content_filename = files["file_name"]
        #st.write(f"# {content_filename=}")
        content = get_text_content(content_filename)
        #st.write(content)
        total_content.append(content)
    return "\n".join(total_content)

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
        #self.cached_full_content = self.get_full_policy_content()
    
    
    

    def retrieve_documents(self, query: str) -> List[str]:
        """
        Retrieve relevant documents based on the given query.
        
        :param query: User's query string
        :return: List of relevant document contents
        """
        # Generate an embedding for the query and retrieve relevant documents from Pinecone.
        embedding = self.client.embeddings.create(model="text-embedding-ada-002", input=query).data[0].embedding
        results = self.index.query(vector=embedding, top_k=1, namespace="", include_metadata=True)
        
        retrieved_content = [r['metadata']['text'] for r in results['matches']]
        full_content = get_full_policy_content()
        retrieved_content.append(full_content)
        #retrieved_content.append(self.cached_full_content)
        print(f"{query=},{retrieved_content=}")
        return retrieved_content

    def generate_response(self, retrieved_content: List[str], user_query: str, messageHistory: [BaseMessage]) -> str:
        """
        Generate a response based on retrieved content and user query.
        
        :param retrieved_content: List of relevant document contents
        :param user_query: Original user query
        :return: Generated response string
        """
        # Get policy prompt from prompt_store.py
        policy_prompt = get_prompt("policy").format(retrieved_content=retrieved_content)

        # Create a well-formatted message for LLM by passing the retrieved information above to create_llm_msg
        llm_messages = create_llm_msg(policy_prompt, messageHistory)

        # Invoke the model with the well-formatted prompt, including SystemMessage, HumanMessage, and AIMessage
        #llm_response = self.model.invoke(llm_messages)

        # Extract the content attribute from the llm_response object 
        #policy_response = llm_response.content

        #return policy_response
        return self.model.stream(llm_messages)

    def policy_agent(self, state: dict) -> dict:
        """
        Main entry point for policy-related queries.
        
        :param state: Current state dictionary containing user's initial message
        :return: Updated state dictionary with generated response and category
        """
        # Handle policy-related queries by retrieving relevant documents and generating a response.
        
        # Retrieve relevant documents based on the user's initial message
        print("starting policy agent")
        retrieved_content = self.retrieve_documents(state['initialMessage'])
        
        # Generate a response using the retrieved documents and the user's initial message
        #full_response = self.generate_response(retrieved_content, state['initialMessage'], state['message_history'])
        #print("completed policy agent")
        
        # Return the updated state with the generated response and the category set to 'policy'
        return {
            "lnode": "policy_agent", 
            "incrementalResponse": self.generate_response(retrieved_content, state['initialMessage'], state['message_history']),
            "category": "policy"
        }
