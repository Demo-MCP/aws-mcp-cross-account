#!/usr/bin/env python3
"""
Patch IaC MCP server for cross-account AssumeRole support
"""

import sys
import re
from pathlib import Path

def patch_troubleshooter(iac_path):
    """Patch the CloudFormation troubleshooter class."""
    
    troubleshooter_file = iac_path / "awslabs/aws_iac_mcp_server/tools/cloudformation_deployment_troubleshooter.py"
    
    if not troubleshooter_file.exists():
        raise FileNotFoundError(f"Troubleshooter file not found: {troubleshooter_file}")
    
    with open(troubleshooter_file, 'r') as f:
        content = f.read()
    
    # Add import
    if 'from platform_aws_context.assume_role import get_client_for_account' not in content:
        import_pattern = r'(from \.\.client\.aws_client import get_aws_client)'
        replacement = r'\1\nfrom platform_aws_context.assume_role import get_client_for_account'
        content = re.sub(import_pattern, replacement, content)
    
    # Update __init__ method
    old_init = r'def __init__\(self, region: str = \'us-east-1\'\):'
    new_init = r'def __init__(self, region: str = \'us-east-1\', account_context: Dict[str, Any] = None):'
    content = re.sub(old_init, new_init, content)
    
    # Update client creation
    old_cfn_client = r'self\.cfn_client = get_aws_client\(\'cloudformation\', region_name=region\)'
    new_cfn_client = '''if account_context:
            self.cfn_client = get_client_for_account(service="cloudformation", ctx_params=account_context)
        else:
            self.cfn_client = get_aws_client('cloudformation', region_name=region)'''
    content = re.sub(old_cfn_client, new_cfn_client, content)
    
    old_cloudtrail_client = r'self\.cloudtrail_client = get_aws_client\(\'cloudtrail\', region_name=region\)'
    new_cloudtrail_client = '''if account_context:
            self.cloudtrail_client = get_client_for_account(service="cloudtrail", ctx_params=account_context)
        else:
            self.cloudtrail_client = get_aws_client('cloudtrail', region_name=region)'''
    content = re.sub(old_cloudtrail_client, new_cloudtrail_client, content)
    
    with open(troubleshooter_file, 'w') as f:
        f.write(content)
    
    print(f"✅ Patched {troubleshooter_file}")

def patch_server(iac_path):
    """Patch the server file."""
    
    server_file = iac_path / "awslabs/aws_iac_mcp_server/server.py"
    
    if not server_file.exists():
        raise FileNotFoundError(f"Server file not found: {server_file}")
    
    with open(server_file, 'r') as f:
        content = f.read()
    
    # Update function signature
    old_signature = r'def troubleshoot_cloudformation_deployment\(\s*stack_name: str,\s*region: str,\s*include_cloudtrail: bool = True,\s*\) -> str:'
    
    new_signature = '''def troubleshoot_cloudformation_deployment(
    stack_name: str,
    region: str,
    include_cloudtrail: bool = True,
    account_id: str = "",
) -> str:'''
    
    content = re.sub(old_signature, new_signature, content, flags=re.MULTILINE | re.DOTALL)
    
    # Update troubleshooter instantiation
    old_instantiation = r'troubleshooter = DeploymentTroubleshooter\(region=region\)'
    
    new_instantiation = '''account_context = None
    if account_id:
        account_context = {
            "account_id": account_id,
            "region": region,
            "_metadata": {
                "actor": "local-test",
                "repo": "local/mcp-test"
            }
        }
    troubleshooter = DeploymentTroubleshooter(region=region, account_context=account_context)'''
    
    content = re.sub(old_instantiation, new_instantiation, content)
    
    with open(server_file, 'w') as f:
        f.write(content)
    
    print(f"✅ Patched {server_file}")

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 patch-iac-mcp.py <path_to_iac_mcp_server>")
        sys.exit(1)
    
    iac_path = Path(sys.argv[1])
    
    if not iac_path.exists():
        print(f"❌ IaC MCP path does not exist: {iac_path}")
        sys.exit(1)
    
    try:
        print("Patching IaC MCP server for cross-account support...")
        patch_troubleshooter(iac_path)
        patch_server(iac_path)
        print("✅ IaC MCP server patched successfully!")
        
    except Exception as e:
        print(f"❌ Error patching IaC MCP server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
