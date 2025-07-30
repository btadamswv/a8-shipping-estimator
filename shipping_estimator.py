import streamlit as st
import pandas as pd
from openai import OpenAI

# === PAGE CONFIGURATION ===
st.set_page_config(page_title="Shipping Rate ChatBot", layout="wide")
st.title("💬 Shipping Rate ChatBot")

# === LOAD DATA ===
@st.cache_data
def load_data():
    rate_df = pd.read_csv("shipping_rate_by_country.csv")
    definitions_df = pd.read_csv("shipping_definitions_reference.csv")
    return rate_df, definitions_df

df, definitions = load_data()

# === OPENAI API KEY SETUP ===
api_key = st.secrets.get("OPENAI_API_KEY")  # For Streamlit Cloud
if not api_key:
    api_key = st.text_input("🔑 Enter your OpenAI API key", type="password")
if not api_key:
    st.warning("Please enter your OpenAI API key to continue.")
    st.stop()

client = OpenAI(api_key=api_key)

# === SHOW REFERENCE DEFINITIONS ===
with st.expander("📘 What do these terms mean?"):
    for category in definitions['Category'].unique():
        st.markdown(f"### {category}")
        for _, row in definitions[definitions['Category'] == category].iterrows():
            st.markdown(f"- **{row['Name']}**: {row['Definition']}")

st.divider()

# === USER INPUT ===
with st.form("chat_form"):
    user_input = st.text_area("Ask a shipping rate question (e.g. 'How much to ship a hoodie to Japan using economy?')", height=150)
    submitted = st.form_submit_button("Estimate")

# === BUILD PROMPT ===
def build_prompt(user_text):
    return f"""
You are a smart shipping estimator.

From the user's message, infer:
- product_type(s)
- shipping destination (country)
- whether it's domestic or international
- the most likely service types (e.g., ground, expedited, next-day)
- weight_class (Light, Medium, Heavy, Very Heavy)
- size_tier (Envelope, Small Box, Medium Box, Large Box, XL/Custom)

Return:
1. Your assumptions about product, destination, weight class, and size tier
2. A rate estimate table for all **relevant service tiers** matching domestic or international scope.
3. For each tier, show low, high, and average values using the existing shipping rate table.

Be concise and helpful.

User's question:
\"\"\"
{user_text}
\"\"\"
"""

# === PROCESS & DISPLAY RESPONSE ===
if submitted and user_input:
    with st.spinner("Asking ChatGPT..."):
        try:
            prompt = build_prompt(user_input)
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
            )
            answer = response.choices[0].message.content
            st.markdown("### 🤖 ChatGPT's Estimate")
            st.markdown(answer)
        except Exception as e:
            st.error(f"⚠️ Error calling OpenAI API: {e}")

# === OPTIONAL: Show Data (for debugging/testing)
with st.expander("📊 View Sample of Rate Table"):
    st.dataframe(df.sample(5))
