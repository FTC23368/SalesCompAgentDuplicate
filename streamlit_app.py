# streamlit_app.py
# Copyright 2024 Jahangir Iqbal

import os
import json
import random
import streamlit as st
from src.graph import salesCompAgent
from src.google_firestore_integration import get_prompts
from google.oauth2 import service_account

# Set environment variables for Langchain and SendGrid
os.environ["LANGCHAIN_TRACING_V2"]="true"
os.environ["LANGCHAIN_API_KEY"]=st.secrets['LANGCHAIN_API_KEY']
os.environ["LANGCHAIN_PROJECT"]="SalesCompAgent"
os.environ['LANGCHAIN_ENDPOINT']="https://api.smith.langchain.com"
os.environ['SENDGRID_API_KEY']=st.secrets['SENDGRID_API_KEY']

DEBUGGING=0

def get_google_cloud_credentials():
    # Get Google Cloud credentials from JSON file
    js1 = st.secrets["GOOGLE_KEY"]
    #print(" A-plus Google credentials JS: ", js1)
    credentials_dict=json.loads(js1)
    credentials = service_account.Credentials.from_service_account_info(credentials_dict)   
    st.session_state.credentials = credentials
    return credentials

def initialize_prompts():
    if "credentials" not in st.session_state:
        st.session_state.credentials = get_google_cloud_credentials()
    if prompts not in st.session_state:
        prompts = get_prompts(st.session_state.credentials)
        st.session_state.prompts = prompts

# This function sets up the chat interface and handles user interactions
def start_chat():
    # Setup a simple landing page with title and avatars
    st.title('Sales Comp Agent')
    st.markdown("#### Hey! 👋 I'm ready to assist you with all things sales comp.")
    avatars={"system":"💻🧠", "user":"🧑‍💼", "assistant":"🌀"} 
    
    # Keeping context of conversations, checks if there is anything in messages array
    # If not, it creates an empty list where all messages will be saved
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Ensuring a unique thread-id is maintained for every conversation
    if "thread-id" not in st.session_state:
        st.session_state.thread_id = random.randint(1000, 9999)
    thread_id = st.session_state.thread_id

    # Display previous messages in the chat history by keeping track of the messages array
    # in the session state. 
    for message in st.session_state.messages:
        if message["role"] != "system":
            avatar=avatars[message["role"]]
            with st.chat_message(message["role"], avatar=avatar):
                st.markdown(message["content"]) 

    # Handle new user input. Note: walrus operator serves two functions, it checks if
    # the user entered any input. If yes, it returns that value and assigns to 'prompt'. Note that escaped_prompt was
    # used for formatting purposes.
    if prompt := st.chat_input("Ask me anything related to sales comp.."):
        escaped_prompt = prompt.replace("$", "\\$")
        st.session_state.messages.append({"role": "user", "content": escaped_prompt})
        with st.chat_message("user", avatar=avatars["user"]):
            st.write(escaped_prompt)
        
        # Initialize salesCompAgent in graph.py 
        app = salesCompAgent(st.secrets['OPENAI_API_KEY'])
        thread={"configurable":{"thread_id":thread_id}}
        
        # Stream responses from the instance of salesCompAgent which is called "app"
        for s in app.graph.stream({'initialMessage': prompt, 'sessionState': st.session_state, 
        'sessionHistory': st.session_state.messages}, thread):
    
            if DEBUGGING:
                print(f"GRAPH RUN: {s}")
                st.write(s)
            for k,v in s.items():
                if DEBUGGING:
                    print(f"Key: {k}, Value: {v}")
            if resp := v.get("responseToUser"):
                with st.chat_message("assistant", avatar=avatars["assistant"]):
                    st.write(resp) 
                st.session_state.messages.append({"role": "assistant", "content": resp})

if __name__ == '__main__':
    initialize_prompts()
    start_chat()