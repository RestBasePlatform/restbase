from flask import make_response
from flask_restful import Resource

from .common_rest import RestCommon
from exceptions import AdminTokenExistsError


class AdminToken(Resource):
    def __init__(self, rest_helper: RestCommon):
        super().__init__()
        self.rest_helper = rest_helper

    def get(self):
        try:
            new_token = self.rest_helper.token_worker.add_admin_token()
            return make_response({"admin-token": new_token}, 200)
        except AdminTokenExistsError:
            return make_response("Admin token already exists", 409)
