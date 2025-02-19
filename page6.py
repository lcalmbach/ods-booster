import streamlit as st
import ods

column_configuration = {
    "table_name": st.column_config.TextColumn(
        "Table", help="Tables names in Snowflake", max_chars=100, width="medium"
    ),
    "dataset_identifier": st.column_config.TextColumn(
        "Key", help="ODS Identifier", max_chars=100, width="medium"
    ),
}

df_files = ods.get_snowflake_tables()

st.markdown(f"**{len(df_files)} data files found in the Azure Storage**")
selected_rows = ods.select_files(
    df_files, multi_row=False, column_configuration=column_configuration
)
if len(selected_rows["selection"]["rows"]) > 0:
    rowid = selected_rows["selection"]["rows"][0]
    identifier = df_files.iloc[rowid]["dataset_identifier"]
    selected_table = df_files.iloc[rowid]["table_name"]
    ds = ods.ods_metadata[ods.ods_metadata["dataset_identifier"] == identifier].iloc[0]
    st.markdown(f"**Selected file:** {ds['title']}")
    with st.expander("Metadata", expanded=False):
        st.write(ds)

    sql_query = st.text_area("SQL Query", f"SELECT * FROM {selected_table} LIMIT 10")
    if st.button("Run SQL Data", disabled=not (selected_rows["selection"]["rows"])):
        df = ods.run_snowflake_query(sql_query)
        st.markdown(f"**Query Result:** {df.shape[0]} records")
        st.dataframe(df)
