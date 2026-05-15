"""
Student Services Assistant — Streamlit Application

Multi-agent chat interface for the Student Services system.
Routes queries through an orchestrator agent to specialist agents.
Secured with Cognito authentication via Secrets Manager.
"""

import os
import sys

# Suppress OpenTelemetry context detach warnings (harmless in Streamlit's threading model)
os.environ["OTEL_SDK_DISABLED"] = "true"

# Bypass tool consent for all Strands tool operations
os.environ["BYPASS_TOOL_CONSENT"] = "true"

# Add this directory to path for sibling imports within docker_app
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st

from config_file import Config
from utils.auth import Auth
from config import clear_parameter_cache, get_all_config_values, get_model_config
from student_services_agent.agent import create_orchestrator


# --- Page Configuration ---
st.set_page_config(
    page_title="Student Services Assistant",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Cognito Authentication ---
# Read Cognito credentials from Secrets Manager and present login page
secrets_manager_id = Config.SECRETS_MANAGER_ID
region = Config.DEPLOYMENT_REGION

authenticator = Auth.get_authenticator(secrets_manager_id, region)
is_logged_in = authenticator.login()

if not is_logged_in:
    st.stop()

# --- Main App Content (only shown after successful authentication) ---
st.title("🎓 Student Services Assistant")
st.write("Ask about courses, register for classes, get loan predictions, or solve math problems.")

# --- Model Options ---
MODEL_OPTIONS = {
    "Amazon Nova 2 Lite (us.amazon.nova-2-lite-v1:0)": "us.amazon.nova-2-lite-v1:0",
    "Anthropic Claude Sonnet 4 (us.anthropic.claude-sonnet-4-6)": "us.anthropic.claude-sonnet-4-6",
}

# --- Sidebar ---
with st.sidebar:
    st.header("🤖 Model Selection")

    # Initialize session state
    if "selected_model" not in st.session_state:
        st.session_state.selected_model = list(MODEL_OPTIONS.keys())[0]

    selected_model_key = st.selectbox(
        "Choose Model:",
        options=list(MODEL_OPTIONS.keys()),
        index=list(MODEL_OPTIONS.keys()).index(st.session_state.selected_model),
        help="Select which model powers the agents",
    )

    # Detect model change
    if selected_model_key != st.session_state.selected_model:
        st.session_state.selected_model = selected_model_key
        # Force orchestrator recreation
        if "orchestrator" in st.session_state:
            del st.session_state["orchestrator"]

    st.info(f"**Active Model**: {MODEL_OPTIONS[selected_model_key]}")

    # Sample Questions
    st.header("💡 Sample Questions")
    st.markdown("**Course Registration:**")
    st.code("Register student STU001 for CS 441 in Fall 2026", language=None)

    st.markdown("**Course Reviews:**")
    st.code("What are the most challenging courses?", language=None)
    st.code("Find courses about artificial intelligence", language=None)
    st.code("Tell me about CS 441 Machine Learning", language=None)

    st.markdown("**Loan Prediction:**")
    st.code(
        'Will a person with these features accept the loan: `29,2,999,0,1,0,0.0,1.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,1.0,0.0,0.0,0.0,0.0,1.0,0.0,0.0,0.0,0.0,0.0,1.0,0.0,0.0,1.0,0.0,0.0,1.0,0.0,0.0,0.0,1.0,0.0,0.0,0.0,0.0,1.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,1.0,0.0,0.0,1.0,0.0`',
        language=None,
    )

    st.markdown("**Math Tutoring:**")
    st.code("Solve x^2 + 5x + 6 = 0", language=None)
    st.code("What is the derivative of x^3 + 2x?", language=None)

    # Debug Info
    st.header("🔍 Debug Info")
    with st.expander("Configuration Details", expanded=False):
        config_values = get_all_config_values()
        # Override model_id with the user's actual selection
        config_values["model_id"] = MODEL_OPTIONS[st.session_state.selected_model]
        for key, value in config_values.items():
            st.code(f"{key}: {value}")

    # Clear Cache button
    if st.button("🔄 Clear Cache"):
        clear_parameter_cache()
        if "orchestrator" in st.session_state:
            del st.session_state["orchestrator"]
        st.success("Cache cleared! Parameters will be refreshed.")

    # Clear Conversation button
    if st.button("🗑️ Clear Conversation"):
        st.session_state.messages = []
        st.rerun()


# --- Session State Initialization ---
if "messages" not in st.session_state:
    st.session_state.messages = []


# --- Orchestrator Creation ---
def get_orchestrator():
    """Get or create the orchestrator agent."""
    if "orchestrator" not in st.session_state:
        model_config = get_model_config()
        # Override model_id with user selection
        model_config["model_id"] = MODEL_OPTIONS[st.session_state.selected_model]
        st.session_state.orchestrator = create_orchestrator(model_config)
    return st.session_state.orchestrator


# --- Chat Display ---
if not st.session_state.messages:
    st.info(
        "👋 Welcome! I can help with course information, registration, "
        "loan predictions, and math tutoring. Ask me anything!"
    )

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- Chat Input ---
query = st.chat_input("Ask your question here...")

if query:
    # Filter empty/whitespace-only messages
    if not query.strip():
        st.warning("Please enter a non-empty message.")
    else:
        # Add user message
        st.session_state.messages.append({"role": "user", "content": query})
        with st.chat_message("user"):
            st.markdown(query)

        # Process with orchestrator
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    orchestrator = get_orchestrator()
                    response = orchestrator(query)
                    content = str(response)

                    if not content.strip():
                        content = (
                            "I wasn't able to generate a response. "
                            "Please try rephrasing your question."
                        )

                    # Detect which specialist was routed to from conversation history
                    routed_to = None
                    tool_display_names = {
                        "course_review_assistant": "Course Review Agent",
                        "course_registration_assistant": "Course Registration Agent",
                        "loan_offering_assistant": "Loan Application Agent",
                        "math_assistant": "Math Teaching Agent",
                    }
                    try:
                        for msg in orchestrator.messages:
                            if msg.get("role") == "assistant" and "content" in msg:
                                for block in msg["content"]:
                                    if "toolUse" in block:
                                        tool_name = block["toolUse"].get("name", "")
                                        if tool_name in tool_display_names:
                                            routed_to = tool_display_names[tool_name]
                    except Exception:
                        pass

                    if routed_to:
                        content = f"🔀 **Routed to: {routed_to}**\n\n{content}"

                except Exception as e:
                    error_detail = f"{type(e).__name__}: {str(e)}" if str(e) else type(e).__name__
                    content = (
                        f"⚠️ An error occurred while processing your request: {error_detail}\n\n"
                        "Please try again or rephrase your question."
                    )

            st.markdown(content)
            st.session_state.messages.append(
                {"role": "assistant", "content": content}
            )
