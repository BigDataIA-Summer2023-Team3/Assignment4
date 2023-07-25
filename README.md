# Snowflake Queries using Streamlit App

This assignment uses the `snowflake_sample_data` database and the `tpcds_sf10tcl` schema to run Snowflake queries using a Streamlit app.


## Prerequisites

- A Snowflake account. If you don't have one, you can create one on the Snowflake website.
- Docker installed on your machine. If not, you can download it from the Docker website.


## Setup

1. Clone this repository
2. Create a virtual environment
3. Install dependencies
4. Run Streamlit app on local machine or build and run Docker container
5. Access app at `http://localhost:8090`
6. The app is also hosted on GP at `http://<gcp-url>:8090`
7. Enter your Snowflake username, password, account identifier, database name, and schema name as user input in the Streamlit app.


## Queries

1. Calculate the average sales quantity, average sales price, average wholesale cost, total wholesale cost for store sales of different customer types (e.g., based on marital status, education status) including their household demographics, sales price and different combinations of state and sales profit for a given year.


2. This query contains multiple iterations:
    - Iteration 1: First identify items in the same brand, class and category that are sold in all three sales channels in two consecutive years. Then compute the average sales (quantity*list price) across all sales of all three sales channels in the same three years (average sales). Finally, compute the total sales and the total number of sales rolled up for each channel, brand, class and category. Only consider sales of cross channel sales that had sales larger than the average sale.
    - Iteration 2: Based on the previous query compare December store sales.

      
3. Report the total catalog sales for customers in selected geographical regions or who made large purchases for a given year and quarter.

   
4. Report number of orders, total shipping costs and profits from catalog sales of particular counties and states for a given 60 day period for non-returned sales filled from an alternate warehouse

   
5. Analyze, for each state, all items that were sold in stores in a particular quarter and returned in the next three quarters and then re-purchased by the customer through the catalog channel in the three following quarters.


6. Compute, for each county, the average quantity, list price, coupon amount, sales price, net profit, age, and number of dependents for all items purchased through catalog sales in a given year by customers who were born in a given list of six months and living in a given list of seven states and who also belong to a given gender and education demographic.


## Docker Setup

1. Open a terminal or command prompt and navigate to the directory where your Dockerfile is located.
2. Build the Docker image by running the command `docker build -t <image-name> .` where `<image-name>` is the name you want to give to your image.
3. Once the image is built, you can run a container from it by running the command `docker run -p <host-port>:<container-port> <image-name>` where `<host-port>` is the port on your host machine that you want to map to the container's port `<container-port>`.
4. Access your app at `http://localhost:<host-port>`.


## Additional Resources

- For more detailed information about the project, including snapshots of the working application, please refer to this codelab.
- Sample queries - http://www.tpc.org/TPC_Documents_Current_Versions/pdf/TPC-DS_v2.5.0.pdf
- query templates - https://github.com/gregrahn/tpcds-kit/tree/master/query_templates
