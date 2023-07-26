import streamlit as st

st.set_page_config(page_title="DAMG 7245", page_icon="👋")

st.sidebar.success("Assignment 4 sections")
st.title("Assignment 4")

st.markdown("""### SNOWFLAKE QUERIES""")

# Initialize connection.
conn = st.experimental_connection('snowpark')


