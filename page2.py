import streamlit as st

"""
This script is a Streamlit application for managing and downloading datasets from ODS (Open Data Service).
It provides a user interface for selecting datasets, viewing metadata, and downloading selected datasets.

Modules:
    - streamlit as st: Streamlit library for creating web applications.
    - pandas as pd: Pandas library for data manipulation and analysis.
    - ods: Custom module for interacting with ODS.
    - texts: Custom module containing text strings for the application.
    - time: Standard library for time-related functions.

Functions:
    - ods.get_merged_datasets(): Retrieves a DataFrame of merged datasets from ODS.
    - ods.select_files(): Allows users to select files from the merged datasets DataFrame.
    - ods.load_config(): Loads the configuration/log file.
    - ods.save_config(): Saves the configuration/log file.
    - ods.get_ods_table(): Retrieves a table from ODS based on the dataset identifier.

Configuration:
    - column_configuration: Dictionary defining the configuration for displaying dataset columns in the UI.

UI Elements:
    - st.title: Displays the main title of the application.
    - st.expander: Creates expandable sections for additional information.
    - st.markdown: Displays markdown text.
    - st.button: Creates a button for user interaction.
    - st.spinner: Displays a spinner while performing an action.
    - st.success: Displays a success message.
    - st.rerun: Reruns the Streamlit script.

Workflow:
    1. Retrieve merged datasets from ODS.
    2. Display the title and information section.
    3. Allow users to select datasets from the merged datasets DataFrame.
    4. Display metadata for the selected dataset if only one dataset is selected.
    5. Download selected datasets when the download button is clicked.
    6. Update the local metadata and configuration/log file.
    7. Display a success message and rerun the script.
"""
import pandas as pd
import ods
from texts import txt
import time

column_configuration = {
    "dataset_identifier": st.column_config.TextColumn(
        "Identifier", help="Unique identifier for dataset", max_chars=100, width="small"
    ),
    "title": st.column_config.TextColumn(
        "Title",
        help="The user's activity over the last 1 year",
        width="large",
    ),
    "modified_ods": st.column_config.DatetimeColumn(
        "Modified",
        help="Date of last modification of the dataset on ODS",
        width="medium",
    ),
    "modified_local": st.column_config.DatetimeColumn(
        "Uploaded",
        help="Date of last modification of the dataset on remote repository",
        width="medium",
    ),
    "size_of_records_in_the_dataset_in_bytes": st.column_config.NumberColumn(
        "Size Bytes",
        help="Date of last modification of the dataset on remote repository",
        width="medium",
    ),
    "number_of_records_ods": st.column_config.NumberColumn(
        "Records(ODS)",
        help="Number of records in the remote ODS table.",
        width="medium",
    ),
    "number_of_records_local": st.column_config.NumberColumn(
        "Records (Local)",
        help="Number of records in the local table.",
        width="medium",
    ),
}

merged_datasets_df = ods.get_merged_datasets()

st.title(txt["title_download_ods"])
with st.expander("Info", expanded=False):
    st.markdown(txt["info_download_ods"])
selected_row = ods.select_files(
    merged_datasets_df, column_configuration=column_configuration, multi_row=True
)
log = ods.load_config()
if len(selected_row["selection"]["rows"]) == 1:
    row = ods.ods_metadata.iloc[selected_row["selection"]["rows"][0]]
    with st.expander("Show Metadata"):
        st.write(row.to_dict())

if selected_row["selection"]["rows"]:
    if st.button(f"Download {len(selected_row['selection']['rows'])} files"):
        for row in selected_row["selection"]["rows"]:
            ds = ods.ods_metadata.iloc[row].to_dict()
            ds["modified_local"] = merged_datasets_df.iloc[row]["modified_ods"]
            ds["number_of_records_local"] = int(
                merged_datasets_df.iloc[row]["number_of_records_ods"]
            )
            with st.spinner("Downloading data...", show_time=True):
                data = ods.get_ods_table(ds["dataset_identifier"])
                filename = ods.data_folder / f"{ds['dataset_identifier']}.parquet"
                data.to_parquet(filename)
                log.setdefault(ds["dataset_identifier"], ds)
                ods.save_config(log)
                ods.local_metadata = ods.load_config()
        st.success("Data downloaded successfully!")
        time.sleep(5)
        st.rerun()
