import flask

from fields import ADMIN_TOKEN_FIELD_NAME
from fields import DATABASE_DB_NAME_FIELD_NAME
from fields import DATABASE_IP_FIELD_NAME
from fields import DATABASE_NAME_FIELD_NAME
from fields import DATABASE_PASSWORD_FIELD_NAME
from fields import DATABASE_TYPE_FIELD_NAME
from fields import DATABASE_USER_FIELD_NAME
from fields import DESCRIPTION_FIELD_NAME
from fields import FOLDER_NAME_FIELD_NAME
from fields import LOCAL_DATABASE_NAME_FIELD_NAME
from fields import LOCAL_TABLE_NAME_FILED_NAME
from fields import TABLE_NAME_FIELD_NAME
from fields import USER_TOKEN_FIELD_NAME


class RequestValidator:
    @staticmethod
    def is_header_valid(headers: dict) -> bool:
        return ADMIN_TOKEN_FIELD_NAME in headers

    @staticmethod
    def is_defined_local_table_name_or_full_path(request_args: dict) -> bool:
        # check if defined local table name or full path to table
        return (LOCAL_TABLE_NAME_FILED_NAME in request_args) or (
            all(
                i in request_args
                for i in [
                    DATABASE_NAME_FIELD_NAME,
                    FOLDER_NAME_FIELD_NAME,
                    TABLE_NAME_FIELD_NAME,
                ]
            )
        )

    @staticmethod
    def is_all_database_params_defined(request_args: dict) -> bool:
        return all(
            i in request_args
            for i in [
                DATABASE_DB_NAME_FIELD_NAME,
                DATABASE_PASSWORD_FIELD_NAME,
                DATABASE_USER_FIELD_NAME,
                DATABASE_IP_FIELD_NAME,
                DATABASE_TYPE_FIELD_NAME,
            ]
        )

    def validate_generate_user_token(self, request: flask.request):
        return (
            not set(request.args.keys())
            or set(request.args.keys()) == {USER_TOKEN_FIELD_NAME}
            or set(request.args.keys()) == {DESCRIPTION_FIELD_NAME}
            or set(request.args.keys())
            == {DESCRIPTION_FIELD_NAME, USER_TOKEN_FIELD_NAME}
        ) and self.is_header_valid(request.headers)

    def validate_grant_table_access(self, request: flask.request):
        return self.is_defined_local_table_name_or_full_path(
            request.args
        ) and self.is_header_valid(request.headers)

    def validate_add_database_request(self, request: flask.request):
        is_local_database_name_defined = LOCAL_DATABASE_NAME_FIELD_NAME in request.args
        print(is_local_database_name_defined)
        print(self.is_all_database_params_defined(request.args))
        print(self.is_header_valid(request.headers))
        return (
            is_local_database_name_defined
            and self.is_all_database_params_defined(request.args)
            and self.is_header_valid(request.headers)
        )

    def validate_list_databases_request(self, request: flask.request):
        return self.is_header_valid(request.headers)

    def validate_get_database_data_request(self, request: flask.request):
        return LOCAL_TABLE_NAME_FILED_NAME in request.args and self.is_header_valid(
            request.headers
        )

    @staticmethod
    def validate_list_tables_request(request: flask.request) -> bool:
        return USER_TOKEN_FIELD_NAME in request.args

    @staticmethod
    def validate_get_table_data_request(request: flask.request):
        return (
            USER_TOKEN_FIELD_NAME in request.args
            and LOCAL_TABLE_NAME_FILED_NAME in request.args
        )

    def validate_get_data_request(self, request: flask.request):
        return (
            USER_TOKEN_FIELD_NAME in request.args
            and self.is_defined_local_table_name_or_full_path(request.args)
        )
