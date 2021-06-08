import traceback

from fastapi import Header
from fastapi import HTTPException
from schemas import DeleteUserToken
from schemas import GenerateAdminToken

from . import RestBaseTokensRouter
from localbase import LocalBaseWorker
from token_worker import TokenWorker
from utils import make_response, validate_admin_access


@RestBaseTokensRouter.get("/AdminToken/GenerateFirstToken/")
async def generate_main_admin_token():
    try:
        local_base_worker = LocalBaseWorker()
        token_worker = TokenWorker(local_base_worker)
        admin_token = token_worker.add_main_admin_token()
        return make_response(0, {"Token": admin_token})
    except Exception as e:
        raise HTTPException(
            status_code=502, detail={"status": "Error", "message": str(e)}
        )


@RestBaseTokensRouter.post("/AdminToken/Generate/")
async def generate_admin_token(body: GenerateAdminToken, token: str = Header(None)):
    try:
        local_base_worker = LocalBaseWorker()
        if not validate_admin_access(token, local_base_worker, token_object_getter="get_main_admin_tokens_objects_list"):
            raise HTTPException(
                status_code=403,
                detail={"status": "Error", "message": "Permission denied"},
            )
        token_worker = TokenWorker(local_base_worker)
        admin_token = token_worker.add_admin_token(
            body.token_name,
            body.description,
        )
        return make_response(0, {"new_token": admin_token, "token_name": body.token_name})

    except Exception as e:  # noqa: F841
        if not isinstance(e, HTTPException):
            raise HTTPException(
                status_code=502, detail={"status": "Error", "message": str(e)}
            )
        raise


@RestBaseTokensRouter.get("/AdminToken/List/")
async def list_admin_token(token: str = Header(None)):
    try:
        local_base_worker = LocalBaseWorker()
        if not validate_admin_access(token, local_base_worker):
            raise HTTPException(
                status_code=403,
                detail={"status": "Error", "message": "Permission denied"},
            )
        admin_token_list = local_base_worker.get_admin_tokens_objects_list()
        return make_response(0, {"tokens": [i.prepare_for_return() for i in admin_token_list]})
    except Exception as e:
        if not isinstance(e, HTTPException):
            make_response(2, {"message": str(e)})
        raise


@RestBaseTokensRouter.delete("/UserToken/Delete/")
async def remove_amin_tokens(body: DeleteUserToken, token: str = Header(None)):
    try:
        local_base_worker = LocalBaseWorker()
        if not validate_admin_access(token, local_base_worker):
            raise HTTPException(
                status_code=403,
                detail={"status": "Error", "message": "Permission denied"},
            )
        local_base_worker.remove_token(body.token_name)
        make_response(0, {})
    except Exception as e:
        if not isinstance(e, HTTPException):
            raise HTTPException(
                status_code=502, detail={"status": "Error", "message": str(e)}
            )
        raise
