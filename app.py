import streamlit as st

st.set_page_config(
    page_title="Customer Analytics",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Customer Analytics Dashboard")
st.write("Databricks Apps — Version 2")

st.divider()

# KPI section
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Total Customers", "1,250")

with col2:
    st.metric("Total Orders", "3,840")

with col3:
    st.metric("Total Revenue", "$125,430")

st.divider()

st.subheader("Customer Analytics")

customer_name = st.text_input(
    "Search Customer",
    placeholder="Enter customer name..."
)

if customer_name:
    st.info(f"Searching for customer: {customer_name}")
else:
    st.write("Enter a customer name to search.")