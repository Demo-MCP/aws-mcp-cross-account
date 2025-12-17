# Troubleshooting Guide

## Common Issues and Solutions

### 1. Role Assumption Fails

**Error**: `AccessDenied when calling AssumeRole operation`

**Solutions**:
- Verify the role exists: `aws iam get-role --role-name McpReadOnlyRole`
- Check trust policy allows your user to assume the role
- Ensure your AWS credentials have `sts:AssumeRole` permission

### 2. Import Error for platform_aws_context

**Error**: `ModuleNotFoundError: No module named 'platform_aws_context'`

**Solution**:
```bash
cd aws-mcp-cross-account
pip3 install -e ./platform_aws_context
```

### 3. MCP Server Import Errors

**Error**: Various import errors when testing patched MCP servers

**Solutions**:
- Install MCP server dependencies in their respective directories
- For ECS MCP: `cd ecs-mcp-server && pip3 install -r requirements.txt`
- For IaC MCP: `cd aws-iac-mcp-server && pip3 install -r requirements.txt`

### 4. Permission Denied for Specific Services

**Error**: `User is not authorized to perform: ecs:ListClusters`

**Solution**: This is expected behavior! The role only has permissions you've granted.
- To add ECS permissions: Attach `arn:aws:iam::aws:policy/AmazonECS_ReadOnlyAccess`
- To add other services: Create and attach appropriate read-only policies

### 5. Cross-Account Access Issues

**Error**: `AccessDenied` when accessing different account

**Solutions**:
1. Create `McpReadOnlyRole` in the target account
2. Update trust policy in target account to allow your source account:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::SOURCE_ACCOUNT_ID:user/YOUR_USER"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
```

### 6. IAM Policy Propagation Delays

**Error**: Permissions work intermittently

**Solution**: Wait 10-60 seconds after creating/modifying IAM policies for changes to propagate.

### 7. Session Duration Issues

**Error**: `Token expired` or similar

**Solution**: The helper uses 15-minute sessions. For longer operations, consider increasing `DurationSeconds` in `assume_role.py`.

## Debugging Tips

### Check Role Assumption
```bash
# Test role assumption manually
aws sts assume-role \
  --role-arn "arn:aws:iam::ACCOUNT_ID:role/McpReadOnlyRole" \
  --role-session-name "debug-session"
```

### Verify Permissions
```bash
# List attached policies
aws iam list-attached-role-policies --role-name McpReadOnlyRole

# Get policy details
aws iam get-policy-version \
  --policy-arn "arn:aws:iam::ACCOUNT_ID:policy/McpCloudFormationReadOnly" \
  --version-id v1
```

### Test Helper Library Directly
```python
from platform_aws_context.assume_role import get_client_for_account

ctx_params = {
    "account_id": "123456789012",
    "region": "us-east-1",
    "_metadata": {"actor": "debug", "repo": "test"}
}

client = get_client_for_account("cloudformation", ctx_params)
print(client.list_stacks())
```

## Getting Help

1. Check AWS CloudTrail for detailed error messages
2. Enable AWS CLI debug mode: `aws --debug sts assume-role ...`
3. Review IAM policy simulator for permission testing
4. Open an issue in this repository with:
   - Error message
   - Steps to reproduce
   - AWS CLI version
   - Python version
