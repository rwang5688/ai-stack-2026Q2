#!/bin/bash
# deploy-agentcore-infra.sh
#
# Deploys the AgentCore infrastructure stack:
#   - Cognito User Pools (OAuth identity for runtime-to-runtime auth)
#   - IAM Execution Roles (permissions for AgentCore Direct Deploy runtimes)
#
# Prerequisites:
#   - AWS credentials configured
#   - AWS CLI v2 installed
#
# Usage:
#   bash workshop4/phase3/deploy-agentcore-infra.sh
#   (can be run from any directory)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

REGION="us-west-2"
STACK_NAME="student-services-agentcore-infra"
TEMPLATE_FILE="cloudformation/student-services-agentcore-infra.yaml"
OUTPUTS_FILE="cloudformation/stack-outputs.json"

echo "=== Deploying AgentCore Infrastructure Stack ==="
echo "Region:   $REGION"
echo "Stack:    $STACK_NAME"
echo "Template: $TEMPLATE_FILE"
echo ""

# Deploy (CAPABILITY_NAMED_IAM required for IAM roles with custom names)
aws cloudformation deploy \
    --template-file "$TEMPLATE_FILE" \
    --stack-name "$STACK_NAME" \
    --region "$REGION" \
    --capabilities CAPABILITY_NAMED_IAM \
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

# Display IAM roles
echo "=== IAM Execution Roles Created ==="
aws cloudformation describe-stacks \
    --stack-name "$STACK_NAME" \
    --region "$REGION" \
    --query "Stacks[0].Outputs[?contains(OutputKey,'ExecutionRoleArn')].{Key:OutputKey,Value:OutputValue}" \
    --output table

echo ""

# Display Cognito pools
echo "=== Cognito Pools Created ==="
aws cloudformation describe-stacks \
    --stack-name "$STACK_NAME" \
    --region "$REGION" \
    --query "Stacks[0].Outputs[?contains(OutputKey,'UserPoolId')].{Key:OutputKey,Value:OutputValue}" \
    --output table

echo ""
echo "=== Next Steps ==="
echo "1. Update agentcore.json with executionRoleArn for each runtime"
echo "   (use the role ARNs from the table above)"
echo "2. bash register-credentials.sh   (register OAuth credentials)"
echo "3. cd studentservices && agentcore deploy -y"
