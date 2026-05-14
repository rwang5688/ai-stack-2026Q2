#!/bin/bash
# deploy-student-services-identity.sh
#
# Deploys the Cognito identity stack for AgentCore runtimes and captures outputs.
#
# Prerequisites:
#   - AWS credentials configured
#   - AWS CLI v2 installed
#
# Usage:
#   cd workshop4/phase3
#   bash deploy-student-services-identity.sh

set -e

REGION="us-west-2"
STACK_NAME="student-services-identity"
TEMPLATE_FILE="cloudformation/student-services-identity.yaml"
OUTPUTS_FILE="cloudformation/stack-outputs.json"

echo "=== Deploying Identity Stack ==="
echo "Region:   $REGION"
echo "Stack:    $STACK_NAME"
echo "Template: $TEMPLATE_FILE"
echo ""

# Deploy
aws cloudformation deploy \
    --template-file "$TEMPLATE_FILE" \
    --stack-name "$STACK_NAME" \
    --region "$REGION" \
    --no-fail-on-empty-changeset

echo ""
echo "=== Capturing Stack Outputs ==="

# Capture outputs
aws cloudformation describe-stacks \
    --stack-name "$STACK_NAME" \
    --region "$REGION" \
    --query "Stacks[0].Outputs" \
    --output json > "$OUTPUTS_FILE"

echo "Outputs saved to: $OUTPUTS_FILE"
echo ""

# Display summary
echo "=== Cognito Pools Created ==="
aws cloudformation describe-stacks \
    --stack-name "$STACK_NAME" \
    --region "$REGION" \
    --query "Stacks[0].Outputs[?contains(OutputKey,'UserPoolId')].{Key:OutputKey,Value:OutputValue}" \
    --output table

echo ""
echo "=== Next Steps ==="
echo "1. cd studentservices"
echo "2. bash ../register-credentials.sh   (register OAuth credentials)"
echo "3. agentcore deploy -y               (Deploy 1: runtimes + memory + credentials)"
echo "4. agentcore status                  (note runtime URLs for gateway config)"
echo "5. [add gateway to agentcore.json with runtime URLs]"
echo "6. agentcore deploy -y               (Deploy 2: gateway)"
