import streamlit as st
import ods
from texts import txt
import time

from utils import show_header, show_records

MAX_DOWNLOAD_SIZE = 1000000

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
filter = st.sidebar.text_input("Search", "")
merged_datasets_df = ods.get_merged_datasets()
if filter:
    merged_datasets_df = merged_datasets_df[
        merged_datasets_df["title"].str.contains(filter, case=False)
    ]
show_header(
    title=txt["title_page2"],
    help_text=txt["info_page2"],
)
show_records('{} ODS records', len(merged_datasets_df))
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
        number_successful = 0
        for row in selected_row["selection"]["rows"]:
            ds = ods.ods_metadata.iloc[row].to_dict()
            ds["modified_local"] = merged_datasets_df.iloc[row]["modified_ods"]
            ds["number_of_records_local"] = int(
                merged_datasets_df.iloc[row]["number_of_records_ods"]
            )
            with st.spinner("Downloading data...", show_time=True):
                size = ds["size_of_records_in_the_dataset_in_bytes"]
                if size < MAX_DOWNLOAD_SIZE:
                    data = ods.get_ods_table(ds["dataset_identifier"])
                    filename = ods.data_folder / f"{ds['dataset_identifier']}.parquet"
                    data.to_parquet(filename)
                    log.setdefault(ds["dataset_identifier"], ds)
                    ods.save_config(log)
                    ods.local_metadata = ods.load_config()
                    number_successful += 1
                else:
                    st.warning(
                        f"File size is {size} bytes. Downloading files larger than {MAX_DOWNLOAD_SIZE} bytes is not supported in this version. if you wish to synchronize larger ODS files, install the app on a system with suffienct RAM and diskspace."
                    )
        if number_successful > 0:
            st.success(f"{number_successful} tables downloaded successfully and stored as parquet files!")
            time.sleep(5)
        st.rerun()
