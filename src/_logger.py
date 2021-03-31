import flask
import loguru


class Logger:
    def __init__(self):
        self.logger = self._init_logger()

    @staticmethod
    def _init_logger():
        loguru.logger.add(
            "../logs/debug.log",
            format="{time} {level} {message}",
            filter=lambda record: record["level"].name == "DEBUG",
            rotation="10 MB",
        )
        loguru.logger.add(
            "../logs/info.log",
            format="{time} {level} {message}",
            filter=lambda record: record["level"].name == "INFO",
            rotation="10 MB",
        )
        loguru.logger.add(
            "../logs/error.log",
            filter=lambda record: record["level"].name == "ERROR",
            backtrace=True,
            diagnose=True,
            rotation="1 Gb",
        )
        return loguru.logger

    def log_incorrect_request(self, http_path: str, request: flask.request):
        self.logger.info(
            f"Incorrect request in '{http_path}' with:"
            f"\n-header:{request.headers}"
            f"\n-args:{request.args}"
        )

    def log_token_not_found(self, http_path: str, token: str):
        self.logger.info(f"Token {token} not found. Request: {http_path}")

    def log_access_denied(
        self, http_path: str, token: str, entity: str = None, entity_name: str = None
    ):
        """
        :param http_path:
        :param token:
        :param entity:
        :param entity_name:
        :return:
        """
        entity_message_config = {
            "table": f"Access denied to {entity_name} for token {token}. Request: {http_path}",
            "database": f"Access denied to {entity_name} for token {token}. Request: {http_path}",
        }

        self.logger.info(
            entity_message_config.get(
                entity, f"Access denied. Request: '{http_path}'. Token: '{token}'"
            )
        )

    def log_status_execution(
        self,
        http_path: str,
        token: str,
        status: str,
        request: flask.request,
        failure_reason: str = None,
    ):
        if status == "success":
            self.logger.info(
                f"Request: '{http_path}' executed successfully. Token: '{token}'."
                f"\n-header:{request.headers}"
                f"\n-args:{request.args}"
            )
        elif status == "error":
            self.logger.error(
                f"Request: '{http_path}' failed. Token: '{token}'."
                f"\n-header:{request.headers}"
                f"\n-args:{request.args}"
                f"\nReason: {failure_reason}"
            )
        else:
            raise ValueError("Status should be one of [success, error]")

    def log_not_found(
        self, http_path: str, token: str, *, entity: str, entity_name: str
    ):
        self.logger.info(
            f"{entity.capitalize()} '{entity_name}' not Found. Token: '{token}. Request: '{http_path}'"
        )

    def info(self, message: str):
        self.logger.info(message)

    def warning(self, message: str):
        self.logger.warning(message)

    def exception(self, message: str):
        self.logger.error(message)


def _init_logger():
    loguru.logger.add(
        "../logs/debug.log",
        format="{time} {level} {message}",
        filter=lambda record: record["level"].name == "DEBUG",
        rotation="10 MB",
    )
