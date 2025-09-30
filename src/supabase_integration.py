import io
import streamlit as st
from typing import Optional, List
from supabase import create_client, Client


def get_supabase_client():
    """Creates and returns a Supabase client."""
    SUPABASE_URL = st.secrets.get("SUPABASE_URL")
    SUPABASE_KEY = st.secrets.get("SUPABASE_KEY")
    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        return supabase
    except Exception as e:
        st.error(f"Error connecting to Supabase: {e}")
        print(f"Error connecting to Supabase: {e}")
        return None

def get_user_from_db(_supabase, login):
    """Fetches user details from the 'users' table based on email."""
    supabase=_supabase
    if not supabase:
        return None
    try:
        response = supabase.table('users').select('*').eq('login', login).execute()
        if response.data:
            return response.data[0]
        return None
    except Exception as e:
        st.error(f"Error fetching user from database: {e}")
        print(f"Error fetching user from database: {e}")
        return None

def get_conv_from_db(_supabase, user_id):
    """Fetches user details from the 'users' table based on email."""
    supabase=_supabase
    if not supabase:
        return None
    try:
        response = supabase.table('conv_history').select('*').eq('user_id', user_id).execute()
        if response.data:
            return response.data
        return None
    except Exception as e:
        st.error(f"Error fetching conversation history from database: {e}")
        print(f"Error fetching conversation history from database: {e}")
        return None

def upsert_conv_history(_supabase, new_record):
    supabase=_supabase
    thread_id = new_record["thread_id"]
    user_id = new_record["user_id"]
    new_conv = new_record["conv"]
    try:
        response = supabase.table('conv_history').select('*').eq('user_id', user_id).eq('thread_id', thread_id).execute()
        if len(response.data) > 0:
            #st.sidebar.json(response.data)
            #st.sidebar.write(f"update {new_record=}")
            row_id = response.data[0].get("id")
            supabase.table("conv_history").update({'conv': new_conv}).eq("id", row_id).execute()
        else:
            #st.sidebar.write(f"insert {new_record=}")
            supabase.table("conv_history").insert(new_record).execute()

    except Exception as e:
        st.error(f"Error upserting conversation history from database: {e}")
        print(f"Error upserting conversation history from database: {e}")
        return None

def add_org(_supabase, new_record):
    supabase = _supabase
    try:
        response = supabase.table('orgs').insert(new_record).execute()
        if response.data:
            return response.data
        else:
            st.warning("Insert succeeded but no data returned")
            return None
    
    except Exception as e:
        st.error(f"Error inserting org into database: {e}")
        print(f"Error inserting org into database: {e}")
        return None

def add_account(_supabase, new_record):
    supabase = _supabase
    try:
        response = supabase.table('accounts').insert(new_record).execute()
        if response.data:
            return response.data
        else:
            st.warning("Insert succeeded but no data returned")
            return None
    
    except Exception as e:
        st.error(f"Error adding account into database: {e}")
        print(f"Error adding account into database: {e}")
        return None

def add_user(_supabase, new_record):
    supabase = _supabase
    try:
        response = supabase.table('users').insert(new_record).execute()
        if response.data:
            return response.data
        else:
            st.warning("Insert succeeded but no data returned")
            return None
    
    except Exception as e:
        st.error(f"Error adding user into database: {e}")
        print(f"Error adding user into database: {e}")
        return None

def get_orgs(_supabase):
    supabase = _supabase
    try:
        response = supabase.table("orgs").select("*").execute()
        if response:
            return response.data
        else:
            return None

    except Exception as e:
        st.error(f"Error getting orgs from database: {e}")
        print(f"Error getting orgs from database: {e}")
        return None

def get_accounts(_supabase, org_id):
    supabase = _supabase
    try:
        response = supabase.table("accounts").select("*").eq('org_id', org_id).execute()
        if response:
            return response.data
        else:
            return None

    except Exception as e:
        st.error(f"Error getting accounts from database: {e}")
        print(f"Error getting accounts from database: {e}")
        return None


def get_conv_history_for_user(_supabase, user_id):
    supabase = _supabase
    try:
        response = supabase.table("conv_history").select('*').eq('user_id', user_id).order("created_at", desc=True).execute()
        if response:
            return response.data
        else:
            return None

    except Exception as e:
        st.error(f"Error getting conversation history from database: {e}")
        print(f"Error getting conversation history from database: {e}")
        return None

def get_all_users_from_db(_supabase):
    """Fetches user details from the 'users' table based on email."""
    supabase=_supabase
    if not supabase:
        return None
    try:
        response = supabase.table('users').select('*').execute()
        if response.data:
            return response.data
        return None
    except Exception as e:
        st.error(f"Error fetching user from database: {e}")
        print(f"Error fetching user from database: {e}")
        return None

def insert_docs(_supabase, new_record):
    supabase=_supabase

    try:
        supabase.table("docs").insert(new_record).execute()

    except Exception as e:
        st.error(f"Error upserting docs into database: {e}")
        print(f"Error upserting docs into database: {e}")
        return None
        

def get_docs(_supabase, account_id, doc_category):
    supabase=_supabase

    try:
        response = supabase.table("docs").select('*').eq("account_id", account_id).eq("doc_category", doc_category).execute()
        if response.data:
            return response.data
        return None


    except Exception as e:
        st.error(f"Error getting docs from database: {e}")
        print(f"Error getting docs from database: {e}")
        return None


def insert_logos(_supabase, new_record):
    supabase=_supabase

    try:
        supabase.table("logos").insert(new_record).execute()

    except Exception as e:
        st.error(f"Error upserting logos into database: {e}")
        print(f"Error upserting logos into database: {e}")
        return None
        

def get_logos(_supabase, account_id):
    supabase=_supabase

    try:
        response = supabase.table("logos").select('*').eq("account_id", account_id).execute()
        if response.data:
            return response.data
        return None


    except Exception as e:
        st.error(f"Error getting logos from database: {e}")
        print(f"Error getting logos from database: {e}")
        return None


def upload_logo_file(supabase: Client, uploaded_file, account_id: str) -> Optional[str]:
    file_name = uploaded_file.name
    storage_path = f"{account_id}/{file_name}"
    file_bytes = uploaded_file.getvalue()
    try:
        supabase.storage.from_("logos").upload(path=storage_path,file=file_bytes)
        return storage_path
    except Exception as exc:
        st.error(f"Upload failed: {exc}")
        return None

def download_logo_file(supabase: Client, storage_path: str) -> Optional[io.BytesIO]:
    try:
        data = supabase.storage.from_("logos").download(storage_path)
        return io.BytesIO(data)
    except Exception as exc:
        st.error(f"Download failed: {exc}")
        return None

def record_logo_entry(supabase: Client, org_id: str, account_id: str, filename: str, storage_path: str) -> bool:
    payload = {
        "org_id": org_id,
        "account_id": account_id,
        "filename": filename,
        "storage_path": storage_path,
    }
    try:
        response = supabase.table("logos").insert(payload).execute()
    except Exception as exc:
        st.error(f"Storing logo metadata failed: {exc}")
        return False

    error = getattr(response, "error", None)
    if error:
        message = getattr(error, "message", str(error))
        st.error(f"Storing logo metadata failed: {message}")
        return False

    return True

def fetch_logos_for_account(supabase: Client, org_id: str, account_id: str):
    try:
        response = (
            supabase.table("logos")
            .select("account_id, filename, storage_path, created_at")
            .eq("org_id", org_id)
            .eq("account_id", account_id)
            .order("created_at", desc=True)
            .execute()
        )
        return getattr(response, "data", None) or []
    except Exception as exc:
        st.error(f"Could not load logos: {exc}")
        return []


if __name__ == '__main__':
    supabase = get_supabase_client()
    users = get_all_users_from_db(supabase)
    st.dataframe(users)