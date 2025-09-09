import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

# STREAMLIT DASHBOARD

def load_data():
    file_path = "/mnt/data/Cleaned_Trade_and_Custom.xlsx"
    return pd.read_excel(file_path)

def main():
    st.set_page_config(page_title="Trade & Customs EDA", layout="wide")
    st.title("Trade & Customs Exploratory Data Analysis")

    df = load_data()

    # Sidebar filters
    st.sidebar.header("Filters")
    selected_year = st.sidebar.selectbox("Select Year", options=sorted(df['Receipt Date'].dt.year.unique()))
    df_filtered = df[df['Receipt Date'].dt.year == selected_year]

    # ============================
    # DESCRIPTIVE ANALYSIS
    # ============================
    st.subheader("Descriptive Insights")

    imports_by_hs = df_filtered.groupby("HS Code")["CIF Value (N)"].sum().sort_values(ascending=False)
    origin = df_filtered.groupby("Country of Origin")["CIF Value (N)"].sum().sort_values(ascending=False)
    supply = df_filtered.groupby("Country of Supply")["CIF Value (N)"].sum().sort_values(ascending=False)
    tax_by_hs = df_filtered.groupby("HS Code")["Total Tax(N)"].sum().sort_values(ascending=False)
    importers = df_filtered.groupby("Importer")["CIF Value (N)"].sum().sort_values(ascending=False)

    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Import Value (₦)", f"{df_filtered['CIF Value (N)'].sum():,}")
    col2.metric("Total Tax Revenue (₦)", f"{df_filtered['Total Tax(N)'].sum():,}")
    col3.metric("Average Import Value (₦)", f"{df_filtered['CIF Value (N)'].mean():,.0f}")
    col4.metric("Number of Countries of Origin", f"{df_filtered['Country of Origin'].nunique():,}")

    # ============================
    # VISUALIZATIONS
    # ============================
    st.subheader("Visualizations")

    # 1. Top HS Codes by Import Value
    st.markdown("### Top 10 HS Codes by Import Value")
    fig, ax = plt.subplots(figsize=(10,6))
    sns.barplot(x=imports_by_hs.head(10).index.astype(str), y=imports_by_hs.head(10).values, ax=ax, palette="Blues_d")
    ax.set_xlabel("HS Code")
    ax.set_ylabel("Total Import Value (₦)")
    ax.set_title("Top 10 HS Codes by Import Value")
    plt.xticks(rotation=45)
    st.pyplot(fig)

    # 2. Top Countries of Origin
    st.markdown("### Top 10 Countries of Origin")
    fig, ax = plt.subplots(figsize=(10,6))
    sns.barplot(x=origin.head(10).index, y=origin.head(10).values, ax=ax, palette="Greens_d")
    ax.set_xlabel("Country of Origin")
    ax.set_ylabel("Total Import Value (₦)")
    ax.set_title("Top 10 Countries of Origin")
    plt.xticks(rotation=45)
    st.pyplot(fig)

    # 3. Top Countries of Supply
    st.markdown("### Top 10 Countries of Supply")
    fig, ax = plt.subplots(figsize=(10,6))
    sns.barplot(x=supply.head(10).index, y=supply.head(10).values, ax=ax, palette="Purples_d")
    ax.set_xlabel("Country of Supply")
    ax.set_ylabel("Total Import Value (₦)")
    ax.set_title("Top 10 Countries of Supply")
    plt.xticks(rotation=45)
    st.pyplot(fig)

    # 4. Top HS Codes by Tax Revenue
    st.markdown("### Top 10 HS Codes by Tax Revenue")
    fig, ax = plt.subplots(figsize=(10,6))
    sns.barplot(x=tax_by_hs.head(10).index.astype(str), y=tax_by_hs.head(10).values, ax=ax, palette="Oranges_d")
    ax.set_xlabel("HS Code")
    ax.set_ylabel("Total Tax Revenue (₦)")
    ax.set_title("Top 10 HS Codes by Tax Revenue")
    plt.xticks(rotation=45)
    st.pyplot(fig)

    # 5. Top Importers by Import Value
    st.markdown("### Top 10 Importers by Import Value")
    fig, ax = plt.subplots(figsize=(10,6))
    sns.barplot(x=importers.head(10).index.astype(str), y=importers.head(10).values, ax=ax, palette="Reds_d")
    ax.set_xlabel("Importer")
    ax.set_ylabel("Total Import Value (₦)")
    ax.set_title("Top 10 Importers by Import Value")
    plt.xticks(rotation=45)
    st.pyplot(fig)

if __name__ == "__main__":
    main()
