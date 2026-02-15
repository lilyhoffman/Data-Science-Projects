import streamlit as st
import pandas as pd

# Page config
st.set_page_config(page_title="Customer Churn Dashboard", layout="wide")
st.title("Customer Churn Dashboard")

# Load data
DATA_PATH = "data/customer_churn_business_dataset.csv"
df = pd.read_csv(DATA_PATH)

# Ensure churn is numeric & create label
if "churn" in df.columns:
    df["churn"] = pd.to_numeric(df["churn"], errors="coerce")
    df["churn_label"] = df["churn"].map({0: "No Churn", 1: "With Churn"}).fillna("Unknown")
else:
    st.error("Dataset must contain a 'churn' column.")
    st.stop()

# Sidebar filters
st.sidebar.header("Filters")
df_filt = df.copy()

def multiselect_filter(col_name: str):
    """Filter df_filt in-place by a multiselect sidebar widget if column exists."""
    global df_filt
    if col_name not in df_filt.columns:
        return
    vals = df_filt[col_name].dropna().unique().tolist()
    if not vals:
        return
    vals_sorted = sorted(vals, key=lambda x: str(x))
    picked = st.sidebar.multiselect(col_name.replace("_", " ").title(), vals_sorted)
    if picked:
        df_filt = df_filt[df_filt[col_name].isin(picked)]

# Common categorical filters
for c in ["customer_segment", "country", "contract_type", "signup_channel", "payment_method", "gender", "city"]:
    multiselect_filter(c)

# Age range filter
if "age" in df_filt.columns and pd.api.types.is_numeric_dtype(df_filt["age"]):
    a_min = int(df_filt["age"].dropna().min()) if df_filt["age"].dropna().size else 0
    a_max = int(df_filt["age"].dropna().max()) if df_filt["age"].dropna().size else 0
    if a_max >= a_min:
        lo, hi = st.sidebar.slider("Age range", a_min, a_max, (a_min, a_max))
        df_filt = df_filt[df_filt["age"].between(lo, hi)]

st.sidebar.caption(f"Showing **{len(df_filt):,}** of **{len(df):,}** rows")

# Helpers
def safe_mean(col: str):
    return df_filt[col].mean() if col in df_filt.columns and pd.api.types.is_numeric_dtype(df_filt[col]) else None

# Tabs
tab1, tab2, tab3 = st.tabs(["Overview", "Churn Analysis", "Raw Data"])

# TAB 1: Overview (KPIs)
with tab1:
    st.subheader("Key Metrics")

    metrics = [
        ("Total Customers", f"{df_filt.shape[0]:,}"),
        ("Churn Rate", f"{df_filt['churn'].mean():.2%}" if "churn" in df_filt.columns else "—"),
    ]

    m = safe_mean("csat_score")
    metrics.append(("Avg CSAT", f"{m:.2f}" if m is not None else "—"))

    m = safe_mean("escalations")
    metrics.append(("Avg Escalations", f"{m:.2f}" if m is not None else "—"))

    m = safe_mean("avg_session_time")
    metrics.append(("Avg Session Time", f"{m:.2f}" if m is not None else "—"))

    m = safe_mean("age")
    metrics.append(("Avg Age", f"{m:.2f}" if m is not None else "—"))

    cols = st.columns(3)
    for i, (label, value) in enumerate(metrics):
        with cols[i % 3]:
            st.metric(label, value)

    st.divider()
    st.subheader("Quick Snapshot")

    if "churn_label" in df_filt.columns:
        churn_counts = df_filt["churn_label"].value_counts()
        st.write("Churn label distribution")
        st.bar_chart(churn_counts)

# TAB 2: Churn Analysis
with tab2:
    st.subheader("Churn by Feature (Counts)")

    exclude = {"customer_id", "churn", "churn_label"}
    choices = [c for c in df_filt.columns if c not in exclude]

    if choices:
        col_counts = st.selectbox(
            "Select a column to see churn distribution (counts):",
            choices,
            key="counts_feature"
        )
        grouped = df_filt.groupby([col_counts, "churn_label"]).size().unstack(fill_value=0)
        st.bar_chart(grouped)
    else:
        st.info("No columns available for churn distribution (besides excluded ones).")

    st.divider()
    st.subheader("Churn Rate by Feature (Percent)")

    if choices:
        col_rate = st.selectbox(
            "Select a column to see churn rate (%):",
            choices,
            key="rate_feature"
        )
        tmp = df_filt[[col_rate, "churn"]].dropna()
        if len(tmp) == 0:
            st.info("No non-missing rows for this feature.")
        else:
            rate = tmp.groupby(col_rate)["churn"].mean().sort_values(ascending=False)
            st.bar_chart(rate)
            st.caption("Bars show churn percentage within each group.")
    else:
        st.info("No columns available for churn rate.")

    st.divider()
    st.subheader("Highest-risk groups (table)")

    # Choose categorical-ish columns for risk table
    cat_cols = df_filt.select_dtypes(exclude="number").columns.tolist()
    cat_cols = [c for c in cat_cols if c not in ["churn_label"]]
    if cat_cols:
        risk_feature = st.selectbox("Choose a categorical feature:", cat_cols, key="risk_feature")
        grp = (df_filt.groupby(risk_feature)["churn"]
               .agg(churn_rate="mean", customers="size")
               .reset_index()
               .sort_values(["churn_rate", "customers"], ascending=[False, False]))
        min_n = st.slider("Min group size", 5, 200, 25, step=5, key="min_group_size")
        grp = grp[grp["customers"] >= min_n]
        st.dataframe(grp.head(25), hide_index=True, use_container_width=True)
    else:
        st.info("No categorical columns found for risk table.")

# TAB 3: Raw Data Explorer
with tab3:
    st.subheader("Raw Dataset Explorer")

    CATEGORIES = {
        "Customer Profile": [
            "customer_id", "gender", "age", "country", "city", "customer_segment",
            "tenure_months", "signup_channel", "contract_type"
        ],
        "Product Usage": [
            "monthly_logins", "weekly_active_days", "avg_session_time",
            "features_used", "usage_growth_rate", "last_login_days_ago"
        ],
        "Customer Support": [
            "support_tickets", "avg_resolution_time", "complaint_type",
            "csat_score", "escalations", "survey_response"
        ],
        "Marketing & Loyalty": [
            "email_open_rate", "marketing_click_rate", "nps_score",
            "referral_count", "discount_applied"
        ],
        "Billing & Payment": [
            "monthly_fee", "total_revenue", "payment_method",
            "payment_failures", "price_increase_last_3m"
        ],
        "Churn": ["churn", "churn_label"],
    }

    # Build "All" from the filtered df columns
    CATEGORIES["All"] = list(df_filt.columns)

    option = st.selectbox("Select a category to explore:", list(CATEGORIES.keys()), key="raw_category")

    requested_cols = CATEGORIES[option]
    existing_cols = [c for c in requested_cols if c in df_filt.columns]
    missing_cols = [c for c in requested_cols if c not in df_filt.columns]

    if missing_cols and option != "All":
        st.warning(f"Missing columns in dataset (skipped): {', '.join(missing_cols)}")

    if not existing_cols:
        st.error("No columns from this category exist in the dataset.")
        st.stop()

    # Search & row count
    left, right = st.columns([2, 1])
    with left:
        search = st.text_input("Search (keeps rows where any selected cell contains this text):", key="raw_search")
    with right:
        n_rows = st.number_input("Rows to show", min_value=10, max_value=min(5000, len(df_filt)), value=100, step=10)

    view_df = df_filt[existing_cols].copy()

    # Filter by search
    if search.strip():
        s = search.strip().lower()
        mask = view_df.astype(str).apply(lambda col: col.str.lower().str.contains(s, na=False))
        view_df = view_df[mask.any(axis=1)]

    # Missingness summary
    miss = view_df.isna().mean().sort_values(ascending=False)
    with st.expander("Missingness summary (selected columns)"):
        st.dataframe(miss.rename("missing_pct").to_frame(), use_container_width=True)

    # Sorting
    sort_col = st.selectbox("Sort by:", existing_cols, key="raw_sort_col")
    ascending = st.checkbox("Ascending", value=True, key="raw_sort_asc")
    view_df = view_df.sort_values(sort_col, ascending=ascending)

    # Download filtered view
    csv = view_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Download current view as CSV",
        csv,
        file_name="filtered_customers.csv",
        mime="text/csv",
        key="download_csv"
    )

    st.dataframe(view_df.head(int(n_rows)), hide_index=True, use_container_width=True)
