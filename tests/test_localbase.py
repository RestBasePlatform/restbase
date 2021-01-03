from copy import deepcopy

import pytest

from localbase import LocalBaseWorker
from tables import BasesTable
from tables import TablesInfoTable
from tables import TokenTable


class TestLocalBaseWorker:
    def setup(self):
        self.test_object = LocalBaseWorker()

    def test_add_database(self, postgres_test_data):
        conn = self.test_object.db_session

        test_db_list = [postgres_test_data]

        for test_db in test_db_list:
            self.test_object.add_database(
                test_db["type"],
                test_db["description"],
                test_db["name"],
                ip=test_db["ip"],
                port=test_db["port"],
                username=test_db["username"],
                password=test_db["password"],
            )

        db_data = conn.query(BasesTable).all()

        # Compare data in base with dictionaries
        for database, test_db in zip(db_data, test_db_list):
            for key in test_db:
                assert getattr(database, key) == test_db[key]

    def test_write_table_params(self, tables_data_postgres):
        conn = self.test_object.db_session

        # WHAT!?!?!??!?!
        _tables_data_postgres = deepcopy(tables_data_postgres)
        tables_data_postgres.pop("local_name", None)
        tables_data_postgres_no_local_name = tables_data_postgres
        tables_data_postgres = deepcopy(_tables_data_postgres)

        self.test_object.write_table_params(**tables_data_postgres_no_local_name)
        table_data = conn.query(TablesInfoTable).all()[0]

        for key in tables_data_postgres_no_local_name:
            assert getattr(table_data, key) == tables_data_postgres[key]

        assert getattr(table_data, "local_name") == "_".join(
            [
                tables_data_postgres_no_local_name["database_name"],
                tables_data_postgres_no_local_name["folder_name"],
                tables_data_postgres_no_local_name["table_name"],
            ]
        )

        conn.delete(conn.query(TablesInfoTable).first())
        conn.commit()

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
        res = self.test_object.get_database(database_name="test_postgres")

        for key in postgres_test_data:
            assert getattr(res, key) == postgres_test_data[key]

    def test_add_token(self, token_for_test):
        self.test_object.add_token(
            token_for_test["token"], token_for_test["description"]
        )

        token_row = (
            self.test_object.db_session.query(TokenTable)
            .filter_by(token=token_for_test["token"])
            .first()
        )

        for key in token_for_test:
            assert getattr(token_row, key) == token_for_test[key]

    def test_add_table_for_token(self, token_for_test, tables_data_postgres):
        token_row = (
            self.test_object.db_session.query(TokenTable)
            .filter_by(token=token_for_test["token"])
            .first()
        )
        assert not token_row.granted_tables

        self.test_object.add_table_for_token(
            token_for_test["token"], local_table_name=tables_data_postgres["local_name"]
        )

        token_row = (
            self.test_object.db_session.query(TokenTable)
            .filter_by(token=token_for_test["token"])
            .first()
        )
        assert set(token_row.granted_tables) == {tables_data_postgres["local_name"]}
