import authlib
import pandas as pd
import streamlit as st
from datetime import datetime
from cl3vrapp import initialize_prompts, start_chat

def format_timestamp(timestamp):
    try:
        return datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S UTC')
    except:
        return timestamp 

def ui_not_logged_in():
    st.login()

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
    pages = [st.Page(chat_ui, title="Home")]
    
    if auth_needed:
        pages.append(st.Page(ui_not_logged_in, title="Login"))
    else:
        pages.append(st.Page(logout_user, title="Logout"))
    
    pg = st.navigation(pages, position="top")
    pg.run()

ui_with_pagenation()