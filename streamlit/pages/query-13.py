import streamlit as st
#from sqlalchemy import create_engine
from intro import conn

st.write("## Query 13")
st.write("### Calculate the average sales quantity, average sales price, average wholesale cost, total wholesale cost for store sales of different customer types (e.g., based on marital status, education status) including their household demographics, sales price and different combinations of state and sales profit for a given year.")
# Inputs for query parameters
d_year = st.slider("Year", min_value=1950, max_value=2023, value=2023)
state = st.selectbox("State", options=["TX", "OH", "OR", "NM", "KY", "VA", "MS"])
es = st.selectbox("ES", options=["Advanced Degree", "College", "2 yr Degree"])
ms = st.selectbox("MS", options=["M", "S", "W"])


# Save selected parameter values in session state
# if "query_parameters" not in st.session_state:
#     st.session_state.query_parameters = {}
# st.session_state.query_parameters["d_year"] = d_year
# st.session_state.query_parameters["state"] = state
# st.session_state.query_parameters["education status"] = es
# st.session_state.query_parameters["marital status"] = ms
#st.session_state.query_parameters["limit_value"] = limit_value

# Query with placeholders for parameters
query_template = f"""
SELECT 
    AVG(ss_quantity) AS avg_sales_quantity,
    AVG(ss_ext_sales_price) AS avg_sales_price,
    AVG(ss_ext_wholesale_cost) AS avg_wholesale_cost,
    SUM(ss_ext_wholesale_cost) AS total_wholesale_cost
FROM 
    store_sales
JOIN store ON s_store_sk = ss_store_sk
JOIN customer_demographics ON cd_demo_sk = ss_cdemo_sk
JOIN household_demographics ON hd_demo_sk = ss_hdemo_sk
JOIN customer_address ON ss_addr_sk = ca_address_sk
JOIN date_dim ON ss_sold_date_sk = d_date_sk
WHERE 
    d_year = {d_year}
    AND (
        CASE 
            WHEN '{es}' = 'Advanced Degree' AND '{ms}' = 'M' THEN cd_marital_status = '{ms}' AND cd_education_status = '{es}' AND ss_sales_price BETWEEN 100.00 AND 150.00 AND hd_dep_count = 3
            WHEN '{es}' = 'College' AND '{ms}' = 'S' THEN cd_marital_status = '{ms}' AND cd_education_status = '{es}' AND ss_sales_price BETWEEN 50.00 AND 100.00 AND hd_dep_count = 1
            WHEN '{es}' = '2 yr Degree' AND '{ms}' = 'W' THEN cd_marital_status = '{ms}' AND cd_education_status = '{es}' AND ss_sales_price BETWEEN 150.00 AND 200.00 AND hd_dep_count = 1
        END
    )
    AND (
        CASE 
            WHEN '{state}' IN ('TX', 'OH') THEN ca_country = 'United States' AND ca_state IN ('{state}') AND ss_net_profit BETWEEN 100 AND 200
            WHEN '{state}' IN ('OR', 'NM', 'KY') THEN ca_country = 'United States' AND ca_state IN ('{state}') AND ss_net_profit BETWEEN 150 AND 300
            WHEN '{state}' IN ('VA', 'MS') THEN ca_country = 'United States' AND ca_state IN ('{state}') AND ss_net_profit BETWEEN 50 AND 250
        END
    );

"""


# Function to generate query result and save it in cache
@st.cache_data
def generate_query_result(state, es, ms, d_year, limit_value):
    # Format query with selected parameter values
    query = query_template.format(state=state, es=es, ms=ms, d_year=d_year, limit_value=limit_value)
    
    # Execute query and save result in cache
    results = conn.query(query, ttl=600)
    
    return results

# Button to generate query result and display it
if st.button("Generate Query Result"):
    # Generate query result and save it in cache
    with st.spinner("Executing query..."):
        results = generate_query_result(state, es, ms, d_year, limit_value=10)
        
        # Display success message and result table if result is not empty
        st.success("Query executed successfully!")
        if not results.empty:
            st.table(results)
        else:
            st.warning("No results found.")