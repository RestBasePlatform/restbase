import pytest


@pytest.fixture(scope="session")
def test_main_admin_token() -> str:
    return "admin-test-token"


@pytest.fixture(scope="session")
def restbase_url():
    return "http://localhost:54541/"
