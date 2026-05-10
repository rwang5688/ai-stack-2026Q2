#!/bin/bash
set -e

# Note: On Linux/macOS, make this executable with: chmod +x deploy.sh

echo "============================================"
echo "Student Services Infrastructure Deployment"
echo "============================================"
echo ""

echo "Step 1: Deploying CloudFormation stack..."
echo "-------------------------------------------"
aws cloudformation deploy \
  --stack-name student-services-infra \
  --template-file cloudformation/student-services-infra.yaml \
  --capabilities CAPABILITY_IAM \
  --region us-west-2

echo ""
echo "Step 2: Populating seed data..."
echo "-------------------------------------------"
python scripts/populate_seed_data.py --region us-west-2 "$@"

echo ""
echo "============================================"
echo "Deployment complete!"
echo "============================================"
