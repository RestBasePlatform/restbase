import os
import sys

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src/")))


@pytest.fixture
def postgres_test_data():
    return {
        "type": "postgres",
        "description": "test postgres base",
        "name": "test_postgres",
        "ip": "postgres",
        "port": "5432",
        "username": "postgres",
        "password": "password",
    }


@pytest.fixture
def tables_data_postgres():
    return {
        "table_name": "test_table",
        "folder_name": "public",
        "database_name": "test_postgres",
        "local_name": "test_table",
        "columns": {"column1": "type1", "column2": "type2"},
    }


@pytest.fixture
def token_for_test():
    return {
        "token": "test-token",
        "description": "some-description",
        "granted_tables": [],
    }
