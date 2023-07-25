import streamlit as st
#from sqlalchemy import create_engine
from intro import engine

st.write("## Query 14")
st.write("## This query contains multiple iterations")
st.write("## Iteration 1:")
#new line
st.write("")
st.write("### First identify items in the same brand, class and category that are sold in all three sales channels in two consecutive years. Then compute the average sales (quantity*list price) across all sales of all three sales channels in the same three years (average sales). Finally, compute the total sales and the total number of sales rolled up for each channel, brand, class and category. Only consider sales of cross channel sales that had sales larger than the average sale.")
# Inputs for query parameters
year = st.slider("Year", min_value=1950, max_value=2023, value=2001)
#day = st.slider("Day", min_value=1, max_value=28, value=1)
#limit value as user input
limit_value = st.slider("Limit", min_value=1, max_value=100, value=10)


# Save selected parameter values in session state
if "query_parameters" not in st.session_state:
    st.session_state.query_parameters = {}
st.session_state.query_parameters["year"] = year
st.session_state.query_parameters["limit_value"] = limit_value

# Query with placeholders for parameters
query_template = """

with  cross_items as
 (select i_item_sk ss_item_sk
 from item,
 (select iss.i_brand_id brand_id
     ,iss.i_class_id class_id
     ,iss.i_category_id category_id
 from store_sales
     ,item iss
     ,date_dim d1
 where ss_item_sk = iss.i_item_sk
   and ss_sold_date_sk = d1.d_date_sk
   and d1.d_year between {year} AND {year} + 2
 intersect 
 select ics.i_brand_id
     ,ics.i_class_id
     ,ics.i_category_id
 from catalog_sales
     ,item ics
     ,date_dim d2
 where cs_item_sk = ics.i_item_sk
   and cs_sold_date_sk = d2.d_date_sk
   and d2.d_year between {year} AND {year} + 2
 intersect
 select iws.i_brand_id
     ,iws.i_class_id
     ,iws.i_category_id
 from web_sales
     ,item iws
     ,date_dim d3
 where ws_item_sk = iws.i_item_sk
   and ws_sold_date_sk = d3.d_date_sk
   and d3.d_year between {year} AND {year} + 2)
 where i_brand_id = brand_id
      and i_class_id = class_id
      and i_category_id = category_id
),
 avg_sales as
 (select avg(quantity*list_price) average_sales
  from (select ss_quantity quantity
             ,ss_list_price list_price
       from store_sales
           ,date_dim
       where ss_sold_date_sk = d_date_sk
         and d_year between {year} AND {year} + 2
       union all 
       select cs_quantity quantity 
             ,cs_list_price list_price
       from catalog_sales
           ,date_dim
       where cs_sold_date_sk = d_date_sk
         and d_year between {year} AND {year} + 2
       union all
       select ws_quantity quantity
             ,ws_list_price list_price
       from web_sales
           ,date_dim
       where ws_sold_date_sk = d_date_sk
         and d_year between {year} AND {year} + 2) x)
select channel, i_brand_id,i_class_id,i_category_id,sum(sales), sum(number_sales)
 from(
       select 'store' channel, i_brand_id,i_class_id
             ,i_category_id,sum(ss_quantity*ss_list_price) sales
             , count(*) number_sales
       from store_sales
           ,item
           ,date_dim
       where ss_item_sk in (select ss_item_sk from cross_items)
         and ss_item_sk = i_item_sk
         and ss_sold_date_sk = d_date_sk
         and d_year = {year}+2 
         and d_moy = 11
       group by i_brand_id,i_class_id,i_category_id
       having sum(ss_quantity*ss_list_price) > (select average_sales from avg_sales)
       union all
       select 'catalog' channel, i_brand_id,i_class_id,i_category_id, sum(cs_quantity*cs_list_price) sales, count(*) number_sales
       from catalog_sales
           ,item
           ,date_dim
       where cs_item_sk in (select ss_item_sk from cross_items)
         and cs_item_sk = i_item_sk
         and cs_sold_date_sk = d_date_sk
         and d_year = {year}+2 
         and d_moy = 11
       group by i_brand_id,i_class_id,i_category_id
       having sum(cs_quantity*cs_list_price) > (select average_sales from avg_sales)
       union all
       select 'web' channel, i_brand_id,i_class_id,i_category_id, sum(ws_quantity*ws_list_price) sales , count(*) number_sales
       from web_sales
           ,item
           ,date_dim
       where ws_item_sk in (select ss_item_sk from cross_items)
         and ws_item_sk = i_item_sk
         and ws_sold_date_sk = d_date_sk
         and d_year = {year}+2
         and d_moy = 11
       group by i_brand_id,i_class_id,i_category_id
       having sum(ws_quantity*ws_list_price) > (select average_sales from avg_sales)
 ) y
 group by rollup (channel, i_brand_id,i_class_id,i_category_id)
 order by channel,i_brand_id,i_class_id,i_category_id limit {limit_value};
"""

# Button to generate query result and save it in session state
if st.button("Generate Query Result"):
    # Check if selected parameter values are the same as previous values
    if "previous_query_parameters" in st.session_state and st.session_state.previous_query_parameters == st.session_state.query_parameters:
        # Display previously saved query result from session state
        if "query_result1" in st.session_state:
            st.table(st.session_state.query_result1)
    else:
        # Format query with selected parameter values
        query = query_template.format(year=year, limit_value=limit_value)
        
        # Execute query and save result in session state
        with st.spinner("Executing query..."):
            try:
                connection = engine.connect()
                results = connection.execute(query).fetchall()
                st.session_state.query_result1 = results
                
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