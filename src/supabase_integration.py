import streamlit as st
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

def get_conv_from_db(_supabase, account_id):
    """Fetches user details from the 'users' table based on email."""
    supabase=_supabase
    if not supabase:
        return None
    try:
        response = supabase.table('conv_history').select('*').eq('account_id', account_id).execute()
        if response.data:
            return response.data
        return None
    except Exception as e:
        st.error(f"Error fetching conversation history from database: {e}")
        print(f"Error fetching conversation history from database: {e}")
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

if __name__ == '__main__':
    supabase = get_supabase_client()
    users = get_all_users_from_db(supabase)
    st.dataframe(users)