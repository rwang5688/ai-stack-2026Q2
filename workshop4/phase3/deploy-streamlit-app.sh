#!/bin/bash
set -e

echo "=== Student Services Phase 3 — ECS Fargate Deployment ==="
echo ""

cd "$(dirname "$0")/deploy-streamlit-app"

# Install CDK Python dependencies
echo ">>> Installing CDK dependencies..."
pip install -r requirements.txt -q
echo ""

# Bootstrap CDK (idempotent — safe to run multiple times)
echo ">>> Bootstrapping CDK..."
npx -y aws-cdk@latest bootstrap
echo ""

# Deploy stack (builds Docker image, pushes to ECR, deploys CloudFormation)
# Pass the StudentServicesAgent runtime URL as context
AGENT_URL="https://bedrock-agentcore.us-west-2.amazonaws.com/runtimes/arn%3Aaws%3Abedrock-agentcore%3Aus-west-2%3A149057604171%3Aruntime%2Fstudentservices_StudentServicesAgent-DVMRTdBLbs/invocations"

echo ">>> Deploying CDK stack..."
npx -y aws-cdk@latest deploy --require-approval never --outputs-file cdk-outputs.json \
  --context student_services_agent_url="${AGENT_URL}"
echo ""

# Print stack outputs
STACK_NAME="StudentServicesPhase3"
echo "=== Deployment Complete ==="
echo ""

CLOUDFRONT_URL=$(python3 -c "import json; data=json.load(open('cdk-outputs.json')); print(data['${STACK_NAME}']['CloudFrontDistributionURL'])")
COGNITO_POOL_ID=$(python3 -c "import json; data=json.load(open('cdk-outputs.json')); print(data['${STACK_NAME}']['CognitoPoolId'])")

echo "CloudFront URL:      https://${CLOUDFRONT_URL}"
echo "Cognito User Pool ID: ${COGNITO_POOL_ID}"
echo ""
echo "Next steps:"
echo "  1. Create a user in the Cognito User Pool via AWS Console"
echo "  2. Access the CloudFront URL in your browser"
echo "  3. Log in with your Cognito credentials"
