# AI Stack Workshop Series (2026 Q2)

A progressive workshop series covering the full AI/ML stack on AWS — from infrastructure and model training through inference deployment to production agentic applications.

## Workshops

| Workshop | Topic | Key Services |
|----------|-------|--------------|
| [Workshop 1](workshop1/) | Cloud Development Environment | CloudFormation, EC2, CloudFront, ALB |
| [Workshop 2](workshop2/) | Fine-Tune a Language Model | SageMaker AI (managed GPU), HuggingFace Transformers |
| [Workshop 3](workshop3/) | Deploy Inference Endpoints | SageMaker Inference (Serverless + Provisioned GPU) |
| [Workshop 4](workshop4/) | Multi-Agent Applications | Strands Agents SDK, Bedrock, AgentCore, ECS |

## Workshop Progression

```
Workshop 1: Cloud Dev Environment (CloudFormation)
            Provides the code-server used for CDK deploy / Docker build in Workshop 4

Workshop 2: Fine-Tune distilgpt2 (SageMaker managed GPU instance + HuggingFace)
     │
     ▼
Workshop 3: Deploy fine-tuned model (SageMaker Serverless + GPU Inference Endpoints)

Workshop 4: Build Multi-Agent App → Containerize → Decompose to Microservices
            Phase 1 → Phase 2 → Phase 3
```

- **Workshop 1** contains an optional infrastructure topic. It deploys a code-server that is useful for Workshop 4's CDK and Docker workflows.
- **Workshops 2 → 3** are sequential: train a model, then deploy it.
- **Workshop 4 Phases 1 → 2 → 3** are sequential: monolithic agentic AI app → containerized monolithic agentic AI app → agents as microservices.

## Prerequisites

- AWS Account with appropriate permissions
- AWS CLI configured
- Python 3.12+
- Familiarity with AWS console and basic CLI usage

## Region

All resources deploy to **us-west-2**.
