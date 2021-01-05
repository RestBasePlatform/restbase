import json

import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from .db_worker import DatabaseWorker
from exceptions import EmptyDatabaseError
from localbase import LocalBaseWorker


class PostgreWorker(DatabaseWorker):

    GET_TABLE_NAME_REQUEST = """
    SELECT column_name, data_type, table_schema, table_name FROM information_schema.columns
    where table_schema <> 'pg_catalog' and table_schema <> 'information_schema'
    """

    def __init__(
        self,
        host: str,
        db_name: str,
        user: str,
        password: str,
        local_base_worker: LocalBaseWorker,
    ):
        super().__init__()
        self.db_name = db_name
        self.local_base = local_base_worker
        self.host = host
        self.engine = create_engine(f"postgresql://{user}:{password}@{host}/{db_name}")
        self.connection = Session(bind=self.engine)

    def download_table_list(self):
        tables = pd.read_sql(self.GET_TABLE_NAME_REQUEST, con=self.engine)

        # If database is empty
        if not len(tables):
            raise EmptyDatabaseError(ip=self.host, db_name=self.db_name)

        tables = (
            tables.groupby(["table_schema", "table_name"])[["column_name", "data_type"]]
            .apply(self.row_dict_converter)
            .reset_index()
        )
        print(tables.head())
        tables.columns = ["table_schema", "table_name", "columns"]

        for _, row in tables.iterrows():
            self.local_base.write_table_params(
                table_name=row["table_name"],
                columns=row["columns"],
                database_name=self.db_name,
                folder_name=row["table_schema"],
            )

    @staticmethod
    def row_dict_converter(row):
        # Convert row ['col1', 'type1'...] -> {'col1': 'type1'...}
        d = {}
        for l2 in row.values:
            d[l2[0]] = l2[1]
        print(d)
        return json.loads(json.dumps(d))
