# file: frontend_app.py

import streamlit as st
import sseclient
import requests
import uuid
import json

# --- Streamlit Page Config ---
st.set_page_config(page_title="MCP Host", layout="wide")

# --- Backend Base URL ---
BACKEND_URL = "http://localhost:8000"

# --- Session State Initialization ---
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "selected_mcp_servers" not in st.session_state:
    st.session_state.selected_mcp_servers = []
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# --- Sidebar ---
with st.sidebar:
    st.title("⚙️ Configuration")

    # OpenAI API Key setup
    openai_api_key = st.text_input("🔑 OpenAI API Key", type="password")
    if st.button("Set OpenAI Key"):
        if openai_api_key:
            res = requests.post(f"{BACKEND_URL}/config/openai", params={"api_key": openai_api_key})
            if res.status_code == 200:
                st.success("OpenAI API key set successfully.")
            else:
                st.error("Failed to set OpenAI key.")

    st.divider()

    # MCP Servers
    st.subheader("MCP Servers")
    mcp_name = st.text_input("MCP Server Name", value="Area Calculator")
    mcp_url = st.text_input("MCP Server URL (http://localhost:8001, etc.)", value="http://localhost:8002")
    if st.button("Add MCP Server"):
        if mcp_name and mcp_url:
            res = requests.post(f"{BACKEND_URL}/config/mcp_server", json={"name": mcp_name, "base_url": mcp_url})
            if res.status_code == 200:
                st.success("MCP server added.")
            else:
                st.error("Failed to add MCP server.")

    st.divider()

    # MCP Server Selection
    st.subheader("Select MCP Servers")
    mcp_servers = requests.get(f"{BACKEND_URL}/config/mcp_servers").json()
    server_options = {server["name"]: server["mcp_id"] for server in mcp_servers}

    selected_servers = st.multiselect("Choose Servers", options=list(server_options.keys()))
    st.session_state.selected_mcp_servers = [server_options[name] for name in selected_servers]

# --- Main Area ---
st.title("💬 MCP Host - Interactive Chat")

prompt = st.chat_input("Type your request...")

if prompt:
    progress_box = st.empty()
    chat_box = st.empty()

    # Append early
    st.session_state.chat_history.append((prompt, [], ""))

    payload = {
        "prompt": prompt,
        "session_id": st.session_state.session_id,
        "selected_mcp_ids": st.session_state.selected_mcp_servers
    }

    with st.spinner("Sending your prompt..."):
        try:
            response = requests.post(f"{BACKEND_URL}/process_prompt", json=payload, stream=True)
            client = sseclient.SSEClient(response)

            steps_collected = []
            final_answer = ""

            for event in client.events():
                if event.event == "status":
                    progress_box.info(event.data)
                elif event.event == "error":
                    progress_box.error(event.data)
                elif event.event == "result":
                    result_data = json.loads(event.data)
                    steps_collected = result_data.get("steps", [])
                    final_answer = result_data.get("final_answer", "")
        except Exception as e:
            st.error(f"Failed: {str(e)}")

    # Save final result after processing
    st.session_state.chat_history[-1] = (prompt, steps_collected, final_answer)
    progress_box.empty()

# --- Display Chat History (unchanged)
for idx, (prompt_text, steps, final_answer) in enumerate(st.session_state.chat_history):
    with st.container():
        st.chat_message("user").write(prompt_text)
        st.chat_message("assistant").markdown(f"**Steps:**")
        for step in steps:
            with st.container(border=True):
                st.markdown(f"**Server**: {step['server_name']}")
                st.markdown(f"🔹 **Request**: `{step['request']}`")
                st.markdown(f"🔹 **Response**: `{step['response']}`")
        st.chat_message("assistant").markdown(f"💬 **Final Answer:** {final_answer}")



