import streamlit as st

st.markdown("## About the Dataset")

st.markdown("""
This dataset contains **10,000 synthetic but business-realistic customer records** designed to simulate churn behavior in
subscription-based industries such as **SaaS, telecom, and service businesses**.

Customer churn, when a customer stops using a service, is a major business challenge because **retaining customers is far
more cost-effective than acquiring new ones**. This dataset enables predictive modeling to identify customers who are at risk of leaving.
""")

st.markdown("## Target Variable")
st.markdown("""
- **`churn`**
  - `0` = Customer stays  
  - `1` = Customer leaves  

The goal is to use customer data to predict which customers are likely to churn.
""")

st.markdown("## What the Data Includes")

with st.expander("Customer Profile"):
    st.markdown("""
- Age  
- Gender  
- Location  
- Tenure (how long they’ve been a customer)  
- Contract type  
""")

with st.expander("Product Usage"):
    st.markdown("""
- Login frequency  
- Session duration  
- Feature usage  
- Activity trends  
""")

with st.expander("Billing & Payments"):
    st.markdown("""
- Subscription fees  
- Revenue  
- Payment failures  
- Discounts  
""")

with st.expander("Customer Support"):
    st.markdown("""
- Support tickets  
- Resolution time  
- CSAT (Customer Satisfaction Score)  
- Complaints  
""")

with st.expander("Engagement & Feedback"):
    st.markdown("""
- Email activity  
- NPS (Net Promoter Score)  
- Survey responses  
""")

st.markdown("## Why This Dataset is Valuable")
st.markdown("""
By combining **demographics, usage behavior, financial history, support interactions, and engagement metrics**, the dataset helps
machine learning models identify patterns that signal churn risk.
""")
