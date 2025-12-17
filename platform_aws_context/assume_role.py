import boto3
from typing import Dict, Any
from .identity import CallerIdentity

DEFAULT_ROLE_NAME = "McpReadOnlyRole"

def get_client_for_account(service: str, ctx_params: Dict[str, Any]):
    """
    Create a boto3 client for `service` by assuming into a target role
    in the account provided in ctx_params.

    ctx_params MUST contain:
      - account_id (str)
      - region (str)
    and MAY contain:
      - _metadata (dict) with identity info (actor, repo, pr, etc.)
    """
    account_id = ctx_params["account_id"]
    region = ctx_params.get("region", "us-east-1")
    identity = CallerIdentity.from_ctx_params(ctx_params)

    role_arn = f"arn:aws:iam::{account_id}:role/{DEFAULT_ROLE_NAME}"

    sts = boto3.client("sts")  # uses my local laptop's creds
    resp = sts.assume_role(
        RoleArn=role_arn,
        RoleSessionName=f"MCP-{identity.actor}"[:64],
        DurationSeconds=900,
    )

    creds = resp["Credentials"]
    return boto3.client(
        service,
        region_name=region,
        aws_access_key_id=creds["AccessKeyId"],
        aws_secret_access_key=creds["SecretAccessKey"],
        aws_session_token=creds["SessionToken"],
    )
