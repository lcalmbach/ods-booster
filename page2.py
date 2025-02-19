import streamlit as st
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
