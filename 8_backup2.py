# cl3vrapp.py
# Copyright 2024 Jahangir Iqbal

import os
import json
import PyPDF2
import random
import streamlit as st
from src.graph import salesCompAgent
from src.google_firestore_integration import get_all_prompts
from google.oauth2 import service_account
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, BaseMessage

# Set environment variables for Langchain and SendGrid
os.environ["LANGCHAIN_TRACING_V2"]="true"
os.environ["LANGCHAIN_API_KEY"]=st.secrets['LANGCHAIN_API_KEY']
os.environ["LANGCHAIN_PROJECT"]="SalesCompAgent"
os.environ['LANGCHAIN_ENDPOINT']="https://api.smith.langchain.com"
os.environ['SENDGRID_API_KEY']=st.secrets['SENDGRID_API_KEY']

DEBUGGING=0

st.set_page_config(
        page_title="Cl3vr - Your AI assistant for Sales Compensation"
    )

import streamlit as st
from src.google_firestore_integration import list_files, get_file_content, get_text_content
import pandas as pd

st.title("Policy Documents")

files = list_files()
policy_files = [f for f in files if "Policy" in (f.get("doc_category") or [])]
#st.write(f"{files=}, {policy_files=}")
st.dataframe(policy_files)

for files in policy_files:
    content_filename = files["file_name"]
    st.write(f"# {content_filename=}")
    content = get_text_content(content_filename)
    st.write(content)

def get_google_cloud_credentials():
    """
    Gets and sets up Google Cloud credentials for authentication.
    This function:
    1. Retrieves the Google service account key from Streamlit secrets
    2. Converts the JSON string to a Python dictionary
    3. Creates a credentials object that can be used to authenticate with Google services
    
    Returns:
        service_account.Credentials: Google Cloud credentials object
    """
    # Get Google Cloud credentials from Streamlit secrets
    js1 = st.secrets["GOOGLE_KEY"]
    #print(" A-plus Google credentials JS: ", js1)
    credentials_dict=json.loads(js1)
    credentials = service_account.Credentials.from_service_account_info(credentials_dict)   
    st.session_state.credentials = credentials
    return credentials

def initialize_prompts():
    """
    Initializes the application by setting up Google credentials and loading prompts.
    This function:
    1. Checks if credentials exist in the session state, if not gets new credentials
    2. Checks if prompts exist in the session state, if not fetches them from Firestore
    3. Stores both credentials and prompts in Streamlit's session state for later use
    """
    if "credentials" not in st.session_state:
        st.session_state.credentials = get_google_cloud_credentials()
    if "prompts" not in st.session_state:
        prompts = get_all_prompts(st.session_state.credentials)
        st.session_state.prompts = prompts

# Add custom CSS to change the font to Inter
def set_custom_font():
    custom_css = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="st-"] {
        font-family: 'Inter', sans-serif !important;
    }
    
    /* Hide Streamlit header and footer */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}

    /* Improved typography */
    h1 {
        font-weight: 700 !important;
        letter-spacing: -0.5px !important;
        margin-bottom: 1rem !important;
    }
    
    h4 {
        font-weight: 600 !important;
        letter-spacing: -0.3px !important;
        margin-top: 0.75rem !important;
        margin-bottom: 0.5rem !important;
    }
    
    p {
        font-weight: 400 !important;
        line-height: 1.6 !important;
        color: #4A4A4A !important;
        margin-bottom: 1.5rem !important;
    }
    
    /* App title styling */
    .app-title {
        color: #87CEEB;
        font-size: 2.8rem;
        font-weight: 700;
        margin-bottom: 1.2rem;
    }
    
    /* Section title styling */
    .section-title {
        font-size: 1.25rem;
        font-weight: 600;
        margin-top: 1.5rem;
        margin-bottom: 0.75rem;
    }
    
    /* Section subtitle styling */
    .section-subtitle {
        font-size: 1rem;
        font-weight: normal;
        margin-bottom: 1.5rem;
        color: #4A4A4A;
    }
    
    /* Custom styling for chat messages */
    .stChatMessage {
        border-radius: 12px !important;
        padding: 12px !important;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05) !important;
        margin-bottom: 14px !important;
    }
    
    /* Add some spacing and styling */
    .stTextInput > div > div > input {
        border-radius: 8px !important;
        border: 1px solid #E0E0E0 !important;
        padding: 10px 14px !important;
        font-size: 15px !important;
    }
    
    /* Style the chat input box */
    .stChatInputContainer {
        padding-top: 18px !important;
        border-top: 1px solid #f0f0f0 !important;
        margin-top: 20px !important;
    }
    
    /* Footer copyright styling */
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        text-align: center;
        padding: 12px 0;
        background-color: white;
        font-size: 13px;
        color: #888;
        border-top: 1px solid #f0f0f0;
        z-index: 999;
    }
    
    /* Add some breathing room */
    .main-container {
        max-width: 900px !important;
        padding: 0 20px !important;
        margin: 0 auto !important;
    }
    
    /* Button styling */
    .stButton button {
        border-radius: 6px !important;
        font-weight: 500 !important;
        transition: all 0.2s ease !important;
    }
    
    /* Sidebar refinements */
    .css-1d391kg, .css-163ttbj {
        background-color: #fafafa !important;
    }
    
    /* Modern scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f1f1;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #c1c1c1;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #a8a8a8;
    }
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)
    st.markdown("<div class='footer'>© 2025 Cl3vr AI. All rights reserved.</div>", unsafe_allow_html=True)
    

def process_file(upload_file):
    #st.sidebar.image(upload_file)
    #return
    #PDF=application/pdf
    #CSV=text/csv
    with st.sidebar.expander("File contents"):
        st.write("file type:", upload_file.type)
    filetype = upload_file.type
    if filetype == 'application/pdf':

        pdfReader = PyPDF2.PdfReader(upload_file)
        count = len(pdfReader.pages)
        text=""
        for i in range(count):
            page = pdfReader.pages[i]
            text=text+page.extract_text()

        with st.sidebar.expander("File contents"):
            st.write("file type:", upload_file.type)
            st.write(text)
        return text, "pdf"

    elif filetype == 'text/csv':
        print("got a cvs file")
        file_contents = upload_file.read()
        return file_contents, "csv"
    else:
        st.sidebar.write('unknown file type', filetype)

def start_chat(container=st):
    """
    Sets up and manages the main chat interface for the Sales Comp Agent application.
    
    This function:
    1. Creates the UI elements (title, welcome message)
    2. Manages chat history using Streamlit's session state
    3. Maintains conversation threading with unique thread IDs
    4. Handles message display for both user and assistant
    5. Processes user input and generates AI responses using salesCompAgent in graph.py
    6. Handles message escaping for special characters
    7. Manages debugging output when DEBUGGING flag is enabled
    
    The function runs in a continuous loop as part of the Streamlit app, waiting for 
    and responding to user input in real-time.
    """
    # Setup a simple landing page with title and avatars
    st.markdown("<h1 class='app-title' style='color: #87CEEB; font-size: 3.5rem;'>Cl3vr</h1>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Your AI assistant for Sales Compensation</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-subtitle'>Get instant answers to your sales compensation questions, design comp plans or SPIFs, analyze performance data, and streamline your workflows—all with with AI-powered assistance.</div>", unsafe_allow_html=True)
    
    
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
            with st.chat_message(message["role"]):
                st.markdown(message["content"]) 
    

    # Handle new user input. Note: walrus operator serves two functions, it checks if the user entered any input.
    # If yes, it returns that value and assigns to 'prompt'. Note that escaped_prompt was used for formatting purposes.
    if prompt := st.chat_input("Ask me anything related to sales comp..", accept_file=True, file_type=["pdf", "md", "doc", "csv"]):
        if prompt and prompt["files"]:
            uploaded_file=prompt["files"][0]
            
            file_contents, filetype = process_file(uploaded_file)
            if filetype != 'csv':
                prompt.text = prompt.text + f"\n Here are the file contents: {file_contents}"
        
        escaped_prompt = prompt.text.replace("$", "\\$")
        st.session_state.messages.append({"role": "user", "content": escaped_prompt})
        
        with st.chat_message("user"):
            st.write(escaped_prompt)
        message_history = []
        
        msgs = st.session_state.messages
    
    # Iterate through chat history, and based on the role (user or assistant) tag it as HumanMessage or AIMessage
        for m in msgs:
            if m["role"] == "user":
                # Add user messages as HumanMessage
                message_history.append(HumanMessage(content=m["content"]))
            elif m["role"] == "assistant":
                # Add assistant messages as AIMessage
                message_history.append(AIMessage(content=m["content"]))
        
        # Initialize salesCompAgent in graph.py 
        app = salesCompAgent(st.secrets['OPENAI_API_KEY'])
        thread={"configurable":{"thread_id":thread_id}}
        parameters = {'initialMessage': prompt.text, 
                      #'sessionState': st.session_state, 
                        #'sessionHistory': st.session_state.messages, 
                        'message_history': message_history}
        if 'csv_data' in st.session_state:
            parameters['csv_data'] = st.session_state['csv_data']
        if prompt['files'] and filetype == 'csv':
            parameters['csv_data'] = file_contents
            st.session_state['csv_data'] = file_contents
        # Stream responses from the instance of salesCompAgent which is called "app"
        with st.spinner("Thinking ...", show_time=True):
        
            for s in app.graph.stream(parameters, thread):
        
                if DEBUGGING:
                    print(f"GRAPH RUN: {s}")
                    st.write(s)
                for k,v in s.items():
                    if DEBUGGING:
                        print(f"Key: {k}, Value: {v}")
                if resp := v.get("responseToUser"):
                    with st.chat_message("assistant"):
                        st.write(resp) 
                    st.session_state.messages.append({"role": "assistant", "content": resp})

if __name__ == '__main__':
    initialize_prompts()
    #set_custom_font()
    #start_chat()