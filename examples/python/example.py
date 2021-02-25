import json

import requests

RESTBASE_IP = "http://localhost:54541/"

if __name__ == "__main__":
    # https://restbase-api.readthedocs.io/en/latest/rest_docs/tokens/get_admin_token.html
    response = requests.get(RESTBASE_IP + "GenerateAdminToken")
    response_body = json.loads(response.text)
    admin_token = response_body["admin-token"]

    # Header for some requests
    admin_header = {"admin_token": admin_token}

    # Add database
    # https://restbase-api.readthedocs.io/en/latest/rest_docs/database/add_database.html
    add_database_body = {
        "base_type": "postgres",
        "description": "some-base",
        "local_database_name": "some_local_name",
        "ip": "IP_HERE",
        "port": "PORT_HERE",
        "username": "DATABASE_USER_HERE",
        "password": "DATABASE_PASSWORD_HERE",
        "database": "BASE_NAME_HERE",
    }

    response = requests.put(
        RESTBASE_IP + "/Database/", headers=admin_header, params=add_database_body
    )

    # Check if database added successfully
    # https://restbase-api.readthedocs.io/en/latest/rest_docs/database/list_database.html
    response = requests.get(RESTBASE_IP + "/Database/list/", headers=admin_header)

    # Add user token
    # https://restbase-api.readthedocs.io/en/latest/rest_docs/tokens/generate_user_token.html
    body_generate_token = {
        "description": "demo-description",
        "token_name": "demo-token",  # comment for random generating
        "user_token": "demo-token",
    }

    response = requests.put(
        RESTBASE_IP + "/GenerateUserToken",
        headers=admin_header,
        params=body_generate_token,
    )

    # Check if token added successfully
    #
    response = requests.get(
        RESTBASE_IP + "/ListUserTokens",
        headers=admin_header,
    )
    response_body = json.loads(response.text)
    user_token = response_body["tokens"][0]["token"]

    # Check tables list
    # https://restbase-api.readthedocs.io/en/latest/rest_docs/table/list_table.html
    response = requests.get(
        RESTBASE_IP + "Table/list", headers={"user_token": admin_token}
    )
    response_body = json.loads(response.text)
    local_table_names = response_body["List"]
    print(local_table_names)
    # Grant access to tables for new token
    # https://restbase-api.readthedocs.io/en/latest/rest_docs/tokens/grant_table_access.html
    for local_table_name in local_table_names:
        body_grant_access = {
            "user_token": user_token,
            "local_table_name": local_table_name,
        }

        response = requests.post(
            RESTBASE_IP + "/GrantTableAccess",
            headers=admin_header,
            params=body_grant_access,
        )

    # Extract data from table
    # https://restbase-api.readthedocs.io/en/latest/rest_docs/get_data_request.html
    body_get_data = {
        "local_database_name": "some_local_name",  # Here local name from Add database request
        "query": "SELECT * FROM public.test_table",
    }

    response = requests.get(
        RESTBASE_IP + "/GetData",
        headers={"user_token": user_token},
        params=body_get_data,
    )
