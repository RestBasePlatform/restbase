import datetime
from typing import List

from controller.v1.secret.sqlite_storage import SQLiteSecretWorker
from controller.v1.utils import generate_secret_token
from models.user_groups import Users
from models.user_groups import Groups

from exceptions import EntityAlreadyExistsException


def create_user_in_database(
    username: str,
    db_session,
    db_access_list: List[dict] = None,
    password: str = None,
    *,
    expired_at: datetime.datetime,
    description: str = None
) -> int:

    user = Users(
        username_secret_id=SQLiteSecretWorker().add_secret(username),
        password_secret_id=SQLiteSecretWorker().add_secret(password),
        access_config=db_access_list,
        groups=[],
        description=description,
        expired_at=expired_at,
    )

    db_session.add(user)
    db_session.commit()
    return user.id


def add_user_to_group(user_id: int, group_id: int):
    pass


def list_groups(db_session):
    pass


def list_user_login(db_session) -> List[str]:
    secret_worker = SQLiteSecretWorker()

    return [secret_worker.get_secret(i.username_secret_id, db_session) for i in db_session.query(Users)]


def create_user(
    username: str,
    db_session,
    db_access_list: List[dict] = None,
    groups: List[int] = None,
    password: str = None,
    **kwargs,
) -> int:
    if not password:
        password = generate_secret_token()

    if username in list_user_login(db_session):
        raise EntityAlreadyExistsException("User", username)

    user_id = create_user_in_database(
        username,
        password,
        db_access_list,
        **kwargs,
    )

    for group in groups:
        pass

    return user_id
