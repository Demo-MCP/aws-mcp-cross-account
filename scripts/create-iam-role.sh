#!/bin/bash

# Create IAM role and policies for MCP cross-account access

set -e

echo "Creating McpReadOnlyRole and policies..."

# Get current AWS identity
CURRENT_USER_ARN=$(aws sts get-caller-identity --query 'Arn' --output text)
ACCOUNT_ID=$(aws sts get-caller-identity --query 'Account' --output text)

echo "Current user: $CURRENT_USER_ARN"
echo "Account ID: $ACCOUNT_ID"

# Create trust policy
cat > /tmp/trust-policy.json << EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "AWS": "$CURRENT_USER_ARN"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF

# Create CloudFormation read-only policy
cat > /tmp/cfn-policy.json << EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "cloudformation:Describe*",
        "cloudformation:List*",
        "cloudformation:Get*"
      ],
      "Resource": "*"
    }
  ]
}
EOF

# Create ECS read-only policy
cat > /tmp/ecs-policy.json << EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ecs:Describe*",
        "ecs:List*"
      ],
      "Resource": "*"
    }
  ]
}
EOF

# Create IAM role
echo "Creating IAM role..."
aws iam create-role \
  --role-name McpReadOnlyRole \
  --assume-role-policy-document file:///tmp/trust-policy.json \
  --description "Role for MCP servers to access AWS resources with limited permissions"

# Create policies
echo "Creating CloudFormation policy..."
aws iam create-policy \
  --policy-name McpCloudFormationReadOnly \
  --policy-document file:///tmp/cfn-policy.json \
  --description "CloudFormation read-only access for MCP servers"

echo "Creating ECS policy..."
aws iam create-policy \
  --policy-name McpEcsReadOnly \
  --policy-document file:///tmp/ecs-policy.json \
  --description "ECS read-only access for MCP servers"

# Attach policies to role
echo "Attaching policies to role..."
aws iam attach-role-policy \
  --role-name McpReadOnlyRole \
  --policy-arn "arn:aws:iam::$ACCOUNT_ID:policy/McpCloudFormationReadOnly"

aws iam attach-role-policy \
  --role-name McpReadOnlyRole \
  --policy-arn "arn:aws:iam::$ACCOUNT_ID:policy/McpEcsReadOnly"

# Clean up temp files
rm -f /tmp/trust-policy.json /tmp/cfn-policy.json /tmp/ecs-policy.json

echo "✅ Successfully created McpReadOnlyRole with CloudFormation and ECS read-only permissions"
echo "Role ARN: arn:aws:iam::$ACCOUNT_ID:role/McpReadOnlyRole"

# Test role assumption
echo "Testing role assumption..."
aws sts assume-role \
  --role-arn "arn:aws:iam::$ACCOUNT_ID:role/McpReadOnlyRole" \
  --role-session-name "test-session" \
  --query 'AssumedRoleUser.Arn' \
  --output text

echo "✅ Role assumption test successful!"
