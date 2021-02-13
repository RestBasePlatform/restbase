from flask import make_response
from flask import request
from flask_restful import Resource

from .common_rest import RestCommon
from fields import DATABASE_NAME_FIELD_NAME
from fields import FOLDER_NAME_FIELD_NAME
from fields import LOCAL_TABLE_NAME_FILED_NAME
from fields import NEW_LOCAL_TABLE_NAME_FILED_NAME
from fields import TABLE_NAME_FIELD_NAME
from fields import USER_TOKEN_FIELD_NAME
from fields import ADMIN_TOKEN_FIELD_NAME


class Table(Resource):
    def __init__(self, rest_helper: RestCommon):
        super().__init__()
        self.rest_helper = rest_helper

    def get(self):
        if not self.rest_helper.request_validator.validate_get_table_data_request(
            request
        ):
            return make_response(self.rest_helper.get_bad_request_answer())

        token = request.args.get(USER_TOKEN_FIELD_NAME)
        table_name = request.args.get(LOCAL_TABLE_NAME_FILED_NAME)
        if token not in self.rest_helper.local_worker.get_tokens_list():
            return make_response("Token not found.", 403)

        if table_name not in self.rest_helper.local_worker.get_token_tables(token):
            return make_response("Access for token denied", 403)

        return make_response(
            {
                "status": "success",
                "TableData": self.rest_helper.local_worker.get_table_params(table_name),
            }
        )

    def post(self):
        # Function to change local table name
        if not self.rest_helper.request_validator.validate_set_local_table_name_request(
            request
        ):
            return make_response(*self.rest_helper.get_bad_request_answer())

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
            return make_response("Table not found", 404)

        if (
            request.get_json().get(NEW_LOCAL_TABLE_NAME_FILED_NAME)
            in self.rest_helper.local_worker.get_local_name_list()
        ):
            return make_response(
                f"Table with local name: '{request.get_json().get(NEW_LOCAL_TABLE_NAME_FILED_NAME)}' already exists",
                409,
            )

        self.rest_helper.local_worker.change_local_name(
            "table",
            local_table_name,
            request.get_json().get(NEW_LOCAL_TABLE_NAME_FILED_NAME),
        )

        return make_response(
            {
                "status": "success",
                "new_table_name": request.get_json().get(
                    NEW_LOCAL_TABLE_NAME_FILED_NAME
                ),
            }
        )


class ListTable(Resource):
    def __init__(self, rest_helper: RestCommon):
        super().__init__()
        self.rest_helper = rest_helper

    def get(self):
        if not self.rest_helper.request_validator.validate_list_tables_request(request):
            return make_response(*self.rest_helper.get_bad_request_answer())

        if USER_TOKEN_FIELD_NAME in request.args:
            token = request.args.get(USER_TOKEN_FIELD_NAME)
        else:
            token = request.args.get(ADMIN_TOKEN_FIELD_NAME)

        if token not in self.rest_helper.local_worker.get_tokens_list():
            return make_response("Token not found.", 201)

        return make_response(
            {
                "status": "success",
                "List": self.rest_helper.local_worker.get_token_tables(token),
            }
        )
