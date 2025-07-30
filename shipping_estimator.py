import streamlit as st
import pandas as pd

# Load data
rate_df = pd.read_csv("shipping_rate_by_country.csv")
definitions_df = pd.read_csv("shipping_definitions_reference.csv")

st.set_page_config(page_title="Shipping Rate Estimator", layout="wide")
st.title("📦 Shipping Rate Estimator")

# Help/definitions
with st.expander("📘 What do these terms mean?"):
    for category in definitions_df['Category'].unique():
        st.markdown(f"### {category}")
        subset = definitions_df[definitions_df['Category'] == category]
        for _, row in subset.iterrows():
            st.markdown(f"**{row['Name']}**: {row['Definition']}")

st.divider()

# User inputs
col1, col2, col3, col4 = st.columns(4)
with col1:
    size = st.selectbox("Package Size", sorted(rate_df['size_tier'].unique()))
with col2:
    weight = st.selectbox("Weight Class", sorted(rate_df['weight_class'].unique()))
with col3:
    service = st.selectbox("Service Tier", sorted(rate_df['service_tier'].unique()))
with col4:
    country = st.selectbox("Destination Country", sorted(rate_df['to_country'].unique()))

# Filter and estimate
filtered = rate_df[
    (rate_df['size_tier'] == size) &
    (rate_df['weight_class'] == weight) &
    (rate_df['service_tier'] == service) &
    (rate_df['to_country'] == country)
]

st.divider()

# Result
st.subheader("Estimated Shipping Cost")
if not filtered.empty:
    row = filtered.iloc[0]
    st.success(f"""
    - 📦 **Package Size**: {size}  
    - ⚖️ **Weight Class**: {weight}  
    - 🚚 **Service Tier**: {service}  
    - 🌍 **To Country**: {country}

    ### 💰 Estimated Rate Range
    - **Low**: ${row['low_rate']}
    - **Average**: ${row['average_rate']}
    - **High**: ${row['high_rate']}
    """)
else:
    st.warning("No matching rate found for this combination. Try adjusting inputs.")
