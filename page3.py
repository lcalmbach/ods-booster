import streamlit as st

"""
This script uses Streamlit to create a web interface for managing and uploading parquet files to Azure Storage.

Modules:
    - streamlit as st: Streamlit library for creating web applications.
    - pandas as pd: Pandas library for data manipulation and analysis.
    - ods: Custom module for ODS-related operations.

Functions:
    - ods.data_folder.glob: Retrieves a list of parquet files from the data folder.
    - ods.extend_columns: Extends the DataFrame with additional columns based on the identifier.
    - ods.upload_to_azure_storage: Uploads a file to Azure Storage.

Column Configuration:
    - file_path: Text column for displaying the parquet file name.
    - identifier: Text column for displaying the ODS identifier.
    - title: Text column for displaying the title associated with the ODS identifier.
    - modified: Text column for displaying the last update timestamp on ODS.

Streamlit Components:
    - st.subheader: Displays the number of local files found.
    - st.dataframe: Displays the DataFrame with the specified column configuration and allows multi-row selection.
    - st.button: Button to trigger the upload of selected files to Azure Storage.
    - st.spinner: Displays a spinner while uploading files.
    - st.success: Displays a success message after files are uploaded.

Usage:
    - The script lists all parquet files in the specified data folder.
    - It extracts the identifier from the file path and extends the DataFrame with additional columns.
    - The user can select multiple files from the displayed DataFrame.
    - Upon clicking the "Upload Files to Azure Storage" button, the selected files are uploaded to Azure Storage.
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
if st.button("Upload Files to Azure Storage"):
    index = 0
    for item in selected_rows["selection"]["rows"]:
        file_path = files_df.iloc[item]["file_path"]
        with st.spinner(f"Uploading {file_path}..."):
            ods.upload_to_azure_storage(file_path)
        index += 1
    st.success(f"{index} files uploaded to Azure Storage!")
