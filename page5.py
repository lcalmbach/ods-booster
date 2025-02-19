import streamlit as st

"""
This script uses Streamlit to create a web application for interacting with data files stored in Azure Storage.
It allows users to select a file from a list of remote files, view metadata, and display the data.

Functions:
- ods.get_remote_files(container_name): Retrieves a list of remote files from the specified Azure Storage container.
- ods.select_files(df_files, multi_row, column_configuration): Allows users to select files from the list with specified column configuration.
- ods.load_remote_data(file): Loads data from the specified remote file.

Streamlit Components:
- st.markdown: Displays markdown text.
- st.column_config.TextColumn: Configures the display of text columns in the selection table.
- st.expander: Creates an expandable section to display additional content.
- st.button: Creates a button that can trigger actions when clicked.
- st.write: Displays various types of content, including dataframes.

Variables:
- column_configuration: Configuration for the display of the 'file_name' column in the selection table.
- df_files: DataFrame containing the list of remote files retrieved from Azure Storage.
- selected_rows: Dictionary containing information about the selected rows from the file selection table.
- rowid: Index of the selected row.
- identifier: Identifier extracted from the selected file name.
- ds: Metadata of the selected dataset.
- file: Name of the selected file.
- df: DataFrame containing the data loaded from the selected remote file.
"""
import pandas as pd
import ods

column_configuration = {
    "file_name": st.column_config.TextColumn(
        "Filename", help="parquet file name", max_chars=100, width="medium"
    ),
}

df_files = ods.get_remote_files(ods.data_container_name)
st.markdown(f"**{len(df_files)} data files found in the Azure Storage**")
selected_rows = ods.select_files(
    df_files, multi_row=False, column_configuration=column_configuration
)
if selected_rows["selection"]["rows"]:
    rowid = selected_rows["selection"]["rows"][0]
    identifier = df_files.iloc[rowid]["file_name"].split(".")[0]
    ds = ods.ods_metadata[ods.ods_metadata["dataset_identifier"] == identifier].iloc[0]
    st.markdown(f"**Selected file:** {ds['title']}")
    with st.expander("Metadata", expanded=False):
        st.write(ds)
    if st.button("Show Data", disabled=not (selected_rows["selection"]["rows"])):
        file = df_files.iloc[rowid][0]
        df = ods.load_remote_data(file)
        st.write(df)
