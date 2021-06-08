from fastapi import Header
from fastapi import HTTPException
from schemas import DeleteUserToken
from schemas import GenerateUserToken

from . import RestBaseTokensRouter
from localbase import LocalBaseWorker
from token_worker import TokenWorker
from utils import make_response
from utils import validate_admin_access


@RestBaseTokensRouter.post("/UserToken/Generate/")
async def generate_user_token(body: GenerateUserToken, token: str = Header(None)):
    try:
        local_base_worker = LocalBaseWorker()
        if not validate_admin_access(token, local_base_worker):
            raise HTTPException(
                status_code=403,
                detail={"status": "Error", "message": "Permission denied"},
            )
        token_worker = TokenWorker(local_base_worker)
        user_token = token_worker.add_token(
            body.token_name,
            body.description,
            token=body.token,
            access_tables=body.access_tables,
        )
        return make_response(
            0, {"new_token": user_token, "token_name": body.token_name}
        )
    except Exception as e:
        if not isinstance(e, HTTPException):
            raise HTTPException(
                status_code=502, detail={"status": "Error", "message": str(e)}
            )
        raise


@RestBaseTokensRouter.get("/UserToken/List/")
async def list_user_tokens(token: str = Header(None)):
    try:
        local_base_worker = LocalBaseWorker()
        if not validate_admin_access(token, local_base_worker):
            raise HTTPException(
                status_code=403,
                detail={"status": "Error", "message": "Permission denied"},
            )
        user_tokens = local_base_worker.get_user_tokens_objects_list()
        return make_response(
            0,
            {
                "tokens": [i.prepare_for_return() for i in user_tokens],
            },
        )
    except Exception as e:
        if not isinstance(e, HTTPException):
            raise HTTPException(
                status_code=502, detail={"status": "Error", "message": str(e)}
            )
        raise


@RestBaseTokensRouter.delete("/UserToken/Delete/")
async def remove_user_tokens(body: DeleteUserToken, token: str = Header(None)):
    try:
        local_base_worker = LocalBaseWorker()
        if not validate_admin_access(token, local_base_worker):
            raise HTTPException(
                status_code=403,
                detail={"status": "Error", "message": "Permission denied"},
            )
        local_base_worker.remove_token(body.token_name)
        return make_response(0, {})
    except Exception as e:
        if not isinstance(e, HTTPException):
            raise HTTPException(
                status_code=502, detail={"status": "Error", "message": str(e)}
            )
        raise
