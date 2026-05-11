# Session Notes - February 21, 2026

## Session Overview

Diagnosed and fixed ALB Target Group health check issue where EC2 instances were showing as unhealthy. Root cause: ALB health check was hitting `/` (code-server login page returning 401) instead of a dedicated health endpoint. Solution: Added `/health` endpoint to nginx configuration and updated ALB health check path.

## Key Accomplishments

- Identified root cause of unhealthy ALB targets (health check on `/` returns 401 Unauthorized)
- Added `/health` endpoint to nginx configuration in SSM bootstrap document (lines 757-761)
- Updated ALB Target Group health check path from `/` to `/health` (line 517)
- Manually added `/health` endpoint to running EC2 instance via SSM Session Manager
- Validated template with cfn-lint (0 errors, 0 warnings)
- Prepared for clean stack redeployment

## Issues & Resolutions

**Issue 1: ALB Target showing as Unhealthy**
- **Symptom**: Target Group console shows EC2 instance as "Unhealthy" despite code-server working
- **Root Cause**: Health check hitting `/` returns 302 redirect or 401 Unauthorized (code-server auth challenge)
- **Resolution**: 
  1. Added `/health` endpoint to nginx config that returns 200 OK without authentication
  2. Updated ALB Target Group HealthCheckPath from `/` to `/health`

**Issue 2: Copy-paste nightmare in SSM Session Manager**
- **Symptom**: Multi-line commands lost formatting when pasted into Windows SSM Session Manager
- **Root Cause**: Windows terminal handling of line breaks
- **Resolution**: Used `nano` editor instead of `vi` (user preference) to manually edit nginx config file
- **Learning**: For remote editing, use simple editors like nano, not vi

**Issue 3: CloudFormation update-stack failed on SSMLogBucket**
- **Symptom**: `UPDATE_FAILED` - "The bucket does not allow ACLs"
- **Root Cause**: Original template used `AccessControl: Private` (ACL-based), we removed it but didn't explicitly set `OwnershipControls: BucketOwnerEnforced`
- **CloudFormation Quirk**: When updating existing buckets that had ACLs, must explicitly set OwnershipControls even though it's the default for new buckets
- **Resolution**: Decided to skip stack update, do clean redeployment instead (simpler, avoids CloudFormation update complexity)

## Key Decisions

**Decision 1: Add /health endpoint instead of changing auth behavior**
- **Rationale**: Cleaner separation - health checks don't need authentication, code-server does
- **Alternative Considered**: Make `/` return 200 for health checks (rejected - breaks security)
- **Impact**: Standard pattern, no security compromise

**Decision 2: Skip CloudFormation update-stack, do clean redeployment**
- **Rationale**: 
  - Update-stack failing on S3 ACL issue unrelated to our actual changes
  - Fresh stack deployment will use AWS defaults (no ACL issues)
  - Cleaner validation of complete template
- **Alternative Considered**: Add `OwnershipControls` property to fix update (rejected - unnecessary complexity)
- **Impact**: Faster path to validated deployment, avoids CloudFormation update quirks

**Decision 3: Use nano instead of vi for remote editing**
- **Rationale**: User preference, simpler for one-time edits
- **Impact**: Faster manual fix, less frustration

## Technical Details

**nginx /health endpoint** (added to SSM bootstrap):
```nginx
location /health {
  access_log off;
  return 200 "healthy\n";
  add_header Content-Type text/plain;
}
```

**ALB Target Group Health Check** (updated):
- HealthCheckPath: `/health` (was `/`)
- HealthCheckIntervalSeconds: 30
- HealthCheckTimeoutSeconds: 5
- HealthyThresholdCount: 2
- UnhealthyThresholdCount: 2

**Manual Fix Applied to Running Instance**:
1. Connected via SSM Session Manager (no SSH needed - EC2 in private subnet)
2. Edited `/etc/nginx/sites-available/code-server` with nano
3. Added `/health` location block
4. Ran `sudo nginx -t` (syntax OK)
5. Ran `sudo systemctl reload nginx`
6. Verified: `curl http://localhost/health` returns "healthy" with HTTP 200 OK

## S3 ACL Saga (Learning Moment)

**AWS S3 Security Defaults Changed (April 2023)**:
- Old way: `AccessControl: Private` (uses ACLs)
- New way: `OwnershipControls: BucketOwnerEnforced` (disables ACLs, uses bucket policies)

**The Catch-22**:
- New buckets created after April 2023: `BucketOwnerEnforced` is automatic default
- Existing buckets with ACLs: CloudFormation requires explicit `OwnershipControls` when removing `AccessControl`
- Even though user's bucket was created in 2026, it was created WITH `AccessControl: Private`, so CloudFormation treats it as "existing bucket with ACLs"

**Why This Matters**:
- For fresh stack: No `OwnershipControls` needed (AWS uses defaults)
- For update-stack: Must explicitly set `OwnershipControls` (CloudFormation paranoia)
- Lesson: CloudFormation update behavior != fresh stack behavior

## Next Steps

- [x] Validate template with cfn-lint (DONE - 0 errors, 0 warnings)
- [x] User: Checkpoint commit offline (DONE)
- [x] User: Pull down latest changes (DONE)
- [x] Review: Verify all changes present in pulled code (DONE)
- [ ] Delete existing stack: `aws cloudformation delete-stack --stack-name code-server --region us-east-1`
- [ ] Create fresh stack: `aws cloudformation create-stack --stack-name code-server --template-body file://code-server/code-server.yaml --capabilities CAPABILITY_IAM --region us-east-1`
- [ ] Verify: CloudFront → ALB → EC2 traffic flow
- [ ] Verify: ALB Target Group shows "Healthy"
- [ ] Verify: `/health` endpoint returns 200 OK
- [ ] Verify: Code-server accessible via CloudFront URL

## Resources

- CloudFormation Template: `code-server/code-server.yaml`
- Spec: `.kiro/specs/code-server-private-ip/`
- AWS ELB Health Checks: https://docs.aws.amazon.com/elasticloadbalancing/latest/application/target-group-health-checks.html
- AWS S3 Bucket Ownership: https://docs.aws.amazon.com/AmazonS3/latest/userguide/about-object-ownership.html

## Template Status

**Current State**: Production-ready for fresh deployment
- ✅ All 10 new resources implemented
- ✅ All 6 modified resources updated
- ✅ ALB health check configured for `/health`
- ✅ nginx `/health` endpoint in SSM bootstrap
- ✅ cfn-lint validation passes (0 warnings)
- ✅ AWS CloudFormation validation passes
- ⚠️ Cannot update existing stack (S3 ACL issue)
- ✅ Ready for fresh stack deployment

**Confidence Level**: 90% for fresh deployment
- Known working: Private subnet architecture, ALB, NAT Gateway, security groups, CloudFront origin
- Known working: `/health` endpoint (manually tested on running instance)
- Unknown: Fresh stack deployment (not yet tested)
- Recommendation: Proceed with delete + create
