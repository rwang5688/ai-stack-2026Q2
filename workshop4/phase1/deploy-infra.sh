#!/bin/bash
set -e

# Deploys the student-services-infra CloudFormation stack.
# Usage: ./deploy-infra.sh

echo "Deploying student-services-infra CloudFormation stack..."
aws cloudformation deploy \
  --stack-name student-services-infra \
  --template-file cloudformation/student-services-infra.yaml \
  --capabilities CAPABILITY_NAMED_IAM \
  --region us-west-2

echo "Done."
