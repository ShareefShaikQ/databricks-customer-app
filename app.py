import os
import json

import streamlit as st
from databricks.sdk import WorkspaceClient


# ============================================================
# APP CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Customer Analytics",
    page_icon="📊",
    layout="wide"
)   


# ============================================================
# DATABRICKS APP RESOURCES
# ============================================================

WAREHOUSE_ID = os.getenv("WAREHOUSE_ID")
CUSTOMER_TABLE = os.getenv("CUSTOMER_TABLE")


# ============================================================
# DATABRICKS CLIENT
# ============================================================

w = WorkspaceClient()


# ============================================================
# SQL EXECUTION FUNCTION
# ============================================================

def run_query(sql, parameters=None):

    response = w.statement_execution.execute_statement(
        warehouse_id=WAREHOUSE_ID,
        statement=sql,
        parameters=parameters,
        wait_timeout="30s"
    )

    if response.status.state.name != "SUCCEEDED":

        st.error(
            f"SQL execution failed: {response.status.state}"
        )

        st.error(str(response))

        raise Exception("SQL execution failed")

    return response.result.data_array


# ============================================================
# HEADER
# ============================================================

st.title("📊 Customer Analytics Dashboard")

st.write(
    "Databricks Apps + SQL Warehouse + Unity Catalog"
)

st.divider()


# ============================================================
# RESOURCE VALIDATION
# ============================================================

if not WAREHOUSE_ID:

    st.error(
        "WAREHOUSE_ID is not available."
    )

    st.stop()


if not CUSTOMER_TABLE:

    st.error(
        "CUSTOMER_TABLE is not available."
    )

    st.stop()


# ============================================================
# MAIN APPLICATION
# ============================================================

try:

    # ========================================================
    # 1. LOAD ALL FILTER OPTIONS
    #
    # ONE SQL QUERY:
    # State + City + Customer Segment
    # ========================================================

    filter_options_result = run_query(
        f"""
        SELECT
            sort_array(
                collect_set(state)
            ) AS states,

            sort_array(
                collect_set(city)
            ) AS cities,

            sort_array(
                collect_set(customer_segment)
            ) AS segments

        FROM {CUSTOMER_TABLE}
        """
    )


    # --------------------------------------------------------
    # EXTRACT FILTER OPTIONS
    # --------------------------------------------------------

    states_data = json.loads(
        filter_options_result[0][0]
    )

    cities_data = json.loads(
        filter_options_result[0][1]
    )

    segments_data = json.loads(
        filter_options_result[0][2]
    )


    states = ["All"] + [
        value
        for value in states_data
        if value is not None
    ]

    cities = ["All"] + [
        value
        for value in cities_data
        if value is not None
    ]

    segments = ["All"] + [
        value
        for value in segments_data
        if value is not None
    ]


    # ========================================================
    # 2. KPI QUERY
    #
    # ONE SQL QUERY FOR ALL KPI METRICS
    # ========================================================

    kpi_result = run_query(
        f"""
        SELECT

            COUNT(*) AS total_customers,

            SUM(
                CASE
                    WHEN customer_segment = 'Premium'
                    THEN 1
                    ELSE 0
                END
            ) AS premium_customers,

            SUM(
                CASE
                    WHEN customer_segment = 'Enterprise'
                    THEN 1
                    ELSE 0
                END
            ) AS enterprise_customers

        FROM {CUSTOMER_TABLE}
        """
    )


    # --------------------------------------------------------
    # EXTRACT KPI VALUES
    # --------------------------------------------------------

    total_customers = int(
        kpi_result[0][0]
    )

    premium_customers = int(
        kpi_result[0][1]
    )

    enterprise_customers = int(
        kpi_result[0][2]
    )


    # ========================================================
    # 3. KPI CARDS
    # ========================================================

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "Total Customers",
            total_customers
        )

    with col2:

        st.metric(
            "Premium Customers",
            premium_customers
        )

    with col3:

        st.metric(
            "Enterprise Customers",
            enterprise_customers
        )


    st.divider()


    # ========================================================
    # 4. CUSTOMER FILTERS
    # ========================================================

    st.subheader("🔎 Customer Filters")

    col1, col2, col3 = st.columns(3)


    # --------------------------------------------------------
    # STATE
    # --------------------------------------------------------

    with col1:

        state = st.selectbox(
            "State",
            states
        )


    # --------------------------------------------------------
    # CITY
    # --------------------------------------------------------

    with col2:

        city = st.selectbox(
            "City",
            cities
        )


    # --------------------------------------------------------
    # CUSTOMER SEGMENT
    # --------------------------------------------------------

    with col3:

        segment = st.selectbox(
            "Customer Segment",
            segments
        )


    # ========================================================
    # 5. BUILD PARAMETERIZED FILTERS
    #
    # IMPORTANT:
    # User-selected values are NOT directly inserted
    # into the SQL string.
    #
    # Example:
    #
    # state = :state
    #
    # The actual value is sent separately through
    # the parameters list.
    # ========================================================

    filter_conditions = []

    parameters = []


    # --------------------------------------------------------
    # STATE FILTER
    # --------------------------------------------------------

    if state != "All":

        filter_conditions.append(
            "state = :state"
        )

        parameters.append(
            {
                "name": "state",
                "value": state,
                "type": "STRING"
            }
        )


    # --------------------------------------------------------
    # CITY FILTER
    # --------------------------------------------------------

    if city != "All":

        filter_conditions.append(
            "city = :city"
        )

        parameters.append(
            {
                "name": "city",
                "value": city,
                "type": "STRING"
            }
        )


    # --------------------------------------------------------
    # CUSTOMER SEGMENT FILTER
    # --------------------------------------------------------

    if segment != "All":

        filter_conditions.append(
            "customer_segment = :segment"
        )

        parameters.append(
            {
                "name": "segment",
                "value": segment,
                "type": "STRING"
            }
        )


    # ========================================================
    # 6. BUILD WHERE CLAUSE
    # ========================================================

    where_clause = ""

    if filter_conditions:

        where_clause = (
            "WHERE "
            + " AND ".join(filter_conditions)
        )

    # ========================================================
    # 7. CUSTOMER ANALYTICS
    # ========================================================

    st.divider()

    st.subheader("📊 Customer Analytics")


    # ========================================================
    # CUSTOMERS BY SEGMENT
    # ========================================================

    segment_result = run_query(
        f"""
        SELECT
            customer_segment,
            COUNT(*) AS customer_count
        FROM {CUSTOMER_TABLE}
        GROUP BY customer_segment
        ORDER BY customer_count DESC
        """
    )
    # ========================================================
    # 7. CUSTOMER RESULT QUERY
    # ========================================================

    filter_sql = f"""
    SELECT

        customer_id,
        customer_name,
        email,
        city,
        state,
        gender,
        customer_segment,
        signup_date

    FROM {CUSTOMER_TABLE}

    {where_clause}

    ORDER BY customer_name
    """


    # ========================================================
    # EXECUTE PARAMETERIZED QUERY
    # ========================================================

    results = run_query(
        filter_sql,
        parameters
    )


    # ========================================================
    # 8. CUSTOMER RESULTS
    # ========================================================

    st.subheader(
        "Customer Results"
    )


    if results:

        st.success(
            f"Found {len(results)} customer(s)"
        )

        st.dataframe(
            results,
            use_container_width=True
        )

    else:

        st.warning(
            "No customers found."
        )


# ============================================================
# ERROR HANDLING
# ============================================================

except Exception as e:

    st.error(
        "Unable to load customer data."
    )

    st.exception(e)