import pytest
from botocore.exceptions import ClientError
from unittest.mock import MagicMock

from authorizer.main import handler as authorizer

@pytest.fixture
def event():
    return {
        "headers": {
            "Authorization": "valid-token"
        },
        "methodArn": "arn:aws:execute-api:region:account-id:api-id/stage/GET/resource"
    }

def test_lambda_handler_with_valid_token(event, monkeypatch):
    # Mocking the environment variable
    monkeypatch.setenv('SECRET_NAME', 'test-secret')

    # Mocking the secrets_manager client
    mock_secrets_manager = MagicMock()
    mock_secrets_manager.get_secret_value.return_value = {
        'SecretString': 'valid-token'
    }
    monkeypatch.setattr('authorizer.main.secrets_manager', mock_secrets_manager)

    # Call Lambda function with valid token
    response = authorizer(event, None)

    # Assertions
    assert response["principalId"] == "*"
    assert response["policyDocument"]["Statement"][0]["Effect"] == "Allow"
    assert response["policyDocument"]["Statement"][0]["Resource"] == event['methodArn']

def test_lambda_handler_with_invalid_token(event, monkeypatch):
    # Mocking the environment variable
    monkeypatch.setenv('SECRET_NAME', 'test-secret')

    # Mocking the secrets_manager client
    mock_secrets_manager = MagicMock()
    mock_secrets_manager.get_secret_value.return_value = {
        'SecretString': 'valid-token'
    }
    monkeypatch.setattr('authorizer.main.secrets_manager', mock_secrets_manager)

    # Call Lambda function with invalid token
    event['headers']['Authorization'] = 'invalid-token'
    with pytest.raises(Exception, match="Unauthorized"):
        authorizer(event, None)

def test_lambda_handler_with_missing_secret_name(event):
    # Call Lambda function without SECRET_NAME environment variable
    with pytest.raises(KeyError):
        authorizer(event, None)

def test_lambda_handler_with_secret_not_found(event, monkeypatch):
    # Mocking the environment variable
    monkeypatch.setenv('SECRET_NAME', 'test-secret')

    # Mocking the secrets_manager client to raise ClientError
    mock_secrets_manager = MagicMock()
    mock_secrets_manager.get_secret_value.side_effect = ClientError(
        operation_name='get_secret_value',
        error_response={'Error': {'Code': 'ResourceNotFoundException', 'Message': 'Secrets Manager can’t find the specified secret.'}},
    )
    monkeypatch.setattr('authorizer.main.secrets_manager', mock_secrets_manager)

    # Call Lambda function with missing secret in Secrets Manager
    with pytest.raises(Exception, match="Unauthorized. ClientError"):
        authorizer(event, None)