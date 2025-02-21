import streamlit as st

__version__ = "0.0.2"
__author__ = "Lukas Calmbach"
__author_email__ = "lcalmbach@gmail.com"
VERSION_DATE = "2025-02-25"
APP_NAME = "ODS Booster"
APP_EMOJI = "🚀"
GIT_REPO = "https://github.com/lcalmbach/ods-booster"
SOURCE_URL = "https://data.bs.ch/"

APP_INFO = f"""<div style="background-color:silver; padding: 10px;border-radius: 15px; border:solid 1px white;">
    <small>Author <a href="mailto:{__author_email__}">{__author__}</a><br>
    Version: {__version__} ({VERSION_DATE})<br>
    Data  Source: <a href="{SOURCE_URL}">data.bs</a><br>
    <a href="{GIT_REPO}">Git-repo</a></small></div>
    """


def init():
    st.set_page_config(
        page_title=APP_NAME,
        page_icon=APP_EMOJI,
        layout="wide",
        initial_sidebar_state="expanded",
    )

    st.markdown(
        """
        <style>
            .title-container {
                text-align: center;
                font-size: 24px;
                font-weight: bold;
                margin-bottom: 10px;
            }
        </style>
    """,
        unsafe_allow_html=True,
    )

    # Title above the menu
    title = f"{APP_EMOJI}{APP_NAME}"
    st.sidebar.markdown(
        f'<div class="title-container">{title}</div>', unsafe_allow_html=True
    )


menu = [
    st.Page("page1.py", title="🏠 About this app"),
    st.Page("page2.py", title="📥 Download ODS datasets"),
    st.Page("page3.py", title="📤☁️ Upload parquet files to Azure"),
    st.Page("page4.py", title="📤❄️ Upload parquet files to Snowflake"),
    st.Page("page5.py", title="📥☁️ Load remote data from Azure"),
    st.Page("page6.py", title="🔎❄️ Query Snowflake data"),
    st.Page("page7.py", title="🔎🖥️ Query local data"),
]

init()

pg = st.navigation(menu)
pg.run()
st.sidebar.markdown(APP_INFO, unsafe_allow_html=True)
