#!/bin/bash
# register-credentials.sh
#
# Fetches Cognito client secrets from the student-services-identity CloudFormation
# stack and registers them as AgentCore OAuth credentials.
#
# Prerequisites:
#   - AWS credentials configured
#   - CloudFormation stack "student-services-identity" deployed
#   - agentcore CLI installed
#
# Usage:
#   bash workshop4/phase3/register-credentials.sh
#   (can be run from any directory)

set -e

# agentcore CLI must run from the agentcore project directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/studentservices"
echo "Working directory: $(pwd)"

REGION="us-west-2"
STACK_NAME="student-services-identity"

echo "=== Registering AgentCore OAuth Credentials ==="
echo "Region: $REGION"
echo "Stack:  $STACK_NAME"
echo ""

# Helper: get a stack output value by key
get_output() {
    aws cloudformation describe-stacks \
        --stack-name "$STACK_NAME" \
        --region "$REGION" \
        --query "Stacks[0].Outputs[?OutputKey=='$1'].OutputValue" \
        --output text
}

# Helper: get client secret from Cognito
get_secret() {
    aws cognito-idp describe-user-pool-client \
        --user-pool-id "$1" \
        --client-id "$2" \
        --region "$REGION" \
        --query "UserPoolClient.ClientSecret" \
        --output text
}

# Define credentials to register
declare -a CRED_NAMES=(
    "CourseRegistrationMcp-oauth"
    "CourseReviewMcp-oauth"
    "LoanApplicationMcp-oauth"
    "MathTeachingMcp-oauth"
    "StudentServicesGateway-oauth"
)

declare -a POOL_ID_KEYS=(
    "CourseRegistrationUserPoolId"
    "CourseReviewUserPoolId"
    "LoanApplicationUserPoolId"
    "MathTeachingUserPoolId"
    "StudentServicesGatewayUserPoolId"
)

declare -a CLIENT_ID_KEYS=(
    "CourseRegistrationClientId"
    "CourseReviewClientId"
    "LoanApplicationClientId"
    "MathTeachingClientId"
    "StudentServicesGatewayClientId"
)

declare -a DISCOVERY_URL_KEYS=(
    "CourseRegistrationDiscoveryUrl"
    "CourseReviewDiscoveryUrl"
    "LoanApplicationDiscoveryUrl"
    "MathTeachingDiscoveryUrl"
    "StudentServicesGatewayDiscoveryUrl"
)

declare -a SCOPES=(
    "course-registration/access"
    "course-review/access"
    "loan-application/access"
    "math-teaching/access"
    "student-services-gateway/access"
)

# Register each credential
for i in "${!CRED_NAMES[@]}"; do
    NAME="${CRED_NAMES[$i]}"
    POOL_ID=$(get_output "${POOL_ID_KEYS[$i]}")
    CLIENT_ID=$(get_output "${CLIENT_ID_KEYS[$i]}")
    DISCOVERY_URL=$(get_output "${DISCOVERY_URL_KEYS[$i]}")
    SCOPE="${SCOPES[$i]}"

    echo "Registering: $NAME"
    echo "  Pool ID:       $POOL_ID"
    echo "  Client ID:     $CLIENT_ID"
    echo "  Discovery URL: $DISCOVERY_URL"
    echo "  Scope:         $SCOPE"

    # Fetch client secret
    SECRET=$(get_secret "$POOL_ID" "$CLIENT_ID")
    echo "  Secret:        ${SECRET:0:8}..."

    # Register with AgentCore CLI
    agentcore add credential \
        --name "$NAME" \
        --type oauth \
        --discovery-url "$DISCOVERY_URL" \
        --client-id "$CLIENT_ID" \
        --client-secret "$SECRET" \
        --scopes "$SCOPE"

    echo "  ✓ Done"
    echo ""
done

echo "=== All credentials registered ==="
echo "Run 'agentcore deploy -y' to provision them to AWS."
