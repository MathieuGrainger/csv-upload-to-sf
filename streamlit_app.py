import streamlit as st
import pandas as pd
import json
from snowflake.snowpark import Session

st.set_page_config(page_title='CSV uploader',  initial_sidebar_state="auto", menu_items=None)
s = st.session_state
if not s:
        s.pressed_first_button = False

with st.sidebar:
    
    SF_ACCOUNT = st.text_input('Snowflake account:')
    SF_USR = st.text_input('Snowflake user:')
    SF_PWD = st.text_input('Snowflake password:', type='password')

    conn = {'ACCOUNT': SF_ACCOUNT,'USER': SF_USR,'PASSWORD': SF_PWD}
            
    if st.button('Connect') or s.pressed_first_button:
                   
            session = Session.builder.configs(conn).create()
            s.pressed_first_button = True

            if session != '':
                datawarehouse_list = session.sql("show warehouses;").collect()
                datawarehouse_list =  pd.DataFrame(datawarehouse_list)
                datawarehouse_list= datawarehouse_list["name"]

                datawarehouse_option = st.selectbox('Select Virtual datawarehouse', datawarehouse_list)

                database_list_df = session.sql("show databases;").collect()
                database_list_df =  pd.DataFrame(database_list_df)
                database_list_df = database_list_df["name"]
                
                database_option = st.selectbox('Select database', database_list_df)
                set_database = session.sql(f'''USE DATABASE {database_option}   ;''').collect()

                if set_database != '':
                    set_database = session.use_database(database_option)
                    schema_list_df = session.sql("show schemas;").collect()
                    schema_list_df =  pd.DataFrame(schema_list_df)
                    schema_list_df = schema_list_df["name"]

                    schema_option = st.selectbox('Select schema', schema_list_df)
                    set_schema = session.sql(f'''USE schema {schema_option}   ;''').collect()

                    if set_schema != '':
                        table_list_df = session.sql("show tables;").collect()
                        table_list_df =  pd.DataFrame(table_list_df)
                        if not table_list_df.empty:
                            table_list_df = table_list_df["name"]

                            table_option = st.selectbox('Select tables', table_list_df)
                            upload_table = st.text_input('Use table:',table_option)

                            conn2 = {
                                    'ACCOUNT': SF_ACCOUNT,
                                    'user': SF_USR,
                                    'password': SF_PWD,
                                    'schema': schema_option,
                                    'database': database_option,
                                    'warehouse': datawarehouse_option,
                                }

uploaded_file = st.file_uploader("Choose a file")
if uploaded_file:
    # Read the uploaded CSV file into a Pandas DataFrame
    dataframe = pd.read_csv(uploaded_file)

    # Load the DataFrame into a local stage (replace 'your_stage' with your stage name)
    session.create_stage("WGS_LOCAL_STAGE")
    session.create_or_replace_file_format("csv_format", "TYPE = CSV")
    session.put(uploaded_file.name, f"@~/WGS_LOCAL_STAGE/{uploaded_file.name}")

    st.success(f"CSV file '{uploaded_file.name}' uploaded to local stage!")
