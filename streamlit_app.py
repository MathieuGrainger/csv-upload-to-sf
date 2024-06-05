import streamlit as st
from snowflake.snowpark.context import get_active_session

# Connect to Snowflake (credentials stored in snowflake.yml)
session = get_active_session()

# File uploader component
uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

if uploaded_file:
    # Read the uploaded CSV file into a Pandas DataFrame
    dataframe = pd.read_csv(uploaded_file)

    # Load the DataFrame into a local stage (replace 'your_stage' with your stage name)
    session.create_stage("WGS_LOCAL_STAGE")
    session.create_or_replace_file_format("csv_format", "TYPE = CSV")
    session.put(uploaded_file.name, f"@~/WGS_LOCAL_STAGE/{uploaded_file.name}")

    st.success(f"CSV file '{uploaded_file.name}' uploaded to local stage!")
