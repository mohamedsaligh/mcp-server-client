import streamlit as st
import requests


def rerun_with_success(flag_name: str, message: str):
    if st.session_state.get(flag_name):
        st.success(message)
        del st.session_state[flag_name]

def set_success_and_rerun(flag_name: str):
    st.session_state[flag_name] = True
    st.rerun()

st.set_page_config(page_title="🖥️ MCP Server Management", layout="wide")

BACKEND_URL = "http://localhost:8000/api"

with st.sidebar:
    st.title("📋 Menu")
    st.page_link("main.py", label=" 💬 ChatBot")
    st.page_link("pages/app_config.py", label=" 🛠️ LLM Config")
    st.page_link("pages/mcp_config.py", label=" 🖥️ MCP Servers")
    st.page_link("pages/prompt_config.py", label=" 🗂 Prompt Contexts")
    st.divider()

st.subheader("🖥️ MCP Server Management")
st.divider()

rerun_with_success("mcp_added", "✅ MCP Server added successfully!")
rerun_with_success("mcp_saved", "✅ MCP Server updated successfully!")
rerun_with_success("mcp_deleted", "✅ MCP Server deleted successfully!")

# --- Fetch existing MCP Servers ---
existing_mcp_servers = []
try:
    response = requests.get(f"{BACKEND_URL}/config/mcp_servers")
    if response.status_code == 200:
        existing_mcp_servers = response.json()
except Exception as e:
    st.error(f"Failed to fetch MCP servers: {str(e)}")

# --- Add / Update ---
st.markdown("##### ➕ Add / Update MCP Server")

mcp_name = st.text_input("MCP Server Name")
mcp_keywords = st.text_input("Keywords (comma-separated)")
mcp_endpoint_url = st.text_input("Endpoint URL", placeholder="http://localhost:9001/process")


if st.button("Save MCP Server"):
    if mcp_name and mcp_endpoint_url:
        payload = {
            "name": mcp_name,
            "keywords": mcp_keywords,
            "endpoint_url": mcp_endpoint_url
        }
        res = requests.post(f"{BACKEND_URL}/config/mcp_servers", json=payload)
        if res.status_code == 200:
            set_success_and_rerun("mcp_added")
        else:
            st.error("Failed to save MCP Server.")

st.divider()

# --- Existing MCP Servers ---
st.markdown("##### 🔎 Existing MCP Servers")

if not existing_mcp_servers:
    st.info("No MCP Servers found. Please add a new one using the form above.")
else:
    for mcp in existing_mcp_servers:
        with st.expander(f"🖥️ {mcp['name']}"):
            current_name = st.text_input("Server Name", value=mcp['name'], key=f"name_{mcp['id']}")
            current_keywords = st.text_input("Keywords", value=mcp.get('keywords') or '', key=f"kw_{mcp['id']}")
            current_url = st.text_input("Endpoint URL", value=mcp['endpoint_url'], key=f"url_{mcp['id']}")

            col1, col2 = st.columns(2)

            with col1:
                if st.button(f"💾 Save Changes {mcp['name']}", key=f"save_{mcp['id']}"):
                    payload = {
                        "id": mcp['id'],
                        "name": current_name,
                        "keywords": current_keywords,
                        "endpoint_url": current_url
                    }
                    res = requests.post(f"{BACKEND_URL}/config/mcp_servers", json=payload)
                    if res.status_code == 200:
                        set_success_and_rerun("mcp_saved")

            with col2:
                if st.button(f"❌ Delete {mcp['name']}", key=f"delete_{mcp['id']}"):
                    res = requests.delete(f"{BACKEND_URL}/config/mcp_servers/{mcp['id']}")
                    if res.status_code == 200:
                        set_success_and_rerun("mcp_deleted")
