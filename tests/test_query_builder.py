import pytest

from query_builders.query_builder import QueryBuilder
from tables import TablesInfoTable


@pytest.fixture
def local_base_worker_emulator(tables_data_postgres):
    # Class to emulate LocalBaseWorker for tests
    class WorkerEmulator:
        @staticmethod
        def get_table(local_table_name):
            if local_table_name == tables_data_postgres["local_name"]:
                table = TablesInfoTable()
                setattr(table, "folder_name", tables_data_postgres["folder_name"])
                setattr(table, "table_name", tables_data_postgres["table_name"])
                return table

    return WorkerEmulator()


class TestQueryBuilder:
    @pytest.mark.parametrize(
        "request_body, query",
        [
            ({"table": "test_table"}, "SELECT * FROM public.test_table"),
            (
                {"table": "test_table", "columns": ["column1", "column2"]},
                "SELECT column1, column2 from public.test_table",
            ),
            (
                {
                    "table": "test_table",
                    "columns": ["column1", "column2"],
                    "filter": {"column1": {"filter_type": ">", "value": 10}},
                },
                "SELECT column1, column2 from public.test_table WHERE column1 > 10",
            ),
            (
                {
                    "table": "test_table",
                    "columns": ["column1", "column2"],
                    "filter": {
                        "column1": {"filter_type": ">", "value": 10},
                        "column2": {"filter_type": ">", "value": 10},
                    },
                    "filter_type": "and",
                },
                "SELECT column1, column2 from public.test_table WHERE column1 > 10 and column2 > 10",
            ),
            (
                {
                    "table": "test_table",
                    "columns": ["column1", "column2"],
                    "filter": {
                        "column1": {"filter_type": ">", "value": 10},
                        "column2": {"filter_type": ">", "value": 10},
                    },
                    "filter_type": "or",
                },
                "SELECT column1, column2 from public.test_table WHERE column1 > 10 or column2 > 10",
            ),
            (
                {
                    "table": "test_table",
                    "filter": {
                        "column1": {"filter_type": ">", "value": 10},
                        "column2": {"filter_type": ">", "value": 10},
                    },
                    "filter_type": "or",
                },
                "SELECT * from public.test_table WHERE column1 > 10 or column2 > 10",
            ),
            (
                {
                    "table": "test_table",
                    "filter": {
                        "column1": {"filter_type": ">", "value": 10},
                        "column2": {"filter_type": "<", "value": 100},
                    },
                    "filter_type": "or",
                    "limit": "10",
                },
                "SELECT * from public.test_table WHERE column1 > 10 or column2 < 100 limit 10",
            ),
        ],
    )
    def test_query_generation(self, request_body, query, local_base_worker_emulator):
        obj = QueryBuilder(local_base_worker_emulator, request_body)
        assert obj.get_query().lower() == query.lower()
