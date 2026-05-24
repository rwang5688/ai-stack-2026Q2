# Run the local Streamlit thin client for Student Services Agent
# Requires: AWS credentials configured (SigV4 signing)

Set-Location $PSScriptRoot

pip install -r requirements.txt -q

$env:STUDENT_SERVICES_AGENT_URL = "https://bedrock-agentcore.us-west-2.amazonaws.com/runtimes/arn%3Aaws%3Abedrock-agentcore%3Aus-west-2%3A149057604171%3Aruntime%2Fstudentservices_StudentServicesAgent-DVMRTdBLbs/invocations"

streamlit run app.py
