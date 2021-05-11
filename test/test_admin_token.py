import pytest
import requests
import json


def test_generate_admin_token(restbase_url, test_main_admin_token):
    response = requests.post(restbase_url + "AdminToken/Generate/",
                             headers={"token": test_main_admin_token},
                             data=json.dumps({"token_name": "test_token"}))
    assert response.status_code == 200
