# file: pages/chatbot.py

import streamlit as st
import requests
import sseclient
import uuid
import json

# --- Streamlit Page Config ---
st.set_page_config(page_title="💬 MCP Host", layout="wide")

# --- Backend Base URL ---
BACKEND_URL = "http://localhost:8000/api"

# --- Session State Initialization ---
if "selected_session_id" not in st.session_state:
    st.session_state.selected_session_id = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# --- Helper functions ---
def fetch_sessions():
    try:
        res = requests.get(f"{BACKEND_URL}/chat_sessions")
        if res.status_code == 200:
            return res.json()
    except Exception:
        return []
    return []

def fetch_chat_history(session_id):
    try:
        res = requests.get(f"{BACKEND_URL}/chat_history/{session_id}")
        if res.status_code == 200:
            chats = res.json()
            return [(chat["user_prompt"], chat["steps"], chat["final_answer"]) for chat in chats]
    except Exception:
        return []
    return []

def switch_session(sess_id):
    st.session_state.selected_session_id = sess_id
    st.session_state.chat_history = fetch_chat_history(sess_id)
    st.rerun()

# --- Sidebar ---
with st.sidebar:
    st.title("📋 Menu")
    st.page_link("main.py", label=" 💬 ChatBot")
    st.page_link("pages/app_config.py", label=" 🛠️ LLM Config")
    st.page_link("pages/mcp_config.py", label=" 🖥️ MCP Servers")
    st.page_link("pages/prompt_config.py", label=" 🗂 Prompt Config")
    st.write("---")

    st.title("🕑 History")
    sessions = fetch_sessions()

    if st.button("➕ New Chat", use_container_width=True):
        st.session_state.selected_session_id = str(uuid.uuid4())
        st.session_state.chat_history = []
        st.rerun()

    sessions = fetch_sessions()
    for session in sessions:
        label = session["session_title"][:22] + "..." if len(session["session_title"]) > 25 else session["session_title"]
        if st.button(label, key=session["session_id"], use_container_width=True):
            st.session_state.selected_session_id = session["session_id"]
            st.session_state.chat_history = fetch_chat_history(session["session_id"])
            st.rerun()


# --- Main Area ---
st.markdown("### 💬 MCP Calculator")

if not st.session_state.selected_session_id:
    st.info("Please start a new chat or select from history.")
    st.stop()

prompt = st.chat_input("Type your request...")

if prompt:
    progress_box = st.empty()

    payload = {
        "prompt": prompt,
        "session_id": st.session_state.selected_session_id
    }

    with st.spinner("Sending your prompt..."):
        try:
            response = requests.post(f"{BACKEND_URL}/prompt/stream", json=payload, stream=True)
            client = sseclient.SSEClient(response)

            steps_collected = []
            requests_collected = []
            final_answer = ""

            for event in client.events():
                if event.event == "status":
                    progress_box.info(event.data)
                elif event.event == "error":
                    progress_box.error(event.data)
                elif event.event == "steps":
                    try:
                        steps_collected = json.loads(event.data)
                        progress_box.info("✅ Received steps.")
                    except:
                        progress_box.warning("⚠️ Failed to parse steps JSON.")
                elif event.event == "requests":
                    try:
                        requests_collected = json.loads(event.data)
                        progress_box.info("✅ Received requests.")
                    except:
                        progress_box.warning("⚠️ Failed to parse requests JSON.")
                elif event.event == "result":
                    result_data = json.loads(event.data)
                    final_answer = result_data.get("final", "")
                    st.session_state.chat_history.append((prompt, steps_collected, final_answer))
                    progress_box.success("✅ Complete.")
                    break

        except Exception as e:
            st.error(f"Failed: {str(e)}")

    # Save the new chat step into history
    # st.session_state.chat_history.append((prompt, steps_collected, final_answer))
    st.rerun()
    # progress_box.empty()

# --- Display Chat History ---
for idx, (prompt_text, steps, final_answer) in enumerate(st.session_state.chat_history):
    with st.container(border=True):
        st.chat_message("user").write(prompt_text)
        with st.chat_message("assistant"):
            if steps:
                st.markdown("**Assistant Response:**")
                for step_idx, step in enumerate(steps, start=1):
                    with st.expander(f"Step {step_idx} - Server: {step['server_name']}", expanded=False):
                        st.markdown("> **Request:**")
                        st.code(step['request'], language="json")
                        st.markdown("> **Response:**")
                        st.code(step['response'], language="json")

                     # with st.expander(f"Step {step_idx} - Server: {step['server_name']}", expanded=False):
                    #     st.markdown("> **Request:**")
                    #     st.code(step['request'], language="json")
                    #     st.markdown("> **Response:**")
                    #     st.code(step['response'], language="json")

            if final_answer:
                st.success(f"💬 **Final Answer:** {final_answer}")
