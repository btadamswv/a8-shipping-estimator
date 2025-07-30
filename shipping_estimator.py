import streamlit as st
import pandas as pd
import openai

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

client = openai.OpenAI(api_key=api_key)

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
    size_tier = st.selectbox("Select a package size (if known):", ["Not specified", "Envelope", "Small Box", "Medium Box", "Large Box", "XL/Custom"])
    submitted = st.form_submit_button("Estimate")

# === PROMPT BUILDING ===
def build_prompt(user_text):
    return f"""
You are a smart shipping estimator.

1. From the user's message, infer:
   - product_type(s)
   - shipping destination (country)
   - whether it's domestic or international
   - the most likely service types (e.g., ground, expedited, next-day)
   - and weight_class (Light, Medium, Heavy, Very Heavy)

2. Return:
   - your assumptions about product, destination, and class
   - a summary of rates by matching size_tier, weight_class, country, and service_tier scope (domestic or international)
   - include a rate table (min, max, average) for all applicable service tiers based on the user's request

User's question:
"""
{user_text}
"""
"""

# === RESPONSE PROCESSING ===
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
            st.error(f"\u26a0\ufe0f Error calling OpenAI API: {e}")

# === OPTIONAL: Show Data ===
with st.expander("📊 View Sample of Rate Table"):
    st.dataframe(df.sample(5))
