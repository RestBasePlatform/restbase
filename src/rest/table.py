from flask import make_response
from flask import request
from flask_restful import Resource

from .common_rest import RestCommon
from fields import LOCAL_TABLE_NAME_FILED_NAME
from fields import USER_TOKEN_FIELD_NAME


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


class ListTable(Resource):
    def __init__(self, rest_helper: RestCommon):
        super().__init__()
        self.rest_helper = rest_helper

    def get(self):
        if not self.rest_helper.request_validator.validate_list_tables_request(request):
            return make_response(self.rest_helper.get_bad_request_answer())

        token = request.args.get(USER_TOKEN_FIELD_NAME)

        if not token not in self.rest_helper.local_worker.get_tokens_list():
            return make_response("Token not found.", 403)

        return make_response(
            {
                "status": "success",
                "List": self.rest_helper.local_worker.get_token_tables(token),
            }
        )
