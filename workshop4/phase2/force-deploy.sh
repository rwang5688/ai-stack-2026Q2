#!/bin/bash
set -e

echo "=== Force Deploy: Rebuilding and redeploying ECS service ==="

cd "$(dirname "$0")/deploy-streamlit-app"

# Step 1: CDK deploy (rebuilds Docker image, pushes to ECR, updates stack)
echo "Running cdk deploy..."
cdk deploy --require-approval never

# Step 2: Force ECS service to pull the new image
echo "Forcing ECS service redeployment..."

# Find the cluster containing "StudentServicesPhase2"
CLUSTER_ARN=$(aws ecs list-clusters --query "clusterArns[?contains(@, 'StudentServicesPhase2')]" --output text)

if [ -z "$CLUSTER_ARN" ]; then
    echo "ERROR: Could not find ECS cluster containing 'StudentServicesPhase2'"
    exit 1
fi

echo "Found cluster: $CLUSTER_ARN"

SERVICE_NAME="StudentServicesPhase2-stl-front"

aws ecs update-service \
    --cluster "$CLUSTER_ARN" \
    --service "$SERVICE_NAME" \
    --force-new-deployment

echo "=== Force deploy complete ==="
echo "ECS service is pulling the new image. It may take a few minutes for the new task to become healthy."
