class SecretWorker:
    def add_secret(self, not_encrypted_secret_string: str, secret_session):
        raise NotImplementedError()

    def get_secret(self, secret_id: int, secret_session):
        raise NotImplementedError()

    def delete_secret(self, secret_id: int, secret_session):
        raise NotImplementedError()
