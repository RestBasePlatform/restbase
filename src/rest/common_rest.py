from localbase import LocalBaseWorker
from request_validator import RequestValidator
from token_worker import TokenWorker


class RestCommon:
    def __init__(
        self,
        local_worker: LocalBaseWorker,
        token_worker: TokenWorker,
        request_validator: RequestValidator,
    ):
        self.local_worker = local_worker
        self.token_worker = token_worker
        self.request_validator = request_validator

    @staticmethod
    def get_bad_request_answer() -> list:
        return [{"status": "error", "message": "Incorrect request"}, 400]
