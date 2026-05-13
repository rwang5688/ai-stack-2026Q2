#!/bin/bash
set -e

# Uploads data to S3, seeds DynamoDB, triggers KB ingestion, writes SSM params.
# Usage: ./populate-seed-data.sh --xgboost-endpoint-name <name>
#        ./populate-seed-data.sh   (skips XGBoost endpoint if not provided)

echo "Populating seed data..."
python scripts/populate_seed_data.py --region us-west-2 "$@"
echo "Done."
