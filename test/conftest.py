import sys
import os

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../source/")))


@pytest.fixture(scope="session")
def test_main_admin_token() -> str:
    return "admin-test-token"


@pytest.fixture(scope="session")
def restbase_url():
    return "http://localhost:54541/"


@pytest.fixture(scope="session")
def postgres_engine():
    db_str = "postgresql://postgres:password@internal_postgres/postgres"
    engine = create_engine(db_str)
    return engine


@pytest.fixture(scope="session")
def postgres_session(postgres_engine):
    session = Session(bind=postgres_engine)
    return session
