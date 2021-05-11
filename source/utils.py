import os
import typing

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
            f"{con_params.get('ip')}:{con_params.get('port')}/{con_params.get('database')}"
        )
    elif db_type == "mysql":
        return create_engine(
            f"mysql://{con_params.get('username')}:{con_params.get('password')}@"
            f"{con_params.get('ip')}:{con_params.get('port')}/{con_params.get('database')}"
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


def validate_request():
    pass
