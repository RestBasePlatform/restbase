import sql_metadata

from localbase import LocalBaseWorker


class SqlQueryWorker:
    def __init__(self, query: str, local_worker: LocalBaseWorker, local_db_name: str):
        self.query = query
        self.local_worker = local_worker
        self.local_db_name = local_db_name

    def get_local_table_names(self) -> list:
        """
        :return: List with local table names
        """
        local_names = []
        for query_data in sql_metadata.get_query_tables(self.query):
            folder, table_name = query_data.split(".")
            local_table_name = self.local_worker.get_local_table_name(
                database_name=self.local_db_name,
                folder_name=folder,
                table_name=table_name,
            )

            # If table not found - add folder and table from request
            # In validate access it will raise an error
            if local_table_name:
                local_names.append(local_table_name)
            else:
                local_names.append(f"{folder}.{table_name}")
        return local_names
