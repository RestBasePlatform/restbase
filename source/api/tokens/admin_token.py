import traceback

from fastapi import HTTPException
from fastapi import Header
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
async def generate_admin_token(body: GenerateAdminToken, token: str = Header(None)):
    try:
        local_base_worker = LocalBaseWorker()
        if token not in [
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
        return {
            "new_token": admin_token,
            "token_name": body.token_name
        }

    except Exception as e:
        raise HTTPException(
            status_code=502, detail={"status": "Error", "message": str(traceback.format_exc())}
        )


@RestBaseTokensRouter.get("/AdminToken/List/")
async def list_admin_token(token: str = Header(None)):
    try:
        local_base_worker = LocalBaseWorker()
        if token not in [
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
