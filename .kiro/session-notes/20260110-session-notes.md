# Session Notes - January 10, 2026

## Session Overview
After two days of reviewing Bedrock AgentCore sample code, made a strategic architectural decision to simplify the DATASCI 210 course focus. Decided to remove Bedrock AgentCore complexity and focus on monolithic Streamlit applications that orchestrate multiple Strands Agents-based agents within a single ECS Fargate deployment.

## Key Decisions Made

### Bedrock AgentCore Analysis Conclusion
- **Finding**: Bedrock AgentCore is excellent for stable, independently scalable microservices
- **Decision**: Too complex for DATASCI 210 course objectives
- **Rationale**: Course focus should be on model training, deployment, and application development - not microservice orchestration

### Simplified Architecture Direction
- **Keep**: Strands Agents for building multiple agents and tools
- **Keep**: Python Streamlit app development (local Ubuntu/Windows)
- **Keep**: CDK deploy for ECS Fargate deployment
- **Keep**: Bedrock and SageMaker AI model integration choices
- **Remove**: Bedrock AgentCore independent runtime complexity
- **Remove**: MCP servers on independent AgentCore runtimes

### Course Alignment
The simplified approach better serves DATASCI 210 capstone project requirements:
1. **Model Training/Fine-tuning**: Focus on predictive models and generative model fine-tuning
2. **Model Deployment**: Deploy and host models on AWS
3. **Agentic AI Application**: Build applications that use these models in a cohesive way

## Issues & Resolutions
- **Issue**: Bedrock AgentCore adds unnecessary complexity dimension
  - **Resolution**: Maintain monolithic Streamlit app approach with embedded agents

## Next Steps
- [ ] Update workshop4-architecture-refactoring spec to reflect simplified direction
- [ ] Remove Bedrock AgentCore references from documentation
- [ ] Focus documentation on Strands Agents + Streamlit + ECS Fargate pattern
- [ ] Maintain Bedrock vs SageMaker AI model choice capabilities
- [ ] Ensure local development to production deployment journey remains clear

## Resources
- Existing workshop4 documentation structure provides good foundation
- Current multi_agent_bedrock and deploy_multi_agent_bedrock implementations align with simplified direction
- Architecture refactoring spec needs updates to remove AgentCore complexity

## Architectural Decision Impact
This decision simplifies the learning journey while maintaining the core value proposition:
- Students learn model training and deployment
- Students build practical agentic applications
- Deployment patterns remain production-ready
- Complexity is focused on AI/ML rather than microservice orchestration