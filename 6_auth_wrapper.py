import authlib
import pandas as pd
import streamlit as st
from datetime import datetime
from cl3vrapp import initialize_prompts, start_chat
from src.admin_pages import show_admin_page
from src.supabase_integration import get_supabase_client, get_user_from_db, get_conv_from_db, fetch_logos_for_account 
from src.supabase_integration import download_logo_file, add_user

def format_timestamp(timestamp):
    try:
        return datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S UTC')
    except:
        return timestamp 

def create_cl3vr_direct_customer(user_login, user_name, auth_source="google", user_role="guest", 
    org_id=1001, account_id=4, org_name='clv3r org', account_name='cl3vr direct customer'):
    new_user = {
            "login": user_login,
            "auth_source": auth_source,
            "full_name": user_name,
            "org_id": org_id,
            "account_id": account_id,
            "org_name": org_name,
            "account_name": account_name, 
            "role": user_role
        }
    supabase = get_supabase_client()
    response = add_user(supabase, new_user)

    if response:
        return new_user
    else:
        return None

def add_user_info_to_session_state():
    email_address = st.user.get("email")
    if email_address:
        supabase = get_supabase_client()
        user_record = get_user_from_db(supabase, email_address)
        if user_record:
            st.session_state.user_record = user_record
        else:
            response = create_cl3vr_direct_customer(email_address, st.user.get('name', 'unknown name'))
            if response:
                user_record = get_user_from_db(supabase, email_address)
                if user_record:
                    st.session_state.user_record = user_record
            #st.warning(f"Sorry, record not found for {email_address}. Please contact support")
    else:
        st.warning(f"Please contact Cl3VR support at: hello@cl3vr.ai")


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

def show_logo(supabase, user_record):
    if user_record:
        org_id = user_record.get("org_id")
        account_id = user_record.get("account_id")
        if org_id is None:
            st.error("Org ID not found.")
            return 
        if account_id is None:
            st.error("Account ID not found.")
            return
        
        logo_files = fetch_logos_for_account(supabase, org_id, account_id)
        
        if logo_files is None or len(logo_files) == 0:
            #st.warning("User doesn't have a logo")
            return
        
        logo_path = logo_files[0].get('storage_path')
        
        if logo_path is None:
            st.error(f"Missing storage path in {logo_files}")
            return

        logo_buffer = download_logo_file(supabase, logo_path)
        if logo_buffer is None:
            st.error(f"Missing logo buffer in {logo_path}")
            return

        col1, col2, col3 = st.sidebar.columns([1, 2, 1])
        with col2:
            st.image(logo_buffer, width=100)




def ui_with_pagenation():
    if st.user and st.user.is_logged_in:
        supabase = get_supabase_client()
        user_record = st.session_state.get("user_record")
        if not user_record:
            add_user_info_to_session_state()
            user_record = st.session_state.get("user_record")

        show_logo(supabase, user_record)
        
        #with st.sidebar.expander("account information"):
        #    st.write(st.session_state)
        st.sidebar.write(f"{st.user.get('name')}")
        

        user_role = None
        
        if user_record:
            account_name = user_record.get("account_name")
            #st.sidebar.write(f"{account_name}")
            user_id = user_record.get("id")
            #st.sidebar.write(f"{user_id=}")
            user_role = user_record.get("role", "guest")
            #st.sidebar.write(f"{user_role=}")
            
            conv_history = get_conv_from_db(supabase, user_id)
            show_conv_history(conv_history)

    config_auth_needed=st.secrets.get("AUTH_NEEDED","True").lower()=="true"
    auth_needed=config_auth_needed and not st.user.is_logged_in
    pages = [st.Page(chat_ui, title="Home")]
    
    if auth_needed:
        pages.append(st.Page(ui_not_logged_in, title="Login"))
    else:
        if user_role and user_role == 'superadmin':
            pages.append(st.Page(show_admin_page, title="Super Admin"))

        
        #print(f"{st.user.to_dict()}")
        pages.append(st.Page(logout_user, title="Logout"))
    
    pg = st.navigation(pages, position="top")
    pg.run()

ui_with_pagenation()