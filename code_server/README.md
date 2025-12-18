# Code Server Deployment

Cloud-based VS Code development environment deployed via AWS CloudFormation with automated bootstrap and global CloudFront distribution.

## Quick Links

- **Deployment Guide**: [DEPLOYMENT.md](DEPLOYMENT.md)
- **Improvements Documentation**: [IMPROVEMENTS.md](IMPROVEMENTS.md)
- **Spec Documentation**: [../.kiro/specs/code-server-deployment/](../.kiro/specs/code-server-deployment/)

## Files

| File | Purpose |
|------|---------|
| `code-server.yaml` | Original working template |
| `code-server-original.yaml` | Backup of original |
| `code-server-improved.yaml` | **Production-ready template** with reliability fixes |
| `DEPLOYMENT.md` | Deployment instructions and troubleshooting |
| `IMPROVEMENTS.md` | Detailed documentation of improvements |
| `tests/template-validation.py` | Property-based test suite |

## Key Features

✅ **Reliable Bootstrap** - Uses official Node.js binaries instead of broken package repos  
✅ **Secure Access** - CloudFront-only access with password authentication  
✅ **Auto-Recovery** - Services automatically restart on failure  
✅ **Debugging Support** - Optional SSH access and comprehensive logging  
✅ **Global Distribution** - CloudFront CDN for worldwide access  
✅ **Spec-Driven** - Complete requirements, design, and task documentation  

## Quick Deploy

```bash
aws cloudformation create-stack \
  --stack-name code-server-dev \
  --template-body file://code-server-improved.yaml \
  --parameters ParameterKey=EC2KeyPair,ParameterValue=your-key \
  --capabilities CAPABILITY_IAM \
  --region us-west-2
```

## Architecture

```
Internet → CloudFront (HTTPS) → EC2 (nginx → code-server)
```

## Access

- **URL**: CloudFront domain from stack outputs
- **Password**: Your AWS Account ID
- **Workspace**: `/home/ubuntu/workshop/`

## Troubleshooting

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed troubleshooting steps.

Common issues:
- **504 Error**: Bootstrap still running (wait 10-15 min)
- **Can't SSH**: Set `AllowSSHAccess=true` parameter
- **Services Down**: Check SSM logs in S3 bucket

## Testing

Run validation tests:
```bash
cd tests
python3 -m pytest template-validation.py -v
```

## Documentation

Complete spec documentation available at:
- Requirements: `../.kiro/specs/code-server-deployment/requirements.md`
- Design: `../.kiro/specs/code-server-deployment/design.md`
- Tasks: `../.kiro/specs/code-server-deployment/tasks.md`

## Session Notes

Development session notes: `../.kiro/session-notes/20251218-session-notes.md`