import streamlit as st
import re

from src.supabase_integration import get_supabase_client, add_org, get_orgs, add_account, add_user, get_accounts

def is_valid_email(email):
    """
    Checks if the given string is a valid email address using a regular expression.
    """
    # A common regex for email validation
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.fullmatch(email_regex, email) is not None

def create_org():
    st.title("Create Org")
    org_name = st.text_input("org name")
    if org_name and st.button("create org"):
        supabase = get_supabase_client()
        new_org = {
            "name": org_name
        }
        response = add_org(supabase, new_org)
        if response:
            st.success(f"Organization '{org_name}' created successfully!")
        else:
            st.error("Failed to create organization")


def create_account():
    st.title("Create Account")
    supabase = get_supabase_client()
    orgs = get_orgs(supabase)
    #st.write(f"{orgs}")
    org_names = [r.get('name') for r in orgs]
    org_map = {r.get('name'): r.get('id') for r in orgs}
    option = st.selectbox("org", org_names)
    #st.write(f"r selected: {option}")
    #st.write(f"{org_map=}")
    org_id = org_map.get(option, -1)
    account_name = st.text_input("account name")
    if account_name and st.button("create account"):
        new_account = {
            "name": account_name,
            "org_id": org_id
        }
        response = add_account(supabase, new_account)
        if response:
            st.success(f"Account '{account_name}' created successfully!")
        else:
            st.error("Failed to create organization")

def create_user():
    st.title("Create User")
    supabase = get_supabase_client()
    orgs = get_orgs(supabase)
    org_names = [r.get('name') for r in orgs]
    org_map = {r.get('name'): r.get('id') for r in orgs}
    option = st.selectbox("org", org_names)
    org_id = org_map.get(option, -1)

    accounts = get_accounts(supabase, org_id)
    account_names = [r.get('name') for r in accounts]
    account_map = {r.get('name'): r.get('id') for r in accounts}
    option_account = st.selectbox("account", account_names)
    account_id = account_map.get(option_account, -2)

    login_value = st.text_input("user login")
    if login_value:
        if is_valid_email(login_value):
            user_login = login_value
        else:
            st.error("sorry, login needs to be a valid email address")
            user_login = None
    user_name = st.text_input("user_name")
    user_role = st.selectbox("role", ['guest', 'admin', 'superadmin'])
    auth_source = st.selectbox("auth_source", ["google"])
    ready_for_user = user_login and user_name and user_role and account_id > 0 and org_id > 0
    if ready_for_user and st.button("create user"):
        new_user = {
            "login": user_login,
            "auth_source": auth_source,
            "full_name": user_name,
            "org_id": org_id,
            "account_id": account_id,
            "org_name": option,
            "account_name": option_account, 
            "role": user_role
        }
        response = add_user(supabase, new_user)
        if response:
            st.success(f"User '{user_login}' created successfully!")
        else:
            st.error("Failed to create user")

