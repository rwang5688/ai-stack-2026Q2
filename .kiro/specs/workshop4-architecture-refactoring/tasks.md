# Implementation Plan: Workshop 4 Architecture Refactoring

## Overview

This implementation plan refactors the Workshop 4 multi-agent architecture to simplify naming conventions, add model choice capabilities, prepare for AgentCore integration, and add MCP-enabled Lambda functions. The refactoring will demonstrate the contrast between local development and production deployment while showcasing different model hosting options.

## Tasks

- [ ] 1. Directory Renaming and Reference Updates
  - Rename "deploy_multi_agent_bedrock" to "deploy_multi_agent"
  - Rename "multi_agent_bedrock" to "multi_agent"
  - Update all file imports, documentation, and configuration files
  - Validate all references are updated correctly
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_

- [ ]* 1.1 Write property test for directory rename consistency
  - **Property 1: Directory Rename Consistency**
  - **Validates: Requirements 1.3, 1.4, 1.5**

- [ ] 2. Add Model Selection Interface to Local Application
  - [ ] 2.1 Create model configuration interface in multi_agent app
    - Add dropdown selection for Bedrock Nova Pro and SageMaker AI GPT OSS
    - Implement model switching logic with configuration updates
    - Add model status indicators and connection validation
    - _Requirements: 2.1, 2.5_

  - [ ] 2.2 Implement SageMaker AI integration for GPT OSS models
    - Create SageMaker AI model client and endpoint configuration
    - Implement standardized interface matching Bedrock patterns
    - Add error handling and fallback mechanisms
    - _Requirements: 2.3_

  - [ ] 2.3 Update agent configurations for dynamic model switching
    - Modify all specialized agents to use selected model configuration
    - Ensure seamless switching between Bedrock and SageMaker AI
    - Maintain existing Bedrock functionality and tool integrations
    - _Requirements: 2.2, 2.4_

  - [ ]* 2.4 Write property test for model integration functionality
    - **Property 2: Model Integration Functionality**
    - **Validates: Requirements 2.2, 2.3, 2.4**

- [ ] 3. Checkpoint - Model selection functionality complete
  - Ensure model dropdown provides correct options
  - Validate both Bedrock and SageMaker AI models work correctly
  - Verify agent configurations update properly when switching models
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_

- [ ] 4. Prepare Architecture for AgentCore Integration
  - [ ] 4.1 Refactor agent code for modular design
    - Extract agent logic into separate modules with clear interfaces
    - Implement modular design patterns supporting future AgentCore deployment
    - Create agent communication protocols and message formats
    - _Requirements: 3.2, 3.4_

  - [ ] 4.2 Document AgentCore migration path
    - Create detailed migration planning documentation
    - Document current embedded architecture vs future AgentCore architecture
    - Provide step-by-step migration guide and timeline
    - _Requirements: 3.3_

  - [ ] 4.3 Maintain current functionality while preparing for migration
    - Ensure all existing multi-agent capabilities continue to work
    - Keep Strands Agents embedded in Streamlit app for current version
    - Validate backward compatibility during refactoring
    - _Requirements: 3.1, 3.5_

  - [ ]* 4.4 Write property test for AgentCore preparation architecture
    - **Property 3: AgentCore Preparation Architecture**
    - **Validates: Requirements 3.2, 3.4, 3.5**

- [ ] 5. Checkpoint - AgentCore preparation complete
  - Ensure agent code is properly modularized
  - Validate migration documentation is comprehensive
  - Verify all existing functionality is preserved
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_

- [ ] 6. Implement MCP Integration with Classification Model
  - [ ] 6.1 Create MCPified Lambda function
    - Implement AWS Lambda function with Model Context Protocol interface
    - Create wrapper around SageMaker AI trained classification model
    - Implement standardized tool interface for agent integration
    - _Requirements: 4.1_

  - [ ] 6.2 Set up SageMaker AI classification model
    - Deploy or reference a trained SageMaker AI classification model
    - Configure real-time inference endpoint for classification tasks
    - Implement model versioning and deployment management
    - _Requirements: 4.5_

  - [ ] 6.3 Integrate MCP Lambda with AgentCore Gateway
    - Configure Bedrock AgentCore Gateway for MCP Lambda access
    - Implement authentication and authorization for tool access
    - Set up request routing and response handling
    - _Requirements: 4.2_

  - [ ] 6.4 Enable agent access to classification capabilities
    - Integrate MCP tools with Strands Agents tool system
    - Demonstrate end-to-end agent access to classification via MCP
    - Add error handling and response formatting for agent consumption
    - _Requirements: 4.4_

  - [ ]* 6.5 Write property test for MCP integration functionality
    - **Property 4: MCP Integration Functionality**
    - **Validates: Requirements 4.1, 4.2, 4.3, 4.4**

- [ ] 7. Checkpoint - MCP integration complete
  - Ensure MCP Lambda function works correctly with classification model
  - Validate AgentCore Gateway integration
  - Verify agents can access classification capabilities
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_

- [ ] 8. Update Authentication and Environment Configuration
  - [ ] 8.1 Ensure local environment operates without authentication
    - Verify multi_agent app runs without Cognito requirements
    - Maintain development ease and quick testing capabilities
    - Document local development setup and configuration
    - _Requirements: 5.1, 5.4_

  - [ ] 8.2 Validate production authentication integration
    - Ensure deploy_multi_agent maintains AWS Cognito authentication
    - Verify proper user management and session handling
    - Test authentication flows and error handling
    - _Requirements: 5.2, 5.5_

  - [ ] 8.3 Document environment differences and setup
    - Create clear documentation comparing local vs deployed configurations
    - Provide setup instructions for both environments
    - Document authentication requirements and configuration
    - _Requirements: 5.3, 5.4_

  - [ ]* 8.4 Write property test for authentication integration
    - **Property 5: Authentication Integration**
    - **Validates: Requirements 5.2, 5.5**

- [ ] 9. Checkpoint - Authentication and environment configuration complete
  - Ensure local app works without authentication
  - Validate production app enforces Cognito authentication
  - Verify documentation is clear and comprehensive
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_

- [ ] 10. Implement System Modularity and Configuration
  - [ ] 10.1 Create modular agent selection and configuration
    - Implement configurable agent combinations and selection
    - Support independent deployment of different system components
    - Create pluggable model interfaces for easy switching
    - _Requirements: 6.1, 6.2, 6.3_

  - [ ] 10.2 Standardize MCP tool integration interfaces
    - Create standardized interfaces for MCP tool integration
    - Support configuration-driven customization without code changes
    - Implement consistent tool discovery and invocation protocols
    - _Requirements: 6.4, 6.5_

  - [ ]* 10.3 Write property test for system modularity and configuration
    - **Property 6: System Modularity and Configuration**
    - **Validates: Requirements 6.1, 6.2, 6.3, 6.4, 6.5**

- [ ] 11. Create Comprehensive Documentation
  - [ ] 11.1 Create architecture diagrams and documentation
    - Design clear architecture diagrams showing simplified design
    - Document the differences between Bedrock and SageMaker AI integration
    - Create visual representations of local vs production environments
    - _Requirements: 7.1, 7.2_

  - [ ] 11.2 Document AgentCore migration and MCP setup
    - Provide detailed AgentCore migration path documentation
    - Create complete MCP Lambda setup and integration guides
    - Document troubleshooting procedures for all components
    - _Requirements: 7.3, 7.4, 7.5_

- [ ] 12. Final Integration and Validation
  - [ ] 12.1 Conduct end-to-end testing
    - Test complete workflow from local development to production deployment
    - Validate model switching works correctly in both environments
    - Test MCP integration and classification capabilities
    - Verify authentication works properly in production environment
    - _Requirements: All requirements_

  - [ ] 12.2 Create final refactored package
    - Organize all deliverables with new naming conventions
    - Ensure all documentation is updated and consistent
    - Create setup verification and validation checklist
    - Validate all functionality works with new architecture
    - _Requirements: All requirements_

- [ ] 13. Final checkpoint - Architecture refactoring complete
  - Ensure all directory renaming is complete and functional
  - Validate model choice capabilities work in local environment
  - Verify AgentCore preparation is documented and implemented
  - Confirm MCP integration provides classification capabilities
  - Test authentication differences between local and production
  - Validate system modularity and configuration capabilities
  - _Requirements: All requirements_

## Notes

- Tasks marked with `*` are optional and can be skipped for faster implementation
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation and progress tracking
- Property tests validate universal correctness properties
- Unit tests validate specific examples and edge cases
- Focus on maintaining existing functionality while adding new capabilities