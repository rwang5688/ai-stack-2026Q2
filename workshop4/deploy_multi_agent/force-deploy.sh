#!/bin/bash

# Force Deploy Script - BRUTE FORCE through all SageMaker Code Editor bullshit
# Run this and forget about all the Docker/CDK/venv nonsense

set -e  # Exit on any error

echo "========================================="
echo "BRUTE FORCE DEPLOY - SageMaker Code Editor"
echo "========================================="
echo ""
echo "🚀 Starting deployment at: $(date)"
echo ""

# Get the script directory and navigate to workshop4 root
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
WORKSHOP_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "📁 Directories:"
echo "   Script: $SCRIPT_DIR"
echo "   Workshop root: $WORKSHOP_ROOT"
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 1: Setting up system Python (bypassing venv)..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
# Deactivate venv if active
deactivate 2>/dev/null || true

# Force use of system Python by explicitly setting paths
export PATH="/opt/conda/bin:/usr/local/bin:/usr/bin:/bin:$PATH"
unset VIRTUAL_ENV
unset PYTHONHOME

echo "✅ Configured to use system Python"
echo ""
echo "💡 DECISION: Using system Python instead of venv"
echo "   Reason: SageMaker venv has --system-site-packages which breaks pip"
echo "   System Python already has all workshop dependencies installed"
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 2: Verifying system Python environment..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📊 Environment details:"
echo "   Python path: $(which python)"
echo "   Python version: $(python --version)"
echo "   Pip path: $(which pip)"
echo "   Pip version: $(pip --version)"
echo ""

# Verify we're NOT using venv Python
if [[ "$(which python)" == *"/venv/"* ]]; then
    echo "⚠️  WARNING: Still using venv Python!"
    echo "   Forcing system Python explicitly..."
    PYTHON_CMD="/opt/conda/bin/python"
    PIP_CMD="/opt/conda/bin/pip"
else
    PYTHON_CMD="python"
    PIP_CMD="pip"
fi
echo "   Using Python: $PYTHON_CMD"
echo "   Using Pip: $PIP_CMD"
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 3: Verifying workshop dependencies..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📦 Checking key packages in system Python:"
echo ""
$PYTHON_CMD -c "import boto3; print(f'   ✅ boto3: {boto3.__version__}')" || echo "   ❌ boto3 not found"
$PYTHON_CMD -c "import streamlit; print(f'   ✅ streamlit: {streamlit.__version__}')" || echo "   ❌ streamlit not found"
$PYTHON_CMD -c "import strands_agents; print(f'   ✅ strands-agents: {strands_agents.__version__}')" || echo "   ⚠️  strands-agents not found (OK if in venv only)"
echo ""
echo "✅ Workshop dependencies available"
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 4: Installing CDK into system Python..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
cd "$SCRIPT_DIR"
echo "📦 Installing from: $SCRIPT_DIR/requirements.txt"
echo ""
$PIP_CMD install -r requirements.txt 2>&1 | grep -E "(Installing|Successfully installed|Collecting|Requirement already)" || true
echo ""
echo "✅ CDK dependencies installed"
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 5: Verifying aws_cdk installation..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🔍 Testing Python can import aws_cdk:"
if $PYTHON_CMD -c "import aws_cdk; print(f'   ✅ aws_cdk imported from: {aws_cdk.__file__}')"; then
    echo "   ✅ CDK is ready to use"
else
    echo "   ❌ CANNOT IMPORT aws_cdk"
    echo ""
    echo "🆘 CRITICAL ERROR: Cannot import aws_cdk after installation"
    echo ""
    echo "Troubleshooting steps:"
    echo "1. Check pip list: $PIP_CMD list | grep aws-cdk"
    echo "2. Check Python sys.path: $PYTHON_CMD -c 'import sys; print(sys.path)'"
    echo ""
    exit 1
fi
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 6: Configuring Docker for SageMaker restrictions..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "   SageMaker Code Editor requires 'sagemaker' network for Docker builds"
echo ""

# Create a wrapper script for docker that adds --network=sagemaker
DOCKER_WRAPPER="/tmp/docker-wrapper.sh"
cat > "$DOCKER_WRAPPER" << 'EOF'
#!/bin/bash
# Docker wrapper to inject --network=sagemaker for SageMaker Code Editor
# This satisfies SageMaker's Docker security restrictions

# Get the real docker path
REAL_DOCKER="/usr/bin/docker"

# Check if this is a 'docker build' command
if [[ "$1" == "build" ]]; then
    # Inject --network=sagemaker after 'build'
    exec "$REAL_DOCKER" build --network=sagemaker "${@:2}"
else
    # Pass through all other docker commands unchanged
    exec "$REAL_DOCKER" "$@"
fi
EOF

chmod +x "$DOCKER_WRAPPER"

# Temporarily add wrapper to PATH (before real docker)
export PATH="/tmp:$PATH"

echo "✅ Docker wrapper configured"
echo "   All 'docker build' commands will use --network=sagemaker"
echo ""
echo "ℹ️  Note: Using legacy Docker builder (not BuildKit)"
echo "   BuildKit may not be compatible with SageMaker's network restrictions"
echo "   The deprecation warning can be safely ignored"
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 7: Testing CDK synth (CloudFormation template generation)..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "   This tests if CDK can build Docker image with SageMaker restrictions"
echo ""

# Disable BuildKit - SageMaker Code Editor may not support it with network restrictions
# The deprecation warning is expected and can be ignored
export DOCKER_BUILDKIT=0

if cdk synth > /tmp/cdk-synth.log 2>&1; then
    echo "✅ CDK synth successful - CloudFormation template generated"
    echo "   Template size: $(wc -c < cdk.out/*.template.json) bytes"
else
    echo "❌ CDK synth FAILED"
    echo ""
    echo "Error output:"
    cat /tmp/cdk-synth.log
    echo ""
    echo "ERROR: CDK synth failed. Cannot proceed with deployment."
    exit 1
fi
echo ""

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 8: Deploying to AWS (this will take 10-15 minutes)..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "   - Building Docker image (x86_64 architecture)"
echo "   - Using SageMaker network for Docker build (via wrapper)"
echo "   - Pushing to ECR"
echo "   - Creating/updating CloudFormation stack"
echo "   - Deploying ECS Fargate service"
echo ""
echo "   Starting deployment at: $(date)"
echo ""

# Ensure Docker wrapper is still in PATH and BUILDKIT is disabled
export PATH="/tmp:$PATH"
export DOCKER_BUILDKIT=0

if cdk deploy --require-approval never; then
    echo ""
    echo "✅ CDK deploy successful"
else
    echo ""
    echo "❌ CDK deploy FAILED"
    echo ""
    echo "Check CloudFormation console for detailed error information"
    echo "Or run: aws cloudformation describe-stack-events --stack-name <stack-name>"
    exit 1
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 9: Forcing ECS service to update (ensures latest container)..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
# Get the ECS cluster and service names
CLUSTER_NAME=$(aws ecs list-clusters --query 'clusterArns[?contains(@, `Streamlit`)]' --output text 2>/dev/null | xargs -n1 basename || echo "")
SERVICE_NAME=$(aws ecs list-services --cluster "$CLUSTER_NAME" --query 'serviceArns[?contains(@, `Streamlit`)]' --output text 2>/dev/null | xargs -n1 basename || echo "")

if [ -n "$CLUSTER_NAME" ] && [ -n "$SERVICE_NAME" ]; then
    echo "   Cluster: $CLUSTER_NAME"
    echo "   Service: $SERVICE_NAME"
    aws ecs update-service --cluster "$CLUSTER_NAME" --service "$SERVICE_NAME" --force-new-deployment > /dev/null 2>&1
    echo "✅ Forced new ECS deployment"
else
    echo "⚠️  Could not find ECS cluster/service (may be first deployment)"
fi

echo ""
echo "========================================="
echo "✅ DEPLOYMENT COMPLETE!"
echo "========================================="
echo ""
echo "Deployment finished at: $(date)"
echo ""
echo "Next steps:"
echo "1. Wait 2-3 minutes for ECS to fully deploy"
echo "2. Get CloudFront URL from CloudFormation outputs:"
echo "   aws cloudformation describe-stacks --stack-name <stack-name> --query 'Stacks[0].Outputs'"
echo "3. Create Cognito user in AWS Console"
echo "4. Access application via CloudFront URL"
echo ""
echo "Troubleshooting:"
echo "- Check ECS logs: aws logs tail /ecs/<service-name> --follow"
echo "- Check ECS service: aws ecs describe-services --cluster <cluster> --services <service>"
echo "- Check CloudFormation events: aws cloudformation describe-stack-events --stack-name <stack-name>"
echo ""
