from models import Secrets

from .secret_worker import SecretWorker
from .utils import decrypt_string
from .utils import encrypt_string


class SQLiteSecretWorker(SecretWorker):
    def add_secret(self, not_encrypted_secret_string: str, db_session) -> int:
        encrypted_data = encrypt_string(not_encrypted_secret_string)
        secret = Secrets(secret=encrypted_data)
        db_session.add(secret)
        db_session.commit()
        return secret.id

    def get_secret(self, secret_id: int, db_session):
        row = db_session.query(Secrets).filter_by(id=secret_id).first()
        return decrypt_string(row.secret)