import flask

from exceptions import AccessAlreadyGrantedError
from exceptions import AdminTokenExistsError
from exceptions import DatabaseAlreadyExistsError
from exceptions import TableNotFoundError
from localbase import LocalBaseWorker
from query_builders import QueryBuilder
from token_worker import TokenWorker
from utils import get_local_table_name_from_request
from utils import get_worker

app = flask.Flask("RestBase")


local_base_worker = LocalBaseWorker()
token_worker = TokenWorker(local_base_worker)


@app.route("/GetAdminToken", methods=["GET"])
def get_admin_token():
    try:
        new_token = token_worker.add_admin_token()
        return flask.make_response(new_token, 200)
    except AdminTokenExistsError:
        return flask.make_response("Token already exists", 409)


@app.route("/GenerateUserToken", methods=["GET"])
def generate_user_token():
    token = flask.request.headers.get("token")

    if not token_worker.is_token_admin(token):
        return flask.make_response("Access denied", 403)

    # If new token defined - add it to db else - generate new
    new_token = token_worker.add_token(
        token=flask.request.args.get("token"),
        description=flask.request.args.get("description"),
    )
    return flask.make_response({"status": "success", "new_token": new_token}, 201)


@app.route("/GrantTableAccess", methods=["POST"])
def grant_table_access():
    token = flask.request.headers.get("token")

    if not token_worker.is_token_admin(token):
        return flask.make_response("Access denied", 403)

    try:
        local_base_worker.add_table_for_token(
            token=flask.request.args.get("user_token"),
            local_table_name=get_local_table_name_from_request(
                flask.request.args, local_base_worker
            ),
        )

        return flask.make_response({"status": "success"}, 200)
    except (TableNotFoundError, AccessAlreadyGrantedError) as e:
        return flask.make_response({"status": "failed", "error": str(e)}, 404)


@app.route("/AddDatabase", methods=["POST"])
def add_database():
    token = flask.request.headers.get("token")

    if not token_worker.is_token_admin(token):
        return flask.make_response("Access denied", 403)

    try:
        local_base_worker.add_database(
            flask.request.args.get("base_type"),
            flask.request.args.get("description"),
            flask.request.args.get("local_name"),
            ip=flask.request.args.get("ip"),
            port=flask.request.args.get("port"),
            database=flask.request.args.get("database"),
            username=flask.request.args.get("username"),
            password=flask.request.args.get("password"),
        )

        return flask.make_response({"status": "success"}, 201)
    except (DatabaseAlreadyExistsError, ConnectionError) as e:
        return flask.make_response({"status": "failed", "error": str(e)}, 409)


@app.route("/GetData", methods=["GET"])
def get_data_request():
    # Check if token has access to table
    token = flask.request.headers.get("token")
    print(token)
    local_table_name = get_local_table_name_from_request(
        flask.request.args, local_base_worker
    )

    if local_table_name not in local_base_worker.get_local_name_list():
        response = flask.Response("Table not found")
        response.status_code = 404
        return response

    if not token_worker.validate_access(token, local_table_name):
        return flask.make_response("Access denied", 403)

    query_builder = QueryBuilder(local_base_worker, flask.request.args)
    query = query_builder.get_query()

    worker = get_worker(
        local_base_worker.get_db_type(local_table_name=local_table_name)
    )

    return_data = worker.execute_get_data_request(query)

    flask.make_response({"data": return_data}, 200)


if __name__ == "__main__":
    app.run()
