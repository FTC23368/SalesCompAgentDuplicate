import streamlit as st
from src.google_firestore_integration import list_files, get_file_content, get_text_content

file_list = list_files()
st.dataframe(file_list)
for file in file_list:
    #st.write(f"Now working on {file=}")
    file_name = file["file_name"]
    st.write(f"{file_name=}")
    fc = get_file_content(file_name)
    st.write(f"{len(fc)=}")
    tc = get_text_content(file_name)
    st.write(f"{len(tc)=}")