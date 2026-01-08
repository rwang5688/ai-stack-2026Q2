# Implementation Plan: Multi-Agent Bedrock Deployment Fixes

## Overview

This implementation plan addresses two critical issues: (1) debugging and fixing the CDK stack where CloudFront bypasses Cognito authentication, and (2) adding the missing STRANDS_KNOWLEDGE_BASE_ID environment variable to the Docker container. The plan also includes updating documentation to provide three focused sections for builders.

## Tasks

- [x] 1. Analyze and debug existing CDK authentication issue
  - Investigate why existing Cognito resources don't enforce authentication at CloudFront
  - Review current CDK stack configuration in deploy_multi_agent_bedrock/cdk/cdk_stack.py
  - Identify missing authentication integration components
  - Document findings and root cause of authentication bypass
  - _Requirements: 1.1, 1.2, 4.1, 4.2_

- [ ] 2. Fix CloudFront Cognito authentication integration
  - [ ] 2.1 Add Lambda@Edge function for authentication
    - Create Lambda@Edge function to validate JWT tokens from Cognito
    - Implement redirect logic to Cognito hosted UI for unauthenticated requests
    - Add proper error handling and logging for authentication failures
    - _Requirements: 1.1, 1.3, 4.3_

  - [ ] 2.2 Update CloudFront distribution configuration
    - Modify existing CloudFront distribution to use Lambda@Edge function
    - Configure viewer-request event type for authentication checking
    - Maintain existing custom header protection for ALB
    - _Requirements: 1.2, 4.2, 4.4_

  - [ ] 2.3 Integrate with existing Cognito resources
    - Use existing Cognito UserPool and UserPoolClient from CDK stack
    - Leverage existing Secrets Manager configuration for Cognito parameters
    - Ensure Lambda@Edge can access Cognito configuration securely
    - _Requirements: 4.1, 4.3_

  - [ ]* 2.4 Write property test for authentication enforcement
    - **Property 1: Authentication Enforcement**
    - **Validates: Requirements 1.1, 1.2, 4.2, 4.4**

  - [ ]* 2.5 Write property test for authentication flow management
    - **Property 2: Authentication Flow Management**
    - **Validates: Requirements 1.3, 1.4, 1.5**

- [ ] 3. Checkpoint - Authentication fix complete
  - Deploy updated CDK stack with authentication integration
  - Test unauthenticated access redirects to Cognito sign-in
  - Verify successful authentication grants access to Streamlit app
  - Validate session management and sign-out functionality
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_

- [ ] 4. Synchronize source code between local and deployed versions
  - [ ] 4.1 Copy latest multi-agent source code to docker_app
    - Copy app.py from workshop4/multi_agent_bedrock/ to workshop4/deploy_multi_agent_bedrock/docker_app/
    - Copy all assistant files (math_assistant.py, english_assistant.py, etc.)
    - Copy cross_platform_tools.py and other supporting files
    - Ensure requirements.txt includes all necessary dependencies
    - _Requirements: 2.1, 2.2, 2.3_

  - [ ] 4.2 Verify source code synchronization
    - Compare files between multi_agent_bedrock and docker_app directories
    - Ensure identical functionality between local and deployed versions
    - Test that copied files maintain all knowledge base integration features
    - _Requirements: 2.2, 2.3_

- [ ] 5. Add STRANDS_KNOWLEDGE_BASE_ID environment variable to Dockerfile
  - [x] 5.1 Update existing Dockerfile
    - Add STRANDS_KNOWLEDGE_BASE_ID environment variable with current value "IMW46CITZE"
    - Include clear documentation comments for builders to replace with their own KB ID
    - Maintain existing Dockerfile structure and commands
    - _Requirements: 2.1, 5.1, 5.3_

  - [ ] 5.2 Test Docker container environment configuration
    - Build Docker image with updated Dockerfile
    - Verify STRANDS_KNOWLEDGE_BASE_ID environment variable is set correctly
    - Test container startup and environment variable accessibility
    - _Requirements: 5.1, 5.2_

  - [ ]* 5.3 Write property test for environment variable configuration
    - **Property 3: Environment Variable Configuration**
    - **Validates: Requirements 2.1, 5.1, 5.2**

- [ ] 6. Test knowledge base functionality in deployed environment
  - [ ] 6.1 Deploy updated Docker container
    - Rebuild and deploy container with environment variable
    - Verify deployment succeeds with updated configuration
    - Test container health and startup logs
    - _Requirements: 2.1, 5.2_

  - [ ] 6.2 Validate knowledge base operations
    - Test knowledge storage functionality: "Remember that my name is John"
    - Test knowledge retrieval functionality: "What is my name?"
    - Verify both operations work correctly in deployed environment
    - Test error handling when knowledge base is unavailable
    - _Requirements: 2.2, 2.3, 2.4_

  - [ ]* 6.3 Write property test for knowledge base integration
    - **Property 4: Knowledge Base Integration**
    - **Validates: Requirements 2.2, 2.3, 2.4**

- [ ] 7. Checkpoint - Environment variable and knowledge base functionality complete
  - Ensure Docker container has proper environment variable configuration
  - Validate knowledge base storage and retrieval work in production
  - Test error handling for missing environment variables
  - Verify builder customization scenarios work correctly
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 5.1, 5.2_

- [ ] 8. Update MULTI_AGENT_BEDROCK.md documentation
  - [ ] 8.1 Restructure documentation into three focused sections
    - Create "Local Development and Debugging" section for multi_agent_bedrock usage
    - Create "Deployment Process" section for copying files, setting KB ID, and CDK commands
    - Create "Production Usage with Authentication" section for Cognito user management
    - Remove overwhelming detail and focus on actionable steps
    - _Requirements: 3.1, 3.5_

  - [ ] 8.2 Add deployment validation instructions
    - Include steps to verify Cognito authentication is working
    - Add knowledge base functionality testing instructions
    - Provide troubleshooting guide for common authentication and KB issues
    - Include clear examples for each section
    - _Requirements: 3.2, 3.3, 3.4_

  - [ ]* 8.3 Write example test for documentation structure
    - **Validates: Requirements 3.1**

- [ ] 9. Final integration testing and validation
  - [ ] 9.1 End-to-end authentication and functionality testing
    - Test complete flow from unauthenticated access to successful sign-in
    - Verify knowledge base functionality works with authentication
    - Test session management, sign-out, and re-authentication
    - Validate all three documentation sections with actual deployment
    - _Requirements: 1.1, 1.2, 1.3, 2.2, 2.3_

  - [ ] 9.2 Builder experience validation
    - Follow documentation to deploy from scratch
    - Test customization scenarios (replacing KB ID)
    - Verify error messages are helpful and actionable
    - Validate troubleshooting instructions work correctly
    - _Requirements: 3.2, 3.3, 3.4, 3.5_

  - [ ]* 9.3 Write property test for CDK Cognito integration
    - **Property 5: CDK Cognito Integration**
    - **Validates: Requirements 4.1, 4.3**

  - [ ]* 9.4 Write property test for environment-specific configuration support
    - **Property 6: Environment-Specific Configuration Support**
    - **Validates: Requirements 5.4, 5.5**

- [ ] 10. Final checkpoint - All fixes and documentation complete
  - Ensure CloudFront properly enforces Cognito authentication
  - Verify knowledge base functionality works in deployed environment
  - Validate documentation provides clear, actionable guidance
  - Confirm builder experience is smooth and well-documented
  - _Requirements: 1.1, 1.2, 1.3, 2.1, 2.2, 2.3, 3.1, 3.2, 3.3, 3.4_

## Notes

- Tasks marked with `*` are optional and can be skipped for faster implementation
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation of fixes
- Property tests validate universal correctness properties
- Unit tests validate specific examples and edge cases
- Focus on debugging existing CDK stack rather than rebuilding from scratch
- Maintain existing infrastructure while adding missing authentication integration
- Ensure source code synchronization between local and deployed versions