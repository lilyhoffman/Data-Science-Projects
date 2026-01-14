import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd

# Setting icon and tab label
st.set_page_config(page_title="Finances", page_icon="🌆")

# Show information:
st.write("# Your Personal Finances")
st.write("If there seem to be any discrepancies in your information, please email the team behind this page!")
st.write("We would be glad to help fix and bolster your experience on FinClad!")

# Try to get user info
customer_id = st.session_state.get('customer_id')
user = st.session_state.get('user_data')

if user:
    name_display = f"{user.get('firstName', '')} {user.get('lastName', '')}".strip()
    st.success(f"Welcome{',' if name_display else ''} {name_display}!")

    # Safely convert data to float
    def safe_float(value):
        try:
            return float(value)
        except:
            return 0.0

    user_data = {
        "Account Balance": safe_float(user.get("accountBalance", 0)),
        "Credit Limit": safe_float(user.get("creditLimit", 0)),
        "Credit Card Balance": safe_float(user.get("creditCardBalance", 0)),
    }

    # Create DataFrame
    user_df = pd.DataFrame(user_data.items(), columns=["Category", "Amount"])

    # Plot bar chart
    fig, ax = plt.subplots()
    sns.barplot(data=user_df, x="Category", y="Amount", ax=ax, palette="Blues_d")
    ax.set_title("Your Financial Summary")
    st.pyplot(fig)

    # Optional: show percentages
    user_df["Percentage"] = user_df["Amount"] / user_df["Amount"].sum() * 100

    # Show data table
    st.dataframe(user_df.set_index("Category"))

    # Optional: download CSV
    st.download_button(
        label="Download Summary as CSV",
        data=user_df.to_csv(index=False),
        file_name="financial_summary.csv",
        mime="text/csv"
    )

else:
    st.error("User data is missing. Please go to the Home page to enter your details or upload a CSV.")
