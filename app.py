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

    if response.status.state != "SUCCEEDED":
        st.error(f"SQL execution failed: {response.status.state}")
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
    st.error("WAREHOUSE_ID is not available.")
    st.stop()

if not CUSTOMER_TABLE:
    st.error("CUSTOMER_TABLE is not available.")
    st.stop()


# ============================================================
# LOAD CUSTOMER DATA
# ============================================================

try:

    # --------------------------------------------------------
    # Total Customers
    # --------------------------------------------------------

    total_result = run_query(
        f"""
        SELECT COUNT(*)
        FROM {CUSTOMER_TABLE}
        """
    )

    total_customers = int(total_result[0][0])


    # --------------------------------------------------------
    # Premium Customers
    # --------------------------------------------------------

    premium_result = run_query(
        f"""
        SELECT COUNT(*)
        FROM {CUSTOMER_TABLE}
        WHERE customer_segment = 'Premium'
        """
    )

    premium_customers = int(premium_result[0][0])


    # --------------------------------------------------------
    # Enterprise Customers
    # --------------------------------------------------------

    enterprise_result = run_query(
        f"""
        SELECT COUNT(*)
        FROM {CUSTOMER_TABLE}
        WHERE customer_segment = 'Enterprise'
        """
    )

    enterprise_customers = int(enterprise_result[0][0])


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
    # CUSTOMER SEARCH
    # ========================================================

    st.subheader("🔎 Search Customers")

    customer_name = st.text_input(
        "Customer Name",
        placeholder="Enter customer name..."
    )


    if customer_name:

        search_sql = f"""
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
        WHERE LOWER(customer_name)
              LIKE LOWER('%{customer_name}%')
        ORDER BY customer_name
        """

        results = run_query(search_sql)


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

    else:

        st.info(
            "Enter a customer name to search."
        )


# ============================================================
# ERROR HANDLING
# ============================================================

except Exception as e:

    st.error(
        "Unable to load customer data."
    )

    st.exception(e)