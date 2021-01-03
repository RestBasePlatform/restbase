import pytest

from localbase import LocalBaseWorker
from tables import BasesTable
from tables import TablesInfoTable


class TestLocalBaseWorker:
    def setup(self):
        self.test_object = LocalBaseWorker()

    def test_add_database(self, postgres_test_data):
        conn = self.test_object.db_session

        test_db_list = [
            #  1 fixture with local name, 1 for test default
            postgres_test_data, 
            postgres_test_data.pop('name', None)
        ]

        for test_db in test_db_list:
            if "name" in test_db:
                self.test_object.add_database(
                    test_db["type"],
                    test_db["description"],
                    ip=test_db["ip"],
                    port=test_db["port"],
                    username=test_db["username"],
                    password=test_db["password"],
                    name = test_db['name']
                )
            else: 
                self.test_object.add_database(
                    test_db["type"],
                    test_db["description"],
                    ip=test_db["ip"],
                    port=test_db["port"],
                    username=test_db["username"],
                    password=test_db["password"],
                )

        db_data = conn.query(BasesTable).all()

        # Compare data in base with dictionaries
        for database, test_db in zip(db_data, test_db_list):
            if "name" not in test_db:
                assert getattr(database, "key") == '_'.join(
                    [
                        test_db['database_name'],
                        test_db['folder_name'], 
                        test_db['table_name']
                    ]
                )

            for key in test_db:
                assert getattr(database, key) == test_db[key]

    def test_write_table_params(self, tables_data_postgres):
        conn = self.test_object.db_session

        self.test_object.write_table_params(**tables_data_postgres)
        table_data = conn.query(TablesInfoTable).all()[0]
        for key in tables_data_postgres:
            assert getattr(table_data, key) == tables_data_postgres[key]

    def test_get_table(self, tables_data_postgres):
        res = self.test_object.get_table(
            local_table_name=tables_data_postgres["local_name"]
        )

        for key in tables_data_postgres:
            assert getattr(res, key) == tables_data_postgres[key]

        res = self.test_object.get_table(
            database_name=tables_data_postgres["database_name"],
            folder_name=tables_data_postgres["folder_name"],
            table_name=tables_data_postgres["table_name"],
        )

        for key in tables_data_postgres:
            assert getattr(res, key) == tables_data_postgres[key]

    def test_get_database(self, postgres_test_data):
        res = self.test_object.get_database(database_name = 'test_postgres')

        for key in postgres_test_data:
            assert getattr(res, key) == postgres_test_data[key]