import json

import pandas as pd
import pytest
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


@pytest.mark.parametrize(
    "db_data",
    [
        {
            "type": "postgres",
            "local_database_name": "test-base",
            "ip": "postgres_test_base",
            "port": "5432",
            "database": "postgres",
            "username": "postgres",
            "password": "password",
        },
        {
            "type": "mysql",
            "local_database_name": "test-base-mysql",
            "ip": "mysql_test_base",
            "port": "3306",
            "database": "mysql",
            "username": "root",
            "password": "password",
        },
    ],
)
def test_add_database(internal_db_session, db_data):
    headers = {"admin_token": "admin-test-token"}

    body = {
        "base_type": db_data["type"],
        "description": f"test-base-{db_data['type']}",
        **db_data,
    }

    response = requests.put("http://api:54541/Database", headers=headers, params=body)
    print(response.text)
    assert response.status_code == 200
    # Check that cant add the same base again
    response = requests.put("http://api:54541/Database", headers=headers, params=body)
    assert response.status_code == 500
    #
    tables = pd.read_sql(
        f"""SELECT * FROM tables_info where database_name = '{db_data["local_database_name"]}'""",
        con=internal_db_session,
    )
    bases = pd.read_sql("SELECT * FROM bases", con=internal_db_session)
    assert "test_table_1" in tables["table_name"].values
    assert db_data["local_database_name"] in bases["local_name"].values


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


def test_list_databases(internal_db_session, postgre_db_data, mysql_db_data):
    headers = {"admin_token": "admin-test-token"}

    response = requests.get("http://api:54541/Database/list", headers=headers)
    response_body = json.loads(response.text)
    assert response.status_code == 200

    assert set(response_body["List"]) == {
        postgre_db_data["local_database_name"],
        mysql_db_data["local_database_name"],
    }


def test_rename_table_by_local_table_name(internal_db_session, postgre_db_data):
    # Database added in test_add_database with test_table_1
    headers_admin = {
        "content-type": "application/json",
        "admin_token": "admin-test-token",
    }
    headers_user = {
        "content-type": "application/json",
        "user_token": "test_rename_table_by_local_table_name",
    }

    body_grant_access = {
        "user_token": "test_rename_table_by_local_table_name",
        "local_table_name": "_".join(
            [postgre_db_data.get("local_database_name"), "public", "test_table_1"]
        ),
    }

    body_generate_token = {
        "description": "test-description",
        "token_name": "test_rename_table_by_local_table_name",
        "user_token": "test_rename_table_by_local_table_name",
    }

    resp = requests.put(
        "http://api:54541/GenerateUserToken",
        headers=headers_admin,
        params=body_generate_token,
    )
    assert resp.status_code == 201

    resp = requests.post(
        "http://api:54541/GrantTableAccess",
        headers=headers_admin,
        params=body_grant_access,
    )
    assert resp.status_code == 200

    body_rename = {
        "table": {
            "local_table_name": "_".join(
                [postgre_db_data.get("local_database_name"), "public", "test_table_1"]
            )
        },
        "new_local_table_name": "new_test_table_1",
    }

    response = requests.post(
        "http://api:54541/Table", headers=headers_admin, json=body_rename
    )
    print(response.text)
    response_body = json.loads(response.text)
    assert response.status_code == 200

    # Check that response is correct
    assert response_body["new_table_name"] == "new_test_table_1"

    response = requests.get("http://api:54541/Table/list", headers=headers_user)
    print(response.text)
    response_body = json.loads(response.text)
    assert response.status_code == 200

    assert "new_test_table_1" in response_body["List"]


def test_rename_table_by_full_table_path(internal_db_session, postgre_db_data):
    # Database added in test_add_database with test_table_1 and table renamed to new_test_table_1 in
    # test_rename_table_by_local_table_name
    headers_admin = {
        "content-type": "application/json",
        "admin_token": "admin-test-token",
    }
    headers_user = {
        "content-type": "application/json",
        "user_token": "test_rename_table_by_full_table_path",
    }

    body_grant_access = {
        "user_token": "test_rename_table_by_full_table_path",
        "local_table_name": "new_test_table_1",
    }

    body_generate_token = {
        "description": "test-description",
        "token_name": "test_rename_table_by_full_table_path",
        "user_token": "test_rename_table_by_full_table_path",
    }

    resp = requests.put(
        "http://api:54541/GenerateUserToken",
        headers=headers_admin,
        params=body_generate_token,
    )
    assert resp.status_code == 201

    resp = requests.post(
        "http://api:54541/GrantTableAccess",
        headers=headers_admin,
        params=body_grant_access,
    )
    assert resp.status_code == 200

    body_rename = {
        "table": {"database": "test-base", "folder": "public", "table": "test_table_1"},
        "new_local_table_name": "new_test_table_2",
    }

    response = requests.post(
        "http://api:54541/Table", headers=headers_admin, json=body_rename
    )

    response_body = json.loads(response.text)
    assert response.status_code == 200

    # Check that response is correct
    assert response_body["new_table_name"] == "new_test_table_2"

    response = requests.get("http://api:54541/Table/list", headers=headers_user)
    print(response.text)
    response_body = json.loads(response.text)
    assert response.status_code == 200

    assert "new_test_table_2" in response_body["List"]


def test_rename_table_errors(internal_db_session, postgre_db_data):
    # Database added in test_add_database with test_table_1
    headers = {"content-type": "application/json", "admin_token": "admin-test-token"}
    body = {
        "table": {"local_table_name": "some_table_random"},
        "new_local_table_name": "new_test_table_2",
    }
    response = requests.post("http://api:54541/Table", headers=headers, json=body)
    assert response.status_code == 404

    # Check that response is correct
    assert response.text == "Table not found"

    body = {
        "table": {"database": "test-base", "folder": "public", "table": "test_table_2"},
        "new_local_table_name": "new_test_table_2",
    }
    response = requests.post("http://api:54541/Table", headers=headers, json=body)
    assert response.status_code == 404

    # Check that response is correct
    assert response.text == "Table not found"


def test_list_tables_request_admin_token(internal_db_session, postgre_db_data):
    # Database added in test_add_database with test_table_1 and renamed to new_test_table_2 in
    # test_rename_table_by_full_table_path
    headers = {"content-type": "application/json", "admin_token": "admin-test-token"}

    response = requests.get("http://api:54541/Table/list", headers=headers)
    response_body = json.loads(response.text)
    assert response.status_code == 200

    assert "new_test_table_2" in response_body["List"]


def test_list_tables_request_user_token(internal_db_session, postgre_db_data):
    # Database added in test_add_database with test_table_1 and renamed to new_test_table_2 in
    # test_rename_table_by_full_table_path
    headers = {"content-type": "application/json", "admin_token": "admin-test-token"}

    response = requests.get("http://api:54541/Table/list", headers=headers)
    assert response.status_code == 200

    body_grant_access = {
        "user_token": "test_list_tables_request_user_token",
        "local_table_name": "new_test_table_2",
    }

    body_generate_token = {
        "description": "test-description",
        "token_name": "test_list_tables_request_user_token",
        "user_token": "test_list_tables_request_user_token",
    }

    resp = requests.put(
        "http://api:54541/GenerateUserToken",
        headers=headers,
        params=body_generate_token,
    )
    assert resp.status_code == 201

    resp = requests.post(
        "http://api:54541/GrantTableAccess",
        headers=headers,
        params=body_grant_access,
    )
    assert resp.status_code == 200

    user_headers = {
        "content-type": "application/json",
        "user_token": "test_list_tables_request_user_token",
    }

    response = requests.get("http://api:54541/Table/list", headers=user_headers)
    response_body = json.loads(response.text)
    assert response.status_code == 200

    assert "new_test_table_2" in response_body["List"]


def test_get_data_no_table(internal_db_session, postgre_db_data):
    headers_admin = {
        "content-type": "application/json",
        "admin_token": "admin-test-token",
    }

    body_generate_token = {
        "description": "test-description",
        "token_name": "test_get_data_no_table",
        "user_token": "test_get_data_no_table",
    }

    resp = requests.put(
        "http://api:54541/GenerateUserToken",
        headers=headers_admin,
        params=body_generate_token,
    )
    assert resp.status_code == 201

    body_grant_access = {
        "user_token": "test_get_data_no_table",
        "local_table_name": "new_test_table_2",
    }

    resp = requests.post(
        "http://api:54541/GrantTableAccess",
        headers=headers_admin,
        params=body_grant_access,
    )
    assert resp.status_code == 200

    headers_user = {
        "content-type": "application/json",
        "user_token": "test_get_data_no_table",
    }
    # Table test_table_2 doesn't exists - so we got permission denied
    body_get_data = {
        "local_database_name": "test-base",
        "query": "SELECT * FROM public.test_table_2",
    }

    resp = requests.get(
        "http://api:54541/GetData",
        headers=headers_user,
        params=body_get_data,
    )

    assert resp.status_code == 403


def test_get_data_no_access(internal_db_session, postgre_db_data):
    headers_admin = {
        "content-type": "application/json",
        "admin_token": "admin-test-token",
    }

    body_generate_token = {
        "description": "test-description",
        "token_name": "test_get_data_no_access",
        "user_token": "test_get_data_no_access",
    }

    resp = requests.put(
        "http://api:54541/GenerateUserToken",
        headers=headers_admin,
        params=body_generate_token,
    )
    assert resp.status_code == 201

    headers_user = {
        "content-type": "application/json",
        "user_token": "test_get_data_no_access",
    }
    # Table test_table_1 exists but we don't grant access for this
    body_get_data = {
        "local_database_name": "test-base",
        "query": "SELECT * FROM public.test_table_1",
    }

    resp = requests.get(
        "http://api:54541/GetData",
        headers=headers_user,
        params=body_get_data,
    )
    print(resp.text)
    assert resp.status_code == 403


def test_get_data_success(internal_db_session, postgre_db_data):
    headers_admin = {
        "content-type": "application/json",
        "admin_token": "admin-test-token",
    }

    body_generate_token = {
        "description": "test-description",
        "token_name": "test_get_data_success",
        "user_token": "test_get_data_success",
    }

    resp = requests.put(
        "http://api:54541/GenerateUserToken",
        headers=headers_admin,
        params=body_generate_token,
    )
    assert resp.status_code == 201

    body_grant_access = {
        "user_token": "test_get_data_success",
        "local_table_name": "new_test_table_2",
    }

    resp = requests.post(
        "http://api:54541/GrantTableAccess",
        headers=headers_admin,
        params=body_grant_access,
    )
    assert resp.status_code == 200

    headers_user = {
        "content-type": "application/json",
        "user_token": "test_get_data_success",
    }
    # Table test_table_1 exists but we don't grant access for this
    body_get_data = {
        "local_database_name": "test-base",
        "query": "SELECT * FROM public.test_table_1",
    }

    resp = requests.get(
        "http://api:54541/GetData",
        headers=headers_user,
        params=body_get_data,
    )

    assert resp.status_code == 200
