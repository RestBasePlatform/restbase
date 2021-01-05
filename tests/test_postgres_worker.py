import pytest

from db_workers.postrgre_worker import PostgreWorker
from exceptions import EmptyDatabaseError
from localbase import LocalBaseWorker


class TestPostgreWorker:
    def setup(self):
        self.local_worker = LocalBaseWorker(ip="postgres_internal")

    def test_download_table_list(self):
        worker = PostgreWorker(
            host="postgres_test_base",
            db_name="postgres",
            user="postgres",
            password="password",
            local_base_worker=self.local_worker,
        )

        with pytest.raises(EmptyDatabaseError):
            worker.download_table_list()
