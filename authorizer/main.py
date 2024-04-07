import os

import boto3
from botocore.exceptions import ClientError

secrets_manager = boto3.client('secretsmanager')


def handler(event, context):
    try:
        # Get the secret name from the environment variable
        secret_name = os.environ['SECRET_NAME']

        # Get the token from the request headers
        token = event['headers']['x-api-key']

        # Retrieve the secret from Secrets Manager
        response = secrets_manager.get_secret_value(SecretId=secret_name)
        secret = response['SecretString']

        # Validate the token against the secret
        if token == secret:
            # If the token is valid, return an IAM policy
            return generate_policy('*', 'Allow', event['methodArn'])
        else:
            # If the token is invalid, deny access
            raise Exception("Unauthorized")
            # return generate_policy('*', 'Deny', event['methodArn'])
    except ClientError:
        # return generate_policy('*', 'Deny', event['methodArn'])
        raise Exception("Unauthorized. ClientError")


def generate_policy(principal_id, effect, resource):
    policy_document = {
        'Version': '2012-10-17',
        'Statement': [{
            'Action': 'execute-api:Invoke',
            'Effect': effect,
            'Resource': resource
        }]
    }

    return {
        'principalId': principal_id,
        'policyDocument': policy_document
    }
