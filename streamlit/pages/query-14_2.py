import streamlit as st
#from sqlalchemy import create_engine
from intro import conn

st.write("## Query 14")
#st.write("## This query contains multiple iterations")
st.write("## Iteration 2:")
#new line
st.write("")
st.write("### Based on the previous query compare December store sales.")
# Inputs for query parameters
year = st.slider("Year", min_value=1950, max_value=2023, value=2001)
day = st.slider("Day", min_value=1, max_value=28, value=1)
#limit value as user input
limit_value = st.slider("Limit", min_value=1, max_value=100, value=10)


# # Save selected parameter values in session state
# if "query_parameters" not in st.session_state:
#     st.session_state.query_parameters = {}
# st.session_state.query_parameters["year"] = year
# st.session_state.query_parameters["limit_value"] = limit_value
# st.session_state.query_parameters["day"] = day

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
   and d3.d_year between {year} AND {year} + 2) x
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
  select this_year.channel ty_channel
                           ,this_year.i_brand_id ty_brand
                           ,this_year.i_class_id ty_class
                           ,this_year.i_category_id ty_category
                           ,this_year.sales ty_sales
                           ,this_year.number_sales ty_number_sales
                           ,last_year.channel ly_channel
                           ,last_year.i_brand_id ly_brand
                           ,last_year.i_class_id ly_class
                           ,last_year.i_category_id ly_category
                           ,last_year.sales ly_sales
                           ,last_year.number_sales ly_number_sales 
 from
 (select 'store' channel, i_brand_id,i_class_id,i_category_id
        ,sum(ss_quantity*ss_list_price) sales, count(*) number_sales
 from store_sales 
     ,item
     ,date_dim
 where ss_item_sk in (select ss_item_sk from cross_items)
   and ss_item_sk = i_item_sk
   and ss_sold_date_sk = d_date_sk
   and d_week_seq = (select d_week_seq
                     from date_dim
                     where d_year = {year} + 1
                       and d_moy = 12
                       and d_dom = {day})
 group by i_brand_id,i_class_id,i_category_id
 having sum(ss_quantity*ss_list_price) > (select average_sales from avg_sales)) this_year,
 (select 'store' channel, i_brand_id,i_class_id
        ,i_category_id, sum(ss_quantity*ss_list_price) sales, count(*) number_sales
 from store_sales
     ,item
     ,date_dim
 where ss_item_sk in (select ss_item_sk from cross_items)
   and ss_item_sk = i_item_sk
   and ss_sold_date_sk = d_date_sk
   and d_week_seq = (select d_week_seq
                     from date_dim
                     where d_year = {year}
                       and d_moy = 12
                       and d_dom = {day})
 group by i_brand_id,i_class_id,i_category_id
 having sum(ss_quantity*ss_list_price) > (select average_sales from avg_sales)) last_year
 where this_year.i_brand_id= last_year.i_brand_id
   and this_year.i_class_id = last_year.i_class_id
   and this_year.i_category_id = last_year.i_category_id
 order by this_year.channel, this_year.i_brand_id, this_year.i_class_id, this_year.i_category_id
 LIMIT {limit_value};
"""

# Function to generate query result and save it in cache
@st.cache_data
def generate_query_result(year, day, limit_value):
    # Format query with selected parameter values
    query = query_template.format(year=year, day=day, limit_value=limit_value)
    
    # Execute query and save result in cache
    results = conn.query(query, ttl=600)
    
    return results

# Button to generate query result and display it
if st.button("Generate Query Result"):
    # Generate query result and save it in cache
    with st.spinner("Executing query..."):
        results = generate_query_result(year, day, limit_value)
        
        # Display success message and result table if result is not empty
        st.success("Query executed successfully!")
        if not results.empty:
            st.table(results)
        else:
            st.warning("No results found.")