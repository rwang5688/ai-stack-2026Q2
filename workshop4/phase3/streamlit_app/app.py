"""Student Services Agent — Local Streamlit Thin Client.

Chat interface that sends prompts to the StudentServicesAgent runtime on AgentCore
via SigV4-signed HTTP POST. Displays the configured model ID from SSM as read-only
sidebar information.

Run with:
    streamlit run app.py

Requires:
    STUDENT_SERVICES_AGENT_URL environment variable set to the runtime endpoint URL.
"""

import boto3
import streamlit as st

from agent_client import get_config_errors, invoke

# --- Page Configuration ---
st.set_page_config(
    page_title="Student Services Agent",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("🎓 Student Services Agent")
st.write("Ask about courses, register for classes, get loan predictions, or solve math problems.")

# --- Validate Configuration ---
errors = get_config_errors()
if errors:
    st.error(f"Missing required environment variables: {', '.join(errors)}")
    st.stop()

# --- Sidebar ---
with st.sidebar:
    # Model configuration display (read-only from SSM)
    st.header("⚙️ Configuration")
    try:
        ssm = boto3.client("ssm", region_name="us-west-2")
        param = ssm.get_parameter(Name="/student-services/model-id")
        model_id = param["Parameter"]["Value"]
    except Exception:
        model_id = "(unable to read from SSM)"
    st.text_input("Model ID (from SSM)", value=model_id, disabled=True)

    st.markdown("---")

    # Sample Prompts
    st.header("💡 Sample Prompts")

    st.markdown("**Course Registration:**")
    st.code("Register student STU001 for CS 441 in Fall 2026", language=None)

    st.markdown("**Course Reviews:**")
    st.code("What are the most challenging courses?", language=None)
    st.code("Find courses about artificial intelligence", language=None)
    st.code("Tell me about CS 441 Machine Learning", language=None)

    st.markdown("**Loan Prediction:**")
    st.code(
        "Will a person with these features accept the loan: "
        "`29,2,999,0,1,0,0.0,1.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,"
        "1.0,0.0,0.0,0.0,0.0,1.0,0.0,0.0,0.0,0.0,0.0,1.0,0.0,0.0,1.0,0.0,0.0,"
        "1.0,0.0,0.0,0.0,1.0,0.0,0.0,0.0,0.0,1.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,"
        "0.0,1.0,0.0,0.0,1.0,0.0`",
        language=None,
    )

    st.markdown("**Math Tutoring:**")
    st.code("Solve x^2 + 5x + 6 = 0", language=None)
    st.code("What is the derivative of x^3 + 2x?", language=None)

    st.markdown("---")

    # Clear Chat
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()

# --- Chat History ---
if "messages" not in st.session_state:
    st.session_state.messages = []

if not st.session_state.messages:
    st.info(
        "👋 Welcome! I can help with course information, registration, "
        "loan predictions, and math tutoring. Ask me anything!"
    )

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- Chat Input ---
if prompt := st.chat_input("Ask the Student Services Agent..."):
    if not prompt.strip():
        st.warning("Please enter a non-empty message.")
    else:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    response = invoke(prompt)
                except Exception as e:
                    response = f"⚠️ Error: {e}"

            st.markdown(response)

        st.session_state.messages.append({"role": "assistant", "content": response})
