"""Student Services Agent — Production Streamlit Thin Client with Cognito Auth.

Chat interface behind Cognito login that sends prompts to the StudentServicesAgent
runtime on AgentCore via SigV4-signed HTTP POST. Displays the configured model ID
from SSM as read-only sidebar information.

Run with:
    streamlit run app.py --server.port=8501 --server.address=0.0.0.0
"""

import boto3
import streamlit as st

import agent_client
import cognito_client
from config_file import Config

# --- Page Configuration ---
st.set_page_config(
    page_title="Student Services Agent",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Cognito Authentication ---
authenticator = cognito_client.get_authenticator(
    Config.SECRETS_MANAGER_ID, Config.DEPLOYMENT_REGION
)
is_logged_in = authenticator.login()
if not is_logged_in:
    st.stop()

# --- Main App (only shown after authentication) ---
st.title("🎓 Student Services Agent")
st.write("Ask about courses, register for classes, get loan predictions, or solve math problems.")

# --- Validate Configuration ---
errors = agent_client.get_config_errors()
if errors:
    st.error(f"Missing required environment variables: {', '.join(errors)}")
    st.stop()

# --- Sidebar ---
with st.sidebar:
    # User info and logout
    st.text(f"Welcome,\n{authenticator.get_username()}")
    st.button("Logout", "logout_btn", on_click=authenticator.logout)

    st.markdown("---")

    # Model Selection (read-only — configured via SSM)
    st.header("🤖 Model Selection")
    try:
        ssm = boto3.client("ssm", region_name=Config.DEPLOYMENT_REGION)
        param = ssm.get_parameter(Name="/student-services/model-id")
        model_id = param["Parameter"]["Value"]
    except Exception:
        model_id = "(unable to read from SSM)"
    st.text_input("Active Model:", value=model_id, disabled=True)
    st.caption(
        "In Phase 3, model selection is managed centrally via SSM Parameter Store. "
        "To change the model for all agents, an administrator updates the "
        "`/student-services/model-id` parameter in AWS Systems Manager. "
        "The change takes effect on the next new session."
    )

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

    # Configuration Details
    st.header("🔍 Configuration")
    with st.expander("Details", expanded=False):
        st.code(f"model_id: {model_id}")
        st.code(f"region: {Config.DEPLOYMENT_REGION}")
        st.code(f"stack: {Config.STACK_NAME}")

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
                    response = agent_client.invoke(prompt)
                except Exception as e:
                    response = f"⚠️ Error: {e}"

            st.markdown(response)

        st.session_state.messages.append({"role": "assistant", "content": response})
