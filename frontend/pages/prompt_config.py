import streamlit as st
import requests

def rerun_with_success(flag_name: str, message: str):
    if st.session_state.get(flag_name):
        st.success(message)
        del st.session_state[flag_name]

def set_success_and_rerun(flag_name: str):
    st.session_state[flag_name] = True
    st.rerun()

st.set_page_config(page_title="🛠️ Prompt Context Configurations", layout="wide")

BACKEND_URL = "http://localhost:8000/api"

with st.sidebar:
    st.title("📋 Menu")
    st.page_link("main.py", label=" 💬 ChatBot")
    st.page_link("pages/app_config.py", label=" 🛠️ LLM Config")
    st.page_link("pages/mcp_config.py", label=" 🖥️ MCP Servers")
    st.page_link("pages/prompt_config.py", label=" 🗂 Prompt Config")
    st.divider()

st.subheader("🗂 Prompt Context Management")
st.divider()

rerun_with_success("context_added", "✅ Prompt Context added successfully!")
rerun_with_success("context_saved", "✅ Prompt Context saved successfully!")
rerun_with_success("context_deleted", "✅ Prompt Context deleted successfully!")

# --- Fetch existing prompt contexts ---
existing_contexts = []
try:
    response = requests.get(f"{BACKEND_URL}/config/prompt_contexts")
    if response.status_code == 200:
        existing_contexts = response.json()
except Exception as e:
    st.error(f"Failed to fetch Prompt Contexts: {str(e)}")

# --- Add / Update ---
st.markdown("##### ➕ Add / Update Prompt Context")

ctx_name = st.text_input("Context Name")
ctx_desc = st.text_area("Description")
ctx_llm_id = st.text_input("LLM API ID (uuid)")
ctx_request_instruction = st.text_area("Request Instruction")
ctx_response_instruction = st.text_area("Response Instruction")

if st.button("Save Prompt Context"):
    if ctx_name:
        payload = {
            "name": ctx_name,
            "description": ctx_desc,
            "llm_api_id": ctx_llm_id,
            "request_instruction": ctx_request_instruction,
            "response_instruction": ctx_response_instruction
        }
        res = requests.post(f"{BACKEND_URL}/config/prompt_contexts", json=payload)
        if res.status_code == 200:
            set_success_and_rerun("context_added")
        else:
            st.error("Failed to save Prompt Context.")

st.divider()

# --- Existing contexts with edit/delete ---
st.markdown("##### 🔎 Existing Prompt Contexts")

for ctx in existing_contexts:
    with st.expander(f"📄 {ctx['name']}"):
        current_name = st.text_input("Name", value=ctx['name'], key=f"name_{ctx['id']}")
        current_desc = st.text_area("Description", value=ctx.get('description') or '', key=f"desc_{ctx['id']}")
        current_llm_id = st.text_input("LLM API ID", value=ctx.get('llm_api_id') or '', key=f"llm_{ctx['id']}")
        req_inst = st.text_area("Request Instruction", value=ctx.get('request_instruction') or '', key=f"req_{ctx['id']}")
        res_inst = st.text_area("Response Instruction", value=ctx.get('response_instruction') or '', key=f"res_{ctx['id']}")

        col1, col2 = st.columns(2)

        with col1:
            if st.button(f"💾 Save Changes {ctx['name']}", key=f"save_{ctx['id']}"):
                payload = {
                    "id": ctx['id'],
                    "name": current_name,
                    "description": current_desc,
                    "llm_api_id": current_llm_id,
                    "request_instruction": req_inst,
                    "response_instruction": res_inst
                }
                res = requests.post(f"{BACKEND_URL}/config/prompt_contexts", json=payload)
                if res.status_code == 200:
                    set_success_and_rerun("context_saved")

        with col2:
            if st.button(f"❌ Delete {ctx['name']}", key=f"delete_{ctx['id']}"):
                res = requests.delete(f"{BACKEND_URL}/config/prompt_contexts/{ctx['id']}")
                if res.status_code == 200:
                    set_success_and_rerun("context_deleted")
