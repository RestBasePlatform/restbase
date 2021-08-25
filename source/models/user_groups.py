from sqlalchemy import Column
from sqlalchemy import ARRAY
from sqlalchemy import Integer
from sqlalchemy import DateTime
from sqlalchemy import JSON
from sqlalchemy import String

from . import Base


class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username_secret_id = Column(Integer, nullable=False)
    password_secret_id = Column(Integer, nullable=False)
    access_config = Column(JSON)
    groups = Column(ARRAY(Integer()))
    expired_at = Column(DateTime)
    description = Column(String)


class Groups(Base):
    __tablename__ = "groups"
    id = Column(Integer, primary_key=True)
    description = Column(String)
    access_config = Column(JSON)
