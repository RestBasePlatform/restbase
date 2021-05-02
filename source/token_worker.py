import random
import string
import typing

from exceptions import AdminTokenExistsError
from localbase import LocalBaseWorker


class TokenWorker:
    def __init__(self, local_base: LocalBaseWorker):
        self.local_base_worker = local_base

    def add_token(
        self,
        token_name: str,
        description: str = None,
        access_tables: typing.List[str] = [],
        token: str = None,
        is_admin: bool = False,
    ):
        if not token:
            token = self.generate_token()
        if is_admin and self.local_base_worker.is_main_admin_token_exists:
            raise AdminTokenExistsError
        self.local_base_worker.add_token(
            token_name, token, description, is_admin=is_admin
        )

        for table in access_tables:
            self.local_base_worker.add_table_for_token(
                token=token, local_table_name=table
            )
        return token

    def validate_access(self, token: str, local_table_name: str) -> bool:
        token_tables = self.local_base_worker.get_token_tables(token)
        return local_table_name in token_tables if token_tables else False

    @staticmethod
    def generate_token() -> str:
        return "".join(
            random.choice(string.ascii_uppercase + string.digits) for _ in range(64)
        )

    def add_admin_token(self) -> str:
        return self.add_token("main_admin", "main admin token", is_admin=True)

    def is_token_admin(self, token) -> bool:
        return token in [
            i.token for i in self.local_base_worker.get_admin_tokens_objects_list()
        ]
