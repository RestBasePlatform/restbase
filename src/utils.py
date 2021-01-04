from src.localbase import LocalBaseWorker


def validate_request_body(
    required_fields: list, request_body: dict, local_db_worker: LocalBaseWorker
) -> dict:
    # Check if all fields defined
    for f in required_fields:
        if f not in request_body:
            raise FileNotFoundError(f"Field {f} not defined in request")

    #  If columns defined - check if all exits in database
    if "columns" in request_body:
        table_data = local_db_worker.get_table(local_table_name=request_body["table"])
        for col in request_body["columns"]:
            if col not in table_data.columns:
                KeyError(f"Column {col} not found in table {request_body['table']}")

    #  If limit defined - check that it can be converter to float
    if "limit" in request_body:
        request_body["limit"] = float(request_body["limit"])

    return request_body
