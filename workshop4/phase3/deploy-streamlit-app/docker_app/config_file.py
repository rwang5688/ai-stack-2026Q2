"""Configuration constants for the CDK stack and Docker app."""


class Config:
    STACK_NAME = "StudentServicesPhase3"
    CUSTOM_HEADER_VALUE = "StudentServicesPhase3SecureHeader2026"
    SECRETS_MANAGER_ID = f"{STACK_NAME}CognitoSecret"
    DEPLOYMENT_REGION = "us-west-2"
