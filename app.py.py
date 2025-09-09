import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Configure Streamlit page
st.set_page_config(
    page_title="Trade & Customs Exploratory Data Analysis",
    layout="wide"
)

# ===============================
# Load Data Function
# ===============================
@st.cache_data
def load_data(file_path="cleaned_trade_custom.xlsx"):
    try:
        df = pd.read_excel(file_path)
    except FileNotFoundError:
        st.error(f"Could not find {file_path}. Please upload the dataset below.")
        df = pd.DataFrame()
    return df

# Sidebar uploader (for presentation flexibility)
uploaded_file = st.sidebar.file_uploader("Upload your Excel dataset", type=["xlsx"])

if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)
    st.success("Custom dataset uploaded successfully.")
else:
    df = load_data()

# ===============================
# App Title
# ===============================
st.title("Trade & Customs Exploratory Data Analysis")

# Preview data
if not df.empty:
    st.subheader("Dataset Preview")
    st.dataframe(df.head())
    st.write("Available columns:", df.columns.tolist())
else:
    st.warning("No data available. Please upload a valid Excel file to continue.")

# Proceed only if dataframe is available
if not df.empty:

    # ===============================
    # High-Level Metrics
    # ===============================
    st.header("Key Metrics")

    total_imports = df["CIF Value (N)"].sum()
    total_tax = df["Total Tax(N)"].sum()
    unique_hs_codes = df["HS Code"].nunique()
    unique_countries_origin = df["Country of Origin"].nunique()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Imports (CIF Value)", f"₦{total_imports:,.0f}")
    col2.metric("Total Tax Revenue", f"₦{total_tax:,.0f}")
    col3.metric("Unique HS Codes", unique_hs_codes)
    col4.metric("Countries of Origin", unique_countries_origin)

    # ===============================
    # Charts
    # ===============================
    st.header("Exploratory Visualizations")

    # 1. Top HS Codes by Import Value
    st.subheader("Top HS Codes by Import Value (CIF)")
    top_hs = df.groupby("HS Code")["CIF Value (N)"].sum().sort_values(ascending=False).head(10)
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.barplot(x=top_hs.values, y=top_hs.index, ax=ax)
    ax.set_xlabel("CIF Value (₦)")
    ax.set_ylabel("HS Code")
    st.pyplot(fig)

    # 2. Top Countries of Origin
    st.subheader("Top Countries of Origin by Import Value")
    top_origin = df.groupby("Country of Origin")["CIF Value (N)"].sum().sort_values(ascending=False).head(10)
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.barplot(x=top_origin.values, y=top_origin.index, ax=ax, palette="Blues_r")
    ax.set_xlabel("CIF Value (₦)")
    ax.set_ylabel("Country of Origin")
    st.pyplot(fig)

    # 3. Top Countries of Supply
    st.subheader("Top Countries of Supply by Import Value")
    top_supply = df.groupby("Country of Supply")["CIF Value (N)"].sum().sort_values(ascending=False).head(10)
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.barplot(x=top_supply.values, y=top_supply.index, ax=ax, palette="Greens_r")
    ax.set_xlabel("CIF Value (₦)")
    ax.set_ylabel("Country of Supply")
    st.pyplot(fig)

    # 4. Tax Revenue by HS Code
    st.subheader("Top HS Codes by Tax Revenue")
    top_tax = df.groupby("HS Code")["Total Tax(N)"].sum().sort_values(ascending=False).head(10)
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.barplot(x=top_tax.values, y=top_tax.index, ax=ax, palette="Reds_r")
    ax.set_xlabel("Tax Revenue (₦)")
    ax.set_ylabel("HS Code")
    st.pyplot(fig)

    # 5. Top Importers by Import Value
    st.subheader("Top Importers by Import Value (CIF)")
    top_importers = df.groupby("Importer")["CIF Value (N)"].sum().sort_values(ascending=False).head(10)
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.barplot(x=top_importers.values, y=top_importers.index, ax=ax, palette="Purples_r")
    ax.set_xlabel("CIF Value (₦)")
    ax.set_ylabel("Importer")
    st.pyplot(fig)

    # ===============================
    # Closing Notes
    # ===============================
    st.markdown("---")
    st.markdown(
        """
        ### Summary
        - The analysis highlights top-performing HS Codes and countries driving import activity.  
        - Tax revenue contributions are concentrated in certain product categories.  
        - Importer distribution provides insight into market concentration and key trade actors.  

        This dashboard is designed to support decision-making in customs monitoring, 
        policy formulation, and trade facilitation strategies.
        """
    )
