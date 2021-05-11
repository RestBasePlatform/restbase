import json

from fastapi import HTTPException
from fastapi import Request
from fastapi import Response
from pydantic import ValidationError
from schemas import BaseHeader
from schemas import GenerateAdminToken

from . import RestBaseTokensRouter
from localbase import LocalBaseWorker
from token_worker import TokenWorker


@RestBaseTokensRouter.get("/AdminToken/GenerateFirstToken/")
async def generate_main_admin_token():
    try:
        local_base_worker = LocalBaseWorker()
        token_worker = TokenWorker(local_base_worker)
        admin_token = token_worker.add_main_admin_token()
        return admin_token
    except Exception as e:
        raise HTTPException(
            status_code=502, detail={"status": "Error", "message": str(e)}
        )


@RestBaseTokensRouter.post("/AdminToken/Generate/")
async def generate_admin_token(request: Request):
    try:
        headers = BaseHeader(**request.headers)
        body = GenerateAdminToken(**json.loads(await request.body()))
        local_base_worker = LocalBaseWorker()
        if headers.token not in [
            i.token for i in local_base_worker.get_main_admin_tokens_objects_list()
        ]:
            raise HTTPException(
                status_code=403,
                detail={"status": "Error", "message": "Permission denied"},
            )
        token_worker = TokenWorker(local_base_worker)
        admin_token = token_worker.add_admin_token(
            body.token_name,
            body.description,
        )
        return Response(content=admin_token)
    except Exception as e:
        if isinstance(e, HTTPException) or isinstance(e, ValidationError):
            raise
        raise HTTPException(
            status_code=502, detail={"status": "Error", "message": str(e)}
        )


@RestBaseTokensRouter.get("/AdminToken/List/")
async def list_admin_token(request: Request):
    headers = BaseHeader(**request.headers)
    try:
        local_base_worker = LocalBaseWorker()
        print(local_base_worker.get_main_admin_tokens_objects_list())
        if headers.token not in [
            i.token for i in local_base_worker.get_main_admin_tokens_objects_list()
        ]:
            raise HTTPException(
                status_code=403,
                detail={"status": "Error", "message": "Permission denied"},
            )
        admin_token_list = local_base_worker.get_admin_tokens_objects_list()
        return [i.prepare_for_return() for i in admin_token_list]
    except Exception as e:
        if not isinstance(e, HTTPException):
            raise HTTPException(
                status_code=502, detail={"status": "Error", "message": str(e)}
            )
        raise
