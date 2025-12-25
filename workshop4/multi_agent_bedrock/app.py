import streamlit as st
from strands import Agent
from strands.models import BedrockModel

# Import the specialized assistants
from computer_science_assistant import computer_science_assistant
from english_assistant import english_assistant
from language_assistant import language_assistant
from math_assistant import math_assistant
from no_expertise import general_assistant

# Define the teacher's assistant system prompt
TEACHER_SYSTEM_PROMPT = """
You are TeachAssist, a sophisticated educational orchestrator designed to coordinate educational support across multiple subjects. Your role is to:

1. Analyze incoming student queries and determine the most appropriate specialized agent to handle them:
   - Math Agent: For mathematical calculations, problems, and concepts
   - English Agent: For writing, grammar, literature, and composition
   - Language Agent: For translation and language-related queries
   - Computer Science Agent: For programming, algorithms, data structures, and code execution
   - General Assistant: For all other topics outside these specialized domains

2. Key Responsibilities:
   - Accurately classify student queries by subject area
   - Route requests to the appropriate specialized agent
   - Maintain context and coordinate multi-step problems
   - Ensure cohesive responses when multiple agents are needed

3. Decision Protocol:
   - If query involves calculations/numbers → Math Agent
   - If query involves writing/literature/grammar → English Agent
   - If query involves translation → Language Agent
   - If query involves programming/coding/algorithms/computer science → Computer Science Agent
   - If query is outside these specialized areas → General Assistant
   - For complex queries, coordinate multiple agents as needed

Always confirm your understanding before routing to ensure accurate assistance.
"""

# Set up the page
st.set_page_config(
    page_title="TeachAssist - Educational Assistant", 
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🎓 TeachAssist - Educational Assistant")
st.write("Ask a question in any subject area, and I'll route it to the appropriate specialist.")

# Display service and model information
st.info("🤖 **Powered by Amazon Bedrock** | Model: `us.amazon.nova-pro-v1:0` (Amazon Nova Pro)")

# Add sidebar with information
with st.sidebar:
    st.header("🤖 AI Service Details")
    st.markdown("""
    **Service**: Amazon Bedrock  
    **Model**: `us.amazon.nova-pro-v1:0`  
    **Foundation Model**: Amazon Nova Pro  
    **Temperature**: 0.3
    """)
    
    st.header("📚 Available Specialists")
    st.markdown("""
    - **🧮 Math Assistant**: Calculations, equations, mathematical concepts
    - **📝 English Assistant**: Writing, grammar, literature, composition
    - **🌍 Language Assistant**: Translation and language queries
    - **💻 Computer Science Assistant**: Programming, algorithms, code execution
    - **🎯 General Assistant**: All other topics
    """)
    
    st.header("💡 Sample Questions")
    st.markdown("""
    - "Solve the quadratic equation x^2 + 5x + 6 = 0"
    - "Write a Python function to check if a string is a palindrome"
    - "Translate 'Hello, how are you?' to Spanish"
    - "Help me improve this essay paragraph"
    - "What is the capital of France?"
    """)
    
    # Add clear conversation button
    if st.button("🗑️ Clear Conversation"):
        st.session_state.messages = []
        st.rerun()

# Initialize session state for conversation history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display conversation history or welcome message
if not st.session_state.messages:
    st.info("👋 Welcome! Ask me any question and I'll route it to the most appropriate specialist. Try asking about math, programming, writing, translations, or general knowledge!")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Initialize the teacher agent
@st.cache_resource
def get_teacher_agent():
    # Amazon Bedrock Model Configuration
    # Service: Amazon Bedrock
    # Model ID: us.amazon.nova-pro-v1:0 (Amazon Nova Pro foundation model)
    # Note: This can be replaced with cross-region inference profile IDs for multi-region deployments
    bedrock_model = BedrockModel(
        model_id="us.amazon.nova-pro-v1:0",  # Amazon Nova Pro via Amazon Bedrock
        temperature=0.3,
    )
    
    # Create the teacher agent with specialized tools
    return Agent(
        model=bedrock_model,
        system_prompt=TEACHER_SYSTEM_PROMPT,
        callback_handler=None,
        tools=[math_assistant, language_assistant, english_assistant, computer_science_assistant, general_assistant],
    )

# Get user input
query = st.chat_input("Ask your question here...")

if query:
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": query})
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(query)
    
    # Display assistant response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        
        try:
            # Get the teacher agent
            teacher_agent = get_teacher_agent()
            
            # Process the query
            with st.spinner("Thinking..."):
                response = teacher_agent(query)
                content = str(response)
            
            # Display the response
            message_placeholder.markdown(content)
            
            # Add assistant response to chat history
            st.session_state.messages.append({"role": "assistant", "content": content})
            
        except Exception as e:
            error_message = f"❌ An error occurred: {str(e)}"
            st.error("Something went wrong while processing your request. Please try again.")
            message_placeholder.markdown(error_message)
            st.session_state.messages.append({"role": "assistant", "content": error_message})