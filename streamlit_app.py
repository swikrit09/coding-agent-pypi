# streamlit_app.py
import os
import sys
import tempfile
import shutil
import traceback
from pathlib import Path
from dotenv import load_dotenv
import streamlit as st
from google import genai
from google.genai.types import Content, Part
from coding_agent.config import gemini_config
from coding_agent.functions.call_function import call_function

# ---------- helpers ----------
def _extract_text(response) -> str:
    """Return best-effort plain text from a response."""
    if getattr(response, "text", None):
        return response.text
    pieces = []
    for cand in (response.candidates or []):
        if not cand or not cand.content:
            continue
        for part in (cand.content.parts or []):
            if getattr(part, "text", None):
                pieces.append(part.text)
    return "\n".join(pieces).strip()

def make_client(api_key: str):
    return genai.Client(api_key=api_key)

def run_agent_loop(prompt: str, work_dir_path: str, client, max_iters: int = 20, verbose: bool = False, log_fn=print):
    """Run the agent loop and return final result + conversation as list of dicts."""
    messages = [Content(parts=[Part(text=prompt)], role="user")]
    conversation = [{"role": "user", "text": prompt}]

    for step in range(max_iters):
        if verbose:
            log_fn(f"[iter {step}] sending request...")

        response = client.models.generate_content(
            model="gemini-2.0-flash-001",
            contents=messages,
            config=gemini_config,
        )

        if response is None:
            log_fn("Response is None")
            return {"status": "error", "message": "Response is None", "conversation": conversation}

        if verbose and getattr(response, "usage_metadata", None):
            log_fn(f"[iter {step}] prompt_tokens={response.usage_metadata.prompt_token_count} "
                   f"resp_tokens={response.usage_metadata.candidates_token_count}")

        # keep model candidates in history
        if response.candidates:
            for cand in response.candidates:
                if cand and cand.content:
                    messages.append(cand.content)

        # if function calls
        if response.function_calls:
            tool_parts = []
            for fc in response.function_calls:
                # call user tool and append tool parts (call_function should return a Part-like object)
                part = call_function(fc.name, fc.args, work_dir_path, verbose)
                tool_parts.append(part)
                # log function call and returned part (if present)
                try:
                    fr = part.function_response.response
                except Exception:
                    fr = getattr(part, "text", str(part))
                conversation.append({"role": "tool", "name": fc.name, "args": fc.args, "result": fr})
                log_fn(f"Function call: {fc.name} -> {fr}")

            messages.append(Content(role="tool", parts=tool_parts))
            # continue loop to let the model consume tool outputs
            continue

        # no function calls -> final text
        final_text = _extract_text(response)
        if final_text:
            conversation.append({"role": "assistant", "text": final_text})
            log_fn("Assistant: " + final_text)
            return {"status": "ok", "text": final_text, "conversation": conversation}

    return {"status": "ok", "text": "", "conversation": conversation}

# ---------- Streamlit UI ----------
st.set_page_config(page_title="Coding Agent", layout="wide")

st.title("Coding Agent (GenAI) — Streamlit UI")
st.caption("Run prompts, view function/tool calls, and set a work directory from the UI.")

# Sidebar: settings
with st.sidebar:
    st.header("Settings")
    load_dotenv()  # load .env if present
    GEMINI_API_KEY = st.text_input("GEMINI_API_KEY (or set in .env)", value=os.getenv("GEMINI_API_KEY", ""), type="password")
    model = st.selectbox("Model", ["gemini-2.0-flash-001"], index=0)
    max_iters = st.number_input("Max iterations", min_value=1, max_value=100, value=20, step=1)
    verbose = st.checkbox("Verbose logs", value=False)
    st.markdown("---")
    st.write("Work dir selection (choose one)")
    # Base server folder to expose for browsing - configurable via env var
    BASE_WORK_DIR = Path(os.getenv("STREAMLIT_BASE_WORK_DIR", os.getcwd()))
    st.caption(f"Server browse base: `{BASE_WORK_DIR}` (set STREAMLIT_BASE_WORK_DIR to change)")

# Main area
prompt = st.text_area("Prompt", height=160, placeholder="Describe task for the coding agent...")
run_button = st.button("Run Prompt")

# Conversation and state
if "conversation" not in st.session_state:
    st.session_state.conversation = []
if "uploaded_tmp_dir" not in st.session_state:
    st.session_state.uploaded_tmp_dir = None

# --- WORK DIR SELECTION UI ---
st.subheader("Work Directory (from UI)")

# Method selection
method = st.radio("Select method", ("Upload files/folder (recommended)", "Browse server directories", "Enter path manually"))

selected_work_dir = None

if method == "Upload files/folder (recommended)":
    st.write("Upload files (multiple). Uploaded files will be saved into a temporary work directory and used for the run.")
    uploaded = st.file_uploader("Upload files", accept_multiple_files=True)
    if st.button("Save uploaded files to temp workdir"):
        if not uploaded:
            st.warning("No files selected to upload.")
        else:
            # create temp dir and save uploads
            tmpdir = Path(tempfile.mkdtemp(prefix="sca_agent_"))
            for f in uploaded:
                # preserve subfolders if file.name contains path separators (rare), otherwise flat
                target = tmpdir / Path(f.name).name
                with open(target, "wb") as out:
                    out.write(f.getbuffer())
            st.success(f"Saved {len(uploaded)} file(s) to temporary workdir: `{tmpdir}`")
            st.session_state.uploaded_tmp_dir = str(tmpdir)
            selected_work_dir = str(tmpdir)

    if st.session_state.uploaded_tmp_dir:
        st.info(f"Current temporary workdir: `{st.session_state.uploaded_tmp_dir}`")
        if st.button("Clear temporary uploaded workdir"):
            try:
                shutil.rmtree(st.session_state.uploaded_tmp_dir)
            except Exception as ex:
                st.warning(f"Could not remove temp dir: {ex}")
            st.session_state.uploaded_tmp_dir = None

elif method == "Browse server directories":
    st.write("Browse server-side directories under the configured base directory.")
    # list directories (non-recursive) under BASE_WORK_DIR
    try:
        dirs = [str(p) for p in sorted(BASE_WORK_DIR.iterdir()) if p.is_dir()]
    except Exception as e:
        st.error(f"Could not list base directory `{BASE_WORK_DIR}`: {e}")
        dirs = []

    if not dirs:
        st.info("No subdirectories found under the base. You can create them on the server or upload files instead.")
    else:
        chosen = st.selectbox("Choose directory", options=["-- none --"] + dirs, index=0)
        if chosen and chosen != "-- none --":
            st.success(f"Selected workdir: `{chosen}`")
            selected_work_dir = chosen

else:  # Enter path manually
    manual = st.text_input("Enter absolute work directory path", value=str(os.getcwd()))
    if manual:
        if Path(manual).exists() and Path(manual).is_dir():
            st.success(f"Using manual path: `{manual}`")
            selected_work_dir = manual
        else:
            st.warning("Path does not exist or is not a directory. Please create it on the server or use upload option.")

# Show final selected workdir
st.markdown("**Active work directory (used during run):**")
if selected_work_dir:
    st.code(selected_work_dir)
else:
    # if user previously uploaded, show that as default
    if st.session_state.uploaded_tmp_dir:
        st.code(st.session_state.uploaded_tmp_dir)
        selected_work_dir = st.session_state.uploaded_tmp_dir
    else:
        st.code("None selected (will default to current working directory)")

# logs area
log_placeholder = st.empty()
log_lines = []

def log_fn(msg):
    log_lines.append(str(msg))
    log_placeholder.code("\n".join(log_lines), language="text")

# Run
if run_button:
    if not GEMINI_API_KEY:
        st.error("GEMINI_API_KEY is required. Set it in the sidebar or in your .env file as GEMINI_API_KEY.")
    elif not prompt.strip():
        st.error("Please enter a prompt.")
    else:
        # decide final work_dir to pass
        work_dir_to_use = selected_work_dir or st.session_state.uploaded_tmp_dir or os.getcwd()

        # ensure it exists
        try:
            Path(work_dir_to_use).mkdir(parents=True, exist_ok=True)
        except Exception as e:
            st.error(f"Could not use workdir `{work_dir_to_use}`: {e}")
            work_dir_to_use = os.getcwd()
            st.info(f"Falling back to cwd: `{work_dir_to_use}`")

        try:
            client = make_client(GEMINI_API_KEY)
        except Exception as e:
            st.error(f"Failed to initialize client: {e}")
            st.exception(traceback.format_exc())
            client = None

        if client:
            # Clear logs
            log_lines.clear()
            log_placeholder.empty()
            with st.spinner("Running agent..."):
                result = run_agent_loop(prompt, work_dir_to_use, client, max_iters=max_iters, verbose=verbose, log_fn=log_fn)

            # Append conversation to session state
            if result.get("conversation"):
                st.session_state.conversation.extend(result["conversation"])

            # Show result panels
            if result.get("status") == "ok":
                st.success("Finished")
                st.subheader("Assistant Output")
                st.write(result.get("text", ""))

            else:
                st.error("Error: " + result.get("message", "unknown error"))

# Show conversation history with expandable items
st.subheader("Conversation History")
if st.session_state.conversation:
    for i, turn in enumerate(st.session_state.conversation):
        with st.expander(f"{i+1}. {turn.get('role', 'unknown').upper()}"):
            if turn.get("role") == "user":
                st.markdown(f"**User:** {turn.get('text')}")
            elif turn.get("role") == "assistant":
                st.markdown(f"**Assistant:** {turn.get('text')}")
            elif turn.get("role") == "tool":
                st.markdown(f"**Tool:** `{turn.get('name')}`")
                st.markdown("**Args:**")
                st.json(turn.get("args"))
                st.markdown("**Result:**")
                st.json(turn.get("result"))
            else:
                st.json(turn)
else:
    st.info("No conversation yet. Run a prompt above.")

# Footer: small controls
st.markdown("---")
if st.button("Clear conversation"):
    st.session_state.conversation = []
    log_placeholder.empty()
    st.experimental_rerun()
