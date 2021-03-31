import os

from flask import make_response
from flask import request
from flask_restful import Resource

from .common_rest import RestCommon
from fields import ADMIN_TOKEN_FIELD_NAME


class Logs(Resource):
    def __init__(self, rest_helper: RestCommon, log_dir: str = "../../logs/"):
        super().__init__()
        self.log_dir = log_dir
        self.rest_helper = rest_helper

    def get(self):
        if not self.rest_helper.request_validator.validate_admin_header_only(request):
            self.rest_helper.logger.log_incorrect_request("/Logs/Get/", request)
            return make_response(*self.rest_helper.get_bad_request_answer())

        level = None
        if "level" in request.args and request.args.get("level", "").lower() in [
            "info",
            "debug",
            "error",
        ]:
            level = request.args.get("level")

        try:
            answer = list()
            if not level:
                for f in os.listdir(self.log_dir):
                    with open("../../logs/" + f) as file:
                        data = file.read()
                        answer = answer + data.split("\n")
            else:
                with open("../../logs/" + level + ".log") as file:
                    data = file.read()
                    answer = answer + data.split("\n")
            self.rest_helper.logger.log_status_execution(
                "/Logs/Get/",
                request.headers.get(ADMIN_TOKEN_FIELD_NAME),
                "success",
                request,
            )
            return make_response(
                {
                    "status": "success",
                    "List": answer,
                },
                200,
            )
        except Exception as e:
            self.rest_helper.logger.log_status_execution(
                "/Logs/Get/",
                request.headers.get(ADMIN_TOKEN_FIELD_NAME),
                "error",
                request,
                failure_reason=str(e),
            )
            return make_response(
                {
                    "status": "Unexpected error",
                },
                400,
            )
