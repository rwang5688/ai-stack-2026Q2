#!/usr/bin/env python3
"""CDK app entry point for the Student Services Phase 3 Streamlit deployment."""

import os
import sys

# Add parent directory to path so docker_app.config_file is importable
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import aws_cdk as cdk

from cdk_stack import CdkStack
from docker_app.config_file import Config

app = cdk.App()
CdkStack(
    app,
    Config.STACK_NAME,
    env=cdk.Environment(region=Config.DEPLOYMENT_REGION),
)
app.synth()
