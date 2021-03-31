from flask import make_response
from flask import request
from flask_restful import Resource

from .common_rest import RestCommon
from fields import ADMIN_TOKEN_FIELD_NAME
from fields import DATABASE_DB_NAME_FIELD_NAME
from fields import DATABASE_IP_FIELD_NAME
from fields import DATABASE_PASSWORD_FIELD_NAME
from fields import DATABASE_PORT_FIELD_NAME
from fields import DATABASE_TYPE_FIELD_NAME
from fields import DATABASE_USER_FIELD_NAME
from fields import DESCRIPTION_FIELD_NAME
from fields import LOCAL_DATABASE_NAME_FIELD_NAME
from utils import get_worker
from utils import update_data_about_db_structure


class Database(Resource):
    def __init__(self, rest_helper: RestCommon):
        super().__init__()
        self.rest_helper = rest_helper

    def get(self):
        if not self.rest_helper.request_validator.validate_get_database_data_request(
            request
        ):
            self.rest_helper.logger.log_incorrect_request("/Database/Get/", request)
            return make_response(*self.rest_helper.get_bad_request_answer())

        token = request.headers.get(ADMIN_TOKEN_FIELD_NAME)

        if not self.rest_helper.token_worker.is_token_admin(token):
            self.rest_helper.logger.log_access_denied("/Database/Get/", token)
            return make_response("Access denied", 403)

        if (
            request.args.get(LOCAL_DATABASE_NAME_FIELD_NAME)
            not in self.rest_helper.local_worker.get_db_name_list()
        ):
            self.rest_helper.logger.log_not_found(
                "/Database/Get/",
                token,
                entity="database",
                entity_name=request.args.get(LOCAL_DATABASE_NAME_FIELD_NAME),
            )
            return make_response("Database not found", 404)

        try:
            data = self.rest_helper.local_worker.get_database_data(
                request.args.get(LOCAL_DATABASE_NAME_FIELD_NAME)
            )
            self.rest_helper.logger.log_status_execution(
                "/Database/Get/", token, "success", request
            )
            return make_response(
                {
                    "status": "success",
                    "Data": data,
                }
            )
        except:  # noqa: E722
            self.rest_helper.logger.log_status_execution(
                "/Database/Get/", token, "error", request
            )
            return make_response(
                {
                    "status": "Error",
                }
            )

    def put(self):
        if not self.rest_helper.request_validator.validate_add_database_request(
            request
        ):
            self.rest_helper.logger.log_incorrect_request("/Database/Put/", request)
            return make_response(*self.rest_helper.get_bad_request_answer())

        # to prevent variable not found in except block
        local_name = None

        token = request.headers.get(ADMIN_TOKEN_FIELD_NAME)

        if not self.rest_helper.token_worker.is_token_admin(token):
            self.rest_helper.logger.log_access_denied("/Database/Put/", token)
            return make_response("Access denied", 403)

        try:
            local_name = self.rest_helper.local_worker.add_database(
                request.args.get(DATABASE_TYPE_FIELD_NAME),
                request.args.get(DESCRIPTION_FIELD_NAME),
                request.args.get(LOCAL_DATABASE_NAME_FIELD_NAME),
                ip=request.args.get(DATABASE_IP_FIELD_NAME),
                port=request.args.get(DATABASE_PORT_FIELD_NAME),
                database=request.args.get(DATABASE_DB_NAME_FIELD_NAME),
                username=request.args.get(DATABASE_USER_FIELD_NAME),
                password=request.args.get(DATABASE_PASSWORD_FIELD_NAME),
            )
            self.rest_helper.logger.info(
                f"Database '{local_name}' successfully added to local database"
            )
            worker = get_worker(request.args.get(DATABASE_TYPE_FIELD_NAME))(
                local_name, self.rest_helper.local_worker
            )
            tables = worker.download_table_list()
            self.rest_helper.logger.info(
                f"Tables from '{local_name}' successfully downloaded"
            )
            for local_table_name in tables:
                self.rest_helper.logger.info(
                    f"Table '{local_table_name}' successfully added for admin token"
                )
                self.rest_helper.local_worker.add_table_for_token(
                    token, local_table_name=local_table_name
                )
            self.rest_helper.logger.log_status_execution(
                "/Database/Put/", token, "success", request
            )
            return make_response({"status": "success", "local_name": local_name}, 200)
        except Exception as e:
            self.rest_helper.logger.log_status_execution(
                "/Database/Put/", token, "error", request
            )
            if local_name:
                self.rest_helper.local_worker.remove_database(local_name)

            return make_response({"status": "failed", "error": str(e)}, 500)

    def post(self):
        if not self.rest_helper.request_validator.is_admin_header_valid(
            request.headers
        ):
            self.rest_helper.logger.log_incorrect_request("/Database/Post/", request)
            return make_response(*self.rest_helper.get_bad_request_answer())

        token = request.headers.get(ADMIN_TOKEN_FIELD_NAME)

        if not self.rest_helper.token_worker.is_token_admin(token):
            self.rest_helper.logger.log_access_denied("/Database/Post/", token)
            return make_response("Access denied", 403)

        # Rescan database structures
        update_data_about_db_structure(self.rest_helper.local_worker)
        self.rest_helper.logger.info(
            f"Successfully updated database structure. Started by token: '{token}'"
        )


class ListDatabase(Resource):
    def __init__(self, rest_helper: RestCommon):
        super().__init__()
        self.rest_helper = rest_helper

    def get(self):
        if not self.rest_helper.request_validator.validate_admin_header_only(request):
            self.rest_helper.logger.log_incorrect_request("/ListDatabase/Get/", request)
            return make_response(*self.rest_helper.get_bad_request_answer())

        token = request.headers.get(ADMIN_TOKEN_FIELD_NAME)

        if not self.rest_helper.token_worker.is_token_admin(token):
            self.rest_helper.logger.log_access_denied("/ListDatabase/Get/", token)
            return make_response("Access denied", 403)

        try:
            db_list = self.rest_helper.local_worker.get_db_name_list()
            self.rest_helper.logger.log_status_execution(
                "/ListDatabase/Get/", token, "success", request
            )
            return make_response(
                {
                    "status": "success",
                    "List": db_list,
                },
                200,
            )
        except Exception:
            self.rest_helper.logger.log_status_execution(
                "/ListDatabase/Get/", token, "error", request
            )

            return make_response(
                {
                    "status": "error",
                },
                400,
            )
