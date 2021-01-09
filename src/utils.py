import re
import typing

from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError

from db_workers import DatabaseWorker
from db_workers import PostgreWorker


def validate_get_data_request_body(
    required_fields: list, request_body: dict, local_db_worker
) -> dict:
    # Check if all fields defined
    for f in required_fields:
        if f not in request_body:
            raise KeyError(f"Field {f} not defined in request")

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


def get_existing_data(
    sql_session, table_class_object, target_attr: str = None
) -> typing.List:
    if not getattr(table_class_object, "__tablename__"):
        raise ValueError("Получен неверный table_class_object.")

    data = sql_session.query(table_class_object).all()

    return [getattr(i, target_attr) for i in data] if target_attr else data


def get_local_table_name_from_request(request_body: dict, local_worker):
    return (
        request_body["local_table_name"]
        if "local_table_name" in request_body
        else local_worker.get_local_table_name(
            database_name=request_body["database"],
            folder_name=request_body["schema"],
            table_name=request_body["table"],
        )
    )


def get_worker(db_type: str) -> typing.Type[DatabaseWorker]:
    if db_type == "postgres":
        return PostgreWorker


def database_healthcheck(engine) -> bool:
    try:
        engine.connect()
        return True
    except OperationalError:
        return False


def get_db_engine(db_type: str, **con_params):
    if db_type == "postgres":
        return create_engine(
            f"postgresql://{con_params.get('username')}:{con_params.get('password')}@{con_params.get('ip')}:{con_params.get('port')}/{con_params.get('db_name')}"
        )
