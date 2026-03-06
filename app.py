import streamlit as st
from agent import ask_groq

st.set_page_config(
    page_title="BOTIC — IT Support Assistant",
    page_icon="🤖",
    layout="centered"
)

st.title("🤖 BOTIC")
st.caption("Agentic IT Support Assistant — Llama 3.3 70b via Groq")
st.divider()

# Session state
if "messages" not in st.session_state:
    st.session_state.messages = []      # for display
if "traces" not in st.session_state:
    st.session_state.traces = []        # for trace panels
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []  # for LLM memory

ICONS = {
    "Thought": "💡", "Action": "🔧", "Observation": "👀",
    "Safety": "🛡️", "Resolution": "✅", "Error": "❌"
}

def render_trace(trace_steps):
    with st.expander("🔍 Agent Trace — see full reasoning", expanded=False):
        if not trace_steps:
            st.caption("No trace steps recorded.")
            return
        for step in trace_steps:
            icon = ICONS.get(step["type"], "•")
            st.markdown(f"**{icon} {step['type']}** `+{step['elapsed_seconds']}s`")
            content = step["content"]
            if isinstance(content, dict):
                st.json(content)
            else:
                st.markdown(f"> {content}")
            st.divider()

# Display existing messages
for i, message in enumerate(st.session_state.messages):
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
    if message["role"] == "assistant":
        trace_index = i // 2
        if trace_index < len(st.session_state.traces):
            render_trace(st.session_state.traces[trace_index])

# Input
user_input = st.chat_input("Describe your IT incident...")

if user_input:

    with st.chat_message("user"):
        st.markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("assistant"):
        with st.spinner("Investigating..."):
            # Pass chat history for memory
            result = ask_groq(user_input, st.session_state.chat_history)

        if isinstance(result, str):
            answer = result
            trace = []
        else:
            answer = result.get("answer") or "Something went wrong. Please try again."
            trace = result.get("trace", [])

        st.markdown(answer)
        render_trace(trace)

    st.session_state.messages.append({"role": "assistant", "content": answer})
    st.session_state.traces.append(trace)

    # Update LLM memory — store user + assistant exchange
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    st.session_state.chat_history.append({"role": "assistant", "content": answer})