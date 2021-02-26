import os
import sys

import pytest
import sqlalchemy

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src/")))

from utils import get_existing_data  # noqa: E402


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
def internal_db_session():
    main_db_string = "postgresql://postgres:password@api/postgres"
    return sqlalchemy.create_engine(main_db_string)


@pytest.fixture
def postgre_db_data():
    return {
        "local_database_name": "test-base",
        "ip": "postgres_test_base",
        "port": "5432",
        "database": "postgres",
        "username": "postgres",
        "password": "password",
    }


class Helpers:
    @staticmethod
    def get_column_data_from_table(session, table_object, col_name):
        return get_existing_data(session, table_object, col_name)
