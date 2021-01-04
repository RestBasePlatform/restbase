from src.localbase import LocalBaseWorker


class QueryBuilder:

    required_fields = ["table"]

    def __init__(self, local_db_worker: LocalBaseWorker, request_body: dict):
        self.local_db_worker = local_db_worker
        self.request = request_body
        self.query = "SELECT %columns% from %table_name%"

    def get_query(self) -> str:
        self.add_columns()
        self.add_table_name()

        if "filter" in self.request:
            self.apply_filter()
        if "limit" in self.request:
            self.apply_limit()
        return self.query

    def add_columns(self):
        self.query = (
            self.query.replace("%columns%", ",".join(self.request["columns"]))
            if "columns" in self.request
            else self.query.replace("%columns%", "*")
        )

    def add_table_name(self):
        table_data = self.local_db_worker.get_table(
            local_table_name=self.request["table"]
        )

        self.query = self.query.replace(
            "%table_name%", f"{table_data.folder_name}.{table_data.table_name}"
        )

    def apply_filter(self):
        self.query += " WHERE "
        filters = []
        for col in self.request["filter"]:
            filters.append(
                # concatenate columns sign and filter value (col == value)
                " ".join(
                    [
                        col,
                        self.request["filter"][col]["filter_type"],
                        self.request["filter"][col]["value"],
                    ]
                )
            )
        # Append filter if condition single - else use filter type to concatenate condition than append to request
        self.query = (
            self.query + filters[0]
            if len(filters) == 1
            else self.query + f" {self.request['filter_type']} ".join(filters)
        )

    def apply_limit(self):
        self.query += " ".join(["limit", self.request["limit"]])
