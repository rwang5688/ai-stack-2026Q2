# Session Notes - December 17, 2025

## Session Overview
Fixed CloudFormation template deployment issues for the code-server workshop infrastructure. Identified and resolved YAML parsing errors that prevented template deployment, while maintaining maximum compatibility with the original template for easy future updates.

## Key Accomplishments
- **Fixed CloudFormation null values error**: Root cause was unquoted shell commands and inline comments in SSM Document
- **Resolved CloudFront Tags error**: Moved Tags property from DistributionConfig to resource level  
- **Removed SSH security risk**: Eliminated SSH access rule entirely to avoid security warnings
- **Maintained template compatibility**: Made minimal changes (only 50 bytes difference) to preserve original structure
- **Improved SSM reliability**: Used instance ID targeting instead of tag-based targeting for more reliable bootstrap execution
- **Conservative installation approach**: Kept original software installation methods while fixing only critical YAML issues

## Issues & Resolutions
- **Issue**: CloudFormation error "null values are not allowed in templates" at mainSteps/1/inputs/runCommand/3
  - **Root Cause**: Unquoted shell commands and inline comments in SSM Document YAML
  - **Resolution**: Quoted all shell commands as strings, removed inline comments, used consistent formatting

- **Issue**: CloudFront deployment error "extraneous key [Tags] is not permitted"
  - **Root Cause**: Tags property incorrectly placed inside DistributionConfig
  - **Resolution**: Moved Tags to top-level resource properties

- **Issue**: SSH port 22 open to world (0.0.0.0/0) triggering security warnings
  - **Root Cause**: Original template allowed SSH access from any IP address
  - **Resolution**: Removed SSH access rule entirely from security group



## Decisions Made
- **Conservative approach**: Keep original software installation methods (NodeSource repos, package managers) to maintain compatibility
- **Minimize template differences**: Keep original structure and size (34KB vs 34KB) for easy diffing and future updates
- **Focus on core fixes**: Only fix critical deployment issues - YAML parsing and reliability problems
- **Improve SSM reliability**: Use instance ID targeting (more reliable than tag-based) as beneficial change
- **Maintain original functionality**: Preserve all parameters, mappings, and resource configurations from original
- **Security improvement**: Remove SSH access rule entirely to eliminate security warnings

## Key Technical Insights
- **YAML in CloudFormation SSM Documents**: Every command in runCommand arrays must be properly quoted as strings
- **CloudFormation intrinsic functions**: Avoid complex substitutions within SSM document content - use environment variables instead
- **CloudFront resource structure**: Tags go at resource level, not inside DistributionConfig
- **SSM Association targeting**: Instance ID targeting is more reliable than tag-based targeting for bootstrap execution

## Next Steps
- [ ] Monitor current deployment to ensure bootstrap process completes successfully
- [ ] Test code-server access via CloudFront URL once deployment finishes
- [ ] Update spec documentation with lessons learned
- [ ] Document the minimal set of changes needed for future workshop template updates

## Resources
- [CloudFormation SSM Document Reference](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ssm-document.html)
- [CloudFront Distribution Properties](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-cloudfront-distribution.html)
- Workshop repository: https://github.com/VincentV89/agentic-ai-with-mcp-and-strands

## Template Changes Summary
**Final approach - minimal changes for maximum compatibility:**
1. **Quoted all SSM Document shell commands** - prevents YAML null values error
2. **Removed inline comments from command arrays** - eliminates YAML parsing issues  
3. **Fixed CloudFront Tags placement** - moved from DistributionConfig to resource level
4. **Removed SSH security risk** - eliminated SSH access rule entirely
5. **Used instance ID targeting** - more reliable than tag-based SSM association
6. **Preserved original installation methods** - kept NodeSource repos, Docker installation, Python setup as-is

**File management:**
- Replaced `code-server-improved.yaml` with minimal-change version
- Removed redundant `code-server-original.yaml` 
- Maintained `code-server.yaml` as reference original