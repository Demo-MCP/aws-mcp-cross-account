# AWS MCP Cross-Account AssumeRole Setup

This repository provides scripts to enable cross-account AssumeRole support for AWS MCP servers (ECS and IaC). After setup, your MCP servers can assume IAM roles in different AWS accounts dynamically based on each API call.

## Overview

- **Before**: MCP servers use your local AWS credentials (broad permissions)
- **After**: MCP servers assume specific IAM roles per account (least privilege)

## Prerequisites

- macOS with Python 3.7+
- AWS CLI configured with admin-like permissions
- Git

## Quick Start

### 1. Clone AWS MCP Repositories

```bash
# Clone the official AWS MCP repositories
git clone https://github.com/awslabs/mcp-server-aws.git
cd mcp-server-aws

# Note the paths to ECS and IaC MCP servers:
# - ECS MCP: src/ecs-mcp-server/
# - IaC MCP: src/aws-iac-mcp-server/
```

### 2. Clone This Repository

```bash
git clone https://github.com/suhaibchishti/aws-mcp-cross-account.git
cd aws-mcp-cross-account
```

### 3. Install Dependencies

```bash
# Install the cross-account helper library
pip3 install -e ./platform_aws_context

# Install required dependencies
pip3 install astor boto3
```

### 4. Create IAM Role

```bash
# Create the McpReadOnlyRole in your AWS account
./scripts/create-iam-role.sh

# This creates:
# - Role: McpReadOnlyRole
# - Policies: CloudFormation + ECS read-only permissions
```

### 5. Patch MCP Servers

```bash
# Patch ECS MCP server
python3 scripts/patch-ecs-mcp.py /path/to/mcp-server-aws/src/ecs-mcp-server

# Patch IaC MCP server  
python3 scripts/patch-iac-mcp.py /path/to/mcp-server-aws/src/aws-iac-mcp-server
```

### 6. Test the Setup

```bash
# Test cross-account functionality
python3 scripts/test-cross-account.py
```

## Usage

After patching, your MCP tools accept an `account_id` parameter:

```python
# ECS MCP Tool
ecs_resource_management(
    api_operation="ListClusters",
    api_params={},
    account_id="123456789012",  # Target account
    region="us-east-1"
)

# IaC MCP Tool
troubleshoot_cloudformation_deployment(
    stack_name="my-stack",
    region="us-east-1", 
    account_id="123456789012"  # Target account
)
```

## Multi-Account Setup

To use with multiple accounts:

1. Create the same `McpReadOnlyRole` in each target account
2. Update trust policies to allow your source account to assume the role
3. Use different `account_id` values in MCP calls

## Security

- MCP servers use least-privilege IAM roles instead of broad credentials
- Each account can have different permission policies
- Role assumption is logged in CloudTrail for auditing

## Troubleshooting

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for common issues and solutions.

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   MCP Client    │───▶│   MCP Server     │───▶│  AWS Account A  │
│                 │    │  (Patched)       │    │  McpReadOnlyRole│
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │  AWS Account B  │
                       │  McpReadOnlyRole│
                       └─────────────────┘
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test with the provided scripts
5. Submit a pull request
