import streamlit as st
from src.supabase_integration import get_supabase_client, get_all_users_from_db, get_user_from_db

supabase = get_supabase_client()
users = get_all_users_from_db(supabase)

st.dataframe(users)
user_record = get_user_from_db(supabase, "malihajburney@gmail.com")
st.dataframe(user_record)