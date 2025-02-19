import streamlit as st

"""
This script is a Streamlit application that interacts with Snowflake tables and displays metadata.

Functions:
- ods.get_snowflake_tables(): Retrieves a DataFrame containing information about Snowflake tables.
- ods.select_files(df_files, multi_row=False, column_configuration=column_configuration): Allows the user to select files from the DataFrame.
- ods.run_snowflake_query(sql_query): Executes a SQL query on Snowflake and returns the result as a DataFrame.

Streamlit Components:
- st.markdown: Displays markdown text.
- st.column_config.TextColumn: Configures the columns for displaying table information.
- st.text_area: Provides a text area for SQL query input.
- st.button: Creates a button to run the SQL query.
- st.expander: Creates an expandable section for displaying metadata.
- st.dataframe: Displays a DataFrame in a tabular format.

Variables:
- column_configuration: Dictionary defining the configuration for table columns.
- df_files: DataFrame containing information about Snowflake tables.
- selected_rows: Dictionary containing the selected rows from the DataFrame.
- rowid: Index of the selected row.
- identifier: ODS identifier of the selected table.
- selected_table: Name of the selected table.
- ds: Metadata of the selected dataset.
- sql_query: SQL query input by the user.
- df: DataFrame containing the result of the executed SQL query.
"""
import pandas as pd
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
