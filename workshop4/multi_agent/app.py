import streamlit as st
import os
from strands import Agent
from strands_tools import memory, use_agent

# Import configuration module
from config import (
    get_sagemaker_model_endpoint,
    get_sagemaker_model_inference_component,
    get_aws_region,
    get_default_model_config,
    get_max_results,
    get_min_score,
    get_strands_knowledge_base_id,
    get_temperature,
)

# Import model creation modules
from bedrock_model import create_bedrock_model
from sagemaker_model import create_sagemaker_model
from model_factory import create_model_from_config

# Bypass tool consent for knowledge base operations
os.environ["BYPASS_TOOL_CONSENT"] = "true"

# Import the specialized assistants
from computer_science_assistant import computer_science_assistant
from english_assistant import english_assistant
from language_assistant import language_assistant
from loan_offering_assistant import loan_offering_assistant
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
   - Loan Offering Assistant: For loan acceptance predictions based on customer features
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
   - If query involves loan predictions/acceptance → Loan Offering Assistant
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
- "Will a person accept a loan" -> "teacher"
- "Predict loan acceptance" -> "teacher"
- "Will a person with these features accept the loan: 29,2,999,0,1,0,0.0,1.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,1.0,0.0,0.0,0.0,0.0,1.0,0.0,0.0,0.0,0.0,0.0,1.0,0.0,0.0,1.0,0.0,0.0,1.0,0.0,0.0,0.0,1.0,0.0,0.0,0.0,0.0,1.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,1.0,0.0,0.0,1.0,0.0" -> "teacher"
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
STRANDS_KNOWLEDGE_BASE_ID = get_strands_knowledge_base_id()
MIN_SCORE = get_min_score()
MAX_RESULTS = get_max_results()
TEMPERATURE = get_temperature()

# NOTE: STRANDS_KNOWLEDGE_BASE_ID must be set as an environment variable BEFORE starting the app
# The Strands Agents framework checks for this during initialization
# Set it with: export STRANDS_KNOWLEDGE_BASE_ID=<your-kb-id>
# Or add it to your .bashrc or shell profile

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
    # Model Selection
    st.header("🤖 Model Selection")
    
    # Define model options
    model_options = {
        "Amazon Nova Pro (us.amazon.nova-pro-v1:0)": {
            "provider": "bedrock",
            "model_id": "us.amazon.nova-pro-v1:0",
            "display_name": "Amazon Nova Pro"
        },
        "Amazon Nova 2 Lite (us.amazon.nova-2-lite-v1:0)": {
            "provider": "bedrock",
            "model_id": "us.amazon.nova-2-lite-v1:0",
            "display_name": "Amazon Nova 2 Lite"
        },
        "Anthropic Claude Haiku 4.5 (us.anthropic.claude-haiku-4-5-20251001-v1:0)": {
            "provider": "bedrock",
            "model_id": "us.anthropic.claude-haiku-4-5-20251001-v1:0",
            "display_name": "Anthropic Claude Haiku 4.5"
        },
        "Anthropic Claude Sonnet 4.5 (us.anthropic.claude-sonnet-4-5-20250929-v1:0)": {
            "provider": "bedrock",
            "model_id": "us.anthropic.claude-sonnet-4-5-20250929-v1:0",
            "display_name": "Anthropic Claude Sonnet 4.5"
        },
        "Custom SageMaker Model": {
            "provider": "sagemaker",
            "model_id": "sagemaker-endpoint",
            "display_name": "Custom SageMaker Model"
        }
    }
    
    # Initialize session state for selected model if not exists
    if "selected_model_key" not in st.session_state:
        st.session_state.selected_model_key = "Amazon Nova 2 Lite (us.amazon.nova-2-lite-v1:0)"
    
    # Model selection dropdown
    selected_model_key = st.selectbox(
        "Choose Agent Model:",
        options=list(model_options.keys()),
        index=list(model_options.keys()).index(st.session_state.selected_model_key),
        help="Select which model to use for the teacher agent"
    )
    
    # Update session state if model changed
    if selected_model_key != st.session_state.selected_model_key:
        st.session_state.selected_model_key = selected_model_key
        # Clear the cached teacher agent to force recreation with new model
        if "teacher_agent" in st.session_state:
            del st.session_state.teacher_agent
    
    # Get selected model info
    selected_model_info = model_options[selected_model_key]
    
    # Format provider name with proper capitalization
    def format_provider_name(provider: str) -> str:
        """Format provider name with proper capitalization."""
        if provider == 'sagemaker':
            return 'SageMaker'
        elif provider == 'bedrock':
            return 'Bedrock'
        else:
            return provider.title()
    
    provider_display = format_provider_name(selected_model_info['provider'])
    
    # Display active model information
    st.info(f"**Active Model**: {selected_model_info['display_name']}\n\n**Provider**: {provider_display}")
    
    st.header("🔧 AI Service Details")
    aws_region = get_aws_region()
    
    # For SageMaker models, show the actual endpoint name instead of generic model_id
    if selected_model_info['provider'] == 'sagemaker':
        sagemaker_endpoint = get_sagemaker_model_endpoint()
        display_model_id = sagemaker_endpoint
    else:
        display_model_id = selected_model_info['model_id']
    
    st.markdown(f"""
    **Model Provider**: {provider_display}  
    **Model ID**: `{display_model_id}`  
    **Temperature**: {TEMPERATURE}  
    **Knowledge Base**: {STRANDS_KNOWLEDGE_BASE_ID}  
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
    - **💰 Loan Offering Assistant**: Loan acceptance predictions
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
    """)
    
    st.markdown("**Loan Predictions:**")
    st.text_area(
        "Copy this example:",
        value='Will a person with these features accept the loan: 29,2,999,0,1,0,0.0,1.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,1.0,0.0,0.0,0.0,0.0,1.0,0.0,0.0,0.0,0.0,0.0,1.0,0.0,0.0,1.0,0.0,0.0,1.0,0.0,0.0,0.0,1.0,0.0,0.0,0.0,0.0,1.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,1.0,0.0,0.0,1.0,0.0',
        height=100,
        key="loan_example"
    )
    
    st.markdown("""
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
    
    # Debugging section - show all configuration
    st.header("🔍 Debug Info")
    with st.expander("Configuration Details", expanded=False):
        st.markdown("**Environment:**")
        st.code(f"TEACHERS_ASSISTANT_ENV: {os.getenv('TEACHERS_ASSISTANT_ENV', 'dev')}")
        st.code(f"AWS_REGION: {aws_region}")
        
        st.markdown("**Active Model Configuration:**")
        st.code(f"Provider: {selected_model_info['provider']}")
        st.code(f"Model ID: {selected_model_info['model_id']}")
        st.code(f"Display Name: {selected_model_info['display_name']}")
        st.code(f"Temperature: {TEMPERATURE}")
        
        st.markdown("**SageMaker Configuration (from SSM):**")
        sagemaker_endpoint = get_sagemaker_model_endpoint()
        sagemaker_inference_component = get_sagemaker_model_inference_component()
        st.code(f"Endpoint Name: {sagemaker_endpoint}")
        st.code(f"Inference Component: {sagemaker_inference_component}")
        
        # Show if inference component will be used when SageMaker is selected
        if selected_model_info['provider'] == 'sagemaker':
            if sagemaker_inference_component and sagemaker_inference_component != "my-sagemaker-model-inference-component":
                st.success("✅ SageMaker model WILL use inference component")
            else:
                st.warning("⚠️ SageMaker model will use endpoint only (NO inference component)")
        else:
            st.info("ℹ️ SageMaker not selected (using Bedrock)")
        
        st.markdown("**Knowledge Base:**")
        st.code(f"KB ID: {STRANDS_KNOWLEDGE_BASE_ID}")
        st.code(f"Min Score: {MIN_SCORE}")
        st.code(f"Max Results: {MAX_RESULTS}")
        
        st.markdown("**XGBoost Endpoint (Loan Assistant):**")
        from config import get_xgboost_model_endpoint
        xgboost_endpoint = get_xgboost_model_endpoint()
        st.code(f"Endpoint: {xgboost_endpoint}")

# Initialize session state for conversation history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Knowledge base functions
def determine_action(query, model, model_info):
    """Determine if the query should go to teacher agent or knowledge base agent."""
    agent = Agent(
        model=model,
        tools=[use_agent]
    )
    
    try:
        # Build model_settings based on provider
        model_settings = {}
        if model_info['provider'] == 'bedrock':
            model_settings = {
                'model_id': model_info['model_id'],
                'temperature': TEMPERATURE
            }
        elif model_info['provider'] == 'sagemaker':
            inference_component = get_sagemaker_model_inference_component()
            model_settings = {
                'endpoint_name': get_sagemaker_model_endpoint(),
                'temperature': TEMPERATURE
            }
            # Add inference component if it's set and not the default placeholder
            if inference_component and inference_component != "my-sagemaker-model-inference-component":
                model_settings['inference_component_name'] = inference_component
        
        result = agent.tool.use_agent(
            prompt=f"Query: {query}",
            system_prompt=ACTION_DETERMINATION_PROMPT,
            model_provider=model_info['provider'],
            model_settings=model_settings
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

def determine_kb_action(query, model, model_info):
    """Determine if the knowledge base query is a store or retrieve action."""
    agent = Agent(
        model=model,
        tools=[use_agent]
    )
    
    try:
        # Build model_settings based on provider
        model_settings = {}
        if model_info['provider'] == 'bedrock':
            model_settings = {
                'model_id': model_info['model_id'],
                'temperature': TEMPERATURE
            }
        elif model_info['provider'] == 'sagemaker':
            inference_component = get_sagemaker_model_inference_component()
            model_settings = {
                'endpoint_name': get_sagemaker_model_endpoint(),
                'temperature': TEMPERATURE
            }
            # Add inference component if it's set and not the default placeholder
            if inference_component and inference_component != "my-sagemaker-model-inference-component":
                model_settings['inference_component_name'] = inference_component
        
        result = agent.tool.use_agent(
            prompt=f"Query: {query}",
            system_prompt=KB_ACTION_SYSTEM_PROMPT,
            model_provider=model_info['provider'],
            model_settings=model_settings
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

def run_kb_agent(query, model, model_info):
    """Process a user query with the knowledge base agent."""
    agent = Agent(
        model=model,
        tools=[memory, use_agent]
    )
    
    # Determine the action - store or retrieve
    action = determine_kb_action(query, model, model_info)
    
    if action == "store":
        # For store actions, store the full query
        try:
            result = agent.tool.memory(
                action="store",
                content=query
            )
            return "✅ I've stored this information in your knowledge base."
        except Exception as e:
            return f"❌ Error storing information: {str(e)}"
    else:
        # For retrieve actions, query the knowledge base with appropriate parameters
        try:
            result = agent.tool.memory(
                action="retrieve", 
                query=query,
                min_score=MIN_SCORE,
                max_results=MAX_RESULTS
            )
            # Convert the result to a string to extract just the content text
            result_str = str(result)
            
            # Build model_settings based on provider
            model_settings = {}
            if model_info['provider'] == 'bedrock':
                model_settings = {
                    'model_id': model_info['model_id'],
                    'temperature': TEMPERATURE
                }
            elif model_info['provider'] == 'sagemaker':
                inference_component = get_sagemaker_model_inference_component()
                model_settings = {
                    'endpoint_name': get_sagemaker_model_endpoint(),
                    'temperature': TEMPERATURE
                }
                # Add inference component if it's set and not the default placeholder
                if inference_component and inference_component != "my-sagemaker-model-inference-component":
                    model_settings['inference_component_name'] = inference_component
            
            # Generate a clear, conversational answer using the retrieved information
            answer = agent.tool.use_agent(
                prompt=f"User question: \"{query}\"\n\nInformation from knowledge base:\n{result_str}\n\nStart your answer with newline character and provide a helpful answer based on this information:",
                system_prompt=KB_ANSWER_SYSTEM_PROMPT,
                model_provider=model_info['provider'],
                model_settings=model_settings
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

# Initialize the teacher agent with selected model
@st.cache_resource
def get_teacher_agent(_model):
    """
    Create teacher agent with the specified model.
    
    Args:
        _model: The model instance (BedrockModel or SageMakerAIModel)
    
    Returns:
        Configured Agent instance
    """
    # Create the teacher agent with specialized tools
    return Agent(
        model=_model,
        system_prompt=TEACHER_SYSTEM_PROMPT,
        callback_handler=None,
        tools=[math_assistant, language_assistant, english_assistant, computer_science_assistant, loan_offering_assistant, general_assistant],
    )


def create_model_from_selection(model_info):
    """
    Create a model instance based on the selected model info.
    
    Args:
        model_info: Dictionary containing provider and model_id
    
    Returns:
        Model instance (BedrockModel or SageMakerAIModel)
    """
    if model_info['provider'] == 'bedrock':
        return create_bedrock_model(
            model_id=model_info['model_id'],
            temperature=TEMPERATURE
        )
    elif model_info['provider'] == 'sagemaker':
        try:
            return create_sagemaker_model(
                temperature=TEMPERATURE
            )
        except ValueError as e:
            st.error(f"❌ SageMaker endpoint not configured: {str(e)}")
            st.info("💡 Set the SAGEMAKER_MODEL_ENDPOINT environment variable to use SageMaker models.")
            # Fallback to default Bedrock model
            st.warning("⚠️ Falling back to Amazon Nova 2 Lite (Bedrock)")
            return create_bedrock_model(
                model_id="us.amazon.nova-2-lite-v1:0",
                temperature=TEMPERATURE
            )
    else:
        raise ValueError(f"Unknown provider: {model_info['provider']}")

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
            
            # Create model instance based on selection
            selected_model_info = model_options[st.session_state.selected_model_key]
            current_model = create_model_from_selection(selected_model_info)
            
            if selected_agent_type == "Teacher Agent":
                # Route directly to teacher agent
                with st.spinner("Routing to educational specialist..."):
                    teacher_agent = get_teacher_agent(current_model)
                    response = teacher_agent(query)
                    content = str(response)
            
            elif selected_agent_type == "Knowledge Base":
                # Route directly to knowledge base agent
                with st.spinner("Processing with Knowledge Base..."):
                    response = run_kb_agent(query, current_model, selected_model_info)
                    content = str(response)
            
            else:  # Auto-Route
                # Determine if query should go to teacher agent or knowledge base
                with st.spinner("Analyzing query..."):
                    action = determine_action(query, current_model, selected_model_info)
                
                if action == "knowledge":
                    # Route to knowledge base agent
                    with st.spinner("Processing with Knowledge Base..."):
                        response = run_kb_agent(query, current_model, selected_model_info)
                        content = str(response)
                else:
                    # Route to teacher agent (existing functionality)
                    with st.spinner("Routing to educational specialist..."):
                        teacher_agent = get_teacher_agent(current_model)
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
