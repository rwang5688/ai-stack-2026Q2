#!/bin/bash

# Force Deploy Script - Ensures complete Docker rebuild and ECS service update
# This script forces CDK to rebuild the Docker image without using cache

echo "========================================="
echo "Force Deploy - Complete Rebuild"
echo "========================================="
echo ""

# Navigate to the CDK directory
cd "$(dirname "$0")"

echo "Step 1: Cleaning up local Docker cache..."
# Remove any cached Docker images for this project
docker system prune -f

echo ""
echo "Step 2: Running CDK deploy with --force flag..."
# Deploy with force flag to ensure CloudFormation updates
cdk deploy --force --require-approval never

echo ""
echo "Step 3: Forcing ECS service to update..."
# Get the ECS cluster and service names
CLUSTER_NAME=$(aws ecs list-clusters --query 'clusterArns[?contains(@, `Streamlit`)]' --output text | xargs -n1 basename)
SERVICE_NAME=$(aws ecs list-services --cluster "$CLUSTER_NAME" --query 'serviceArns[?contains(@, `Streamlit`)]' --output text | xargs -n1 basename)

if [ -n "$CLUSTER_NAME" ] && [ -n "$SERVICE_NAME" ]; then
    aws ecs update-service --cluster "$CLUSTER_NAME" --service "$SERVICE_NAME" --force-new-deployment > /dev/null 2>&1
    echo "✅ Forced new deployment"
else
    echo "⚠️  Could not find ECS cluster/service"
fi

echo ""
echo "Done. Wait 2-3 minutes for ECS to deploy."

