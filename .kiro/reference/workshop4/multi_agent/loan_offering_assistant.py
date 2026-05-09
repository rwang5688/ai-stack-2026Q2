from strands import Agent, tool
from config import get_default_model_config, get_xgboost_model_endpoint, get_aws_region
from model_factory import create_model_from_config
import boto3

LOAN_OFFERING_ASSISTANT_SYSTEM_PROMPT = """
You are a loan offering specialist, a financial assistant that predicts loan acceptance. Your capabilities include:

1. Loan Prediction:
   - Analyze customer demographics and engagement features
   - Predict loan acceptance or rejection
   - Provide confidence scores for predictions

2. Analysis Tools:
   - XGBoost model predictions
   - Feature interpretation
   - Risk assessment

3. Communication Approach:
   - Present predictions clearly
   - Explain confidence levels
   - Provide actionable insights

Focus on accuracy and clarity when presenting loan acceptance predictions.
"""


@tool
def loan_offering_prediction(payload: str) -> str:
    """
    Predict loan acceptance using XGBoost model endpoint.
    
    Args:
        payload: CSV string with 59 features representing customer demographics and engagement
                 Format: "age,campaign,pdays,previous,<one-hot encoded features>"
                 Example: "29,2,999,0,1,0,0.0,1.0,0.0,..."
        
    Returns:
        Formatted prediction result with raw score, label, and confidence
    """
    try:
        # Get configuration
        endpoint_name = get_xgboost_model_endpoint()
        region = get_aws_region()
        
        # Create SageMaker Runtime client
        runtime = boto3.client(
            service_name='sagemaker-runtime',
            region_name=region
        )
        
        # Invoke endpoint with CSV payload
        response = runtime.invoke_endpoint(
            EndpointName=endpoint_name,
            Body=payload,
            ContentType="text/csv"
        )
        
        # Parse response
        result = response['Body'].read().decode()
        prediction = float(result.strip())
        
        # Determine prediction label and confidence
        if prediction >= 0.5:
            prediction_label = "Accept"
            confidence = prediction * 100
        else:
            prediction_label = "Reject"
            confidence = (1 - prediction) * 100
        
        # Return formatted response
        return (
            f"Feature Payload: {payload}\n"
            f"Raw Prediction Score: {prediction:.4f}\n"
            f"Prediction: {prediction_label}\n"
            f"Confidence: {confidence:.2f}%"
        )
        
    except Exception as e:
        return f"Error invoking XGBoost endpoint: {str(e)}"


@tool
def loan_offering_assistant(query: str) -> str:
    """
    Process and respond to loan offering prediction queries using XGBoost model.
    
    Args:
        query: A loan prediction question with CSV feature payload from the user
        
    Returns:
        A detailed prediction with raw score, label, and confidence
    """
    # Format the query for the loan offering agent with clear instructions
    formatted_query = f"Please analyze the following loan offering query and provide a prediction: {query}"
    
    try:
        print("Routed to Loan Offering Assistant")
        
        # Get default model config from SSM Parameter Store
        model_config = get_default_model_config()
        
        # Create model from config
        model = create_model_from_config(model_config)
        
        # Create the loan offering agent with prediction capability
        loan_agent = Agent(
            model=model,
            system_prompt=LOAN_OFFERING_ASSISTANT_SYSTEM_PROMPT,
            tools=[loan_offering_prediction],
        )
        agent_response = loan_agent(formatted_query)
        text_response = str(agent_response)

        if len(text_response) > 0:
            return text_response

        return "I apologize, but I couldn't process this loan offering prediction. Please check if your query includes a valid CSV feature payload."
    except Exception as e:
        # Return specific error message for loan offering processing
        return f"Error processing your loan offering query: {str(e)}"
