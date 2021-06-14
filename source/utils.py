import os
import typing

from fastapi.responses import JSONResponse
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError


def run_migrations():
    """
    run migrations in database with alembic
    """
    user = os.getenv("internal_db_user")
    password = os.getenv("internal_db_password")
    ip = os.getenv("internal_db_ip")
    port = os.getenv("internal_db_port")
    database = os.getenv("internal_db_database_name")

    with open("alembic.ini") as f:
        data = f.read()
    data = data.replace(
        "%URL%", f"postgresql://{user}:{password}@{ip}:{port}/{database}"
    )

    with open("alembic.ini", "w") as f:
        f.write(data)

    os.system("alembic upgrade head")


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
            f"{con_params.get('host')}:{con_params.get('port')}/{con_params.get('database')}"
        )
    elif db_type == "mysql":
        return create_engine(
            f"mysql://{con_params.get('username')}:{con_params.get('password')}@"
            f"{con_params.get('host')}:{con_params.get('port')}/{con_params.get('database')}"
        )


def get_existing_data(
    sql_session, table_class_object, target_attr: str = None
) -> typing.List:
    if not getattr(table_class_object, "__tablename__"):
        raise ValueError("Получен неверный table_class_object.")

    try:
        data = sql_session.query(table_class_object).all()
    except:  # noqa: E722
        sql_session.rollback()
        raise ConnectionError("Database transaction error")

    return [getattr(i, target_attr) for i in data] if target_attr else data


def make_response(status_code: int, data: dict):
    statuses = {"0": "Success", "1": "Processed error", "2": "Unexpected error"}

    response_data = {**{"Status": statuses[str(status_code)]}, **data}
    return JSONResponse(response_data)


def validate_admin_access(
    token, local_worker, token_object_getter: str = "get_admin_tokens_objects_list"
) -> bool:
    """
    token_object_getter - function to call for token objects list
    Return ture if token has admin access, else false
    """
    # we need kwargs because get_admin_tokens_objects_list and get_main_admin_tokens_objects_list has different args
    kwargs = (
        {"with_main_admin": True}
        if token_object_getter == "get_admin_tokens_objects_list"
        else {}
    )
    return token in [
        i.token for i in getattr(local_worker, token_object_getter)(**kwargs)
    ]
