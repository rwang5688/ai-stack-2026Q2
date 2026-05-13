#!/bin/bash
set -e

echo "=== Student Services Phase 2 — ECS Fargate Deployment ==="
echo ""

cd "$(dirname "$0")/deploy-streamlit-app"

# Bootstrap CDK (idempotent — safe to run multiple times)
echo ">>> Bootstrapping CDK..."
cdk bootstrap
echo ""

# Deploy stack (builds Docker image, pushes to ECR, deploys CloudFormation)
echo ">>> Deploying CDK stack..."
cdk deploy --require-approval never --outputs-file cdk-outputs.json
echo ""

# Print stack outputs
STACK_NAME="StudentServicesPhase2"
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
