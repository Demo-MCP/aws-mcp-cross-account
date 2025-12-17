#!/usr/bin/env python3
"""
Test cross-account functionality
"""

import boto3
from platform_aws_context.assume_role import get_client_for_account

def get_current_account():
    """Get current AWS account ID."""
    sts = boto3.client("sts")
    return sts.get_caller_identity()["Account"]

def test_cloudformation_access():
    """Test CloudFormation access via AssumeRole."""
    
    account_id = get_current_account()
    print(f"Testing CloudFormation access for account: {account_id}")
    
    ctx_params = {
        "account_id": account_id,
        "region": "us-east-1",
        "_metadata": {
            "actor": "local-test",
            "repo": "test-repo"
        }
    }
    
    try:
        cfn_client = get_client_for_account(service="cloudformation", ctx_params=ctx_params)
        result = cfn_client.list_stacks(StackStatusFilter=['CREATE_COMPLETE', 'UPDATE_COMPLETE'])
        stacks = result.get('StackSummaries', [])
        
        print(f"✅ CloudFormation access via McpReadOnlyRole succeeded!")
        print(f"   Found {len(stacks)} stacks")
        
        return True
        
    except Exception as e:
        print(f"❌ CloudFormation access failed: {e}")
        return False

def test_ecs_access():
    """Test ECS access via AssumeRole."""
    
    account_id = get_current_account()
    print(f"Testing ECS access for account: {account_id}")
    
    ctx_params = {
        "account_id": account_id,
        "region": "us-east-1",
        "_metadata": {
            "actor": "local-test",
            "repo": "test-repo"
        }
    }
    
    try:
        ecs_client = get_client_for_account(service="ecs", ctx_params=ctx_params)
        result = ecs_client.list_clusters()
        clusters = result.get('clusterArns', [])
        
        print(f"✅ ECS access via McpReadOnlyRole succeeded!")
        print(f"   Found {len(clusters)} clusters")
        
        return True
        
    except Exception as e:
        if "AccessDenied" in str(e) or "not authorized" in str(e):
            print(f"❌ ECS access denied (expected if role lacks ECS permissions): {e}")
        else:
            print(f"❌ ECS access failed with unexpected error: {e}")
        return False

def test_multi_region():
    """Test access to different regions."""
    
    account_id = get_current_account()
    regions = ["us-east-1", "us-west-2"]
    
    print(f"Testing multi-region access for account: {account_id}")
    
    for region in regions:
        ctx_params = {
            "account_id": account_id,
            "region": region,
            "_metadata": {
                "actor": "local-test",
                "repo": "test-repo"
            }
        }
        
        try:
            cfn_client = get_client_for_account(service="cloudformation", ctx_params=ctx_params)
            result = cfn_client.list_stacks(StackStatusFilter=['CREATE_COMPLETE', 'UPDATE_COMPLETE'])
            stacks = result.get('StackSummaries', [])
            
            print(f"✅ {region}: Found {len(stacks)} stacks")
            
        except Exception as e:
            print(f"❌ {region}: Access failed: {e}")

def main():
    print("🧪 Testing AWS MCP Cross-Account Setup")
    print("=" * 50)
    
    # Test 1: CloudFormation access
    print("\n1. Testing CloudFormation Access")
    print("-" * 30)
    cf_success = test_cloudformation_access()
    
    # Test 2: ECS access
    print("\n2. Testing ECS Access")
    print("-" * 30)
    ecs_success = test_ecs_access()
    
    # Test 3: Multi-region access
    print("\n3. Testing Multi-Region Access")
    print("-" * 30)
    test_multi_region()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Summary")
    print(f"CloudFormation: {'✅ PASS' if cf_success else '❌ FAIL'}")
    print(f"ECS: {'✅ PASS' if ecs_success else '❌ FAIL (check role permissions)'}")
    
    if cf_success:
        print("\n🎉 Cross-account setup is working!")
        print("Your MCP servers can now assume roles in different accounts.")
    else:
        print("\n⚠️  Setup needs attention. Check:")
        print("- McpReadOnlyRole exists")
        print("- Trust policy allows your user to assume the role")
        print("- Role has CloudFormation permissions")

if __name__ == "__main__":
    main()
