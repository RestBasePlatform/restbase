import pytest

from db_workers.postrgre_worker import PostgreWorker
from localbase import LocalBaseWorker


@pytest.fixture
def postgres_test_base_data():
    return {
        "host": "postgres_test_base",
        "db_name": "postgres",
        "schema": "public",
        "user": "postgres",
        "password": "password",
        # Defined in tests/alembic/versions/41a89aff45aa_test_table_1.py
        "test_table_name": "test_table_1",
        "columns": {
            "int_column": "integer",
            "bool_column": "boolean",
            "text_columns": "text_columns",
        },
    }


class TestPostgreWorker:
    def setup(self):
        self.local_worker = LocalBaseWorker(ip="postgres_internal")

    def test_download_table_list(self, postgres_test_base_data):
        worker = PostgreWorker(
            host=postgres_test_base_data["host"],
            db_name=postgres_test_base_data["db_name"],
            user=postgres_test_base_data["user"],
            password=postgres_test_base_data["password"],
            local_base_worker=self.local_worker,
        )

        worker.download_table_list()
        table_object = self.local_worker.get_table(
            local_table_name="_".join(
                [
                    postgres_test_base_data["db_name"],
                    postgres_test_base_data["schema"],
                    postgres_test_base_data["test_table_name"],
                ]
            )
        )
        assert table_object.table_name == postgres_test_base_data["test_table_name"]
        assert table_object.folder_name == postgres_test_base_data["schema"]
        assert table_object.database_name == postgres_test_base_data["db_name"]
        assert set(table_object.columns.keys()) == set(
            postgres_test_base_data["columns"].keys()
        )
