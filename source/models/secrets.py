from sqlalchemy import Column
from sqlalchemy import String
from sqlalchemy import Integer

from . import Base


class Secrets(Base):
    __tablename__ = "secrets"

    id = Column(Integer, primary_key=True, autoincrement=True)
    secret = Column(String, nullable=False)