import streamlit as st
#from sqlalchemy import create_engine
from intro import engine

st.write("## Query 18")
st.write("### Compute, for each county, the average quantity, list price, coupon amount, sales price, net profit, age, and number of dependents for all items purchased through catalog sales in a given year by customers who were born in a given list of six months and living in a given list of seven states and who also belong to a given gender and education demographic.")
# Inputs for query parameters
year = st.slider("Year", min_value=1950, max_value=2023, value=2001)
first_month = st.slider("First Month", min_value=1, max_value=6, value=1)
months = list(range(first_month, first_month + 6))
es = st.selectbox("Education Status", ["Unknown", "Advanced Degree", "College", "2 yr Degree"])
gen = st.selectbox("Gender", ["M", "F"])
limit_value = st.slider("Limit", min_value=1, max_value=100, value=10)

# Save selected parameter values in session state
if "query_parameters" not in st.session_state:
    st.session_state.query_parameters = {}
st.session_state.query_parameters["year"] = year
st.session_state.query_parameters["months"] = months
st.session_state.query_parameters["es"] = es
st.session_state.query_parameters["gen"] = gen
st.session_state.query_parameters["limit_value"] = limit_value

# Format the list of months as a string for use in the query
months_str = ", ".join(map(str, months))

# Query with placeholders for parameters
query_template = f"""
SELECT i_item_id,
    ca_country,
    ca_state, 
    ca_county,
    ROUND(AVG(CAST(cs_quantity AS DECIMAL(12,2))), 2) agg1,
    ROUND(AVG(CAST(cs_list_price AS DECIMAL(12,2))), 2) agg2,
    ROUND(AVG(CAST(cs_coupon_amt AS DECIMAL(12,2))), 2) agg3,
    ROUND(AVG(CAST(cs_sales_price AS DECIMAL(12,2))), 2) agg4,
    ROUND(AVG(CAST(cs_net_profit AS DECIMAL(12,2))), 2) agg5,
    ROUND(AVG(CAST(c_birth_year AS DECIMAL(12,2))), 0) agg6,
    ROUND(AVG(CAST(cd1.cd_dep_count AS DECIMAL(12,2))), 0) agg7
FROM catalog_sales, customer_demographics cd1, 
    customer_demographics cd2, customer, customer_address, date_dim, item
WHERE cs_sold_date_sk = d_date_sk AND
    cs_item_sk = i_item_sk AND
    cs_bill_cdemo_sk = cd1.cd_demo_sk AND
    cs_bill_customer_sk = c_customer_sk AND
    cd1.cd_gender = '{gen}' AND 
    cd1.cd_education_status = '{es}' AND
    c_current_cdemo_sk = cd2.cd_demo_sk AND
    c_current_addr_sk = ca_address_sk AND
    c_birth_month IN ({months_str}) AND
    d_year = {year} AND
    ca_state IN ('VA', 'NM', 'OK', 'ND', 'MS','IN')
GROUP BY ROLLUP (i_item_id, ca_country, ca_state, ca_county)
ORDER BY ca_country,
    ca_state, 
    ca_county,
i_item_id
LIMIT {limit_value};
"""

# Button to generate query result and save it in session state
if st.button("Generate Query Result"):
    # Check if selected parameter values are the same as previous values
    if "previous_query_parameters" in st.session_state and st.session_state.previous_query_parameters == st.session_state.query_parameters:
        # Display previously saved query result from session state
        if "query_result6" in st.session_state:
            st.table(st.session_state.query_result6)
    else:
        # Format query with selected parameter values
        query = query_template.format(year=year, es=es, gen=gen, limit_value=limit_value, months_str=months_str)
        
        # Execute query and save result in session state
        with st.spinner("Executing query..."):
            try:
                connection = engine.connect()
                results = connection.execute(query).fetchall()
                st.session_state.query_result6 = results
                
                # Display success message and result table if result is not empty
                st.success("Query executed successfully!")
                if results:
                    st.table(results)
                else:
                    st.warning("No results found.")
                    
            finally:
                if 'connection' in locals():
                    connection.close()
                engine.dispose()
        
        # Save current parameter values as previous values in session state
        st.session_state.previous_query_parameters = dict(st.session_state.query_parameters)