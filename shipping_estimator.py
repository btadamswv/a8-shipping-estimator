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

openai.api_key = api_key

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
def build_prompt(user_text, columns):
    return f"""
You are a shipping estimator assistant. Based on the user's question, extract the most likely:
- size_tier (e.g. Envelope, Small Box, Medium Box, Large Box, XL/Custom)
- weight_class (Light, Medium, Heavy, Very Heavy)
- service_tier (Domestic Ground, International Economy, etc.)
- to_country (destination country)

You are working with a shipping rate table with the following columns:
{', '.join(columns)}

Your answer should include:
1. A clear interpretation of the request
2. Estimated rate ranges from the table (low, high, average)
3. Clarifications if key info is missing

User's question:
\"\"\"
{user_text}
\"\"\"
"""

# === PROCESS & DISPLAY RESPONSE ===
if submitted and user_input:
    with st.spinner("Asking ChatGPT..."):
        try:
            prompt = build_prompt(user_input, df.columns.tolist())
            client = openai.OpenAI(api_key=api_key)

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
