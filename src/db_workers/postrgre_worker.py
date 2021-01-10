import json

import pandas as pd
from sqlalchemy.orm import Session

from db_workers import DatabaseWorker
from exceptions import EmptyDatabaseError


class PostgreWorker(DatabaseWorker):

    GET_TABLE_NAME_REQUEST = """
        SELECT column_name, data_type, table_schema, table_name FROM information_schema.columns
        where table_schema <> 'pg_catalog' and table_schema <> 'information_schema'
    """

    def __init__(
        self,
        local_name: str,
        local_base_worker,
    ):
        super().__init__(
            local_name,
            local_base_worker,
        )
        self.local_name = local_name
        self.local_base_worker = local_base_worker

        self.database_obj, self.engine = local_base_worker.get_database_and_connection(
            local_name
        )
        self.connection = Session(bind=self.engine)

    def download_table_list(self):
        tables = pd.read_sql(self.GET_TABLE_NAME_REQUEST, con=self.engine)

        # If database is empty
        if not len(tables):
            raise EmptyDatabaseError(
                ip=self.database_obj.ip, db_name=self.database_obj.database
            )

        tables = (
            tables.groupby(["table_schema", "table_name"])[["column_name", "data_type"]]
            .apply(self.row_dict_converter)
            .reset_index()
        )
        tables.columns = ["table_schema", "table_name", "columns"]

        for _, row in tables.iterrows():
            self.local_base_worker.write_table_params(
                table_name=row["table_name"],
                columns=row["columns"],
                database_name=self.database_obj.local_name,
                folder_name=row["table_schema"],
            )

    @staticmethod
    def row_dict_converter(row):
        # Convert row ['col1', 'type1'...] -> {'col1': 'type1'...}
        d = {}
        for l2 in row.values:
            d[l2[0]] = l2[1]
        return json.loads(json.dumps(d))

    def execute_get_data_request(self, request: str, return_type: str = "json"):
        if return_type == "json":
            return pd.read_sql(request, con=self.engine).to_json(orient="columns")
