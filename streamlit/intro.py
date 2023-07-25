import streamlit as st
from sqlalchemy import create_engine

st.set_page_config(page_title="DAMG 7245", page_icon="👋")

st.sidebar.success("Assignment 4 sections")
st.title("Assignment 4")

st.markdown("""### SNOWFLAKE QUERIES""")

# Sidebar inputs for Snowflake credentials
st.sidebar.title("Snowflake Credentials")
user = st.sidebar.text_input("User")
password = st.sidebar.text_input("Password", type="password")
account_identifier = st.sidebar.text_input("Account Identifier",type="password")
database = st.sidebar.text_input("Database")
schema = st.sidebar.text_input("Schema")

if "snowflake_credentials" not in st.session_state:
        st.session_state.snowflake_credentials = {}
st.session_state.snowflake_credentials["user"] = user
st.session_state.snowflake_credentials["password"] = password
st.session_state.snowflake_credentials["account_identifier"] = account_identifier
st.session_state.snowflake_credentials["database"] = database
st.session_state.snowflake_credentials["schema"] = schema

# Create engine using Snowflake credentials from session state
engine = create_engine(
    'snowflake://{user}:{password}@{account_identifier}/{database}/{schema}'.format(
        user=st.session_state.snowflake_credentials["user"],
        password=st.session_state.snowflake_credentials["password"],
        account_identifier=st.session_state.snowflake_credentials["account_identifier"],
        database=st.session_state.snowflake_credentials["database"],
        schema=st.session_state.snowflake_credentials["schema"]
    )
)