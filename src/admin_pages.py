import streamlit as st
import re
from io import BytesIO
from pathlib import Path
import base64
from src.supabase_integration import insert_logos, get_logos

from src.supabase_integration import get_supabase_client, add_org, get_orgs, add_account, add_user, get_accounts
from src.upload_docs import upload_docs

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
    option = st.selectbox("org", org_names, key="create_account_org")
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
    option = st.selectbox("org", org_names, key="create_user_org")
    org_id = org_map.get(option, -1)

    accounts = get_accounts(supabase, org_id)
    account_names = [r.get('name') for r in accounts]
    account_map = {r.get('name'): r.get('id') for r in accounts}
    option_account = st.selectbox("account", account_names, key="create_user_account")
    account_id = account_map.get(option_account, -2)

    user_login = None
    login_value = st.text_input("user login")
    if login_value:
        if is_valid_email(login_value):
            user_login = login_value
        else:
            st.error("sorry, login needs to be a valid email address")
            user_login = None
    user_name = st.text_input("Full Name")
    user_role = st.selectbox("role", ['user', 'guest', 'admin', 'superadmin'], key="create_user_role")
    auth_source = st.selectbox("auth_source", ["google"], key="create_user_auth_source")
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


def upload_logos():
    st.title("Upload Logos")
    supabase = get_supabase_client()
    logos = get_logos(supabase, 2)
    logobytes = logos[0].get("bytes")
    #image_bytes = base64.b64decode(bytes)
    image_bytes = bytes.fromhex(logobytes[2:])

    #st.image(BytesIO(image_bytes))
    with open("out.png", "wb") as f:
        f.write(image_bytes)
        st.success("wrote file out.png")
    orgs = get_orgs(supabase)
    org_names = [r.get('name') for r in orgs]
    org_map = {r.get('name'): r.get('id') for r in orgs}
    option = st.selectbox("org", org_names, key="upload_logos_org")
    org_id = org_map.get(option, -1)

    accounts = get_accounts(supabase, org_id)
    account_names = [r.get('name') for r in accounts]
    account_map = {r.get('name'): r.get('id') for r in accounts}
    option_account = st.selectbox("account", account_names, key="upload_logos_account")
    account_id = account_map.get(option_account, -2)

    uploaded_file = st.file_uploader("Upload the Logo", type=["jpg", "jpeg", "png", "gif"])
    if uploaded_file is not None:
        if st.button('Upload File'):
            raw_bytes = uploaded_file.read()
            fname = uploaded_file.name
            # Determine file type and process accordingly
            file_extension = Path(uploaded_file.name).suffix.lower()
            b64_value = base64.b64encode(raw_bytes).decode("ascii")
            new_record = {
                "org_id": org_id,
                "account_id": account_id,
                "filename": fname,
                "mime_type": file_extension,
                "bytes": b64_value,
            }
            
            insert_logos(supabase, new_record)



def show_admin_page():
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Create Org", "Create Account", "Create User", "Upload Docs", "Upload Logo"])
    with tab1:
        create_org()
    with tab2: 
        create_account()
    with tab3:
        create_user()
    with tab4:
        upload_docs()
    with tab5: 
        upload_logos()
        