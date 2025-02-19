import streamlit as st
"""
This script renders the about this app page.

Modules:
    streamlit: A library for creating web apps.
    texts: A module containing text data.

Functions:
    st.markdown: Renders the given markdown text on the web page.
"""
from texts import txt

st.markdown(txt['info'])
