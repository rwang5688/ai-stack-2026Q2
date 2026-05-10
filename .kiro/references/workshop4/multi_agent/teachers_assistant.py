#!/usr/bin/env python3
"""
# 📁 Teacher's Assistant Strands Agent

A specialized Strands agent that is the orchestrator to utilize sub-agents and tools at its disposal to answer a user query.

## What This Example Shows

"""

from strands import Agent
from cross_platform_tools import get_platform_capabilities
from config import get_aws_region, get_temperature
from bedrock_model import create_bedrock_model
from sagemaker_model import create_sagemaker_model

from computer_science_assistant import computer_science_assistant
from english_assistant import english_assistant
from language_assistant import language_assistant
from loan_offering_assistant import loan_offering_assistant
from math_assistant import math_assistant
from no_expertise import general_assistant


# Define a focused system prompt for file operations
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


def select_model():
    """
    Prompt user to select a model at startup.
    
    Returns:
        Configured model instance (BedrockModel or SageMakerAIModel)
    """
    # Get temperature and configuration from config
    temperature = get_temperature()
    from config import get_bedrock_custom_model_deployment_arn, get_sagemaker_model_endpoint
    
    custom_model_arn = get_bedrock_custom_model_deployment_arn()
    sagemaker_endpoint = get_sagemaker_model_endpoint()
    
    print("\n🤖 Model Selection")
    print("=" * 60)
    print("Please select the agent model to use:")
    print()
    print("  1. Amazon Nova Pro")
    print("  2. Amazon Nova 2 Lite (Default)")
    print("  3. Anthropic Claude Haiku 4.5")
    print("  4. Anthropic Claude Sonnet 4.5")
    print(f"  5. Bedrock Custom Model Deployment ({custom_model_arn})")
    print(f"  6. SageMaker Model ({sagemaker_endpoint})")
    print()
    
    # Model configuration mapping
    model_options = {
        "1": {
            "name": "Amazon Nova Pro",
            "provider": "bedrock",
            "model_id": "us.amazon.nova-pro-v1:0"
        },
        "2": {
            "name": "Amazon Nova 2 Lite",
            "provider": "bedrock",
            "model_id": "us.amazon.nova-2-lite-v1:0"
        },
        "3": {
            "name": "Anthropic Claude Haiku 4.5",
            "provider": "bedrock",
            "model_id": "us.anthropic.claude-haiku-4-5-20251001-v1:0"
        },
        "4": {
            "name": "Anthropic Claude Sonnet 4.5",
            "provider": "bedrock",
            "model_id": "us.anthropic.claude-sonnet-4-5-20250929-v1:0"
        },
        "5": {
            "name": "Bedrock Custom Model Deployment",
            "provider": "bedrock",
            "model_id": custom_model_arn
        },
        "6": {
            "name": "SageMaker Model",
            "provider": "sagemaker",
            "model_id": "sagemaker-endpoint"
        }
    }
    
    # Get user selection
    while True:
        try:
            choice = input("Enter your choice (1-6) [default: 2]: ").strip()
            
            # Default to option 2 if empty
            if not choice:
                choice = "2"
            
            if choice in model_options:
                selected = model_options[choice]
                print(f"\n✅ Selected: {selected['name']}")
                print(f"   Provider: {selected['provider'].title()}")
                print(f"   Model ID: {selected['model_id']}")
                print(f"   Temperature: {temperature}")
                print()
                
                # Create and return the model
                if selected['provider'] == 'bedrock':
                    return create_bedrock_model(
                        model_id=selected['model_id'],
                        temperature=temperature
                    )
                elif selected['provider'] == 'sagemaker':
                    try:
                        return create_sagemaker_model(temperature=temperature)
                    except ValueError as e:
                        print(f"\n❌ Error: {str(e)}")
                        print("💡 SageMaker endpoint not configured. Falling back to Amazon Nova 2 Lite.")
                        return create_bedrock_model(
                            model_id="us.amazon.nova-2-lite-v1:0",
                            temperature=temperature
                        )
            else:
                print("❌ Invalid choice. Please enter a number between 1 and 6.")
        except KeyboardInterrupt:
            print("\n\n⚠️  Selection cancelled. Using default: Amazon Nova 2 Lite")
            return create_bedrock_model(
                model_id="us.amazon.nova-2-lite-v1:0",
                temperature=temperature
            )
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            print("Using default: Amazon Nova 2 Lite")
            return create_bedrock_model(
                model_id="us.amazon.nova-2-lite-v1:0",
                temperature=temperature
            )


# Example usage
if __name__ == "__main__":
    # Display platform capabilities
    capabilities = get_platform_capabilities()
    platform_info = capabilities['platform']
    
    print(f"\n📁 Teacher's Assistant Strands Agent 📁")
    print(f"Platform: {platform_info['system']} ({platform_info['platform']})")
    
    # Show available tools
    available_tools = capabilities['available_tools']
    unavailable_tools = [tool for tool, available in available_tools.items() if not available]
    
    if unavailable_tools:
        print(f"Note: Some tools are not available on {platform_info['system']}: {', '.join(unavailable_tools)}")
        if 'python_repl' in unavailable_tools or 'shell' in unavailable_tools:
            print("Computer Science Assistant will provide code examples with explanations instead of execution.")
    
    # Prompt user to select model
    model = select_model()
    
    # Create teacher agent with selected model
    teacher_agent = Agent(
        model=model,
        system_prompt=TEACHER_SYSTEM_PROMPT,
        callback_handler=None,
        tools=[math_assistant, language_assistant, english_assistant, computer_science_assistant, loan_offering_assistant, general_assistant],
    )
    
    print("=" * 60)
    print("\nAsk a question in any subject area, and I'll route it to the appropriate specialist.")
    print("Type 'exit' to quit.")

    # Interactive loop
    while True:
        try:
            user_input = input("\n> ")
            if user_input.lower() == "exit":
                print("\nGoodbye! 👋")
                break

            response = teacher_agent(
                user_input, 
            )
            
            # Extract and print only the relevant content from the specialized agent's response
            content = str(response)
            print(content)
            
        except KeyboardInterrupt:
            print("\n\nExecution interrupted. Exiting...")
            break
        except Exception as e:
            print(f"\nAn error occurred: {str(e)}")
            print("Please try asking a different question.")
