import json

import pandas as pd
import requests


# def test_generate_admin_token():
#     #  Admin token already exists -> get error
#     response = requests.get(
#         "http://api:54541/admin_token",
#     )
#
#     assert response.status_code == 409


def test_generate_pre_defined_user_token(internal_db_session):
    headers = {"admin_token": "admin-test-token"}

    body = {
        "description": "test-description",
        "token_name": "test_generate_pre_defined_user_token",
    }

    body = {**body, "user_token": "test-token"}
    response = requests.put(
        "http://api:54541/GenerateUserToken", headers=headers, params=body
    )

    assert response.status_code == 201
    response = json.loads(response.text)
    assert response["new_token"] == "test-token"


def test_generate_random_user_token(internal_db_session):
    headers = {"admin_token": "admin-test-token"}
    body = {
        "description": "test-description",
        "token_name": "test_generate_random_user_token",
    }

    response = requests.put(
        "http://api:54541/GenerateUserToken", headers=headers, params=body
    )

    assert response.status_code == 201

    response = json.loads(response.text)
    assert len(response["new_token"]) == 64

    tables = pd.read_sql("SELECT * FROM tokens", con=internal_db_session)
    assert response["new_token"] in tables["token"].values

    body = {
        "user_token": response["new_token"],
        "token_name": "test_generate_random_user_token",
    }
    response = requests.put(
        "http://api:54541/GenerateUserToken", headers=headers, params=body
    )

    assert response.status_code == 409


def test_add_database(internal_db_session, postgre_db_data):
    headers = {"admin_token": "admin-test-token"}

    body = {"base_type": "postgres", "description": "test-base", **postgre_db_data}

    response = requests.put("http://api:54541/Database", headers=headers, params=body)
    assert response.status_code == 200
    # Check that cant add the same base again
    response = requests.put("http://api:54541/Database", headers=headers, params=body)
    assert response.status_code == 500

    tables = pd.read_sql("SELECT * FROM tables_info", con=internal_db_session)
    bases = pd.read_sql("SELECT * FROM bases", con=internal_db_session)
    assert "test_table_1" in tables["table_name"].values
    assert "test-base" in bases["local_name"].values


def test_grant_table_access_with_local_table_name(internal_db_session, postgre_db_data):

    # Check that for None token we got bad request
    assert requests.post("http://api:54541/GrantTableAccess").status_code == 400
    assert (
        requests.post(
            "http://api:54541/GrantTableAccess",
            headers={"admin_token": "some-random"},
        ).status_code
        == 400  # noqa: W503
    )

    # generate token for give access to
    headers = {"admin_token": "admin-test-token"}

    body = {
        "description": "test-description",
        "user_token": "GrantTableAccessWithLocalName",
        "token_name": "test_grant_table_access_with_local_table_name",
    }

    requests.put("http://api:54541//GenerateUserToken", headers=headers, params=body)

    headers = {"admin_token": "admin-test-token"}
    local_name = "_".join(
        [postgre_db_data.get("local_database_name"), "public", "test_table_1"]
    )
    body = {
        "user_token": "GrantTableAccessWithLocalName",
        "local_table_name": local_name,
    }
    response = requests.post(
        "http://api:54541/GrantTableAccess", headers=headers, params=body
    )
    assert response.status_code == 200

    # Check that we cant grant access to the same table again
    response = requests.post(
        "http://api:54541/GrantTableAccess", headers=headers, params=body
    )
    assert response.status_code == 404

    tokens = pd.read_sql("SELECT * FROM tokens", con=internal_db_session)
    assert (
        local_name
        in tokens[tokens["token"] == "GrantTableAccessWithLocalName"].iloc[0][
            "granted_tables"
        ]
    )


def test_grant_table_access_without_local_table_name(
    internal_db_session, postgre_db_data
):

    # Check that for None token we got access denied
    assert requests.post("http://api:54541/GrantTableAccess").status_code == 400
    assert (
        requests.post(
            "http://api:54541/GrantTableAccess", headers={"admin_token": "some-random"}
        ).status_code
        == 400  # noqa: W503
    )

    # generate token for give access to
    headers = {"admin_token": "admin-test-token"}

    body = {
        "description": "test-description",
        "user_token": "GrantTableAccessWithoutLocalName",
        "token_name": "test_grant_table_access_without_local_table_name",
    }

    requests.put("http://api:54541/GenerateUserToken", headers=headers, params=body)

    local_name = "_".join(
        [postgre_db_data.get("local_database_name"), "public", "test_table_1"]
    )
    body = {
        "user_token": "GrantTableAccessWithoutLocalName",
        "database": postgre_db_data["local_database_name"],
        "folder": "public",
        "table": "test_table_1",
    }
    response = requests.post(
        "http://api:54541/GrantTableAccess", headers=headers, params=body
    )
    assert response.status_code == 200

    # Check that we cant grant access to the same table again
    response = requests.post(
        "http://api:54541/GrantTableAccess", headers=headers, params=body
    )
    assert response.status_code == 404

    tokens = pd.read_sql("SELECT * FROM tokens", con=internal_db_session)
    assert (
        local_name
        in tokens[tokens["token"] == "GrantTableAccessWithoutLocalName"].iloc[0][
            "granted_tables"
        ]
    )


def test_list_databases(internal_db_session, postgre_db_data):
    headers = {"admin_token": "admin-test-token"}

    response = requests.get("http://api:54541/Database/list", headers=headers)
    response_body = json.loads(response.text)
    assert response.status_code == 200

    assert set(response_body["List"]) == {postgre_db_data["local_database_name"]}
