from flask import make_response
from flask import request
from flask_restful import Resource

from .common_rest import RestCommon
from fields import ADMIN_TOKEN_FIELD_NAME
from fields import DESCRIPTION_FIELD_NAME
from fields import USER_TOKEN_FIELD_NAME
from fields import USER_TOKEN_NAME_FIELD_NAME


class UserToken(Resource):
    def __init__(self, rest_helper: RestCommon):
        super().__init__()
        self.rest_helper = rest_helper

    def put(self):
        if not self.rest_helper.request_validator.validate_generate_user_token(request):
            self.rest_helper.logger.log_incorrect_request("/UserToken/Get/", request)
            return make_response(*self.rest_helper.get_bad_request_answer())

        token = request.headers.get(ADMIN_TOKEN_FIELD_NAME)

        if not self.rest_helper.token_worker.is_token_admin(token):
            self.rest_helper.logger.log_access_denied("/UserToken/Get/", request, token)
            return make_response("Access denied", 403)

        if (
            request.args.get(USER_TOKEN_FIELD_NAME)
            in self.rest_helper.local_worker.get_tokens_list()
        ) or (
            request.args.get(USER_TOKEN_NAME_FIELD_NAME)
            in self.rest_helper.local_worker.get_user_tokens_names_list()
        ):
            self.rest_helper.logger.log_status_execution(
                "/UserToken/Get/", token, "error", request, "Token already exists"
            )
            return make_response(
                {"status": "error", "message": "Token already exists"}, 409
            )

        try:
            new_token = self.rest_helper.token_worker.add_token(
                token=request.args.get(USER_TOKEN_FIELD_NAME),
                description=request.args.get(DESCRIPTION_FIELD_NAME),
                token_name=request.args.get(USER_TOKEN_NAME_FIELD_NAME),
            )
            self.rest_helper.logger.log_status_execution(
                "/UserToken/Get/", token, "success", request, "Token already exists"
            )
            return make_response({"status": "success", "new_token": new_token}, 201)
        except Exception as e:
            self.rest_helper.logger.log_status_execution(
                "/UserToken/Get/", token, "error", request, str(e)
            )
            return make_response({"status": "Unexpected error"}, 400)


class ListUserToken(Resource):
    def __init__(self, rest_helper: RestCommon):
        super().__init__()
        self.rest_helper = rest_helper

    def get(self):
        if not self.rest_helper.request_validator.is_admin_header_valid(
            request.headers
        ):
            self.rest_helper.logger.log_incorrect_request(
                "/ListUserToken/Get/", request
            )
            return make_response(*self.rest_helper.get_bad_request_answer())

        token = request.headers.get(ADMIN_TOKEN_FIELD_NAME)

        if not self.rest_helper.token_worker.is_token_admin(token):
            self.rest_helper.logger.log_access_denied(
                "/ListUserToken/Get/", request, token
            )
            return make_response("Access denied", 403)

        tokens = self.rest_helper.local_worker.get_user_tokens_objects_list()

        return_attrs = [
            "token",
            "description",
            "granted_tables",
            "admin_access",
            "create_date",
        ]

        response_list = []

        for token in tokens:
            response_list.append({attr: getattr(token, attr) for attr in return_attrs})

        self.rest_helper.logger.log_status_execution(
            "/ListUserToken/Get/",
            token,
            "success",
            request,
        )
        return make_response({"status": "success", "tokens": response_list}, 201)
