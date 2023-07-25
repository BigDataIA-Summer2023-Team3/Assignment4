import streamlit as st
#from sqlalchemy import create_engine
from intro import engine

st.write("## Query 17")
st.write("### Analyze, for each state, all items that were sold in stores in a particular quarter and returned in the next three quarters and then re-purchased by the customer through the catalog channel in the three following quarters.")
# Inputs for query parameters
year = st.slider("Year", min_value=1950, max_value=2023, value=2023)
quarter = st.selectbox("Quarter", options=["Q1", "Q2", "Q3", "Q4"])
limit_value = st.slider("Limit", min_value=1, max_value=100, value=10)

# Save selected parameter values in session state
if "query_parameters" not in st.session_state:
    st.session_state.query_parameters = {}
st.session_state.query_parameters["year"] = year
st.session_state.query_parameters["quarter"] = quarter

# Compute the next three quarters
#stores the next three quarters in a list of the same year
next_quarters = [f"{year}Q{i}" for i in range(int(quarter[1])+1, 5)]
#stores the next three remaining quarters in a list of the next year
next_year_quarters = [f"{year+1}Q{i}" for i in range(1, 4-len(next_quarters))]
#appends the next three remaining quarters to the list of the same year
next_quarters.extend(next_year_quarters)
#converts the list to a string
next_quarters_str = "', '".join(next_quarters)
st.write(f"Next three quarters: {next_quarters_str}")

st.session_state.query_parameters["limit_value"] = limit_value

# Query with placeholders for parameters
query_template = f"""
SELECT
    i_item_id,
    i_item_desc,
    s_state,
    COUNT(ss_quantity) AS store_sales_quantitycount,
    AVG(ss_quantity) AS store_sales_quantityave,
    STDDEV_SAMP(ss_quantity) AS store_sales_quantitystdev,
    STDDEV_SAMP(ss_quantity)/AVG(ss_quantity) AS store_sales_quantitycov,
    COUNT(sr_return_quantity) AS store_returns_quantitycount,
    AVG(sr_return_quantity) AS store_returns_quantityave,
    STDDEV_SAMP(sr_return_quantity) AS store_returns_quantitystdev,
    STDDEV_SAMP(sr_return_quantity)/AVG(sr_return_quantity) AS store_returns_quantitycov,
    COUNT(cs_quantity) AS catalog_sales_quantitycount,
    AVG(cs_quantity) AS catalog_sales_quantityave,
    STDDEV_SAMP(cs_quantity) AS catalog_sales_quantitystdev,
    STDDEV_SAMP(cs_quantity)/AVG(cs_quantity) AS catalog_sales_quantitycov
FROM
    store_sales
JOIN
    date_dim d1
ON
    ss_sold_date_sk = d1.d_date_sk
JOIN
    item
ON
    i_item_sk = ss_item_sk
JOIN
    store
ON
    s_store_sk = ss_store_sk
JOIN
    store_returns
ON
    ss_customer_sk = sr_customer_sk AND ss_item_sk = sr_item_sk AND ss_ticket_number = sr_ticket_number
JOIN
    date_dim d2
ON
    sr_returned_date_sk = d2.d_date_sk
JOIN
    catalog_sales
ON 
    sr_customer_sk = cs_bill_customer_sk AND sr_item_sk = cs_item_sk 
JOIN 
    date_dim d3 
ON 
    cs_sold_date_sk = d3.d_date_sk 
WHERE 
    d1.d_quarter_name = '{year}{quarter}' AND d2.d_quarter_name IN ('{next_quarters_str}') AND d3.d_quarter_name IN ('{next_quarters_str}') 
GROUP BY 
    i_item_id, i_item_desc, s_state 
ORDER BY 
    i_item_id, i_item_desc, s_state 
limit {limit_value};
"""

# Button to generate query result and save it in session state
if st.button("Generate Query Result"):
    # Check if selected parameter values are the same as previous values
    if "previous_query_parameters" in st.session_state and st.session_state.previous_query_parameters == st.session_state.query_parameters:
        # Display previously saved query result from session state
        if "query_result5" in st.session_state:
            st.table(st.session_state.query_result5)
    else:
        # Format query with selected parameter values
        query = query_template.format(year=year, limit_value=limit_value, quarter=quarter)
        
        # Execute query and save result in session state
        with st.spinner("Executing query..."):
            try:
                connection = engine.connect()
                results = connection.execute(query).fetchall()
                st.session_state.query_result5 = results
                
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