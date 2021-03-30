from flask import make_response
from flask import request
from flask_restful import Resource

from .common_rest import RestCommon
from fields import ADMIN_TOKEN_FIELD_NAME
from fields import DATABASE_NAME_FIELD_NAME
from fields import FOLDER_NAME_FIELD_NAME
from fields import LOCAL_TABLE_NAME_FILED_NAME
from fields import NEW_LOCAL_TABLE_NAME_FILED_NAME
from fields import TABLE_NAME_FIELD_NAME
from fields import USER_TOKEN_FIELD_NAME


class Table(Resource):
    def __init__(self, rest_helper: RestCommon):
        super().__init__()
        self.rest_helper = rest_helper

    def get(self):
        if not self.rest_helper.request_validator.validate_get_table_data_request(
            request
        ):
            self.rest_helper.logger.log_incorrect_request("/Table/Get/", request)
            return make_response(*self.rest_helper.get_bad_request_answer())

        token = request.headers.get(USER_TOKEN_FIELD_NAME)
        table_name = request.args.get(LOCAL_TABLE_NAME_FILED_NAME)
        if token not in self.rest_helper.local_worker.get_tokens_list():
            self.rest_helper.logger.log_not_found(
                "/Table/Get", token, entity="token", entity_name=token
            )
            return make_response("Token not found.", 404)

        if table_name not in self.rest_helper.local_worker.get_local_name_list():
            self.rest_helper.logger.log_not_found(
                "/Table/Get", token, entity="table", entity_name=table_name
            )
            return make_response("Table not found.", 404)

        if table_name not in self.rest_helper.local_worker.get_token_tables(token):
            self.rest_helper.logger.log_access_denied(
                "/Table/Get", token, entity="table", entity_name=table_name
            )
            return make_response("Access for token denied", 403)

        try:
            table_data = self.rest_helper.local_worker.get_table_params(table_name)
            self.rest_helper.logger.log_status_execution(
                "/Table/Get/", token, "success", request
            )
            return make_response(
                {
                    "status": "success",
                    "TableData": table_data,
                },
                200,
            )
        except Exception:
            self.rest_helper.logger.logger.exception("Error.")
            self.rest_helper.logger.log_status_execution(
                "/Table/Get/", token, "error", request
            )
            return make_response({"status": "Unexpected error"}, 400)

    def post(self):
        # Function to change local table name
        if not self.rest_helper.request_validator.validate_set_local_table_name_request(
            request
        ):
            self.rest_helper.logger.log_incorrect_request("/Table/Post/", request)
            return make_response(*self.rest_helper.get_bad_request_answer())

        token = request.headers.get(ADMIN_TOKEN_FIELD_NAME)

        if not self.rest_helper.token_worker.is_token_admin(token):
            self.rest_helper.logger.log_access_denied("/Table/Post/", token)
            return make_response("Access denied", 403)

        # Check if path to old table is correct
        if LOCAL_TABLE_NAME_FILED_NAME not in request.get_json()[TABLE_NAME_FIELD_NAME]:
            local_table_name = self.rest_helper.local_worker.get_local_table_name(
                request.get_json()[TABLE_NAME_FIELD_NAME].get(DATABASE_NAME_FIELD_NAME),
                request.get_json()[TABLE_NAME_FIELD_NAME].get(FOLDER_NAME_FIELD_NAME),
                request.get_json()[TABLE_NAME_FIELD_NAME].get(TABLE_NAME_FIELD_NAME),
            )
        else:
            local_table_name = (
                request.get_json()
                .get(TABLE_NAME_FIELD_NAME)
                .get(LOCAL_TABLE_NAME_FILED_NAME)
            )

        if local_table_name not in self.rest_helper.local_worker.get_local_name_list():
            self.rest_helper.logger.log_not_found(
                "/Table/Post/", token, entity="table", entity_name=local_table_name
            )
            return make_response("Table not found", 404)

        if (
            request.get_json().get(NEW_LOCAL_TABLE_NAME_FILED_NAME)
            in self.rest_helper.local_worker.get_local_name_list()
        ):
            self.rest_helper.logger.log_status_execution(
                "/Table/Post",
                token,
                "error",
                request,
                failure_reason=f"Table with local name: '{request.get_json().get(NEW_LOCAL_TABLE_NAME_FILED_NAME)}' "
                f"already exists",
            )
            return make_response(
                f"Table with local name: '{request.get_json().get(NEW_LOCAL_TABLE_NAME_FILED_NAME)}' already exists",
                409,
            )

        try:
            self.rest_helper.local_worker.change_local_name(
                "table",
                local_table_name,
                request.get_json().get(NEW_LOCAL_TABLE_NAME_FILED_NAME),
            )

            self.rest_helper.logger.info(
                f"Successfully renamed {local_table_name} -> "
                f"{request.get_json().get(NEW_LOCAL_TABLE_NAME_FILED_NAME)}"
            )

            return make_response(
                {
                    "status": "success",
                    "new_table_name": request.get_json().get(
                        NEW_LOCAL_TABLE_NAME_FILED_NAME
                    ),
                },
                200,
            )
        except Exception as e:
            self.rest_helper.logger.log_status_execution(
                "/Table/Post", token, "error", request, failure_reason=str(e)
            )
            return make_response(
                {
                    "status": "Unexpected error",
                },
                400,
            )


class ListTable(Resource):
    def __init__(self, rest_helper: RestCommon):
        super().__init__()
        self.rest_helper = rest_helper

    def get(self):
        if not self.rest_helper.request_validator.validate_list_tables_request(request):
            self.rest_helper.logger.log_incorrect_request("/ListTable/Get/", request)
            return make_response(*self.rest_helper.get_bad_request_answer())

        if ADMIN_TOKEN_FIELD_NAME in request.headers:
            token = request.headers.get(ADMIN_TOKEN_FIELD_NAME)
        else:
            token = request.headers.get(USER_TOKEN_FIELD_NAME)

        if token not in self.rest_helper.local_worker.get_tokens_list():
            self.rest_helper.logger.log_not_found(
                "/ListTable/Get", token, entity="token", entity_name=token
            )
            return make_response("Token not found.", 404)

        try:
            table_list = self.rest_helper.local_worker.get_token_tables(token)
            self.rest_helper.logger.log_status_execution(
                "/ListTable/Get/", token, "success", request
            )
            return make_response(
                {
                    "status": "success",
                    "List": table_list,
                },
                200,
            )

        except Exception as e:
            self.rest_helper.logger.log_status_execution(
                "/ListTable/Get/", token, "error", request, failure_reason=str(e)
            )
            return make_response(
                {
                    "status": "error",
                },
                400,
            )
