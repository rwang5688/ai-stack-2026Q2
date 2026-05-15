# Workshop 3: Deploy Inference Endpoints

Deploy the fine-tuned model from Workshop 2 to SageMaker Inference endpoints using two deployment patterns: serverless (CPU, pay-per-request) and provisioned (GPU, always-on).

## Topics Covered

- SageMaker Real-Time Inference (provisioned GPU endpoints)
- SageMaker Serverless Inference (CPU, pay-per-request)
- Deep Learning Container (DLC) image selection
- DLC version compatibility and troubleshooting
- Cost trade-offs between deployment patterns

## Contents

| Directory | Description |
|-----------|-------------|
| [deploy_serverless/](deploy_serverless/) | Serverless endpoint deployment (CPU, cold starts, minimal cost) |
| [deploy_provisioned/](deploy_provisioned/) | Provisioned GPU endpoint deployment (ml.g6.xlarge, no cold starts) |

## Deployment Comparison

| Aspect | Serverless | Provisioned |
|--------|-----------|-------------|
| Hardware | Managed CPU | ml.g6.xlarge (NVIDIA L4) |
| Cold start | 30-60 seconds | None |
| Cost model | Per-request | ~$0.80/hour |
| Best for | Demos, infrequent traffic | Production, low-latency |

## Outcome

A deployed SageMaker endpoint serving the fine-tuned model. The provisioned XGBoost endpoint is reused in Workshop 4 for the Loan Application agent.
