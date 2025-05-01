# file: pages/chatbot.py

import streamlit as st
import requests
import sseclient
import uuid
import json

# --- Streamlit Page Config ---
st.set_page_config(page_title="💬 MCP Host", layout="wide")

# --- Backend Base URL ---
BACKEND_URL = "http://localhost:8000/api/chat"

# --- Session State Initialization ---
if "selected_session_id" not in st.session_state:
    st.session_state.selected_session_id = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# --- Helper functions ---
def fetch_sessions():
    try:
        res = requests.get(f"{BACKEND_URL}/all")
        if res.status_code == 200:
            return res.json()
    except Exception:
        return []
    return []

def fetch_chat_history(session_id):
    try:
        res = requests.get(f"{BACKEND_URL}/{session_id}")
        if res.status_code == 200:
            chats = res.json()
            print(">> chats:", chats)
            return [(chat["user_prompt"], chat["steps"], chat["final_answer"]) for chat in chats]
    except Exception:
        return []
    return []

def switch_session(sess_id):
    st.session_state.selected_session_id = sess_id
    st.session_state.chat_history = fetch_chat_history(sess_id)
    print(">> switch_session - session_id:", st.session_state.selected_session_id)
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

    for idx, session in enumerate(sessions):
        label = session["session_title"][:22] + "..." if len(session["session_title"]) > 25 else session["session_title"]
        unique_key = f"{session['session_id']}_{idx}"  # Ensure the key is unique
        if st.button(label, key=unique_key, use_container_width=True):
            st.session_state.selected_session_id = session["session_id"]
            st.session_state.chat_history = fetch_chat_history(session["session_id"])
            st.rerun()


# --- Main Area ---
st.markdown("### 💬 MCP Calculator")

if not st.session_state.selected_session_id:
    st.info("Please start a new chat or select from history.")
    st.stop()

prompt = st.chat_input("Type your request...") # , accept_file=True)

if prompt:
    progress_box = st.empty()

    payload = {
        "prompt": prompt,
        "session_id": st.session_state.selected_session_id
    }

    with st.spinner("Sending your prompt..."):
        try:
            response = requests.post(f"{BACKEND_URL}/stream", json=payload, stream=True)
            client = sseclient.SSEClient(response)

            steps_collected = []
            requests_collected = []
            final_answer = ""

            for event in client.events():
                if event.event == "status":
                    progress_box.info(event.data)
                elif event.event == "error":
                    progress_box.error(event.data)
                elif event.event == "result":
                    result_data = json.loads(event.data)
                    print("SSE Final Result:", result_data)
                    steps_collected = result_data.get("steps", [])
                    final_answer = result_data.get("final_answer", "")
        except Exception as e:
            st.error(f"Failed: {str(e)}")

    # Save the new chat step into history
    st.session_state.chat_history.append((prompt, steps_collected, final_answer))
    st.rerun()


# --- Display Chat History ---
for idx, (prompt_text, steps, final_answer) in enumerate(st.session_state.chat_history):
    with st.container(border=True):
        st.chat_message("user").write(prompt_text)
        with st.chat_message("assistant"):
            if steps:
                st.markdown("**Assistant Response:**")
                for step_idx, step in enumerate(steps, start=1):
                    with st.expander(f"Step {step_idx}: {step['server_name']}", expanded=False):
                        st.markdown("> **Request:**")
                        st.code(step['request'], language="json")
                        st.markdown("> **Response:**")
                        st.code(step['response'], language="json")
            if final_answer:
                if any(keyword in final_answer.lower() for keyword in ["error", "fail", "exception"]):
                    st.error(f"❌ **Error:** {final_answer}")
                else:
                    st.success(f"💬 **Final Answer:** {final_answer}")

