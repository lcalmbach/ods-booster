import streamlit as st

def show_header(title: str, help_text):
    st.subheader(title)
    with st.expander("Info", expanded=False):
        st.markdown(help_text)

def show_records(text: str, records: int):
    st.markdown(text.format(records))