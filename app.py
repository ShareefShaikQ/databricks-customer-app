import os
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

def run_query(sql):

    response = w.statement_execution.execute_statement(
        warehouse_id=WAREHOUSE_ID,
        statement=sql,
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
    # LOAD STATE FILTER OPTIONS
    # ========================================================

    state_result = run_query(
        f"""
        SELECT DISTINCT state
        FROM {CUSTOMER_TABLE}
        WHERE state IS NOT NULL
        ORDER BY state
        """
    )

    states = ["All"] + [
        row[0]
        for row in state_result
    ]


    # ========================================================
    # LOAD CITY FILTER OPTIONS
    # ========================================================

    city_result = run_query(
        f"""
        SELECT DISTINCT city
        FROM {CUSTOMER_TABLE}
        WHERE city IS NOT NULL
        ORDER BY city
        """
    )

    cities = ["All"] + [
        row[0]
        for row in city_result
    ]


    # ========================================================
    # KPI QUERY
    # One SQL query for all KPI metrics
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


    # ========================================================
    # EXTRACT KPI VALUES
    # ========================================================

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
    # KPI CARDS
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
    # CUSTOMER FILTERS
    # ========================================================

    st.subheader("🔎 Customer Filters")

    col1, col2, col3 = st.columns(3)


    # ========================================================
    # STATE FILTER
    # ========================================================

    with col1:

        state = st.selectbox(
            "State",
            states
        )


    # ========================================================
    # CITY FILTER
    # ========================================================

    with col2:

        city = st.selectbox(
            "City",
            cities
        )


    # ========================================================
    # CUSTOMER SEGMENT FILTER
    # Still hardcoded - we will make this dynamic next
    # ========================================================

    with col3:

        segment = st.selectbox(
            "Customer Segment",
            [
                "All",
                "Standard",
                "Premium",
                "Enterprise"
            ]
        )


    # ========================================================
    # BUILD FILTER CONDITIONS
    # ========================================================

    conditions = []


    if state != "All":

        conditions.append(
            f"state = '{state}'"
        )


    if city != "All":

        conditions.append(
            f"city = '{city}'"
        )


    if segment != "All":

        conditions.append(
            f"customer_segment = '{segment}'"
        )


    # ========================================================
    # BUILD WHERE CLAUSE
    # ========================================================

    where_clause = ""

    if conditions:

        where_clause = (
            "WHERE "
            + " AND ".join(conditions)
        )


    # ========================================================
    # FILTER QUERY
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
    # EXECUTE FILTER QUERY
    # ========================================================

    results = run_query(
        filter_sql
    )


    # ========================================================
    # CUSTOMER RESULTS
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