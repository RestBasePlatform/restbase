import traceback

from fastapi import HTTPException
from fastapi import Header
from schemas import GenerateUserToken

from . import RestBaseTokensRouter
from localbase import LocalBaseWorker
from token_worker import TokenWorker


@RestBaseTokensRouter.post("/UserToken/Generate/")
async def generate_user_token(body: GenerateUserToken, token: str = Header(None)):
    try:
        local_base_worker = LocalBaseWorker()
        if token not in [
            i.token for i in local_base_worker.get_admin_tokens_objects_list()
        ]:
            raise HTTPException(
                status_code=403,
                detail={"status": "Error", "message": "Permission denied"},
            )
        token_worker = TokenWorker(local_base_worker)
        user_token = token_worker.add_token(
            body.token_name,
            body.description,
            token=body.token,
            access_tables=body.access_tables
        )
        return {
            "new_token": user_token,
            "token_name": body.token_name
        }
    except Exception as e:
        if not isinstance(e, HTTPException):
            raise HTTPException(
                status_code=502, detail={"status": "Error", "message": str(e)}
            )
        raise HTTPException(
            status_code=502, detail={"status": "Error", "message": str(traceback.format_exc())}
        )
