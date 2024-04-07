import os

import boto3
import pytest
import requests

"""
Make sure env variable AWS_SAM_STACK_NAME exists with the name of the stack we are going to test. 
"""


class TestApiGateway:

    @pytest.fixture(scope="class")
    def api_gateway_url(self):
        """ Get the API Gateway URL from Cloudformation Stack outputs """
        stack_name = os.environ.get("AWS_SAM_STACK_NAME")

        if stack_name is None:
            raise ValueError('Please set the AWS_SAM_STACK_NAME environment variable to the name of your stack')

        client = boto3.client("cloudformation")

        try:
            response = client.describe_stacks(StackName=stack_name)
        except Exception as e:
            raise Exception(
                f"Cannot find stack {stack_name} \n" f'Please make sure a stack with the name "{stack_name}" exists'
            ) from e

        stacks = response["Stacks"]
        stack_outputs = stacks[0]["Outputs"]
        api_outputs = [output for output in stack_outputs if output["OutputKey"] == "FastAPISAM"]

        if not api_outputs:
            raise KeyError(f"FastAPISAM not found in stack {stack_name}")

        return api_outputs[0]["OutputValue"]  # Extract url from stack outputs

    @pytest.fixture(scope="class")
    def items_api(self, api_gateway_url):
        return api_gateway_url + "/v1/items"

    @pytest.fixture(scope="class")
    def create_item(self, items_api):
        """Create an item and return the response"""
        response = requests.post(items_api, json={"name": "NewItem", "description": "Sample"},
                                 headers={'x-api-token': 'token'})
        assert response.status_code == 200
        return response.json()

    @pytest.fixture(scope="class")
    def item_id(self, create_item):
        """Extract the item ID from the create response"""
        return create_item['id']

    def test_create_item(self, create_item):
        assert 'id' in create_item

    def test_read_items(self, items_api):
        response = requests.get(items_api, headers={'x-api-token': 'token'})
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_read_item(self, items_api, item_id):
        item_url = items_api + f"/{item_id}"
        response = requests.get(item_url, headers={'x-api-token': 'token'})
        assert response.status_code == 200
        assert response.json()['id'] == item_id

    def test_update_item(self, items_api, item_id):
        item_url = items_api + f"/{item_id}"
        updated_data = {"name": "UpdatedItem", "description": "UpdatedDesc"}
        response = requests.put(item_url, json=updated_data, headers={'x-api-token': 'token'})
        assert response.status_code == 200
        assert response.json()['name'] == "UpdatedItem"

    def test_delete_item(self, items_api, item_id):
        item_url = items_api + f"/{item_id}"
        # Delete the item
        delete_response = requests.delete(item_url, headers={'x-api-token': 'token'})
        assert delete_response.status_code == 200
        # Check to ensure the item is deleted
        get_response = requests.get(item_url)
        assert get_response.status_code == 404
