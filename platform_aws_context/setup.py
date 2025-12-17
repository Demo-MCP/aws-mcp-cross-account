from setuptools import setup, find_packages

setup(
    name="platform_aws_context",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "boto3",
    ],
    description="Cross-account AssumeRole helper for AWS MCP servers",
)
