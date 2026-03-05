import streamlit as st
from agent import ask_groq

st.set_page_config(
    page_title="BOTINIC — IT Support Assistant",
    page_icon="🤖",
    layout="centered"
)

st.title("🤖 BOTINIC")
st.caption("Agentic IT Support Assistant — powered by Llama 3.3")
st.divider()

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "traces" not in st.session_state:
    st.session_state.traces = []

# Icons for each trace step type
ICONS = {
    "Thought":     "💡",
    "Action":      "🔧",
    "Observation": "👀",
    "Safety":      "🛡️",
    "Resolution":  "✅",
    "Error":       "❌"
}

def render_trace(trace_steps):
    """Render the agent trace steps inside an expander."""
    with st.expander("🔍 Agent Trace — see full reasoning", expanded=False):
        for step in trace_steps:
            icon = ICONS.get(step["type"], "•")
            st.markdown(f"**{icon} {step['type']}** `{step['elapsed_seconds']}s`")

            content = step["content"]
            if isinstance(content, dict):
                st.json(content)
            else:
                st.markdown(f"> {content}")

            st.divider()

# Display existing chat messages and their traces
for i, message in enumerate(st.session_state.messages):
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

    # Show trace below each assistant message
    if message["role"] == "assistant" and i < len(st.session_state.traces):
        render_trace(st.session_state.traces[i // 2])

# Chat input
user_input = st.chat_input("Describe your IT incident...")

if user_input:

    # Show user message
    with st.chat_message("user"):
        st.markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Run agent and show response
    with st.chat_message("assistant"):
        with st.spinner("Investigating with tools..."):
            result = ask_groq(user_input)

        answer = result["answer"] or "Something went wrong. Please try again."
        trace  = result["trace"]

        st.markdown(answer)
        render_trace(trace)

    st.session_state.messages.append({"role": "assistant", "content": answer})
    st.session_state.traces.append(trace)