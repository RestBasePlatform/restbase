import typing

from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError

from db_workers import DatabaseWorker
from db_workers import MySQLWorker
from db_workers import PostgreWorker
from fields import DATABASE_NAME_FIELD_NAME
from fields import FOLDER_NAME_FIELD_NAME
from fields import LOCAL_TABLE_NAME_FILED_NAME
from fields import TABLE_NAME_FIELD_NAME


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
        request_body[LOCAL_TABLE_NAME_FILED_NAME]
        if LOCAL_TABLE_NAME_FILED_NAME in request_body
        else local_worker.get_local_table_name(
            database_name=request_body[DATABASE_NAME_FIELD_NAME],
            folder_name=request_body[FOLDER_NAME_FIELD_NAME],
            table_name=request_body[TABLE_NAME_FIELD_NAME],
        )
    )


def get_worker(db_type: str) -> typing.Type[DatabaseWorker]:  # noqa: TYP006
    if db_type == "postgres":
        return PostgreWorker
    elif db_type == "mysql":
        return MySQLWorker


def database_health_check(engine) -> bool:
    try:
        engine.connect()
        return True
    except OperationalError:
        return False


def get_db_engine(db_type: str, **con_params):
    if db_type == "postgres":
        return create_engine(
            f"postgresql://{con_params.get('username')}:{con_params.get('password')}@"
            f"{con_params.get('ip')}:{con_params.get('port')}/{con_params.get('database')}"
        )
    elif db_type == "mysql":
        return create_engine(
            f"mysql://{con_params.get('username')}:{con_params.get('password')}@"
            f"{con_params.get('ip')}:{con_params.get('port')}/{con_params.get('database')}"
        )


def get_bad_request_answer() -> list:
    return [{"status": "error", "message": "Incorrect request"}, 400]


def update_data_about_db_structure(local_worker):
    """
    This function iterates through all databases and refreshes its structure data (about tables/schemas)
    :param local_worker: object of LocalBaseWorker
    """
    for local_base_name in local_worker.get_db_name_list():
        db_type = local_worker.get_database_object(local_base_name).type
        worker = get_worker(db_type)(local_base_name, local_worker)
        tables = worker.download_table_list()

        # After rescan add grant access for admin tokens
        for token_obj in local_worker.get_admin_tokens_objects_list():

            token = token_obj.token

            for local_table_name in tables:
                if local_table_name not in list(token_obj.granted_tables):
                    local_worker.add_table_for_token(
                        token, local_table_name=local_table_name
                    )
