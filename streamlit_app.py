# streamlit_app.py
import os
import random
import streamlit as st
from src.graph import salesCompAgent

# Set environment variables for Langchain and SendGrid
os.environ["LANGCHAIN_TRACING_V2"]="true"
os.environ["LANGCHAIN_API_KEY"]=st.secrets['LANGCHAIN_API_KEY']
os.environ["LANGCHAIN_PROJECT"]="SalesCompAgent"
os.environ['LANGCHAIN_ENDPOINT']="https://api.smith.langchain.com"
os.environ['SENDGRID_API_KEY']=st.secrets['SENDGRID_API_KEY']

DEBUGGING=0

# This function sets up the chat interface and handles user interactions
def start_chat():
    
    # Setup a simple landing page with title and avatars
    st.title('Sales Comp Agent')
    avatars={"system":"💻🧠","user":"🧑‍💼","assistant":"🎓"}
    
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
                st.write(message["content"], unsafe_allow_html=True) # Formatting to take into account '$' in chat history

    # Handle new user input. Note: walrus operator serves two functions, it checks if
    # the user entered any input. If yes, it returns that value and assigns to 'prompt'.
    if prompt := st.chat_input("What is up?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar=avatars["user"]):
            st.markdown(prompt.replace("$", "\\$")) # Formatting to take into account "$" in user input
        
        # Initialize salesCompAgent in graph.py 
        app = salesCompAgent(st.secrets['OPENAI_API_KEY'])
        thread={"configurable":{"thread_id":thread_id}}
        
        # Stream responses from the instance of salesCompAgent which is called "app"
        for s in app.graph.stream({'initialMessage': prompt, 'sessionState': st.session_state}, thread):
    
            if DEBUGGING:
                print(f"GRAPH RUN: {s}")
                st.write(s)
            for k,v in s.items():
                if DEBUGGING:
                    print(f"Key: {k}, Value: {v}")
            if resp := v.get("responseToUser"):
                with st.chat_message("assistant", avatar=avatars["assistant"]):
                    st.write(resp, unsafe_allow_html=True) # Formatting to take into account "$" in LLM response
                st.session_state.messages.append({"role": "assistant", "content": resp})

if __name__ == '__main__':
    start_chat()