import datetime
from typing import List

from controller.v1.secret.sqlite_storage import SQLiteSecretWorker
from controller.v1.utils import generate_secret_token
from models.user_groups import Groups
from models.user_groups import Users

from exceptions import EntityAlreadyExistsException
from exceptions import EntityNotFoundException


def create_user_in_database(
    username: str,
    db_session,
    db_access_list: List[dict] = None,
    password: str = None,
    *,
    expired_at: datetime.datetime,
    description: str = None,
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


def add_user_to_group(user_id: int, group_id: int, db_session):
    if group_id not in list_group_id(db_session):
        raise EntityNotFoundException("Group", str(group_id))

    user_row = db_session.query(Users).filter_by(id=user_id).first()
    group_row = db_session.query(Groups).filter_by(id=group_id).first()

    user_row.groups = user_row.groups.append(group_id)
    group_row.users = user_row.users.append(user_id)

    db_session.commit()


def list_group_id(db_session):
    return [i.id for i in db_session.query(Groups)]


def list_user_login(db_session) -> List[str]:
    secret_worker = SQLiteSecretWorker()

    return [
        secret_worker.get_secret(i.username_secret_id, db_session)
        for i in db_session.query(Users)
    ]


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
        add_user_to_group(user_id, group, db_session)

    return user_id
