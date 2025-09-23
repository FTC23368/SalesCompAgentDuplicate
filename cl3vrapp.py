import os
import json
import PyPDF2
import random
import streamlit as st
from src.graph import salesCompAgent
from langchain_groq import ChatGroq
from src.google_firestore_integration import get_all_prompts
from google.oauth2 import service_account
from langchain_core.messages import HumanMessage, AIMessage
from src.conv_history import message_history_to_string, string_to_message_history, get_short_conv_title
from src.supabase_integration import get_supabase_client, upsert_conv_history, get_conv_history_for_user

os.environ["LANGCHAIN_TRACING_V2"]="true"
os.environ["LANGCHAIN_API_KEY"]=st.secrets['LANGCHAIN_API_KEY']
os.environ["LANGCHAIN_PROJECT"]="SalesCompAgent"
os.environ['LANGCHAIN_ENDPOINT']="https://api.smith.langchain.com"
os.environ['SENDGRID_API_KEY']=st.secrets['SENDGRID_API_KEY']

DEBUGGING=0
DEFAULT_USER_RECORD = {'id': 100000}

def get_google_cloud_credentials():
    # Get Google Cloud credentials from Streamlit secrets
    js1 = st.secrets["GOOGLE_KEY"]
    credentials_dict=json.loads(js1)
    credentials = service_account.Credentials.from_service_account_info(credentials_dict)   
    st.session_state.credentials = credentials
    return credentials

def initialize_prompts():
    if "credentials" not in st.session_state:
        st.session_state.credentials = get_google_cloud_credentials()
    if "prompts" not in st.session_state:
        prompts = get_all_prompts(st.session_state.credentials)
        st.session_state.prompts = prompts
    
def process_file(upload_file):
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

def save_conv_history_to_db(thread_id):
    msgs = st.session_state.messages
    user_record = st.session_state.get('user_record', DEFAULT_USER_RECORD)
    #st.sidebar.json(user_record)
    new_record = {
        "user_id": user_record["id"],
        "thread_id": thread_id,
        "conv": message_history_to_string(msgs),
    }



    if len(msgs) <= 2:
        client = ChatGroq(model=st.secrets['GROQ_MODEL'], temperature=0, api_key=st.secrets['GROQ_API_KEY'])
        summary = get_short_conv_title(client, msgs)
        new_record["short_title"] = summary
        #st.sidebar.write(f"summary is {summary}")


    supabase = get_supabase_client()
    upsert_conv_history(supabase, new_record)
    #st.sidebar.success("save_to_db")

def restore_conv_history_to_ui(conv_id, conv):
    st.session_state.thread_id = conv_id
    messages = string_to_message_history(conv)
    st.session_state.messages = messages
    st.rerun()
    
def start_chat(container=st):
    #st.title("Cl3vr")
    st.markdown("""
    <div style="display:flex;align-items:center;gap:2px;margin:0 0 0.25rem 0;">
    <h1 style="margin:0;">Cl3vr</h1>
    <span style="background:#f59e0b;color:white;border-radius:999px;padding:2px 8px;font-size:0.8rem;font-weight:700;">BETA</span>
    </div>
    """, unsafe_allow_html=True)
    st.subheader("Your AI assistant for Sales Compensation")
    st.markdown("Get instant answers to your sales compensation questions, design comp plans or SPIFs, analyze performance data, and streamline your workflows—all with AI-powered assistance.")
    #st.markdown("© 2025 Cl3vr AI. All rights reserved.")
    st.markdown("<br>", unsafe_allow_html=True)

    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "thread_id" not in st.session_state:
        st.session_state.thread_id = random.randint(1000, 100000000)
    thread_id = st.session_state.thread_id

    #json_str = message_history_to_string(st.session_state.messages)
    #with st.sidebar.expander("json_str"):
    #    st.write(json_str)

    #with st.sidebar.expander("json_object"):
    #    jo = string_to_message_history(json_str)
    #    for message in jo:
    #        role = message["role"]
    #        content = message["content"]
    #        st.write(f"{role=}, {content=}")
    #st.sidebar.write(f"{thread_id=}")
    user_record = st.session_state.get('user_record')
    supabase = get_supabase_client()
    #with st.sidebar.expander('session_state'):
        #st.json(st.session_state)
    if user_record:
        user_id = user_record.get('id', 0)
        #st.write(f"{user_id=}")
        conv_history = get_conv_history_for_user(supabase, user_id)

        if conv_history:
            for conv in conv_history:
                conv_id = conv.get('thread_id')
                short_title = conv.get('short_title')
                conv_name = short_title or f"{conv.get('thread_id')}"
                if st.sidebar.button(conv_name, type="tertiary", key=conv_name):
                    #st.error("to do")
                    r = conv['conv']
                    restore_conv_history_to_ui(conv_id, r)


    for message in st.session_state.messages:
        if message["role"] != "system":
            with st.chat_message(message["role"]):
                display_text = message["content"].replace("$", "\\$")
                display_text = display_text.replace("\\\\$", "\\$")
                st.markdown(display_text)
                #st.markdown(message["content"].replace("$", "\\$")) 
    
    if prompt := st.chat_input("Ask me anything related to sales comp..", accept_file=True, file_type=["pdf", "md", "doc", "csv"]):
        if prompt and prompt["files"]:
            uploaded_file=prompt["files"][0]
            file_contents, filetype = process_file(uploaded_file)
            if filetype != 'csv':
                prompt.text = prompt.text + f"\n Here are the file contents: {file_contents}"
        
        user_prompt = prompt.text
        st.session_state.messages.append({"role": "user", "content": user_prompt})
        
        with st.chat_message("user"):
            st.write(user_prompt.replace("$", "\\$"))

        message_history = []
        msgs = st.session_state.messages
    
    # Iterate through chat history, and based on the role (user or assistant) tag it as HumanMessage or AIMessage
        for m in msgs:
            if m["role"] == "user":
                message_history.append(HumanMessage(content=m["content"]))
            elif m["role"] == "assistant":
                message_history.append(AIMessage(content=m["content"]))
        
        app = salesCompAgent(st.secrets['OPENAI_API_KEY'], st.secrets['EMBEDDING_MODEL'])
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

        with st.spinner("Thinking ...", show_time=True):
            full_response = ""
            
            for s in app.graph.stream(parameters, thread):
                if DEBUGGING:
                    print(f"GRAPH RUN: {s}")
                for k,v in s.items():
                    if DEBUGGING:
                        print(f"Key: {k}, Value: {v}")
                
                if resp := v.get("responseToUser"):
                    with st.chat_message("assistant"):
                        # Clean up response: remove weird line breaks
                        cleaned_resp = resp.replace('\n', ' ').replace('  ', ' ')
                        st.markdown(cleaned_resp, unsafe_allow_html=True)
                        st.session_state.messages.append({"role": "assistant", "content": cleaned_resp})
                        save_conv_history_to_db(thread_id)
                
                if resp := v.get("incrementalResponse"):
                    with st.chat_message("assistant"):
                        placeholder = st.empty()
                        for response in resp:
                            full_response = full_response + response.content
                            display_text = full_response.replace("$", "\\$")
                            display_text = display_text.replace("\\\$", "\\$")
                            placeholder.markdown(display_text)
                            #placeholder.markdown(full_response.replace("$", "\\$"))
                    st.session_state.messages.append({"role": "assistant", "content": full_response})
                    
                    save_conv_history_to_db(thread_id)

if __name__ == '__main__':
    st.set_page_config(page_title="Cl3vr - Your AI assistant for Sales Compensation")
    initialize_prompts()
    start_chat()