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
BACKEND_URL = "http://localhost:8000"

# --- Sidebar Menu ---
with st.sidebar:
    st.title("📋 Menu")
    st.page_link("main.py", label=" 💬 ChatBot")
    st.page_link("pages/app_config.py", label=" 🛠️ LLM Config")
    st.page_link("pages/mcp_config.py", label=" 🖥️ MCP Servers")
    st.page_link("pages/prompt_config.py", label=" 🗂 Prompt Config")
    st.divider()

# --- Main Title ---
st.subheader("🖥️ MCP Server Management")
st.divider()
# --- Show success messages after rerun if needed ---
rerun_with_success("server_added_success", "✅ MCP server added successfully!")
rerun_with_success("server_deleted_success", "✅ MCP server deleted successfully!")

# --- Section: MCP Server Management ---
st.markdown("##### ➕ Add MCP Server")

with st.form("add_mcp_server_form"):
    mcp_name = st.text_input("Server Name", placeholder="Example: Area Calculator")
    mcp_url = st.text_input("Server URL", placeholder="Example: http://localhost:8001")
    submitted = st.form_submit_button("Add MCP Server")

    if submitted and mcp_name and mcp_url:
        res = requests.post(
            f"{BACKEND_URL}/config/mcp_server",
            json={"name": mcp_name, "base_url": mcp_url}
        )
        if res.status_code == 200:
            set_success_and_rerun("server_added_success")
        else:
            st.error("Failed to add MCP server.")

st.divider()

st.markdown("##### 🗑️ Existing MCP Servers")

try:
    mcp_servers = requests.get(f"{BACKEND_URL}/config/mcp_servers").json()

    if not mcp_servers:
        st.info("No MCP servers configured yet.")
    else:
        for server in mcp_servers:
            with st.container(border=True):
                col1, col2 = st.columns([24, 1])

                with col1:
                    st.markdown(f"**{server['name']}**  \n`{server['base_url']}`")

                with col2:
                    if st.button("❌", key=f"delete_{server['mcp_id']}"):
                        res = requests.delete(f"{BACKEND_URL}/config/mcp_server/{server['mcp_id']}")
                        if res.status_code == 200:
                            set_success_and_rerun("server_deleted_success")
                        else:
                            st.error(f"Failed to delete {server['name']}")
except Exception as e:
    st.error(f"Failed to fetch servers: {str(e)}")
