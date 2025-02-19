import streamlit as st

"""
This script is a Streamlit application that allows users to view and upload parquet files to Snowflake Storage.

Modules:
    - streamlit as st: Streamlit library for creating web applications.
    - pandas as pd: Pandas library for data manipulation and analysis.
    - ods: Custom module for ODS-related operations.

Column Configuration:
    - file_path: Text column for displaying the parquet file name.
    - identifier: Text column for displaying the ODS identifier.
    - title: Text column for displaying the ODS title.
    - modified: Text column for displaying the last update timestamp on ODS.

Sidebar:
    - Search: Text input for filtering the displayed files.

Main:
    - file_list: List of all parquet files in the data folder.
    - files_df: DataFrame containing file information and extended columns from ODS.
    - selected_rows: DataFrame displaying the files with the specified column configuration.
    - Upload Files to Snowflake: Button to upload selected files to Snowflake Storage.

Functions:
    - ods.extend_columns: Extends the DataFrame with additional columns based on the identifier.
    - ods.upload_to_snowflake_storage: Uploads a file to Snowflake Storage.

Usage:
    - Run the script in a Streamlit environment.
    - Use the sidebar to filter files.
    - Select files from the displayed DataFrame.
    - Click the "Upload Files to Snowflake" button to upload selected files.
"""
import pandas as pd
import ods


column_configuration = {
    "file_path": st.column_config.TextColumn(
        "Filename", help="parquet file name", max_chars=100, width="medium"
    ),
    "identifier": st.column_config.TextColumn(
        "Identifier", help="ODS identifier", max_chars=100, width="medium"
    ),
    "title": st.column_config.TextColumn(
        "Title", help="ODS identifier", max_chars=100, width="medium"
    ),
    "modified": st.column_config.TextColumn(
        "modified on ODS",
        help="Last update timestamp on ODS",
        max_chars=100,
        width="medium",
    ),
}

filter = st.sidebar.text_input("Search", "")
file_list = list(ods.data_folder.glob("*.parquet"))  # Get all files
files_df = pd.DataFrame(file_list, columns=["file_path"])
files_df["file_path"] = files_df["file_path"].astype(str)
files_df["identifier"] = files_df["file_path"].str.extract(r"(\d+)")
files_df = ods.extend_columns(
    files_df, identifier="identifier", columns=["title", "modified"]
)

st.subheader(f"{len(files_df)} local files")
selected_rows = st.dataframe(
    files_df[column_configuration.keys()],
    column_config=column_configuration,
    use_container_width=True,
    hide_index=True,
    on_select="rerun",
    selection_mode="multi-row",
)
# st.write(selected_rows)
if st.button("Upload Files to Snowflake"):
    index = 0
    for item in selected_rows["selection"]["rows"]:
        file_path = files_df.iloc[item]["file_path"]
        with st.spinner(f"Uploading {file_path}..."):
            ods.upload_to_snowflake_storage(file_path)
        index += 1
    st.success(f"{index} files uploaded to Snowflake Storage!")
