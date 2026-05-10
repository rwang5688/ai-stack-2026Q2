# Implementation Plan: Workshop4 SageMaker Code Editor Deployment

## Overview

This implementation plan guides the deployment of a fixed multi-agent Streamlit application from SageMaker Code Editor to AWS ECS Fargate. The plan focuses on applying the infinite loop fix to the production code, building and validating the Docker container, deploying via CDK, and verifying production functionality.

## Tasks

- [ ] 1. Configure Docker for x86_64 architecture
  - [x] 1.1 Update Dockerfile platform specification
    - Open `workshop4/deploy_multi_agent/docker_app/Dockerfile`
    - Change `FROM --platform=linux/arm64 python:3.12` to `FROM --platform=linux/amd64 python:3.12`
    - Add comment explaining architecture choice for SageMaker Code Editor compatibility
    - _Requirements: 2.1, 2.2_
  
  - [x] 1.2 Verify CDK stack uses x86_64 instance types
    - Open `workshop4/deploy_multi_agent/cdk/cdk_stack.py`
    - Confirm ECS task definition uses x86_64 compatible instance types
    - Update if necessary to match Docker platform
    - _Requirements: 2.3_

- [ ] 2. Apply infinite loop fix to deployment application code
  - [x] 2.1 Update `determine_action()` function to remove `use_agent` tool calls
    - Modify `workshop4/deploy_multi_agent/docker_app/app.py`
    - Replace agent-based classification with direct LLM calls
    - Use structured prompt for classification (return "teacher" or "knowledge")
    - Remove `use_agent` from tools list in the function
    - _Requirements: 1.1, 1.3_
  
  - [x] 2.2 Update `determine_kb_action()` function to remove `use_agent` tool calls
    - Modify the same file
    - Replace agent-based classification with direct LLM calls
    - Use structured prompt for classification (return "store" or "retrieve")
    - Remove `use_agent` from tools list in the function
    - _Requirements: 1.2, 1.3_
  
  - [x] 2.3 Verify Cognito authentication logic is preserved
    - Confirm authentication section at top of file is unchanged
    - Verify logout function remains intact
    - Ensure authentication UI components in sidebar are preserved
    - _Requirements: 1.4_
  
  - [x] 2.4 Verify UI elements and session state management are preserved
    - Confirm model selection dropdown works
    - Verify agent type selection works
    - Ensure clear conversation button is functional
    - Check session state initialization and management
    - _Requirements: 1.5_

- [ ] 3. Test the fixed application locally in SageMaker Code Editor
  - [x] 3.1 Run the application locally with Streamlit
    - Navigate to `workshop4/deploy_multi_agent/docker_app/`
    - Run `streamlit run app.py`
    - Verify application starts without errors
    - _Requirements: 5.2_
  
  - [x] 3.2 Test query routing with sample queries
    - Submit educational queries (math, programming, language)
    - Submit knowledge base queries (store and retrieve)
    - Verify queries complete within reasonable time (< 10 seconds)
    - Confirm no infinite loop behavior in terminal output
    - _Requirements: 2.5_
  
  - [x]* 3.3 Write property test for infinite loop prevention
    - **Property 2: Infinite Loop Prevention**
    - **Validates: Requirements 2.5, 4.3, 4.4, 6.1, 6.2**
    - Create test file `tests/test_routing_properties.py`
    - Use hypothesis to generate random queries
    - Test that all queries complete within 10-second timeout
    - Run with minimum 100 iterations

- [ ] 4. Checkpoint - Verify local application works correctly
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 5. Build and validate Docker container
  - [x] 5.1 Build Docker container locally
    - Navigate to `workshop4/deploy_multi_agent/docker_app/`
    - Run `docker build -t workshop4-app .`
    - Verify build completes without errors
    - Check that all dependencies install successfully
    - _Requirements: 2.1_
  
  - [x] 5.2 Test Docker container locally
    - Run `docker run -p 8501:8501 workshop4-app`
    - Access application at `http://localhost:8501`
    - Verify application starts and serves correctly
    - _Requirements: 2.3_
  
  - [x] 5.3 Test application functionality in container
    - Submit test queries through the containerized application
    - Verify query routing works without infinite loops
    - Test authentication flows (if possible locally)
    - _Requirements: 2.4, 2.5_
  
  - [x]* 5.4 Write property test for dependency completeness
    - **Property 5: Dependency Completeness**
    - **Validates: Requirements 2.2**
    - Create test file `tests/test_container_properties.py`
    - Parse requirements.txt for all packages
    - Test that each package is importable in container
    - Run test inside Docker container

- [ ] 6. Checkpoint - Verify Docker container works correctly
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 7. Deploy application using CDK from SageMaker Code Editor
  - [ ] 7.1 Verify CDK environment is configured
    - Check AWS credentials are configured
    - Verify CDK is installed (`cdk --version`)
    - Confirm AWS region is set correctly
    - _Requirements: 5.3_
  
  - [ ] 7.2 Synthesize CDK stack
    - Navigate to `workshop4/deploy_multi_agent/cdk/`
    - Run `cdk synth`
    - Verify CloudFormation template generates without errors
    - Review synthesized template for correctness
    - _Requirements: 3.1_
  
  - [ ] 7.3 Deploy CDK stack to AWS
    - Run `cdk deploy`
    - Confirm deployment prompts and approve changes
    - Wait for deployment to complete
    - Capture CloudFront distribution URL from outputs
    - _Requirements: 3.2, 3.3_
  
  - [ ] 7.4 Verify AWS resources are created
    - Check ECS Fargate service is running
    - Verify Application Load Balancer is healthy
    - Confirm Cognito User Pool is created
    - Check VPC and networking resources exist
    - _Requirements: 3.4, 3.5_

- [ ] 8. Checkpoint - Verify deployment completed successfully
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 9. Verify production application functionality
  - [ ] 9.1 Test initial access and Cognito authentication
    - Access the CloudFront distribution URL
    - Verify redirect to Cognito login page
    - Create test user in Cognito User Pool
    - Log in with test credentials
    - Verify successful authentication and redirect to application
    - _Requirements: 4.1, 4.2_
  
  - [ ] 9.2 Test educational query routing in production
    - Submit various educational queries (math, programming, language)
    - Verify queries are routed to appropriate agents
    - Confirm responses are generated without infinite loops
    - Monitor query completion times
    - _Requirements: 4.3_
  
  - [ ] 9.3 Test knowledge base query routing in production
    - Submit knowledge base store queries
    - Submit knowledge base retrieve queries
    - Verify queries complete without infinite loops
    - Confirm knowledge base operations work correctly
    - _Requirements: 4.4_
  
  - [ ] 9.4 Test logout functionality
    - Click logout button
    - Verify session is cleared
    - Confirm redirect to Cognito logout page
    - Verify cannot access application without re-authentication
    - _Requirements: 4.5_
  
  - [ ]* 9.5 Write property test for authentication preservation
    - **Property 1: Authentication Preservation**
    - **Validates: Requirements 1.4, 2.4**
    - Create test file `tests/test_auth_properties.py`
    - Test authentication flows with various credential formats
    - Verify session creation and management
    - Run with minimum 100 iterations
  
  - [ ]* 9.6 Write property test for UI state preservation
    - **Property 4: UI State Preservation**
    - **Validates: Requirements 1.5**
    - Test UI elements remain functional after fix
    - Verify session state persists across interactions
    - Test with random user interactions

- [ ] 10. Validate fix effectiveness in production
  - [ ] 10.1 Monitor CloudWatch logs for recursive calls
    - Access CloudWatch Logs for ECS container
    - Search for patterns indicating recursive agent calls
    - Verify no `use_agent` tool calls in routing functions
    - Confirm logs show normal query processing
    - _Requirements: 6.4_
  
  - [ ] 10.2 Test concurrent user scenarios
    - Simulate multiple concurrent users (3-5 users)
    - Submit queries simultaneously from different sessions
    - Verify all queries complete without infinite loops
    - Monitor application performance and response times
    - _Requirements: 6.1_
  
  - [ ] 10.3 Test edge case queries
    - Submit empty queries
    - Submit very long queries (> 1000 characters)
    - Submit queries with special characters
    - Submit queries in different languages
    - Verify all edge cases complete within timeout
    - _Requirements: 6.2_
  
  - [ ]* 10.4 Write property test for no recursive agent calls
    - **Property 3: No Recursive Agent Calls**
    - **Validates: Requirements 6.4**
    - Create test file `tests/test_logging_properties.py`
    - Generate random queries and capture logs
    - Test that logs contain no recursive agent call patterns
    - Verify no `use_agent` calls in routing function logs

- [ ] 11. Final checkpoint - Verify production deployment is stable
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 12. Document deployment workflow
  - [ ] 12.1 Update deployment documentation
    - Document the infinite loop fix applied
    - Record CDK deployment commands used
    - Note CloudFront distribution URL
    - Document Cognito User Pool configuration
    - _Requirements: 5.1, 5.3, 5.4_
  
  - [ ] 12.2 Create troubleshooting guide
    - Document common deployment issues and solutions
    - Include debugging steps for infinite loop issues
    - Add CloudWatch log analysis procedures
    - Document redeployment workflow
    - _Requirements: 5.5_

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation throughout deployment
- Property tests validate universal correctness properties
- Unit tests validate specific examples and edge cases
- The deployment workflow is designed to be executed from SageMaker Code Editor
- All CDK commands should be run from the `workshop4/deploy_multi_agent/cdk/` directory
- CloudWatch logs are essential for validating the infinite loop fix in production
