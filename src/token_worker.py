import random
import string
import typing

from localbase import LocalBaseWorker


class TokenWorker:
    def __init__(self, local_base: LocalBaseWorker):
        self.local_base_worker = local_base

    def add_token(
        self,
        description: str = None,
        access_tables: typing.List[str] = [],
        token: str = None,
    ):
        if not token:
            token = self.generate_token()
        self.local_base_worker.add_token(token, description)

        for table in access_tables:
            self.local_base_worker.add_table_for_token(
                token=token, local_table_name=table
            )
        return token

    def validate_access(self, token: str, local_table_name: str) -> bool:
        return local_table_name in self.local_base_worker.get_token_tables(token)

    @staticmethod
    def generate_token() -> str:
        return "".join(
            random.choice(string.ascii_uppercase + string.digits) for _ in range(64)
        )
