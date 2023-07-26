import streamlit as st
#from sqlalchemy import create_engine
from intro import conn

st.write("## Query 15")
st.write("### Report the total catalog sales for customers in selected geographical regions or who made large purchases for a given year and quarter.")
# Inputs for query parameters
d_year = st.slider("Year", min_value=1950, max_value=2023, value=2023)
d_qoy = st.slider("QOY", min_value=1, max_value=4, value=1)
limit_value = st.number_input("Limit", min_value=1, max_value=100, value=10)


# # Save selected parameter values in session state
# if "query_parameters" not in st.session_state:
#     st.session_state.query_parameters = {}
# st.session_state.query_parameters["d_year"] = d_year
# st.session_state.query_parameters["d_qoy"] = d_qoy
# st.session_state.query_parameters["limit_value"] = limit_value

# Query with placeholders for parameters
query_template = """
SELECT
    ca_zip,
    SUM(cs_sales_price) AS total_catalog_sales
FROM
    catalog_sales
JOIN
    customer ON cs_bill_customer_sk = c_customer_sk
JOIN
    customer_address ON c_current_addr_sk = ca_address_sk
JOIN
    date_dim ON cs_sold_date_sk = d_date_sk
WHERE
    (
        SUBSTR(ca_zip, 1, 5) IN (
            '85669', '86197', '88274', '83405', '86475',
            '85392', '85460', '80348', '81792'
        )
        OR ca_state IN ('CA', 'WA', 'GA')
        OR cs_sales_price > 500
    )
    AND d_qoy = {d_qoy} -- Assuming QOY.01 = 2
    AND d_year = {d_year} -- Assuming YEAR.01 = 2001
GROUP BY
    ca_zip
limit {limit_value} -- Assuming limit_value = 10;
"""

# Function to generate query result and save it in cache
@st.cache_data
def generate_query_result(d_year, d_qoy, limit_value):
    # Format query with selected parameter values
    query = query_template.format(d_year=d_year, d_qoy=d_qoy, limit_value=limit_value)
    
    # Execute query and save result in cache
    results = conn.query(query, ttl=600)
    
    return results

# Button to generate query result and display it
if st.button("Generate Query Result"):
    # Generate query result and save it in cache
    with st.spinner("Executing query..."):
        results = generate_query_result(d_year, d_qoy, limit_value)
        
        # Display success message and result table if result is not empty
        st.success("Query executed successfully!")
        if not results.empty:
            st.table(results)
        else:
            st.warning("No results found.")