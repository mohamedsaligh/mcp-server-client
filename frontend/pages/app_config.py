# file: pages/config.py

import streamlit as st
import requests

# --- Helper to handle rerun-success messages ---
def rerun_with_success(flag_name: str, message: str):
    if st.session_state.get(flag_name):
        st.success(message)
        del st.session_state[flag_name]

def set_success_and_rerun(flag_name: str):
    st.session_state[flag_name] = True
    st.rerun()

# --- Streamlit Page Config ---
st.set_page_config(page_title="🛠️ MCP Configurations", layout="wide")

# --- Backend Base URL ---
BACKEND_URL = "http://localhost:8000/api"

# --- Sidebar Menu ---
with st.sidebar:
    st.title("📋 Menu")
    st.page_link("main.py", label=" 💬 ChatBot")
    st.page_link("pages/app_config.py", label=" 🛠️ LLM Config")
    st.page_link("pages/mcp_config.py", label=" 🖥️ MCP Servers")
    st.page_link("pages/prompt_config.py", label=" 🗂 Prompt Config")
    st.divider()

# --- Main Title ---
st.subheader("🛠️ LLM Configuration Management")
st.divider()

# --- Show success messages after rerun if needed ---
rerun_with_success("openai_key_added", "✅ LLM API key added successfully!")
rerun_with_success("openai_key_saved", "✅ LLM API key saved successfully!")
rerun_with_success("openai_key_delete", "✅ LLM API key deleted successfully!")

# --- Section: OpenAI Key Setup ---

# 1. Fetch Existing OpenAI Key
# st.markdown("##### 🔑 LLM API Key Management")

# --- Fetch existing LLM APIs ---
existing_llms = []
try:
    response = requests.get(f"{BACKEND_URL}/config/llms")
    if response.status_code == 200:
        existing_llms = response.json()
except Exception as e:
    st.error(f"Failed to fetch existing LLM APIs: {str(e)}")


# --- Add New or Update Existing ---
st.markdown("##### ➕ Add / Update LLM API")

llm_name = st.text_input("LLM Name", placeholder="e.g., OpenAI, Anthropic")
llm_key = st.text_input("LLM API Key", type="password", placeholder="sk-...")
base_url = st.text_input("LLM Base Url", placeholder="http://api.openai.com/v1/", value="http://api.openai.com/v1/")

if st.button("Save LLM API"):
    if llm_name and llm_key:
        payload = {"name": llm_name, "api_key": llm_key, "base_url": base_url}
        res = requests.post(f"{BACKEND_URL}/config/llms", json=payload)
        if res.status_code == 200:
            set_success_and_rerun("openai_key_added")
        else:
            st.error("Failed to save LLM API.")

st.divider()

# --- Show existing LLM APIs with edit/delete ---
st.markdown("##### 🔎 Existing LLM APIs")

edited_llm_id = None

for llm in existing_llms:
    with st.expander(f"🔑 {llm['name']}"):
        current_name = st.text_input(f"LLM Name ({llm['name']})", value=llm['name'], key=f"name_{llm['id']}")
        current_key = st.text_input(f"API Key ({llm['name']})", value=llm['api_key'], type="password", key=f"key_{llm['id']}")
        current_url = st.text_input(f"Base Url ({llm['name']})", value=llm['base_url'], key=f"url_{llm['id']}")

        col1, col2 = st.columns(2)

        with col1:
            if st.button(f"💾 Save Changes {llm['name']}", key=f"save_{llm['id']}"):
                payload = {"id": llm['id'], "name": current_name, "api_key": current_key, "base_url": current_url}
                res = requests.post(f"{BACKEND_URL}/config/llms", json=payload)
                if res.status_code == 200:
                    set_success_and_rerun("openai_key_saved")

        with col2:
            if st.button(f"❌ Delete {llm['name']}", key=f"delete_{llm['id']}"):
                res = requests.delete(f"{BACKEND_URL}/config/llms/{llm['id']}")
                if res.status_code == 200:
                    set_success_and_rerun("openai_key_delete")

