from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy.dialects import postgresql
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class TokenTable(Base):
    __tablename__ = "tokens"

    token = Column(String, primary_key=True)
    description = Column(String)
    granted_tables = Column(postgresql.ARRAY(postgresql.TEXT, dimensions=1))
    admin_access = Column(Boolean)
    create_date = Column(DateTime)
    name = Column(String)


class BasesTable(Base):
    __tablename__ = "bases"

    type = Column(String)
    description = Column(String)
    local_name = Column(String, primary_key=True)
    ip = Column(String)
    port = Column(String)
    username = Column(String)
    database = Column(String)
    password = Column(String)


class TablesInfoTable(Base):
    __tablename__ = "tables_info"

    table_name = Column(String)
    folder_name = Column(String)
    database_name = Column(String, ForeignKey("bases.local_name"), primary_key=True)
    local_name = Column(String, primary_key=True)
    columns = Column(postgresql.JSON)
