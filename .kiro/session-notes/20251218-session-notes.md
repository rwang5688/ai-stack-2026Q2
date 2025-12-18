# Session Notes - December 18, 2025

## Session Overview
Troubleshot and resolved 504 Gateway Timeout errors with AWS CloudFormation code-server deployment. Identified and fixed multiple reliability issues in the bootstrap process, then established Kiro project structure with steering rules.

## Key Accomplishments
- ✅ Diagnosed 504 CloudFront error as failed SSM bootstrap association
- ✅ Manually fixed Node.js installation issues (NodeSource repository problems)
- ✅ Successfully deployed working code-server instance accessible via CloudFront
- ✅ Created improved CloudFormation template with reliability fixes
- ✅ Established `.kiro` directory structure with steering rules
- ✅ Documented comprehensive improvements and lessons learned

## Issues & Resolutions

### **Issue**: 504 Gateway Timeout from CloudFront
- **Root Cause**: SSM Association failed during bootstrap, so nginx/code-server were never installed
- **Resolution**: Manually executed SSM document and fixed underlying Node.js installation issues

### **Issue**: NodeSource Repository 404 Errors
- **Root Cause**: NodeSource repository URLs frequently break or become outdated
- **Resolution**: Switched to official Node.js binary distribution method
- **Commands Used**:
  ```bash
  curl -fsSL https://nodejs.org/dist/v20.18.0/node-v20.18.0-linux-arm64.tar.xz -o /tmp/node.tar.xz
  sudo tar -xJf /tmp/node.tar.xz -C /opt/
  sudo ln -sf /opt/node-v20.18.0-linux-arm64/bin/node /usr/local/bin/node
  ```

### **Issue**: npm Module Errors with Snap Installation
- **Root Cause**: Snap version of Node.js had broken npm dependencies
- **Resolution**: Used official binary distribution instead of snap packages

### **Issue**: Circular Dependency in Nginx Configuration
- **Root Cause**: Nginx config referenced CloudFront domain before CloudFront was created
- **Resolution**: Changed `server_name` to `_` (accept any hostname)

## Decisions Made

### **CloudFormation Template Strategy**
- **Decision**: Create three versions of the template
  - `code-server.yaml` - Original working version
  - `code-server-original.yaml` - Backup of original
  - `code-server-improved.yaml` - Enhanced version with reliability fixes
- **Rationale**: Maintain working version while developing improvements

### **Node.js Installation Method**
- **Decision**: Use official Node.js binary distribution instead of package managers
- **Rationale**: More reliable than NodeSource repos or snap packages

### **SSM Association Targeting**
- **Decision**: Use InstanceIds targeting instead of tag-based targeting
- **Rationale**: More reliable during instance startup phase

### **Project Structure**
- **Decision**: Implement Kiro steering rules for session notes and specs management
- **Rationale**: Better organization and spec-driven development approach

## Technical Discoveries

### **Code-Server Information**
- **Project**: Open source VS Code in the browser
- **GitHub**: https://github.com/coder/code-server
- **Website**: https://coder.com/docs/code-server
- **Use Case**: Perfect for cloud-based development environments

### **AWS CloudFormation Reliability Patterns**
- SSM Associations can be unreliable with tag targeting during instance startup
- NodeSource repositories frequently break - use official binaries instead
- Always include SSH access for debugging bootstrap issues
- Explicit SSM policies needed even with AdministratorAccess

## Spec Implementation Completed
- ✅ Created complete spec for code-server-deployment feature
- ✅ Implemented requirements.md with EARS format acceptance criteria
- ✅ Developed comprehensive design.md with correctness properties
- ✅ Created detailed tasks.md with implementation breakdown
- ✅ Built test suite with property-based testing approach
- ✅ Created deployment guide and documentation

## Next Steps
- [ ] Test improved CloudFormation template in clean environment
- [ ] Create spec for ai-stack-2026Q2 repository structure
- [ ] Define features and capabilities for the AI stack project
- [ ] Set up CI/CD pipeline for the project
- [ ] Document architecture decisions for the AI stack

## Resources
- [Code-Server GitHub](https://github.com/coder/code-server) - VS Code in browser
- [Code-Server Docs](https://coder.com/docs/code-server) - Official documentation
- [Node.js Official Downloads](https://nodejs.org/dist/) - Reliable binary distributions
- [AWS SSM Associations](https://docs.aws.amazon.com/systems-manager/latest/userguide/systems-manager-associations.html) - Targeting best practices
- [CloudFormation Wait Conditions](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-waitcondition.html) - Dependency management

## Files Created/Modified
- `.kiro/steering/session-notes-management.md` - Session notes guidelines
- `.kiro/steering/specs-management.md` - Spec management rules  
- `code_server/code-server-original.yaml` - Backup of original template (identical to code-server.yaml)
- `code_server/code-server-improved.yaml` - Enhanced template with reliability fixes
- `code_server/IMPROVEMENTS.md` - Detailed improvement documentation
- `.kiro/specs/code-server-deployment/requirements.md` - Requirements spec for code-server deployment
- `.kiro/specs/code-server-deployment/file-history-documentation.md` - Clarification of file relationships

## File Relationships Clarification
- **code-server.yaml** = Your original deployed template (has issues)
- **code-server-original.yaml** = Exact backup copy of code-server.yaml  
- **code-server-improved.yaml** = Fixed version with Node.js, association, and nginx improvements

## Additional Files Created (Spec Implementation)
- `.kiro/specs/code-server-deployment/requirements.md` - EARS format requirements
- `.kiro/specs/code-server-deployment/design.md` - Technical design with correctness properties  
- `.kiro/specs/code-server-deployment/tasks.md` - Implementation task breakdown
- `.kiro/specs/code-server-deployment/file-history-documentation.md` - File analysis
- `code_server/tests/template-validation.py` - Property-based test suite
- `code_server/DEPLOYMENT.md` - Comprehensive deployment guide