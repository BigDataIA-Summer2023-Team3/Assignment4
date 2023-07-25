import streamlit as st
#from sqlalchemy import create_engine
from intro import engine
from datetime import datetime, timedelta

st.write("## Query 16")
st.write("### Report number of orders, total shipping costs and profits from catalog sales of particular counties and states for a given 60 day period for non-returned sales filled from an alternate warehouse.")
# Inputs for query parameters
#d_year = st.slider("Year", min_value=1950, max_value=2023, value=2023)
#d_month = st.slider("Month", min_value=1, max_value=12, value=1)
state = st.selectbox("State", options=["AL", "AK", "AZ", "AR", "CA", "CZ", "CO", "CT", "DE", "DC", "FL", "GA", "GU", "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ", "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "PR", "RI" ,"SC" ,"SD" ,"TN" ,"TX" ,"UT" ,"VT" ,"VI" ,"VA" ,"WA" ,"WV" ,"WI" ,"WY"])
county = st.selectbox("County",options=["Perry County", "Jefferson Davis Parish", "Terry County", "Wadena County", "Arthur County", "Green Lake County", "Saginaw County", "Brazos County", "Bronx County", "Orange County", "Mariposa County", "Dade County", "Hubbard County", "Harper County", "Maverick County", "Jackson County", "Levy County", "Barrow County", "Dauphin County", "Stillwater County", "Mesa County","Richland County"])
#limit_value = st.number_input("Limit", min_value=1, max_value=100, value=10)
# Inputs for start_date and end_date
start_date = st.date_input("Start Date", value=datetime.today())
end_date = start_date + timedelta(days=60)
st.write(f"End Date: {end_date}")

# Save selected parameter values in session state
if "query_parameters" not in st.session_state:
    st.session_state.query_parameters = {}
st.session_state.query_parameters["start_date"] = start_date
st.session_state.query_parameters["end_date"] = end_date
st.session_state.query_parameters["state"] = state
st.session_state.query_parameters["county"] = county

# Query with placeholders for parameters
query_template = f"""
SELECT
    COUNT(DISTINCT cs1.cs_order_number) AS "order count",
    SUM(cs1.cs_ext_ship_cost) AS "total shipping cost",
    SUM(cs1.cs_net_profit) AS "total net profit"
FROM
    catalog_sales cs1
JOIN
    date_dim ON cs1.cs_ship_date_sk = d_date_sk
JOIN
    customer_address ca ON cs1.cs_ship_addr_sk = ca.ca_address_sk
JOIN
    call_center cc ON cs1.cs_call_center_sk = cc.cc_call_center_sk
WHERE
    d_date BETWEEN '{start_date}' AND DATEADD(DAY, 60, '{start_date}')
    AND ca.ca_state = '{state}'
    AND cc.cc_county = '{county}'
    AND NOT EXISTS (
        SELECT *
        FROM catalog_returns cr1
        WHERE cs1.cs_order_number = cr1.cr_order_number
    )
    AND EXISTS (
        SELECT *
        FROM catalog_sales cs2
        WHERE cs1.cs_order_number = cs2.cs_order_number
          AND cs1.cs_warehouse_sk <> cs2.cs_warehouse_sk)
"""


# Button to generate query result and save it in session state
if st.button("Generate Query Result"):
    # Check if selected parameter values are the same as previous values
    if "previous_query_parameters" in st.session_state and st.session_state.previous_query_parameters == st.session_state.query_parameters:
        # Display previously saved query result from session state
        if "query_result4" in st.session_state:
            st.table(st.session_state.query_result4)
    else:
        # Format query with selected parameter values
        query = query_template.format(state=state, county=county, start_date=start_date, end_date=end_date)
        
        # Execute query and save result in session state
        with st.spinner("Executing query..."):
            try:
                connection = engine.connect()
                results = connection.execute(query).fetchall()
                st.session_state.query_result4 = results
                
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
