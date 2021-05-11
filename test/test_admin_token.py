import json

import requests

from tables import TokenTable
from utils import get_existing_data


def test_generate_admin_token(restbase_url, test_main_admin_token, postgres_session):
    response = requests.post(
        restbase_url + "AdminToken/Generate/",
        headers={"token": test_main_admin_token},
        data=json.dumps({"token_name": "test_token"}),
    )
    assert response.status_code == 200
    new_token = response.text

    tokens = get_existing_data(
        postgres_session,
        TokenTable,
    )

    # Check new token exists in database
    assert new_token in [i.token for i in tokens if i.admin_access]
