from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from tables import BasesTable
from tables import TablesInfoTable


class LocalBaseWorker:
    def __init__(self, ip="localhost", user="postgres", password="password"):
        self.db_session = self._get_connection(ip, user, password)

    @staticmethod
    def _get_connection(ip: str, user: str, password: str) -> Session:
        return Session(
            bind=create_engine(f"postgresql://{user}:{password}@{ip}/postgres")
        )

    def add_database(self, base_type, description, name, **con_params):
        print(base_type, description, name, con_params)
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
        print(local_name)
        if not local_name:
            local_name = "_".join([database_name, folder_name, table_name])
        new_table = TablesInfoTable(
            table_name=table_name,
            folder_name=folder_name,
            local_name=local_name,
            database_name=database_name,
            columns=columns,
        )

        self.db_session.add(new_table)
        self.db_session.commit()

    def get_table(
        self,
        database_name: str = None,
        folder_name: str = None,
        table_name: str = None,
        local_table_name: str = None,
    ):
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
