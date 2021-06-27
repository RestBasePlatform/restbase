import json

import pytest
import requests

from tables import BasesTable
from tables import TokenTable
from utils import get_existing_data


@pytest.mark.parametrize(
    "data_dict,expected_status_code,match_param",
    [
        (
            {
                "type": "postgres",
                "host": "internal_postgres",
                "port": 5433,
                "database": "postgres",
                "username": "postgres",
                "password": "password",
                "description": "some-description",
            },
            200,
            "description",
        ),
        (
            {
                "type": "postgres",
                "host": "internal_postgres",
                "port": 5433,
                "database": "postgres",
                "username": "postgres",
                "password": "password",
                "local_name": "test_local_name",
            },
            200,
            "local_name",
        ),
    ],
)
def test_add_database(
    restbase_url,
    test_main_admin_token,
    postgres_session,
    data_dict,
    expected_status_code,
    match_param,
):
    response = requests.put(
        restbase_url + "Database/Add/",
        headers={"token": test_main_admin_token},
        data=json.dumps(data_dict),
    )
    assert response.text == ''
    assert response.status_code == expected_status_code
    local_name = json.loads(response.text)["local_db_name"]

    bases = get_existing_data(
        postgres_session,
        BasesTable,
    )

    tokens = get_existing_data(
        postgres_session,
        TokenTable,
    )

    # Check new db added correctly
    assert local_name in [i.local_name for i in bases]
    if data_dict.get("description"):
        assert data_dict.get("description") in [
            i.description for i in bases
        ]

    # Check all admin tokens has access to this table
    for token in tokens:
        if token.admin_access:
            assert local_name in token.access_tables
