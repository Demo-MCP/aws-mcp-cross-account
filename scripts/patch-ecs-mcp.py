#!/usr/bin/env python3
"""
Patch ECS MCP server for cross-account AssumeRole support
"""

import sys
import re
from pathlib import Path

def patch_ecs_api(ecs_path):
    """Patch the ECS API resource management file."""
    
    api_file = ecs_path / "awslabs/ecs_mcp_server/api/resource_management.py"
    
    if not api_file.exists():
        raise FileNotFoundError(f"ECS API file not found: {api_file}")
    
    with open(api_file, 'r') as f:
        content = f.read()
    
    # Add import for get_client_for_account
    if 'from platform_aws_context.assume_role import get_client_for_account' not in content:
        import_pattern = r'(from awslabs\.ecs_mcp_server\.utils\.aws import get_aws_client)'
        replacement = r'\1\nfrom platform_aws_context.assume_role import get_client_for_account'
        content = re.sub(import_pattern, replacement, content)
    
    # Modify function signature
    old_signature = r'async def ecs_api_operation\(api_operation: str, api_params: Dict\[str, Any\]\) -> Dict\[str, Any\]:'
    new_signature = r'async def ecs_api_operation(api_operation: str, api_params: Dict[str, Any], account_context: Dict[str, Any] = None) -> Dict[str, Any]:'
    content = re.sub(old_signature, new_signature, content)
    
    # Replace client creation
    old_client = r'ecs_client = await get_aws_client\("ecs"\)'
    new_client = '''if account_context:
            ecs_client = get_client_for_account(service="ecs", ctx_params=account_context)
        else:
            ecs_client = await get_aws_client("ecs")'''
    content = re.sub(old_client, new_client, content)
    
    with open(api_file, 'w') as f:
        f.write(content)
    
    print(f"✅ Patched {api_file}")

def patch_ecs_module(ecs_path):
    """Patch the ECS module file."""
    
    module_file = ecs_path / "awslabs/ecs_mcp_server/modules/resource_management.py"
    
    if not module_file.exists():
        raise FileNotFoundError(f"ECS module file not found: {module_file}")
    
    with open(module_file, 'r') as f:
        content = f.read()
    
    # Add account_id field
    if 'account_id_field' not in content:
        account_id_field = '''    account_id_field = Field(
        default="",
        description="AWS account ID for cross-account access (optional)",
    )'''
        
        content = re.sub(
            r'(api_params_field = Field\([^}]+\))',
            r'\1\n\n' + account_id_field,
            content
        )
    
    # Update function signature
    old_signature = r'async def mcp_ecs_resource_management\(\s*api_operation: str = api_operation_field,\s*api_params: Dict\[str, Any\] = api_params_field,\s*\) -> Dict\[str, Any\]:'
    
    new_signature = '''async def mcp_ecs_resource_management(
        api_operation: str = api_operation_field,
        api_params: Dict[str, Any] = api_params_field,
        account_id: str = account_id_field,
        region: str = Field(default="us-east-1", description="AWS region"),
    ) -> Dict[str, Any]:'''
    
    content = re.sub(old_signature, new_signature, content, flags=re.MULTILINE | re.DOTALL)
    
    # Update function call
    old_call = r'return await ecs_api_operation\(api_operation, api_params\)'
    new_call = '''account_context = None
        if account_id:
            account_context = {
                "account_id": account_id,
                "region": region,
                "_metadata": {
                    "actor": "local-test",
                    "repo": "local/mcp-test"
                }
            }
        return await ecs_api_operation(api_operation, api_params, account_context)'''
    
    content = re.sub(old_call, new_call, content)
    
    with open(module_file, 'w') as f:
        f.write(content)
    
    print(f"✅ Patched {module_file}")

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 patch-ecs-mcp.py <path_to_ecs_mcp_server>")
        sys.exit(1)
    
    ecs_path = Path(sys.argv[1])
    
    if not ecs_path.exists():
        print(f"❌ ECS MCP path does not exist: {ecs_path}")
        sys.exit(1)
    
    try:
        print("Patching ECS MCP server for cross-account support...")
        patch_ecs_api(ecs_path)
        patch_ecs_module(ecs_path)
        print("✅ ECS MCP server patched successfully!")
        
    except Exception as e:
        print(f"❌ Error patching ECS MCP server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
