import streamlit as st
import ods
from texts import txt
from utils import show_header, show_records

column_configuration = {
    "file_name": st.column_config.TextColumn(
        "Filename", help="parquet file name", max_chars=100, width="medium"
    ),
}

df_files = ods.get_remote_files(ods.data_container_name)
show_header(
    title=txt["title_page4"],
    help_text=txt["info_page4"],
)
show_records('{} Azure blobs', len(df_files))
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
