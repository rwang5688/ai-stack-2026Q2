# Code Server CloudFormation Template Improvements

## Key Issues Fixed

### 1. **Node.js Installation Reliability**
**Problem:** NodeSource repository URLs are frequently broken or outdated
**Solution:** Use official Node.js binary distribution instead of apt repository

**Original:**
```yaml
- curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
- apt-get install -y nodejs
```

**Improved:**
```yaml
- rm -f /etc/apt/sources.list.d/nodesource.list  # Clean up broken repos
- curl -fsSL https://nodejs.org/dist/v20.18.0/node-v20.18.0-linux-arm64.tar.xz -o /tmp/node.tar.xz
- tar -xJf /tmp/node.tar.xz -C /opt/
- ln -sf /opt/node-v20.18.0-linux-arm64/bin/node /usr/local/bin/node
```

### 2. **SSM Association Targeting**
**Problem:** Tag-based targeting can be unreliable during instance startup
**Solution:** Use direct InstanceIds targeting with proper dependencies

**Original:**
```yaml
Targets:
  - Key: tag:SSMBootstrap
    Values:
      - true
```

**Improved:**
```yaml
Targets:
  - Key: InstanceIds
    Values:
      - !Ref VSCodeInstanceEC2Instance
DependsOn: 
  - VSCodeInstanceEC2Instance
  - WaitForInstanceReady
```

### 3. **Nginx Configuration Circular Dependency**
**Problem:** Nginx config references CloudFront domain before CloudFront is created
**Solution:** Use generic server_name that accepts any hostname

**Original:**
```yaml
server_name ${CloudFrontDistribution.DomainName};
```

**Improved:**
```yaml
server_name _;  # Accept any hostname
```

### 4. **Missing SSH Access for Debugging**
**Problem:** No way to troubleshoot when bootstrap fails
**Solution:** Optional SSH access parameter

**Added:**
```yaml
Parameters:
  AllowSSHAccess:
    Type: String
    Default: 'true'
    AllowedValues: ['true', 'false']

Conditions:
  EnableSSHAccess: !Equals [!Ref AllowSSHAccess, 'true']

SecurityGroupIngress:
  - !If
    - EnableSSHAccess
    - Description: Allow SSH access for debugging
      IpProtocol: tcp
      FromPort: 22
      ToPort: 22
      CidrIp: 0.0.0.0/0
    - !Ref AWS::NoValue
```

### 5. **Explicit SSM Permissions**
**Problem:** AdministratorAccess should be enough but SSM needs explicit policy
**Solution:** Add AmazonSSMManagedInstanceCore policy explicitly

**Added:**
```yaml
ManagedPolicyArns:
  - !Sub arn:${AWS::Partition}:iam::aws:policy/AdministratorAccess
  - !Sub arn:${AWS::Partition}:iam::aws:policy/AmazonSSMManagedInstanceCore
```

### 6. **Better Error Handling**
**Problem:** Bootstrap continues even when steps fail
**Solution:** Add `set -e` to fail fast and proper timeouts

**Added to each step:**
```yaml
runCommand:
  - '#!/bin/bash'
  - set -e  # Exit on any error
  - # ... rest of commands
```

### 7. **Service Verification**
**Problem:** No verification that services actually started
**Solution:** Check service status at the end

**Added:**
```yaml
- systemctl is-active code-server@ubuntu
- systemctl is-active nginx
- echo "Bootstrap completed successfully!"
```

### 8. **Improved Code-Server Configuration**
**Problem:** Password configuration was complex and unreliable
**Solution:** Use AWS CLI to get Account ID dynamically

**Improved:**
```yaml
password: $(aws sts get-caller-identity --query Account --output text)
```

## Template Structure Improvements

### Simplified Parameters
- Reduced instance type options to commonly used ARM64 types
- Added debugging options
- Better parameter organization

### Better Resource Organization
- Clear section comments
- Logical grouping of resources
- Consistent naming conventions

### Enhanced Outputs
- Added direct IP access URL for debugging
- Clear password information
- SSM document reference for manual execution

## Reliability Improvements

1. **Dependency Management:** Proper CloudFormation dependencies ensure resources are created in the right order
2. **Timeout Handling:** Appropriate timeouts for each installation step
3. **Cleanup:** Remove broken repositories before installing new ones
4. **Verification:** Check that services are actually running before completing
5. **Fallback Options:** SSH access allows manual intervention when needed

## Testing Recommendations

1. **Test in Multiple Regions:** Ensure CloudFront prefix lists are correct
2. **Test Instance Types:** Verify ARM64 vs AMD64 compatibility
3. **Test Network Conditions:** Ensure bootstrap works with slow connections
4. **Test Failure Recovery:** Verify manual SSM execution works when association fails

These improvements make the template much more reliable and easier to troubleshoot when issues occur.

## Nginx Configuration Fix (December 17, 2025)

### Issue
Deployment succeeded but users were seeing the Nginx welcome page instead of code-server interface.

### Root Cause
The default nginx site (`/etc/nginx/sites-enabled/default`) was still enabled, taking precedence over the code-server configuration.

### Solution
Updated the CloudFormation template's `ConfigureCodeServer` step to:

1. **Remove default site**: `sudo rm -f /etc/nginx/sites-enabled/default`
2. **Add configuration validation**: `sudo nginx -t` before restart
3. **Maintain proper order**: Remove default → Enable code-server → Validate → Restart

### Code Changes
```yaml
# Before
- sudo systemctl restart code-server@ubuntu
- sudo ln -s ../sites-available/code-server /etc/nginx/sites-enabled/code-server
- sudo systemctl restart nginx

# After  
- sudo systemctl restart code-server@ubuntu
- sudo rm -f /etc/nginx/sites-enabled/default
- sudo ln -s ../sites-available/code-server /etc/nginx/sites-enabled/code-server
- sudo nginx -t
- sudo systemctl restart nginx
```

### Validation
Created `code_server/tests/nginx-config-test.py` to verify:
- Default site removal
- Configuration validation
- Proper proxy configuration
- WebSocket support

### Impact
- ✅ Fixes the "Nginx welcome page" issue
- ✅ Ensures code-server is properly accessible via CloudFront
- ✅ Adds configuration validation for reliability
- ✅ Maintains all existing functionality

This addresses **Requirements 1.1, 3.3** from the spec and implements **Property 5: Configuration Validation**.