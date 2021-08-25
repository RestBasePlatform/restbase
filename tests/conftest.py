import os
import shutil
import sys

import pytest
from fastapi.testclient import TestClient


sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../source/"))
)

from main import app


def pytest_sessionstart():
    os.system("alembic upgrade head")


@pytest.fixture(scope="function")
def test_client():
    if os.path.exists("./modules"):
        shutil.rmtree("./modules")
    shutil.copy("./source/database.db", "./database.db")
    return TestClient(app)


@pytest.fixture()
def test_module_url():
    return "https://github.com/RestBaseApi/TestModule"
