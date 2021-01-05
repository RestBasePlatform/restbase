from localbase import LocalBaseWorker
from tables import TokenTable
from token_worker import TokenWorker


class TestTokenWorker:
    def setup(self):
        self.local_base_worker = LocalBaseWorker(ip="postgres_internal")
        self.token_worker_fot_tests = TokenWorker(self.local_base_worker)

    def test_add_token(self):
        token = self.token_worker_fot_tests.add_token(description="test-description")
        token_obj = (
            self.local_base_worker.db_session.query(TokenTable)
            .filter_by(token=token)
            .first()
        )
        assert token_obj
        assert token_obj.description == "test-description"

        token = self.token_worker_fot_tests.add_token(
            token="test-token-2", description="test-description"
        )
        token_obj = (
            self.local_base_worker.db_session.query(TokenTable)
            .filter_by(token=token)
            .first()
        )
        assert token_obj
        assert token_obj.description == "test-description"
