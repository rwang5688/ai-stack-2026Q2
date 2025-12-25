# Implementation Plan

- [x] 1. Set up project structure for 4-step multi-agent workshop
  - Create workshop4/multi_agent_bedrock directory with organized subdirectories for each step
  - Set up Step 1 (CLI), Step 2 (UI), Step 3 (Knowledge), Step 4 (Deployment) folders
  - Create shared resources and documentation structure
  - Set up testing framework for multi-agent scenarios with Bedrock models
  - _Requirements: 1.1_

- [x] 2. Implement Step 1: CLI Multi-Agent System with Teacher's Assistant Pattern
  - [x] 2.1 Create Teacher's Assistant orchestrator agent
    - Implement main orchestrator using Strands Agents SDK with natural language routing
    - Create system prompt for query classification and routing logic
    - Set up callback_handler=None to suppress intermediate outputs
    - Add command-line interface for user interactions
    - _Requirements: 2.1, 2.5_

  - [x] 2.2 Implement Math Assistant specialized agent
    - Create Math Assistant as @tool decorated function
    - Integrate calculator tool for mathematical operations
    - Implement domain-specific system prompt for math queries
    - Add error handling and response formatting
    - _Requirements: 2.2, 2.3_

  - [x] 2.3 Implement English Assistant specialized agent
    - Create English Assistant as @tool decorated function
    - Focus on grammar and language comprehension capabilities
    - Implement domain-specific system prompt for English queries
    - Add error handling and response formatting
    - _Requirements: 2.2, 2.3_

  - [x] 2.4 Implement Language Assistant specialized agent
    - Create Language Assistant as @tool decorated function
    - Integrate http_request tool for translation services
    - Implement domain-specific system prompt for translation queries
    - Add error handling and response formatting
    - _Requirements: 2.2, 2.3_

  - [x] 2.5 Implement Computer Science Assistant specialized agent
    - Create Computer Science Assistant as @tool decorated function
    - Integrate python_repl, shell, editor, and file operations tools
    - Implement domain-specific system prompt for programming queries
    - Add error handling and response formatting
    - _Requirements: 2.2, 2.3_

  - [x] 2.6 Implement General Assistant specialized agent
    - Create General Assistant as @tool decorated function
    - Handle queries outside specialized domains (no specific tools)
    - Implement general-purpose system prompt
    - Add error handling and response formatting
    - _Requirements: 2.2, 2.3_

  - [x] 2.7 Create CLI testing interface and sample queries
    - Implement command-line interface for testing all agents
    - Create sample queries for each specialized domain
    - Add exit functionality and user guidance
    - Test routing accuracy and response quality
    - _Requirements: 2.4_

  - [ ]* 2.8 Write property test for CLI multi-agent system functionality
    - **Property 3: CLI Multi-Agent System Functionality**
    - **Validates: Requirements 2.1, 2.2, 2.3, 2.4, 2.5**

- [x] 3. Checkpoint - Step 1 CLI system complete
  - Ensure Teacher's Assistant routes queries correctly to all 5 specialized agents
  - Validate all agents respond appropriately to domain-specific queries
  - Verify clean output with suppressed intermediate processing
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_

- [x] 4. Implement Step 2: Streamlit Web Interface Integration
  - [x] 4.1 Create Streamlit web application
    - Implement Streamlit app that integrates with Teacher's Assistant system
    - Create clean web interface for query submission
    - Add proper response display and formatting
    - Implement session state management
    - _Requirements: 3.1, 3.2_

  - [x] 4.2 Integrate multi-agent system with web interface
    - Connect Streamlit UI to existing Teacher's Assistant system
    - Maintain all specialized agent capabilities in web context
    - Ensure proper routing and response handling
    - Add loading indicators and user feedback
    - _Requirements: 3.1, 3.3_

  - [x] 4.3 Add error handling and user experience enhancements
    - Implement comprehensive error handling for web interface
    - Add user-friendly error messages and feedback
    - Create customizable UI components and styling
    - Add query history and session management
    - _Requirements: 3.4, 3.5_

  - [ ]* 4.4 Write property test for web interface integration
    - **Property 4: Web Interface Integration**
    - **Validates: Requirements 3.1, 3.2, 3.3, 3.4, 3.5**

- [x] 5. Checkpoint - Step 2 web interface complete
  - Ensure Streamlit app integrates correctly with multi-agent system
  - Validate web queries route properly to specialized agents
  - Verify proper response formatting and error handling
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_

- [x] 6. Implement Step 3: Bedrock Knowledge Base Integration
  - [x] 6.1 Set up Bedrock Knowledge Base and S3 storage
    - Create Bedrock Knowledge Base using boto3
    - Set up S3 bucket for document storage
    - Configure knowledge base indexing and retrieval
    - Add document upload and management workflows
    - _Requirements: 4.1, 4.4_

  - [x] 6.2 Enhance specialized agents with knowledge retrieval
    - Integrate knowledge base querying capabilities into agents
    - Modify agent system prompts to use retrieved document information
    - Add knowledge-augmented response generation
    - Implement relevance scoring and context management
    - _Requirements: 4.2, 4.3_

  - [x] 6.3 Create knowledge base management utilities
    - Implement document upload and indexing utilities
    - Add knowledge base querying and testing tools
    - Create document management and organization features
    - Add knowledge base status monitoring and maintenance
    - _Requirements: 4.4, 4.5_

  - [ ]* 6.4 Write property test for knowledge base integration
    - **Property 5: Knowledge Base Integration**
    - **Validates: Requirements 4.1, 4.2, 4.3, 4.4, 4.5**

- [x] 7. Checkpoint - Step 3 knowledge enhancement complete
  - Ensure Bedrock Knowledge Base is properly configured and accessible
  - Validate agents can retrieve and use document information correctly
  - Verify document management and indexing workflows work properly
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_

- [ ] 8. Checkpoint - Step 4 memory integration and enhanced UI complete
  - Ensure memory agent integration works correctly with OpenSearch backend and fallback
  - Validate model selection dropdown updates all agent types appropriately
  - Verify teacher agent toggles enable/disable individual agents correctly
  - Test agent type selection routes queries to appropriate systems
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_

- [ ] 8. Implement Step 4: Memory Integration and Enhanced UI Features
  - [ ] 8.1 Integrate memory agent capabilities from module5
    - Import and adapt memory agent functionality from workshop4/modules/module5/memory_agent.py
    - Add OpenSearch backend support with graceful fallback when OPENSEARCH_HOST is undefined
    - Implement memory operations: store, retrieve, and list functionality
    - Add user-specific memory management with USER_ID support
    - _Requirements: 5.1_

  - [ ] 8.2 Add model selection dropdown to Streamlit interface
    - Implement dropdown selection for multiple Bedrock model IDs
    - Support models: Nova Pro, Nova Lite, Nova Micro, Claude 3.5 Haiku, Claude 3.7 Sonnet, Claude Sonnet 4
    - Update all agents (teacher, knowledge base, memory) to use selected model
    - Add model information display in sidebar
    - _Requirements: 5.2_

  - [ ] 8.3 Implement teacher agent toggle controls
    - Add individual toggle checkboxes for each specialized teacher agent
    - Enable/disable Math, Language, Computer Science, English assistants
    - Update teacher agent initialization to only include toggled agents
    - Maintain Tool-Agent Pattern with selective activation
    - _Requirements: 5.3_

  - [ ] 8.4 Add agent type selection (Teacher, Knowledge Base, Memory)
    - Implement agent type dropdown in sidebar
    - Route queries to appropriate agent type based on user selection
    - Maintain existing query routing logic for teacher and knowledge base
    - Add memory agent as third option with OpenSearch backend check
    - _Requirements: 5.4, 5.5_

  - [ ]* 8.5 Write property test for memory integration and enhanced UI
    - **Property 6: Memory Integration and Enhanced UI**
    - **Validates: Requirements 5.1, 5.2, 5.3, 5.4, 5.5**

- [ ] 9. Implement Step 5: Production Deployment
  - [ ] 9.1 Create Docker container for enhanced application
    - Create Dockerfile for Streamlit multi-agent application
    - Optimize container for production deployment with all enhanced features
    - Add environment configuration and dependency management for memory backends
    - Test container locally with full feature set validation
    - _Requirements: 7.1_

  - [ ] 9.2 Implement AWS CDK infrastructure with memory backend support
    - Create CDK stack for ECS Fargate cluster deployment
    - Add VPC, load balancer, and supporting AWS services with memory backend support
    - Configure auto-scaling and high availability for enhanced application
    - Add monitoring and logging infrastructure for multi-agent system
    - _Requirements: 7.2_

  - [ ] 9.3 Deploy to production and validate functionality
    - Deploy containerized application to ECS Fargate
    - Validate production deployment with all enhanced features
    - Test memory integration, model selection, and agent toggles in production
    - Verify all agent types work correctly in production environment
    - _Requirements: 7.3_

  - [ ] 9.4 Add monitoring, logging, and maintenance procedures
    - Add monitoring dashboards and alerting for production environment
    - Implement logging for multi-agent interactions and memory operations
    - Create cleanup and maintenance procedures for production environment
    - Add cost monitoring and optimization recommendations
    - _Requirements: 7.4, 7.5_

  - [ ]* 9.5 Write property test for production deployment correctness
    - **Property 7: Production Deployment Correctness**
    - **Validates: Requirements 7.1, 7.2, 7.3, 7.4, 7.5**

- [ ] 10. Checkpoint - Step 5 production deployment complete
  - Ensure containerized application deploys successfully to ECS Fargate
  - Validate all enhanced features work correctly in production
  - Verify monitoring, logging, and maintenance procedures are operational
  - Test end-to-end functionality from CLI to production deployment
  - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_

- [ ] 11. Implement Step 6: Comprehensive Documentation and Workshop Materials
- [ ] 11. Implement Step 6: Comprehensive Documentation and Workshop Materials
  - [ ] 11.1 Write complete 6-step workshop documentation
    - Create comprehensive setup and installation guide for all steps
    - Write detailed tutorials for each step with clear progression
    - Add troubleshooting and FAQ documentation for memory integration and enhanced features
    - Include cross-platform compatibility notes and environment setup
    - _Requirements: 8.1, 8.2_

  - [ ] 11.2 Create instructor guide and presentation materials
    - Create instructor guide with teaching notes and timing recommendations
    - Develop presentation materials and slides for workshop delivery
    - Add demonstration scripts and sample queries for each step
    - Include assessment criteria and learning objectives
    - _Requirements: 8.3, 8.4_

  - [ ] 11.3 Create modular and reusable components documentation
    - Document all reusable multi-agent patterns and components
    - Create customization and adaptation guides for model selection and agent toggles
    - Add integration APIs and interface documentation
    - Create performance tuning guides for different Bedrock models and memory backends
    - _Requirements: 8.5_

  - [ ]* 11.4 Write property test for material completeness
    - **Property 8: Material Completeness**
    - **Validates: Requirements 8.1, 8.2, 8.3, 8.4, 8.5**

  - [ ]* 11.5 Write property test for system modularity and configuration
    - **Property 9: System Modularity and Configuration**
    - **Validates: Requirements 6.1, 6.2, 6.3, 6.4, 6.5**

- [ ] 12. Final integration and testing
  - [ ] 12.1 Conduct end-to-end 6-step progression testing
    - Test complete progression from CLI to production deployment
    - Validate each step builds correctly on the previous step
    - Test cross-platform compatibility and performance
    - Verify all Bedrock integrations and enhanced features work correctly
    - _Requirements: 1.2, 1.3, 1.4, 1.5, 1.6, 1.7_

  - [ ]* 12.2 Write property test for 6-step progression correctness
    - **Property 2: 6-Step Progression Correctness**
    - **Validates: Requirements 1.2, 1.3, 1.4, 1.5, 1.6, 1.7**

  - [ ] 12.3 Create final workshop package
    - Organize all deliverables for workshop delivery
    - Create distribution-ready package with all 6 steps
    - Include setup verification and validation checklist
    - Add instructor resources and presentation materials
    - _Requirements: 8.1, 8.4_

- [ ] 13. Final checkpoint - Workshop ready for delivery
  - Ensure all tests pass and 6-step progression works end-to-end
  - Validate workshop materials are complete and consistent
  - Verify production deployment and cleanup procedures work
  - Confirm workshop is ready for instructor delivery with all enhanced features
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 8.1, 8.2, 8.3, 8.4, 8.5_