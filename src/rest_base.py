import os

import flask

from exceptions import AccessAlreadyGrantedError
from exceptions import AdminTokenExistsError
from exceptions import DatabaseAlreadyExistsError
from exceptions import TableNotFoundError
from fields import ADMIN_TOKEN_FIELD_NAME
from fields import DATABASE_DB_NAME_FIELD_NAME
from fields import DATABASE_IP_FIELD_NAME
from fields import DATABASE_PASSWORD_FIELD_NAME
from fields import DATABASE_PORT_FIELD_NAME
from fields import DATABASE_TYPE_FIELD_NAME
from fields import DATABASE_USER_FIELD_NAME
from fields import DESCRIPTION_FIELD_NAME
from fields import LOCAL_DATABASE_NAME_FIELD_NAME
from fields import LOCAL_TABLE_NAME_FILED_NAME
from fields import USER_TOKEN_FIELD_NAME
from localbase import LocalBaseWorker
from query_builders import QueryBuilder
from request_validator import RequestValidator
from token_worker import TokenWorker
from utils import get_bad_request_answer
from utils import get_local_table_name_from_request
from utils import get_worker

app = flask.Flask("RestBase")

local_base_worker = LocalBaseWorker()

token_worker = TokenWorker(local_base_worker)
request_validator = RequestValidator()


@app.route("/GetAdminToken", methods=["GET"])
def get_admin_token():
    try:
        new_token = token_worker.add_admin_token()
        return flask.make_response(new_token, 200)
    except AdminTokenExistsError:
        return flask.make_response("Admin token already exists", 409)


@app.route("/GenerateUserToken", methods=["GET"])
def generate_user_token():
    if not request_validator.validate_generate_user_token(flask.request):
        return flask.make_response(*get_bad_request_answer())
    token = flask.request.headers.get(ADMIN_TOKEN_FIELD_NAME)

    if not token_worker.is_token_admin(token):
        return flask.make_response("Access denied", 403)

    if (
        flask.request.args.get(USER_TOKEN_FIELD_NAME)
        in local_base_worker.get_tokens_list()
    ):
        return flask.make_response(
            {"status": "error", "message": "Token already exists"}, 409
        )

    # If new token defined - add it to db else - generate
    new_token = token_worker.add_token(
        token=flask.request.args.get(USER_TOKEN_FIELD_NAME),
        description=flask.request.args.get(DESCRIPTION_FIELD_NAME),
    )
    return flask.make_response({"status": "success", "new_token": new_token}, 201)


@app.route("/GrantTableAccess", methods=["POST"])
def grant_table_access():
    if not request_validator.validate_grant_table_access(flask.request):
        return flask.make_response(*get_bad_request_answer())

    token = flask.request.headers.get(ADMIN_TOKEN_FIELD_NAME)

    if not token_worker.is_token_admin(token):
        return flask.make_response("Access denied", 403)

    try:
        local_base_worker.add_table_for_token(
            token=flask.request.args.get(USER_TOKEN_FIELD_NAME),
            local_table_name=get_local_table_name_from_request(
                flask.request.args, local_base_worker
            ),
        )

        return flask.make_response({"status": "success"}, 200)
    except (TableNotFoundError, AccessAlreadyGrantedError) as e:
        return flask.make_response({"status": "failed", "error": str(e)}, 404)


@app.route("/AddDatabase", methods=["POST"])
def add_database():
    if not request_validator.validate_add_database_request(flask.request):
        return flask.make_response(*get_bad_request_answer())

    token = flask.request.headers.get(ADMIN_TOKEN_FIELD_NAME)

    if not token_worker.is_token_admin(token):
        return flask.make_response("Access denied", 403)

    try:
        local_name = local_base_worker.add_database(
            flask.request.args.get(DATABASE_TYPE_FIELD_NAME),
            flask.request.args.get(DESCRIPTION_FIELD_NAME),
            flask.request.args.get(LOCAL_DATABASE_NAME_FIELD_NAME),
            ip=flask.request.args.get(DATABASE_IP_FIELD_NAME),
            port=flask.request.args.get(DATABASE_PORT_FIELD_NAME),
            database=flask.request.args.get(DATABASE_DB_NAME_FIELD_NAME),
            username=flask.request.args.get(DATABASE_USER_FIELD_NAME),
            password=flask.request.args.get(DATABASE_PASSWORD_FIELD_NAME),
        )

        worker = get_worker(flask.request.args.get(DATABASE_TYPE_FIELD_NAME))(
            local_name, local_base_worker
        )
        tables = worker.download_table_list()
        for local_table_name in tables:
            local_base_worker.add_table_for_token(
                token, local_table_name=local_table_name
            )
        return flask.make_response({"status": "success", "local_name": local_name}, 200)

    except (DatabaseAlreadyExistsError, ConnectionError) as e:
        return flask.make_response({"status": "failed", "error": str(e)}, 409)


@app.route("/ListDatabase", methods=["GET"])
def list_databases():
    if not request_validator.validate_list_databases_request(flask.request):
        return flask.make_response(*get_bad_request_answer())

    token = flask.request.headers.get(ADMIN_TOKEN_FIELD_NAME)

    if not token_worker.is_token_admin(token):
        return flask.make_response("Access denied", 403)

    return flask.make_response(
        {"status": "success", "List": local_base_worker.get_db_name_list()}, 200
    )


@app.route("/GetDatabaseData", methods=["GET"])
def get_database_data():
    if not request_validator.validate_get_database_data_request(flask.request):
        return flask.make_response(*get_bad_request_answer())

    token = flask.request.headers.get(ADMIN_TOKEN_FIELD_NAME)

    if not token_worker.is_token_admin(token):
        return flask.make_response("Access denied", 403)

    return flask.make_response(
        {
            "status": "success",
            "Data": local_base_worker.get_database_data(
                flask.request.args.get(LOCAL_DATABASE_NAME_FIELD_NAME)
            ),
        }
    )


@app.route("/ListTables", methods=["GET"])
def list_tables():
    if not request_validator.validate_list_tables_request(flask.request):
        return flask.make_response(*get_bad_request_answer())

    token = flask.request.args.get(USER_TOKEN_FIELD_NAME)

    if not token not in local_base_worker.get_tokens_list():
        return flask.make_response("Token not found.", 403)

    return flask.make_response(
        {"status": "success", "List": local_base_worker.get_token_tables(token)}
    )


@app.route("/GetTableData", methods=["GET"])
def get_table_data():
    if not request_validator.validate_get_table_data_request(flask.request):
        return flask.make_response(*get_bad_request_answer())

    token = flask.request.args.get(USER_TOKEN_FIELD_NAME)
    table_name = flask.request.args.get(LOCAL_TABLE_NAME_FILED_NAME)
    if token not in local_base_worker.get_tokens_list():
        return flask.make_response("Token not found.", 403)

    if table_name not in local_base_worker.get_token_tables(token):
        return flask.make_response("Access for token denied", 403)

    return flask.make_response(
        {
            "status": "success",
            "TableData": local_base_worker.get_table_params(table_name),
        }
    )


@app.route("/GetData", methods=["GET"])
def get_data_request():
    if not request_validator.validate_get_data_request(flask.request):
        return flask.make_response(*get_bad_request_answer())

    # Check if token has access to table
    token = flask.request.args.get(USER_TOKEN_FIELD_NAME)
    print(token)
    local_table_name = get_local_table_name_from_request(
        flask.request.args, local_base_worker
    )

    if not token_worker.validate_access(token, local_table_name):
        return flask.make_response("Access denied", 403)

    database_local_name = local_base_worker.get_base_of_table(
        local_table_name=local_table_name
    )
    query_builder = QueryBuilder(local_base_worker, flask.request.args)
    query = query_builder.get_query()

    worker = get_worker(
        local_base_worker.get_db_type(local_table_name=local_table_name)
    )(database_local_name, local_base_worker)

    return_data = worker.execute_get_data_request(query)

    return flask.make_response({"data": return_data}, 200)


if __name__ == "__main__":
    if os.getenv("STAGE") == "test":
        local_base_worker.add_test_token()
    app.run(host="0.0.0.0", port=54541)
