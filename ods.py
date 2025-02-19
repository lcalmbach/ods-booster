import streamlit as st
import pandas as pd
from pathlib import Path
from azure.storage.blob import BlobServiceClient
import json
import re
import snowflake.connector

# Azure Storage Account details
azure_storage_account_name = st.secrets["azure"]["azure_storage_account_name"]
azure_storage_account_key = st.secrets["azure"]["azure_storage_account_key"]
data_container_name = "data"
data_folder = Path(data_container_name)
snow_flake_database = "ogd"

metadata = "100057" # ODS metadata dataset for data.bs.ch
config_file = "log.json"
url_ods_data = "https://data.bs.ch/api/explore/v2.1/catalog/datasets/{}/exports/csv?lang=de&timezone=Europe%2FBerlin&use_labels=false&delimiter=%3B"

blob_service_client = BlobServiceClient.from_connection_string(
    f"DefaultEndpointsProtocol=https;AccountName={azure_storage_account_name};AccountKey={azure_storage_account_key}"
)
containers = blob_service_client.list_containers()


# @st.cache_resource
def get_connection():
    """
    Establishes a connection to a Snowflake database using credentials and connection details
    stored in Streamlit secrets.

    Returns:
        snowflake.connector.SnowflakeConnection: A connection object to interact with the Snowflake database.
    """
    return snowflake.connector.connect(
        user=st.secrets["snowflake"]["user"],
        password=st.secrets["snowflake"]["password"],
        account=st.secrets["snowflake"]["account"],  # e.g., xyz123.region.cloud
        warehouse=st.secrets["snowflake"]["warehouse"],
        database=st.secrets["snowflake"]["database"],
        schema=st.secrets["snowflake"]["schema"],
    )


def get_cursor():
    """
    Establishes a connection to the database and returns a cursor object.

    Returns:
        cursor: A cursor object to interact with the database.

    Raises:
        Exception: If there is an error connecting to the database, an error message is displayed.
    """
    try:
        conn = get_connection()
        cur = conn.cursor()
        return cur
    except Exception as e:
        st.error(f"Error connecting to Snowflake: {e}")


@st.cache_data(show_spinner=False, ttl=3600)
def get_ods_table(ds_id: str) -> pd.DataFrame:
    """
    Fetches and returns a DataFrame from a CSV file located at a URL, referenced by the given dataset identifier.

    Args:
        ds_id (str): The dataset identifier to of the dataset to be downloaded

    Returns:
        pd.DataFrame: A DataFrame containing the data from the CSV file. If the column 'dataset_identifier' exists, 
                      it is converted to a string type.
    """
    df = pd.read_csv(url_ods_data.format(ds_id), sep=";")
    if "dataset_identifier" in df.columns:
        df["dataset_identifier"] = df["dataset_identifier"].astype(str)
    return df


def run_snowflake_query(query: str) -> pd.DataFrame:
    """
    Executes a given SQL query on a Snowflake database and returns the result as a pandas DataFrame.

    Args:
        query (str): The SQL query to be executed.

    Returns:
        pd.DataFrame: A DataFrame containing the query results, with column names derived from the query.
    """
    try:
        cur = get_cursor()
        cur.execute(query)
        rows = cur.fetchall()
        # Get column names
        column_names = [desc[0] for desc in cur.description]
        return pd.DataFrame(rows, columns=column_names)
    except Exception as e:
        st.error(f"Error executing query: {e}")
        return pd.DataFrame()


def save_config(log):
    with open(config_file, "w") as file:
        json.dump(log, file)


def load_config():
    with open(config_file, "r") as file:
        log = json.load(file)
    return log


def get_snowflake_tables() -> pd.DataFrame:
    cur = get_cursor()

    # Step 1: Fetch List of Tables
    cur.execute("SHOW TABLES;")
    tables = cur.fetchall()
    tables = [table[1] for table in tables]
    df = pd.DataFrame(tables, columns=["table_name"])
    df["dataset_identifier"] = df["table_name"].str.extract(r"(\d+)$")
    return df


def upload_to_snowflake_storage(file_path: str):
    def check_if_table_exists():
        # Check if table exists
        file_format = "my_parquet_format"
        cur.execute(
            f"""
            SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_NAME = '{table_name.upper()}' AND TABLE_SCHEMA = CURRENT_SCHEMA();
        """
        )

        table_exists = cur.fetchone()[0] > 0
        # If the table doesn't exist, create it using the Parquet schema
        if not table_exists:
            cur.execute(
                f"""
                SELECT COLUMN_NAME, TYPE 
                FROM TABLE(
                    INFER_SCHEMA(
                        LOCATION=>'@{stage_name}',
                        FILE_FORMAT=>'{file_format}'
                    )
                );
            """
            )
            columns = cur.fetchall()
            if not columns:
                raise Exception(
                    "No columns found. Ensure the files exist in the stage and are readable."
                )

            # Step 2: Generate CREATE TABLE statement dynamically
            columns_sql = ", ".join([f'"{col[0]}" {col[1]}' for col in columns])
            create_table_sql = (
                f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_sql})"
            )

            # Execute the table creation query
            try:
                cur.execute(create_table_sql)
                return True
            except Exception as e:
                st.error(f"Error creating table: {e}")
                return False
        return True

    def get_snowflake_table_name():
        match = re.search(r"(\d+)", file_path)
        number_part = match.group(1) if match else None
        return f"DS_{number_part}"

    stage_name = "OGD_STAGE"  # Internal Snl file and Snowflake destinationowflake stage
    table_name = get_snowflake_table_name()
    cur = get_cursor()

    try:
        # Step 1: Upload file to Snowflake stage
        cur.execute(f"REMOVE @{stage_name};")
        cur.execute(f"PUT file://{file_path} @{stage_name} AUTO_COMPRESS=TRUE")
        ok = check_if_table_exists()
        cur.execute(
            f"""
            COPY INTO {table_name}
            FROM @{stage_name}
            FILE_FORMAT = (TYPE = PARQUET)
            MATCH_BY_COLUMN_NAME = CASE_INSENSITIVE;
        """
        )

    finally:
        cur.close()


def upload_to_azure_storage(file_path: str):
    file_path = Path(file_path)
    blob_client = blob_service_client.get_blob_client(
        container=data_container_name, blob=file_path.name
    )
    with open(file_path, "rb") as data:
        blob_client.upload_blob(data, overwrite=True)


def get_local_files() -> pd.DataFrame:
    """
    Get all local parquet files in the data folder
    """
    file_list = list(data_folder.glob("*.parquet"))  # Get all files
    df_files = pd.DataFrame(file_list, columns=["file_name"])
    return df_files


def get_remote_files(container: str) -> pd.DataFrame:
    """
    Get all remote parquet files in the data folder
    """
    file_list = []
    for blob in blob_service_client.get_container_client(container).list_blobs():
        file_list.append(blob.name)
    df_files = pd.DataFrame(file_list, columns=["file_name"])
    return df_files


def select_files(
    df_files: pd.DataFrame, column_configuration: dict, multi_row: bool = False
) -> pd.DataFrame:
    """
    Display a DataFrame in a Streamlit app and allow the user to select rows.

    Parameters:
    df_files (pd.DataFrame): The DataFrame to display and select rows from.
    multi_row (bool): If True, allows multiple rows to be selected. Defaults to False.

    Returns:
    pd.DataFrame: The DataFrame containing the selected rows.
    """
    selected_rows = st.dataframe(
        df_files[column_configuration.keys()],
        column_config=column_configuration,
        use_container_width=True,
        hide_index=True,
        on_select="rerun",
        selection_mode="multi-row" if multi_row else "single-row",
    )
    return selected_rows


def load_remote_data(file: str) -> pd.DataFrame:
    """
    Load parquet file from Azure Storage
    """
    blob_client = blob_service_client.get_blob_client(
        container=data_container_name, blob=file
    )
    with st.spinner(f"Downloading {file}..."):
        with open(file, "wb") as data:
            blob_client.download_blob().readinto(data)
    df = pd.read_parquet(file)
    return df


def extend_columns(
    files_df: pd.DataFrame, identifier: str, columns: list
) -> pd.DataFrame:
    files_df["identifier"] = files_df["identifier"].astype(str)
    ods_metadata["dataset_identifier"] = ods_metadata["dataset_identifier"].astype(str)
    df = files_df.merge(
        ods_metadata, left_on=identifier, right_on="dataset_identifier", how="left"
    )
    all_columns = files_df.columns.tolist() + [
        col for col in columns if col in df.columns
    ]

    return df[all_columns]


def get_merged_datasets() -> pd.DataFrame:
    remote_fields = [
        "dataset_identifier",
        "title",
        "modified",
        "size_of_records_in_the_dataset_in_bytes",
        "number_of_records",
    ]
    local_fields = ["dataset_identifier", "modified", "number_of_records"]
    df = ods_metadata[remote_fields].merge(
        get_local_metadata()[local_fields], on="dataset_identifier", how="left"
    )
    # Rename columns by replacing postfix "_x" with "_ods" and "_y" with "_local"
    df.rename(
        columns=lambda col: col.replace("_x", "_ods").replace("_y", "_local"),
        inplace=True,
    )

    return df


def get_local_metadata():
    local_metadata = load_config()
    df = pd.DataFrame.from_dict(local_metadata, orient="index")
    df["dataset_identifier"] = df["dataset_identifier"].astype(str)
    return df


ods_metadata = get_ods_table(metadata)
local_metadata_df = get_local_metadata()
