from typing import List

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from exceptions import AccessAlreadyGrantedError
from exceptions import TableNotFoundError
from tables import BasesTable
from tables import TablesInfoTable
from tables import TokenTable
from utils import get_existing_data


class LocalBaseWorker:
    def __init__(
        self,
        ip="localhost",
        user="postgres",
        password="password",
        database_name="postgres",
    ):
        self.db_session = self._get_connection(ip, user, password, database_name)

    @staticmethod
    def _get_connection(
        ip: str, user: str, password: str, database_name: str
    ) -> Session:
        return Session(
            bind=create_engine(f"postgresql://{user}:{password}@{ip}/{database_name}")
        )

    def add_database(self, base_type, description, name, **con_params):
        new_database = BasesTable(
            type=base_type, description=description, name=name, **con_params
        )

        self.db_session.add(new_database)
        self.db_session.commit()

    def write_table_params(
        self,
        table_name: str,
        folder_name: str,
        database_name: str,
        columns: dict,
        local_name: str = None,
    ):

        if not local_name:
            local_name = "_".join([database_name, folder_name, table_name])

        new_table = TablesInfoTable(
            table_name=table_name,
            folder_name=folder_name,
            local_name=local_name,
            database_name=database_name,
            columns=columns,
        )

        exist_obj = (
            self.db_session.query(TablesInfoTable)
            .filter_by(local_name=new_table.local_name)
            .first()
        )
        if not exist_obj:
            self.db_session.add(new_table)
            self.db_session.commit()
        else:
            for attr in ["table_name", "folder_name", "database_name", "columns"]:
                setattr(exist_obj, attr, getattr(new_table, attr))
            self.db_session.commit()

    def get_table(
        self,
        database_name: str = None,
        folder_name: str = None,
        table_name: str = None,
        local_table_name: str = None,
    ) -> TablesInfoTable:
        return (
            self.db_session.query(TablesInfoTable)
            .filter_by(local_name=local_table_name)
            .first()
            if local_table_name
            else self.db_session.query(TablesInfoTable)
            .filter_by(
                database_name=database_name,
                folder_name=folder_name,
                table_name=table_name,
            )
            .first()
        )

    def get_database(self, database_name: str) -> BasesTable:
        return self.db_session.query(BasesTable).filter_by(name=database_name).first()

    def get_db_name_list(self) -> list:
        return get_existing_data(self.db_session, BasesTable, "name")

    def get_local_name_list(self) -> list:
        return get_existing_data(self.db_session, TablesInfoTable, "local_name")

    def add_token(self, new_token: str, description: str, is_admin=False):
        new_token = TokenTable(
            token=new_token,
            description=description,
            granted_tables=[],
            admin_access=is_admin,
        )

        self.db_session.add(new_token)
        self.db_session.commit()

    def get_tokens_list(self) -> List[TokenTable]:
        return get_existing_data(self.db_session, TokenTable)

    def add_table_for_token(
        self,
        token: str,
        database_name: str = None,
        folder_name: str = None,
        table_name: str = None,
        local_table_name: str = None,
    ):
        if not local_table_name:
            local_table_name = self.get_local_table_name(
                database_name=database_name,
                folder_name=folder_name,
                table_name=table_name,
            )
        row = self.db_session.query(TokenTable).filter_by(token=token).first()

        if not self.is_table_exists(local_table_name=local_table_name):
            raise TableNotFoundError(local_table_name)
        if local_table_name in self.get_token_tables(token):
            raise AccessAlreadyGrantedError(local_table_name)
        row.granted_tables = row.granted_tables + [local_table_name]

        self.db_session.commit()

    def get_local_table_name(
        self,
        database_name: str,
        folder_name: str,
        table_name: str,
    ):
        return (
            self.db_session.query(TablesInfoTable)
            .filter_by(
                database_name=database_name,
                folder_name=folder_name,
                table_name=table_name,
            )
            .first()
            .local_name
        )

    def get_token_tables(self, token: str) -> list:
        return (
            self.db_session.query(TokenTable)
            .filter_by(token=token)
            .first()
            .granted_tables
        )

    def is_table_exists(
        self,
        database_name: str = None,
        folder_name: str = None,
        table_name: str = None,
        local_table_name: str = None,
    ):
        return (
            (
                self.db_session.query(TablesInfoTable)
                .filter_by(local_name=local_table_name)
                .first()
                is not None
            )
            if local_table_name
            else (
                self.db_session.query(TablesInfoTable)
                .filter_by(
                    database_name=database_name,
                    folder_name=folder_name,
                    table_name=table_name,
                )
                .first()
            )
            is not None
        )

    def get_db_type(self, local_table_name: str = None, db_name: str = None) -> str:
        if local_table_name:
            db_name = (
                self.db_session.query(TablesInfoTable)
                .filter_by(local_name=local_table_name)
                .first()
                .database_name
            )
        return self.db_session.query(BasesTable).filter_by(name=db_name).first().type

    @property
    def is_main_admin_token_exists(self) -> bool:
        return "main admin token" in get_existing_data(
            self.db_session, TokenTable, "description"
        )
