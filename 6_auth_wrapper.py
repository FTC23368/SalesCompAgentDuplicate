import pandas as pd
import streamlit as st
from datetime import datetime
import authlib

from cl3vrapp import initialize_prompts, start_chat

#st.title("Streamlit OAuth Playground")

# Function to convert timestamp to human-readable format
def format_timestamp(timestamp):
    try:
        return datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S UTC')
    except:
        return timestamp  # Return original if conversion fails

def ui_not_logged_in():
    st.title("Sales Comp Agent")
    if st.button("Log in with Google", type="primary", icon=":material/login:"):
        st.login()





#print(f"{st.context.headers=}")
#config_auth_needed=st.secrets.get("AUTH_NEEDED","True").lower()=="true"

#auth_needed=config_auth_needed and not st.user.is_logged_in
#col1, col2 = st.columns([4,1])


#if auth_needed:
#    ui_not_logged_in()
#else:
    # Display user name
    #main_code()
#    initialize_prompts()
#    start_chat()
    #st.sidebar.json(st.user)
#    st.sidebar.write(f"{st.user.get('name')}")
#    if st.sidebar.button("Log out", type="secondary", icon=":material/logout:"):
#        st.logout()
def chat_ui():
    initialize_prompts()
    start_chat()

def logout_user():
    st.logout()

def ui_with_pagenation():
    if st.user and st.user.is_logged_in:
        st.sidebar.write(f"{st.user.get('name')}")
    config_auth_needed=st.secrets.get("AUTH_NEEDED","True").lower()=="true"
    auth_needed=config_auth_needed and not st.user.is_logged_in
    pages = {
        "home": [st.Page(chat_ui, title="chat")],
    }
    if auth_needed:
        pages["login"] = [st.Page(ui_not_logged_in, title="login")]
    else:
        pages["logout"] = [st.Page(logout_user, title="logout")]

    pg = st.navigation(pages, position="top")
    pg.run()

ui_with_pagenation()