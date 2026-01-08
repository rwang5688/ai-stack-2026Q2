# =============================================================================
# AUTHENTICATION SECTION - Required for Deployed Applications
# =============================================================================
# This section handles Cognito authentication for deployed applications.
# For local development, you can comment out this section.
# For deployment, this section must remain active.

import streamlit as st
import os
from utils.auth import Auth
from config_file import Config

# Authentication Configuration
SECRETS_MANAGER_ID = Config.SECRETS_MANAGER_ID
DEPLOYMENT_REGION = Config.DEPLOYMENT_REGION

# Initialize Cognito Authenticator
authenticator = Auth.get_authenticator(SECRETS_MANAGER_ID, DEPLOYMENT_REGION)

# Enforce Authentication - This stops execution if user is not logged in
is_logged_in = authenticator.login()
if not is_logged_in:
    st.stop()

# Authentication UI Components
def logout():
    """Handle user logout"""
    authenticator.logout()

# =============================================================================
# APPLICATION LOGIC SECTION - Your Custom Application Code Goes Here
# =============================================================================
# This section contains your main application logic.
# Students should copy their application code from multi_agent_bedrock/app.py
# and paste it below this comment, replacing the existing application logic.

# Import application dependencies
from strands import Agent
from strands.models import BedrockModel
from strands_tools import memory, use_agent

# Bypass tool consent for knowledge base operations
os.environ["BYPASS_TOOL_CONSENT"] = "true"

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

# System prompt to determine if query should go to teacher agent or knowledge base agent
ACTION_DETERMINATION_PROMPT = """
You are a query router that determines whether a user query should be handled by:
1. TEACHER - for educational questions requiring specialized subject matter expertise
2. KNOWLEDGE - for storing personal information or retrieving previously stored information

Respond with EXACTLY ONE WORD - either "teacher" or "knowledge".

Examples:
- "Solve this math equation" -> "teacher"
- "Help me with Python programming" -> "teacher" 
- "Translate this to Spanish" -> "teacher"
- "Remember that my birthday is July 4" -> "knowledge"
- "What's my birthday?" -> "knowledge"
- "Store this information: I live in Seattle" -> "knowledge"
- "What do you know about me?" -> "knowledge"
- "My favorite color is blue" -> "knowledge"
- "What is my favorite color?" -> "knowledge"
- "List all k-pop groups that I like" -> "knowledge"
- "What are the symptoms of arthritis?" -> "knowledge"
- "Based on knowledge base, what are symptoms of arthritis?" -> "knowledge"
- "According to our knowledge base" -> "knowledge"
- "What information do you have about" -> "knowledge"

Only respond with "teacher" or "knowledge" - no explanation or other text.
"""

# System prompt for knowledge base action determination
KB_ACTION_SYSTEM_PROMPT = """
You are a knowledge base assistant focusing ONLY on classifying user queries.
Your task is to determine whether a user query requires STORING information to a knowledge base
or RETRIEVING information from a knowledge base.

Reply with EXACTLY ONE WORD - either "store" or "retrieve".
DO NOT include any explanations or other text.

Examples:
- "Remember that my birthday is July 4" -> "store"
- "What's my birthday?" -> "retrieve"
- "The capital of France is Paris" -> "store"
- "What is the capital of France?" -> "retrieve"
- "My name is John" -> "store" 
- "Who am I?" -> "retrieve"
- "I live in Seattle" -> "store"
- "Where do I live?" -> "retrieve"
- "List all k-pop groups that I like" -> "retrieve"
- "What are the symptoms of arthritis?" -> "retrieve"
- "Show me all my favorite movies" -> "retrieve"
- "Tell me about my hobbies" -> "retrieve"
- "I like BTS and BLACKPINK" -> "store"
- "My favorite hobby is reading" -> "store"

Only respond with "store" or "retrieve" - no explanation, prefix, or any other text.
"""

# System prompt for generating answers from retrieved information
KB_ANSWER_SYSTEM_PROMPT = """
You are a helpful knowledge assistant that provides clear, concise answers 
based on information retrieved from a knowledge base.

The information from the knowledge base contains document IDs, titles, 
content previews and relevance scores. Focus on the actual content and 
ignore the metadata.

Your responses should:
1. Be direct and to the point
2. Not mention the source of information (like document IDs or scores)
3. Not include any metadata or technical details
4. Be conversational but brief
5. Acknowledge when information is conflicting or missing
6. Begin the response with \n

When analyzing the knowledge base results:
- Higher scores (closer to 1.0) indicate more relevant results
- Look for patterns across multiple results
- Prioritize information from results with higher scores
- Ignore any JSON formatting or technical elements in the content

Example response for conflicting information:
"Based on my records, I have both July 4 and August 8 listed as your birthday. Could you clarify which date is correct?"

Example response for clear information:
"Your birthday is on July 4."

Example response for missing information:
"I don't have any information about your birthday stored."
"""

# Knowledge base configuration
DEFAULT_KB_ID = "demokb123"
KB_ID = os.getenv("STRANDS_KNOWLEDGE_BASE_ID", DEFAULT_KB_ID)
MIN_SCORE = os.getenv("MIN_SCORE", "0.000001")
MAX_RESULTS = os.getenv("MAX_RESULTS", "9")

# Set up the page
st.set_page_config(
    page_title="TeachAssist - Multi-Agent System with Agent Selection", 
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🎓 TeachAssist - Multi-Agent System with Agent Selection")
st.write("Choose your agent type or let the system auto-route your queries to the most appropriate agent.")

# Add sidebar with information
with st.sidebar:
    # =============================================================================
    # AUTHENTICATION UI - Shows user info and logout button
    # =============================================================================
    st.header("👤 User Authentication")
    st.text(f"Welcome,\n{authenticator.get_username()}")
    st.button("🚪 Logout", "logout_btn", on_click=logout)
    st.divider()
    
    # =============================================================================
    # APPLICATION UI - Your custom sidebar content goes here
    # =============================================================================
    st.header("🤖 AI Service Details")
    aws_region = os.getenv("AWS_REGION", "Not Set")
    st.markdown(f"""
    **Service**: Amazon Bedrock  
    **Model**: `us.amazon.nova-pro-v1:0`  
    **Foundation Model**: Amazon Nova Pro  
    **Temperature**: 0.3  
    **Knowledge Base**: {KB_ID}  
    **AWS Region**: {aws_region}
    """)
    
    # Agent Type Selection
    st.header("🎯 Agent Type Selection")
    agent_type = st.selectbox(
        "Choose Agent Type:",
        ["Auto-Route", "Teacher Agent", "Knowledge Base"],
        index=0,
        help="Select which agent system to use for your queries"
    )
    
    # Store agent type in session state
    st.session_state.selected_agent_type = agent_type
    
    # Display agent type information
    if agent_type == "Auto-Route":
        st.info("🔄 **Auto-Route**: Automatically determines the best agent for your query")
    elif agent_type == "Teacher Agent":
        st.info("🎓 **Teacher Agent**: Routes to specialized educational assistants")
    elif agent_type == "Knowledge Base":
        st.info("🧠 **Knowledge Base**: Store and retrieve personal information")
    
    st.header("📚 Available Specialists")
    st.markdown("""
    - **🧮 Math Assistant**: Calculations, equations, mathematical concepts
    - **📝 English Assistant**: Writing, grammar, literature, composition
    - **🌍 Language Assistant**: Translation and language queries
    - **💻 Computer Science Assistant**: Programming, algorithms, code execution
    - **🎯 General Assistant**: All other topics
    - **🧠 Knowledge Base**: Store and retrieve personal information
    """)
    
    st.header("💡 Sample Questions")
    st.markdown("""
    **Educational Questions:**
    - "Solve the quadratic equation x^2 + 5x + 6 = 0"
    - "Write a Python function to check if a string is a palindrome"
    - "Translate 'Hello, how are you?' to Spanish"
    - "Help me improve this essay paragraph"
    - "What is the capital of France?"
    
    **Knowledge Base:**
    - "Remember that my birthday is July 25"
    - "What's my birthday?"
    - "Store this: I live in Seattle"
    - "Where do I live?"
    """)
    
    # Add clear conversation button
    if st.button("🗑️ Clear Conversation"):
        st.session_state.messages = []
        st.rerun()

# Initialize session state for conversation history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Knowledge base functions
def determine_action(query):
    """Determine if the query should go to teacher agent or knowledge base agent."""
    bedrock_model = BedrockModel(
        model_id="us.amazon.nova-pro-v1:0",
        temperature=0.1,
    )
    
    agent = Agent(
        model=bedrock_model,
        tools=[use_agent]
    )
    
    try:
        result = agent.tool.use_agent(
            prompt=f"Query: {query}",
            system_prompt=ACTION_DETERMINATION_PROMPT,
            model_provider="bedrock",
            model_settings={
                'model_id': 'us.amazon.nova-pro-v1:0'
            }
        )
        
        # Clean and extract the action
        action_text = str(result).lower().strip()
        
        # Handle structured response format
        if isinstance(result, dict) and 'content' in result:
            if result['content'] and len(result['content']) > 0:
                action_text = result['content'][0].get('text', '').lower().strip()
        
        # Default to teacher if response isn't clear
        if "knowledge" in action_text:
            return "knowledge"
        else:
            return "teacher"
    except Exception as e:
        st.error(f"Error determining action: {str(e)}")
        return "teacher"  # Default to teacher on error

def determine_kb_action(query):
    """Determine if the knowledge base query is a store or retrieve action."""
    bedrock_model = BedrockModel(
        model_id="us.amazon.nova-pro-v1:0",
        temperature=0.1,
    )
    
    agent = Agent(
        model=bedrock_model,
        tools=[use_agent]
    )
    
    try:
        result = agent.tool.use_agent(
            prompt=f"Query: {query}",
            system_prompt=KB_ACTION_SYSTEM_PROMPT,
            model_provider="bedrock",
            model_settings={
                'model_id': 'us.amazon.nova-pro-v1:0'
            }
        )
        
        # Clean and extract the action
        action_text = str(result).lower().strip()
        
        # Handle structured response format
        if isinstance(result, dict) and 'content' in result:
            if result['content'] and len(result['content']) > 0:
                action_text = result['content'][0].get('text', '').lower().strip()
        
        # Default to retrieve if response isn't clear
        if "store" in action_text:
            return "store"
        else:
            return "retrieve"
    except Exception as e:
        st.error(f"Error determining KB action: {str(e)}")
        return "retrieve"  # Default to retrieve on error

def run_kb_agent(query):
    """Process a user query with the knowledge base agent."""
    bedrock_model = BedrockModel(
        model_id='us.amazon.nova-pro-v1:0',
        temperature=0.1,
    )
    agent = Agent(
        model=bedrock_model,
        tools=[memory, use_agent]
    )
    
    # Determine the action - store or retrieve
    action = determine_kb_action(query)
    
    if action == "store":
        # For store actions, store the full query
        try:
            result = agent.tool.memory(
                action="store",
                content=query
            )
            # Check if the result indicates success
            result_str = str(result)
            if result and "error" not in result_str.lower():
                return "✅ I've stored this information in your knowledge base."
            else:
                return f"❌ Error storing information: {result_str}"
        except Exception as e:
            return f"❌ Error storing information: {str(e)}"
    else:
        # For retrieve actions, query the knowledge base with appropriate parameters
        try:
            result = agent.tool.memory(
                action="retrieve", 
                query=query,
                min_score=float(MIN_SCORE),
                max_results=int(MAX_RESULTS)
            )
            # Convert the result to a string to extract just the content text
            result_str = str(result)
            
            # Generate a clear, conversational answer using the retrieved information
            answer = agent.tool.use_agent(
                prompt=f"User question: \"{query}\"\n\nInformation from knowledge base:\n{result_str}\n\nStart your answer with newline character and provide a helpful answer based on this information:",
                system_prompt=KB_ANSWER_SYSTEM_PROMPT,
                model_provider="bedrock",
                model_settings={
                    'model_id': 'us.amazon.nova-pro-v1:0'
                }
            )
            
            # Extract clean response from the structured result
            if isinstance(answer, dict) and 'content' in answer:
                # Extract the text from the first content item
                if answer['content'] and len(answer['content']) > 0:
                    raw_text = answer['content'][0].get('text', str(answer))
                    # Clean up the response by removing "Response: " prefix and extra whitespace
                    if raw_text.startswith('Response: '):
                        raw_text = raw_text[10:]  # Remove "Response: " prefix
                    return raw_text.strip()
            
            # Fallback: clean up string response
            clean_answer = str(answer)
            if clean_answer.startswith('Response: '):
                clean_answer = clean_answer[10:]
            return clean_answer.strip()
        except Exception as e:
            return f"❌ Error retrieving information: {str(e)}"

# Display conversation history or welcome message
if not st.session_state.messages:
    st.info("👋 Welcome! I can help with educational questions AND store/retrieve personal information. Try asking about math, programming, writing, translations, or tell me something to remember!")

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
            # Get selected agent type from session state
            selected_agent_type = st.session_state.get('selected_agent_type', 'Auto-Route')
            
            if selected_agent_type == "Teacher Agent":
                # Route directly to teacher agent
                with st.spinner("Routing to educational specialist..."):
                    teacher_agent = get_teacher_agent()
                    response = teacher_agent(query)
                    content = str(response)
            
            elif selected_agent_type == "Knowledge Base":
                # Route directly to knowledge base agent
                with st.spinner("Processing with Knowledge Base..."):
                    response = run_kb_agent(query)
                    content = str(response)
            
            else:  # Auto-Route
                # Determine if query should go to teacher agent or knowledge base
                with st.spinner("Analyzing query..."):
                    action = determine_action(query)
                
                if action == "knowledge":
                    # Route to knowledge base agent
                    with st.spinner("Processing with Knowledge Base..."):
                        response = run_kb_agent(query)
                        content = str(response)
                else:
                    # Route to teacher agent (existing functionality)
                    with st.spinner("Routing to educational specialist..."):
                        teacher_agent = get_teacher_agent()
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

# =============================================================================
# END OF APPLICATION LOGIC
# =============================================================================
# When merging your local app.py with this deployed version:
# 1. Keep the AUTHENTICATION SECTION at the top (lines 1-25)
# 2. Replace the APPLICATION LOGIC SECTION with your custom code
# 3. Ensure the authentication UI remains in the sidebar
# 4. Test that both authentication and your features work together
# =============================================================================