from flask import make_response
from flask import request
from flask_restful import Resource

from .common_rest import RestCommon
from exceptions import DatabaseAlreadyExistsError
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
            return make_response(*self.rest_helper.get_bad_request_answer())

        token = request.headers.get(ADMIN_TOKEN_FIELD_NAME)

        if not self.rest_helper.token_worker.is_token_admin(token):
            return make_response("Access denied", 403)

        if (
            request.args.get(LOCAL_DATABASE_NAME_FIELD_NAME)
            not in self.rest_helper.local_worker.get_db_name_list()
        ):
            return make_response("Database not found", 404)

        return make_response(
            {
                "status": "success",
                "Data": self.rest_helper.local_worker.get_database_data(
                    request.args.get(LOCAL_DATABASE_NAME_FIELD_NAME)
                ),
            }
        )

    def put(self):
        if not self.rest_helper.request_validator.validate_add_database_request(
            request
        ):
            return make_response(*self.rest_helper.get_bad_request_answer())

        # to prevent variable not found in except block
        local_name = None

        token = request.headers.get(ADMIN_TOKEN_FIELD_NAME)

        if not self.rest_helper.token_worker.is_token_admin(token):
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

            worker = get_worker(request.args.get(DATABASE_TYPE_FIELD_NAME))(
                local_name, self.rest_helper.local_worker
            )
            tables = worker.download_table_list()
            for local_table_name in tables:
                self.rest_helper.local_worker.add_table_for_token(
                    token, local_table_name=local_table_name
                )
            return make_response({"status": "success", "local_name": local_name}, 200)
        except (DatabaseAlreadyExistsError, ConnectionError) as e:
            if local_name:
                self.rest_helper.local_worker.remove_database(local_name)

            return make_response({"status": "failed", "error": str(e)}, 500)

    def post(self):
        if not self.rest_helper.request_validator.is_admin_header_valid(
            request.headers
        ):
            return make_response(*self.rest_helper.get_bad_request_answer())

        token = request.headers.get(ADMIN_TOKEN_FIELD_NAME)

        if not self.rest_helper.token_worker.is_token_admin(token):
            return make_response("Access denied", 403)

        # Rescan database structures
        update_data_about_db_structure(self.rest_helper.local_worker)


class ListDatabase(Resource):
    def __init__(self, rest_helper: RestCommon):
        super().__init__()
        self.rest_helper = rest_helper

    def get(self):
        if not self.rest_helper.request_validator.validate_list_databases_request(
            request
        ):
            return make_response(self.rest_helpe.rget_bad_request_answer())

        token = request.headers.get(ADMIN_TOKEN_FIELD_NAME)

        if not self.rest_helper.token_worker.is_token_admin(token):
            return make_response("Access denied", 403)

        return make_response(
            {
                "status": "success",
                "List": self.rest_helper.local_worker.get_db_name_list(),
            },
            200,
        )
