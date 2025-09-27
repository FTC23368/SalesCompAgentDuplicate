import authlib
import pandas as pd
import streamlit as st
from datetime import datetime
from cl3vrapp import initialize_prompts, start_chat
from src.admin_pages import create_user, create_account, create_org
from src.supabase_integration import get_supabase_client, get_user_from_db, get_conv_from_db

def format_timestamp(timestamp):
    try:
        return datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S UTC')
    except:
        return timestamp 

def add_user_info_to_session_state():
    email_address = st.user.get("email")
    if email_address:
        supabase = get_supabase_client()
        user_record = get_user_from_db(supabase, email_address)
        if user_record:
            st.session_state.user_record = user_record
        else:
            st.warning(f"Sorry, record not found for {email_address}. Please contact support")
    else:
        st.warning(f"Sorry, record not found for {email_address}. Please contact support")


def ui_not_logged_in():
    st.login()
    
def show_conv_history(conv_history):
    #st.sidebar.write(f"{conv_history=}")
    pass

def chat_ui():
    initialize_prompts()
    start_chat()

def logout_user():
    st.logout()



def ui_with_pagenation():
    if st.user and st.user.is_logged_in:
        #with st.sidebar.expander("account information"):
        #    st.write(st.session_state)
        st.sidebar.write(f"{st.user.get('name')}")
        user_record = st.session_state.get("user_record")

        if not user_record:
            add_user_info_to_session_state()
            user_record = st.session_state.get("user_record")
        
        if user_record:
            account_name = user_record.get("account_name")
            #st.sidebar.write(f"{account_name}")
            user_id = user_record.get("id")
            #st.sidebar.write(f"{user_id=}")
            user_role = user_record.get("role", "guest")
            st.sidebar.write(f"{user_role=}")
            supabase = get_supabase_client()
            conv_history = get_conv_from_db(supabase, user_id)
            show_conv_history(conv_history)

    config_auth_needed=st.secrets.get("AUTH_NEEDED","True").lower()=="true"
    auth_needed=config_auth_needed and not st.user.is_logged_in
    pages = [st.Page(chat_ui, title="Home")]
    
    if auth_needed:
        pages.append(st.Page(ui_not_logged_in, title="Login"))
    else:
        if user_role and user_role == 'superadmin':
            pages.append(st.Page(create_org, title="Create Org"))
            pages.append(st.Page(create_account, title="Create Account"))
            pages.append(st.Page(create_user, title="Create User"))

        
        #print(f"{st.user.to_dict()}")
        pages.append(st.Page(logout_user, title="Logout"))
    
    pg = st.navigation(pages, position="top")
    pg.run()

ui_with_pagenation()