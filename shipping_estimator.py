import streamlit as st
import pandas as pd
import openai
import os

# === CONFIG ===
st.set_page_config(page_title="Shipping Rate Chat Estimator", layout="wide")
st.title("💬 Shipping Rate ChatBot")

# === Load data ===
df = pd.read_csv("shipping_rate_by_country.csv")
definitions = pd.read_csv("shipping_definitions_reference.csv")

# === OpenAI API Setup ===
openai.api_key = st.secrets.get("OPENAI_API_KEY") or st.text_input("🔑 Enter your OpenAI API key", type="password")

# === Define prompt template ===
def build_prompt(user_input):
    csv_columns = ", ".join(df.columns)
    return f"""
You are a shipping rate assistant. Based on user input, you will extract the most likely:

- size_tier (Envelope, Small Box, Medium Box, Large Box, XL/Custom)
- weight_class (Light, Medium, Heavy, Very Heavy)
- service_tier (Domestic Ground, International Economy, etc.)
- to_country (ISO country name from user input)

Then, search a structured shipping rate table with the following columns:
{csv_columns}

Return your output as:
1. A summary of your interpretation
2. The matching table rows (up to 5 rows max)

User input:
\"\"\"
{user_input}
\"\"\"
"""

# === Chat Interface ===
with st.form("chat"):
    user_query = st.text_area("Ask a shipping cost question:")
    submitted = st.form_submit_button("Estimate")

# === On submission, query GPT and return estimates ===
if submitted and openai.api_key and user_query:
    prompt = build_prompt(user_query)

    with st.spinner("Talking to ChatGPT..."):
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
        )

    gpt_reply = response['choices'][0]['message']['content']
    st.markdown("### 🤖 GPT Interpretation & Result")
    st.markdown(gpt_reply)
